#!/usr/bin/env python3
"""Run guarded NQE TI/TST postprocessing from a confirmed config."""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if raw[:1].isspace() and raw.strip() and not raw.lstrip().startswith("#"):
            raise ValueError(
                f"Unsupported indented or nested config line {line_number}: {raw!r}. "
                "Use flat key: value YAML or JSON only."
            )
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].rstrip()
        if ":" not in line:
            raise ValueError(f"Unsupported config line {line_number}: {raw!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Missing config key on line {line_number}")
        config[key] = parse_scalar(value)
    return config


def load_config(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return load_simple_yaml(path)


def parse_listish(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def as_bool(config: dict[str, Any], key: str, default: bool) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    raise ValueError(f"{key} must be true or false")


def require(config: dict[str, Any], key: str) -> Any:
    value = config.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required config field: {key}")
    return value


def has_value(config: dict[str, Any], key: str) -> bool:
    value = config.get(key)
    return value is not None and value != ""


def require_explicit(config: dict[str, Any], key: str, problems: list[str], reason: str) -> None:
    if not has_value(config, key):
        problems.append(f"{key}: {reason}")


def value_contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        upper = value.upper()
        return "TODO" in upper or "USER_APPROVAL" in upper or "PLACEHOLDER" in upper
    if isinstance(value, (list, tuple)):
        return any(value_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(value_contains_placeholder(item) for item in value.values())
    return False


STOP_AFTER_ORDER = {
    "plot": -1,
    "convergence": 0,
    "extraction": 1,
    "integration": 2,
    "all": 3,
}


def get_stop_after(config: dict[str, Any]) -> str:
    stop_after = str(config.get("stop_after", "all")).strip().lower()
    if stop_after not in STOP_AFTER_ORDER:
        allowed = ", ".join(STOP_AFTER_ORDER)
        raise ValueError(f"stop_after must be one of: {allowed}")
    return stop_after


def normalize_rc_order(value: Any) -> str:
    return str(value).strip().lower()


def reaches_stage(stop_after: str, stage: str) -> bool:
    if stop_after == "plot":
        return False
    return STOP_AFTER_ORDER[stop_after] >= STOP_AFTER_ORDER[stage]


def preflight_config(config: dict[str, Any]) -> None:
    """Reject configs that rely on implicit column or physical defaults."""
    problems: list[str] = []
    stop_after = get_stop_after(config)

    for key, value in config.items():
        if value_contains_placeholder(value):
            problems.append(f"{key}: placeholder value remains in runnable config")

    common_required = {"dataset_label": "dataset label must be user-confirmed"}
    if stop_after != "plot":
        common_required.update({
            "sampling_output_root": "input window root must be user-confirmed",
            "input_file": "sampling output file name must be user-confirmed",
            "window_glob": "window discovery pattern must be user-confirmed",
        })
    for key, reason in common_required.items():
        require_explicit(config, key, problems, reason)

    if stop_after == "plot":
        plot_mean_force = as_bool(config, "plot_mean_force", False) if has_value(config, "plot_mean_force") else False
        plot_free_energy = as_bool(config, "plot_free_energy", False) if has_value(config, "plot_free_energy") else False
        require_explicit(config, "plot_mean_force", problems, "plot-only mean-force plotting choice must be explicit")
        require_explicit(config, "plot_free_energy", problems, "plot-only free-energy plotting choice must be explicit")
        require_explicit(config, "plot_rc_order", problems, "plot-only RC order must be user-confirmed")
        if has_value(config, "plot_rc_order") and normalize_rc_order(config["plot_rc_order"]) not in {"ascending", "descending", "input"}:
            problems.append("plot_rc_order: use ascending, descending, or input")
        if not plot_mean_force and not plot_free_energy:
            problems.append("plot-only mode requires at least one of plot_mean_force or plot_free_energy to be true")
        if plot_mean_force:
            require_explicit(config, "mean_force_table", problems, "plot_mean_force requires an existing mean-force CSV path")
            require_explicit(config, "mean_force_y_column", problems, "plot_mean_force requires an explicit y-column")
        if plot_free_energy:
            require_explicit(config, "free_energy_profile", problems, "plot_free_energy requires an existing free-energy CSV path")
            require_explicit(config, "free_energy_y_column", problems, "plot_free_energy requires an explicit y-column")
            require_explicit(config, "free_energy_plot_unit_label", problems, "plot_free_energy requires an explicit plotted free-energy unit label")

    if has_value(config, "integration_direction") and has_value(config, "plot_rc_order"):
        integration_direction = normalize_rc_order(config["integration_direction"])
        plot_rc_order = normalize_rc_order(config["plot_rc_order"])
        if integration_direction in {"ascending", "descending"} and plot_rc_order in {"ascending", "descending"} and plot_rc_order != integration_direction:
            problems.append(
                "plot_rc_order conflicts with integration_direction; update plot_rc_order to the confirmed plotting/integration direction "
                "or use plot_rc_order: input only when the CSV row order is the reviewed intended direction"
            )

    if stop_after == "convergence" and not as_bool(config, "run_convergence_diagnostics", False):
        problems.append("stop_after: convergence requires run_convergence_diagnostics: true")

    if as_bool(config, "run_convergence_diagnostics", False):
        require_explicit(config, "convergence_columns", problems, "convergence screening columns must be explicit")
        require_explicit(config, "convergence_skiprows", problems, "convergence skip-row handling must be explicit")
        require_explicit(config, "convergence_auto_equilibration", problems, "auto-equilibration screening choice must be explicit")
        require_explicit(config, "convergence_plot", problems, "convergence plot/summary-only choice must be explicit")
        if has_value(config, "convergence_use_row_index_as_step"):
            row_index_axis = as_bool(config, "convergence_use_row_index_as_step", False)
            if row_index_axis and (has_value(config, "convergence_step_column") or has_value(config, "convergence_step_col_index")):
                problems.append(
                    "convergence_use_row_index_as_step: do not combine row-index x-axis with convergence_step_column or convergence_step_col_index"
                )

    if reaches_stage(stop_after, "extraction"):
        extraction_required = {
        "format": "parser mode must be explicit; do not rely on auto-detection",
        "rc_index": "reaction-coordinate index must be user-confirmed",
        "skiprows": "equilibration/skip-row handling must be user-confirmed",
        "rc_scale": "reaction-coordinate unit conversion must be user-confirmed",
        "force_scale": "mean-force unit conversion must be user-confirmed",
        "rc_raw_unit_label": "raw reaction-coordinate unit label must be user-confirmed",
        "force_raw_unit_label": "raw mean-force unit label must be user-confirmed",
        "uncertainty": "uncertainty policy must be user-confirmed",
        }
        for key, reason in extraction_required.items():
            require_explicit(config, key, problems, reason)

        fmt = str(config.get("format", "")).strip().lower()
        if fmt == "auto":
            problems.append("format: use phy_quant or table explicitly; runner preflight refuses parser auto-detection")
        elif fmt == "phy_quant":
            require_explicit(config, "rc_column", problems, "headered extraction requires an explicit reaction-coordinate column")
            require_explicit(config, "force_column", problems, "headered extraction requires an explicit mean-force column")
        elif fmt == "table":
            require_explicit(config, "rc_col_index", problems, "table extraction requires an explicit zero-based reaction-coordinate column index")
            require_explicit(config, "force_col_index", problems, "table extraction requires an explicit zero-based mean-force column index")
        elif fmt:
            problems.append(f"format: unsupported parser mode {fmt!r}; use phy_quant or table")

    if reaches_stage(stop_after, "integration"):
        integration_required = {
        "integration_direction": "TI integration direction must be user-confirmed",
        "zero": "free-energy zero reference must be user-confirmed",
        "free_energy_scale": "free-energy conversion factor must be user-confirmed",
        "free_energy_unit_label": "free-energy unit label must be user-confirmed",
        }
        for key, reason in integration_required.items():
            require_explicit(config, key, problems, reason)

    if stop_after == "all":
        final_stage_required = {
        "plots": "plot generation choice must be explicit",
        "compute_tst": "TST computation choice must be explicit",
        }
        for key, reason in final_stage_required.items():
            require_explicit(config, key, problems, reason)

    if stop_after == "all" and has_value(config, "compute_tst") and as_bool(config, "compute_tst", False):
        tst_required = {
            "elementary_step": "elementary step label must be user-confirmed",
            "temperature_K": "temperature must be user-confirmed",
            "free_energy_column": "free-energy column must be user-confirmed",
            "free_energy_unit": "free-energy unit must be user-confirmed",
            "reactant_mode": "reactant/reference state selection must be user-confirmed",
            "ts_mode": "transition-state selection must be user-confirmed",
            "prefactor_model": "prefactor model must be user-confirmed",
            "prefactor_units": "prefactor/rate units must be user-confirmed",
        }
        for key, reason in tst_required.items():
            require_explicit(config, key, problems, reason)

        reactant_mode = str(config.get("reactant_mode", "")).strip().lower()
        ts_mode = str(config.get("ts_mode", "")).strip().lower()
        prefactor_model = str(config.get("prefactor_model", "")).strip()
        if reactant_mode == "rc":
            require_explicit(config, "reactant_rc", problems, "reactant_mode=rc requires reactant_rc")
        if reactant_mode == "value":
            require_explicit(config, "reactant_value", problems, "reactant_mode=value requires reactant_value")
        if ts_mode == "rc":
            require_explicit(config, "ts_rc", problems, "ts_mode=rc requires ts_rc")
        if ts_mode == "value":
            require_explicit(config, "ts_value", problems, "ts_mode=value requires ts_value")
        if prefactor_model == "custom_numeric":
            require_explicit(config, "prefactor_value", problems, "custom_numeric prefactor requires prefactor_value")
        if prefactor_model == "adsorption_flux_n_v_S":
            require_explicit(config, "density", problems, "adsorption_flux_n_v_S requires density")
            require_explicit(config, "mean_speed", problems, "adsorption_flux_n_v_S requires mean_speed")
            require_explicit(config, "site_area", problems, "adsorption_flux_n_v_S requires site_area")

    if problems:
        formatted = "\n".join(f"- {problem}" for problem in problems)
        raise ValueError(
            "Refusing to run postprocess runner because the config relies on implicit column or physical defaults:\n"
            f"{formatted}"
        )


def path_from(config_dir: Path, value: Any) -> Path:
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = config_dir / path
    return path.resolve()


def load_per_window_skiprows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"sample_label", "skiprows"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"per-window skiprows file {path} is missing required column(s): "
                + ", ".join(sorted(missing))
            )
        mapping: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            sample = (row.get("sample_label") or "").strip()
            skiprows = (row.get("skiprows") or "").strip()
            reason = (row.get("reason") or "").strip()
            if not sample:
                raise ValueError(f"Missing sample_label in per-window skiprows file {path} line {line_number}")
            if sample in mapping:
                raise ValueError(f"Duplicate sample_label {sample!r} in per-window skiprows file {path}")
            try:
                parsed_skiprows = int(skiprows)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid skiprows value for sample_label {sample!r} in {path}: {skiprows!r}"
                ) from exc
            if parsed_skiprows < 0:
                raise ValueError(f"skiprows must be non-negative for sample_label {sample!r} in {path}")
            mapping[sample] = {"skiprows": str(parsed_skiprows), "reason": reason}
    return mapping


def script_paths(config: dict[str, Any], config_dir: Path) -> Path:
    if config.get("ti_tst_scripts_dir"):
        scripts = path_from(config_dir, config["ti_tst_scripts_dir"])
    else:
        scripts = Path(__file__).resolve().parents[2] / "ti-tst-rate" / "scripts"
    if not scripts.exists():
        raise FileNotFoundError(f"ti-tst-rate scripts not found: {scripts}")
    return scripts


def parse_window_sort_key(path: Path) -> tuple[int, float | str]:
    name = path.name
    try:
        if name.startswith("_"):
            return (0, -float(name[1:]))
        return (0, float(name))
    except ValueError:
        return (1, name)


def discover_windows(root: Path, input_file: str, window_glob: str) -> list[Path]:
    candidates = [p for p in root.glob(window_glob) if p.is_dir() and (p / input_file).exists()]
    if (root / input_file).exists():
        candidates.append(root)
    windows = sorted(set(candidates), key=parse_window_sort_key)
    if len(windows) < 2:
        raise ValueError(f"Need at least two windows containing {input_file!r} under {root}")
    return windows


def add_opt(cmd: list[str], flag: str, config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if value is not None and value != "":
        cmd.extend([flag, str(value)])


def add_flag(cmd: list[str], flag: str, enabled: bool) -> None:
    if enabled:
        cmd.append(flag)


def run(cmd: list[str], dry_run: bool, commands: list[list[str]]) -> None:
    commands.append(cmd)
    print("$ " + " ".join(shlex.quote(part) for part in cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def generated_output_paths(commands: Sequence[Sequence[str]]) -> list[Path]:
    paths: list[Path] = []
    for cmd in commands:
        for index, item in enumerate(cmd[:-1]):
            if item in {"--output", "--summary"}:
                paths.append(Path(cmd[index + 1]).expanduser())
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        resolved = path.resolve()
        key = str(resolved)
        if key not in seen:
            seen.add(key)
            unique.append(resolved)
    return unique


def verify_generated_outputs(paths: Sequence[Path], run_started_at: float) -> list[dict[str, Any]]:
    status: list[dict[str, Any]] = []
    stale_or_missing: list[str] = []
    # Some filesystems round mtimes coarsely; this tolerance avoids false stale reports.
    freshness_cutoff = run_started_at - 2.0
    for path in paths:
        exists = path.exists()
        item: dict[str, Any] = {
            "path": str(path),
            "exists": exists,
            "size_bytes": None,
            "mtime": None,
            "fresh_for_this_run": False,
        }
        if exists:
            stat = path.stat()
            item["size_bytes"] = stat.st_size
            item["mtime"] = stat.st_mtime
            item["fresh_for_this_run"] = stat.st_mtime >= freshness_cutoff
        if not item["fresh_for_this_run"]:
            stale_or_missing.append(str(path))
        status.append(item)
    if stale_or_missing:
        raise RuntimeError(
            "Generated output freshness check failed for: "
            + ", ".join(stale_or_missing)
            + ". Do not report old or missing outputs as results from this run."
        )
    return status


def unlink_outputs(paths: Sequence[Path], dry_run: bool) -> None:
    if dry_run:
        return
    for path in paths:
        if path.exists():
            path.unlink()


def guard_existing_output_dir(output_dir: Path, allow_existing: bool, dry_run: bool) -> None:
    """Refuse to run into a non-empty output directory unless explicitly allowed."""
    if dry_run or allow_existing or not output_dir.exists():
        return
    existing = sorted(output_dir.iterdir(), key=lambda item: item.name)
    if not existing:
        return
    preview = ", ".join(item.name for item in existing[:5])
    if len(existing) > 5:
        preview += f", ... ({len(existing)} entries total)"
    raise ValueError(
        f"Refusing to write into non-empty output_dir: {output_dir}. "
        f"Existing entries: {preview}. Use a fresh output_dir, inspect and clean the old outputs, "
        "or set allow_existing_output_dir: true only after user-approved reuse/cleanup."
    )


def build_extract_cmd(
    python: str,
    scripts: Path,
    config: dict[str, Any],
    window: Path,
    output: Path,
    input_file: str,
    skiprows: str | None = None,
    skip_reason: str | None = None,
) -> list[str]:
    effective_skiprows = str(config.get("skiprows") if skiprows is None else skiprows)
    notes = str(config.get("notes", ""))
    if skip_reason:
        suffix = f"per-window skiprows={effective_skiprows}; reason={skip_reason}"
        notes = f"{notes}; {suffix}" if notes else suffix
    cmd = [
        python,
        str(scripts / "extract_mean_force.py"),
        "--input", str(window / input_file),
        "--output", str(output),
        "--dataset-label", str(require(config, "dataset_label")),
        "--sample-label", window.name,
        "--format", str(require(config, "format")),
        "--rc-index", str(require(config, "rc_index")),
        "--skiprows", effective_skiprows,
        "--rc-scale", str(require(config, "rc_scale")),
        "--force-scale", str(require(config, "force_scale")),
        "--rc-raw-unit-label", str(require(config, "rc_raw_unit_label")),
        "--force-raw-unit-label", str(require(config, "force_raw_unit_label")),
        "--uncertainty", str(require(config, "uncertainty")),
        "--confirm-parameters",
    ]
    add_opt(cmd, "--rc-column", config, "rc_column")
    add_opt(cmd, "--force-column", config, "force_column")
    add_opt(cmd, "--rc-col-index", config, "rc_col_index")
    add_opt(cmd, "--force-col-index", config, "force_col_index")
    if notes:
        cmd.extend(["--notes", notes])
    return cmd


def build_convergence_cmd(
    python: str,
    repo_root: Path,
    config: dict[str, Any],
    window: Path,
    output_dir: Path,
    input_file: str,
) -> list[str]:
    columns = parse_listish(config.get("convergence_columns"))
    if not columns:
        raise ValueError(
            "run_convergence_diagnostics=true requires convergence_columns "
            "(comma-separated names or zero-based numeric indices)"
        )
    cmd = [
        python,
        str(repo_root / "chmc-cpihmc-sampling" / "scripts" / "analyze_phy_quant_convergence.py"),
        "--input", str(window / input_file),
        "--summary", str(output_dir / f"{window.name}.csv"),
        "--skiprows", str(config.get("convergence_skiprows", 0)),
        "--confirm-parameters",
    ]
    if as_bool(config, "convergence_plot", True):
        cmd.extend(["--output", str(output_dir / f"{window.name}.png")])
    for item in columns:
        try:
            index = int(item)
        except ValueError:
            cmd.extend(["--column", item])
        else:
            cmd.extend(["--col-index", str(index)])
    add_opt(cmd, "--step-column", config, "convergence_step_column")
    add_opt(cmd, "--step-col-index", config, "convergence_step_col_index")
    add_flag(cmd, "--use-row-index-as-step", as_bool(config, "convergence_use_row_index_as_step", False))
    add_opt(cmd, "--running-window", config, "convergence_running_window")
    add_opt(cmd, "--x-scale", config, "convergence_x_scale")
    add_opt(cmd, "--y-scale", config, "convergence_y_scale")
    add_opt(cmd, "--xlabel", config, "convergence_xlabel")
    add_opt(cmd, "--ylabel", config, "convergence_ylabel")
    add_flag(cmd, "--auto-equilibration", as_bool(config, "convergence_auto_equilibration", False))
    add_flag(cmd, "--no-plot", not as_bool(config, "convergence_plot", True))
    return cmd


def build_integrate_cmd(python: str, scripts: Path, config: dict[str, Any], mean_force: Path, free_energy: Path) -> list[str]:
    cmd = [
        python,
        str(scripts / "integrate_free_energy.py"),
        "--input", str(mean_force),
        "--output", str(free_energy),
        "--dataset-label", str(require(config, "dataset_label")),
        "--rc-index", str(config.get("rc_index", 0)),
        "--integration-direction", str(require(config, "integration_direction")),
        "--zero", str(require(config, "zero")),
        "--free-energy-scale", str(require(config, "free_energy_scale")),
        "--free-energy-unit-label", str(require(config, "free_energy_unit_label")),
        "--confirm-parameters",
    ]
    add_opt(cmd, "--notes", config, "notes")
    return cmd


def add_plot_style_options(cmd: list[str], config: dict[str, Any], prefix: str = "plot") -> None:
    for key, flag in [
        (f"{prefix}_xlabel", "--xlabel"),
        (f"{prefix}_ylabel", "--ylabel"),
        (f"{prefix}_title", "--title"),
        (f"{prefix}_width", "--width"),
        (f"{prefix}_height", "--height"),
        (f"{prefix}_dpi", "--dpi"),
        (f"{prefix}_linewidth", "--linewidth"),
        (f"{prefix}_markersize", "--markersize"),
    ]:
        add_opt(cmd, flag, config, key)
    if has_value(config, f"{prefix}_grid"):
        add_flag(cmd, "--grid", as_bool(config, f"{prefix}_grid", False))


def build_plot_cmds(python: str, scripts: Path, config: dict[str, Any], mean_force: Path, free_energy: Path, out: Path) -> list[list[str]]:
    dataset = str(require(config, "dataset_label"))
    direction = normalize_rc_order(config["plot_rc_order"] if has_value(config, "plot_rc_order") else require(config, "integration_direction"))
    commands: list[list[str]] = []
    plot_mean_force = as_bool(config, "plot_mean_force", True)
    plot_free_energy = as_bool(config, "plot_free_energy", True)
    if plot_mean_force:
        cmd = [
            python, str(scripts / "plot_mean_force.py"),
            "--curve", f"file={mean_force},dataset={dataset},label={config.get('mean_force_curve_label', 'MeanForce')},marker=o",
            "--output", str(config.get("mean_force_plot_output", out / "mean_force.png")),
            "--rc-order", direction,
            "--confirm-parameters",
        ]
        add_opt(cmd, "--y-column", config, "mean_force_y_column")
        add_plot_style_options(cmd, config, "mean_force_plot")
        commands.append(cmd)
    if plot_free_energy:
        cmd = [
            python, str(scripts / "plot_free_energy.py"),
            "--curve", f"file={free_energy},dataset={dataset},label={config.get('free_energy_curve_label', 'FreeEnergy')},marker=o",
            "--output", str(config.get("free_energy_plot_output", out / "free_energy.png")),
            "--rc-order", direction,
            "--free-energy-unit-label", str(
                config["free_energy_plot_unit_label"]
                if has_value(config, "free_energy_plot_unit_label")
                else require(config, "free_energy_unit_label")
            ),
            "--confirm-parameters",
        ]
        add_opt(cmd, "--y-column", config, "free_energy_y_column")
        add_plot_style_options(cmd, config, "free_energy_plot")
        commands.append(cmd)
    return commands


def build_tst_cmd(python: str, scripts: Path, config: dict[str, Any], free_energy: Path, rates: Path) -> list[str]:
    cmd = [
        python,
        str(scripts / "compute_tst_rates.py"),
        "--input", str(free_energy),
        "--output", str(rates),
        "--elementary-step", str(require(config, "elementary_step")),
        "--dataset-label", str(require(config, "dataset_label")),
        "--rc-index", str(require(config, "rc_index")),
        "--temperature", str(require(config, "temperature_K")),
        "--free-energy-column", str(require(config, "free_energy_column")),
        "--free-energy-unit", str(require(config, "free_energy_unit")),
        "--reactant-mode", str(require(config, "reactant_mode")),
        "--ts-mode", str(require(config, "ts_mode")),
        "--prefactor-model", str(require(config, "prefactor_model")),
        "--prefactor-units", str(require(config, "prefactor_units")),
        "--confirm-parameters",
    ]
    for key, flag in [
        ("reactant_rc", "--reactant-rc"),
        ("reactant_value", "--reactant-value"),
        ("ts_rc", "--ts-rc"),
        ("ts_value", "--ts-value"),
        ("prefactor_value", "--prefactor-value"),
        ("density", "--density"),
        ("mean_speed", "--mean-speed"),
        ("site_area", "--site-area"),
        ("notes", "--notes"),
    ]:
        add_opt(cmd, flag, config, key)
    return cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run NQE TI/TST postprocessing from a confirmed config.")
    parser.add_argument("config", help="Flat YAML or JSON config.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config).expanduser().resolve()
    config = load_config(config_path)
    if not as_bool(config, "parameters_confirmed", False):
        raise ValueError("Refusing to run until config contains parameters_confirmed: true")
    preflight_config(config)
    stop_after = get_stop_after(config)

    config_dir = config_path.parent
    repo_root = Path(__file__).resolve().parents[2]
    out = path_from(config_dir, config.get("output_dir", "nqe-postprocess-output"))
    scripts = script_paths(config, config_dir)
    python = str(config.get("python", sys.executable))
    if has_value(config, "mean_force_plot_output"):
        config["mean_force_plot_output"] = str(path_from(config_dir, config["mean_force_plot_output"]))
    if has_value(config, "free_energy_plot_output"):
        config["free_energy_plot_output"] = str(path_from(config_dir, config["free_energy_plot_output"]))

    input_file = ""
    windows: list[Path] = []
    if stop_after != "plot":
        root = path_from(config_dir, require(config, "sampling_output_root"))
        input_file = str(require(config, "input_file"))
        windows = discover_windows(root, input_file, str(require(config, "window_glob")))
    run_convergence = as_bool(config, "run_convergence_diagnostics", False)
    convergence_dir = path_from(config_dir, config.get("convergence_output_dir", out / "convergence"))
    per_window_skiprows: dict[str, dict[str, str]] = {}
    if has_value(config, "per_window_skiprows_file"):
        per_window_skiprows_path = path_from(config_dir, config["per_window_skiprows_file"])
        per_window_skiprows = load_per_window_skiprows(per_window_skiprows_path)
        window_names = {window.name for window in windows}
        unknown = sorted(set(per_window_skiprows).difference(window_names))
        if unknown:
            raise ValueError(
                "per_window_skiprows_file contains sample_label value(s) not discovered as windows: "
                + ", ".join(unknown)
            )

    allow_existing_output_dir = as_bool(config, "allow_existing_output_dir", False)
    guard_existing_output_dir(out, allow_existing_output_dir, args.dry_run)
    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)
    if run_convergence and not args.dry_run:
        convergence_dir.mkdir(parents=True, exist_ok=True)
    if stop_after == "plot":
        mean_force = (
            path_from(config_dir, require(config, "mean_force_table"))
            if as_bool(config, "plot_mean_force", False)
            else out / "mean_force_table.csv"
        )
        free_energy = (
            path_from(config_dir, require(config, "free_energy_profile"))
            if as_bool(config, "plot_free_energy", False)
            else out / "free_energy_profile.csv"
        )
        if as_bool(config, "plot_mean_force", False) and not mean_force.exists():
            raise FileNotFoundError(f"mean_force_table does not exist: {mean_force}")
        if as_bool(config, "plot_free_energy", False) and not free_energy.exists():
            raise FileNotFoundError(f"free_energy_profile does not exist: {free_energy}")
    else:
        mean_force = out / "mean_force_table.csv"
        free_energy = out / "free_energy_profile.csv"
    rates = out / "tst_rates.csv"
    summary = out / ("plot_summary.json" if stop_after == "plot" else "summary.json")
    if stop_after == "plot":
        unlink_outputs([summary], args.dry_run)
    else:
        unlink_outputs([mean_force, free_energy, rates, summary], args.dry_run)

    run_started_at = time.time()
    commands: list[list[str]] = []
    if run_convergence:
        for window in windows:
            run(build_convergence_cmd(python, repo_root, config, window, convergence_dir, input_file), args.dry_run, commands)
    if reaches_stage(stop_after, "extraction"):
        for window in windows:
            override = per_window_skiprows.get(window.name)
            run(
                build_extract_cmd(
                    python,
                    scripts,
                    config,
                    window,
                    mean_force,
                    input_file,
                    skiprows=override["skiprows"] if override else None,
                    skip_reason=override.get("reason") if override else None,
                ),
                args.dry_run,
                commands,
            )
    if reaches_stage(stop_after, "integration"):
        run(build_integrate_cmd(python, scripts, config, mean_force, free_energy), args.dry_run, commands)
    if stop_after in {"all", "plot"}:
        if stop_after == "plot" or as_bool(config, "plots", False):
            if not args.dry_run:
                if as_bool(config, "plot_mean_force", True):
                    Path(str(config.get("mean_force_plot_output", out / "mean_force.png"))).parent.mkdir(parents=True, exist_ok=True)
                if as_bool(config, "plot_free_energy", True):
                    Path(str(config.get("free_energy_plot_output", out / "free_energy.png"))).parent.mkdir(parents=True, exist_ok=True)
            for cmd in build_plot_cmds(python, scripts, config, mean_force, free_energy, out):
                run(cmd, args.dry_run, commands)
        if stop_after == "all" and as_bool(config, "compute_tst", False):
            run(build_tst_cmd(python, scripts, config, free_energy, rates), args.dry_run, commands)

    generated_output_status: list[dict[str, Any]] = []
    if not args.dry_run:
        generated_output_status = verify_generated_outputs(generated_output_paths(commands), run_started_at)

    notes = [
        "All numerical choices come from the confirmed config.",
        "Convergence diagnostics remain screening outputs; review plots or CSV summaries and do not treat suggested cutoffs as proof of equilibration.",
    ]
    if reaches_stage(stop_after, "integration"):
        notes.append("Inspect integration direction, zero reference, units, and sign convention before using the free-energy profile.")
    if stop_after == "plot":
        notes.append("Plot-only mode visualizes existing CSV files; it does not approve convergence, TI choices, TST state selection, or rates.")
    if stop_after == "all" and as_bool(config, "compute_tst", False):
        notes.append("Inspect reactant and transition-state selections before treating rates as final.")

    payload = {
        "config": str(config_path),
        "dataset_label": str(require(config, "dataset_label")),
        "stop_after": stop_after,
        "window_count": len(windows),
        "windows": [{"sample_label": window.name, "input": str(window / input_file)} for window in windows],
        "outputs": {
            "convergence_dir": str(convergence_dir) if run_convergence else None,
            "mean_force_table": str(mean_force) if reaches_stage(stop_after, "extraction") or (stop_after == "plot" and as_bool(config, "plot_mean_force", False)) else None,
            "free_energy_profile": str(free_energy) if reaches_stage(stop_after, "integration") or (stop_after == "plot" and as_bool(config, "plot_free_energy", False)) else None,
            "tst_rates": str(rates) if stop_after == "all" and as_bool(config, "compute_tst", False) else None,
            "mean_force_plot": str(config.get("mean_force_plot_output", out / "mean_force.png")) if (stop_after == "plot" or (stop_after == "all" and as_bool(config, "plots", False))) and as_bool(config, "plot_mean_force", True) else None,
            "free_energy_plot": str(config.get("free_energy_plot_output", out / "free_energy.png")) if (stop_after == "plot" or (stop_after == "all" and as_bool(config, "plots", False))) and as_bool(config, "plot_free_energy", True) else None,
        },
        "per_window_skiprows": per_window_skiprows,
        "commands": commands,
        "generated_output_status": generated_output_status,
        "notes": notes,
    }
    if not args.dry_run:
        summary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote summary to {summary}")
    else:
        print(f"DRY RUN: generated {len(commands)} command(s); no commands were executed and no output files were written.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
