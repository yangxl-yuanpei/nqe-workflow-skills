#!/usr/bin/env python3
"""Run guarded NQE TI/TST postprocessing from a confirmed config."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
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


def path_from(config_dir: Path, value: Any) -> Path:
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = config_dir / path
    return path.resolve()


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


def unlink_outputs(paths: Sequence[Path], dry_run: bool) -> None:
    if dry_run:
        return
    for path in paths:
        if path.exists():
            path.unlink()


def build_extract_cmd(python: str, scripts: Path, config: dict[str, Any], window: Path, output: Path, input_file: str) -> list[str]:
    cmd = [
        python,
        str(scripts / "extract_mean_force.py"),
        "--input", str(window / input_file),
        "--output", str(output),
        "--dataset-label", str(require(config, "dataset_label")),
        "--sample-label", window.name,
        "--format", str(config.get("format", "auto")),
        "--rc-index", str(config.get("rc_index", 0)),
        "--skiprows", str(config.get("skiprows", 0)),
        "--rc-scale", str(config.get("rc_scale", 1.0)),
        "--force-scale", str(config.get("force_scale", 1.0)),
        "--rc-raw-unit-label", str(config.get("rc_raw_unit_label", "input")),
        "--force-raw-unit-label", str(config.get("force_raw_unit_label", "input")),
        "--uncertainty", str(config.get("uncertainty", "sem")),
        "--confirm-parameters",
    ]
    add_opt(cmd, "--rc-column", config, "rc_column")
    add_opt(cmd, "--force-column", config, "force_column")
    add_opt(cmd, "--rc-col-index", config, "rc_col_index")
    add_opt(cmd, "--force-col-index", config, "force_col_index")
    add_opt(cmd, "--notes", config, "notes")
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
        "--output", str(output_dir / f"{window.name}.png"),
        "--summary", str(output_dir / f"{window.name}.csv"),
        "--skiprows", str(config.get("convergence_skiprows", 0)),
        "--confirm-parameters",
    ]
    for item in columns:
        try:
            index = int(item)
        except ValueError:
            cmd.extend(["--column", item])
        else:
            cmd.extend(["--col-index", str(index)])
    add_opt(cmd, "--step-column", config, "convergence_step_column")
    add_opt(cmd, "--step-col-index", config, "convergence_step_col_index")
    add_opt(cmd, "--running-window", config, "convergence_running_window")
    add_opt(cmd, "--x-scale", config, "convergence_x_scale")
    add_opt(cmd, "--y-scale", config, "convergence_y_scale")
    add_opt(cmd, "--xlabel", config, "convergence_xlabel")
    add_opt(cmd, "--ylabel", config, "convergence_ylabel")
    add_flag(cmd, "--auto-equilibration", as_bool(config, "convergence_auto_equilibration", False))
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
        "--zero", str(config.get("zero", "first")),
        "--free-energy-scale", str(config.get("free_energy_scale", 1.0)),
        "--free-energy-unit-label", str(config.get("free_energy_unit_label", "au")),
        "--confirm-parameters",
    ]
    add_opt(cmd, "--notes", config, "notes")
    return cmd


def build_plot_cmds(python: str, scripts: Path, config: dict[str, Any], mean_force: Path, free_energy: Path, out: Path) -> list[list[str]]:
    dataset = str(require(config, "dataset_label"))
    direction = str(require(config, "integration_direction"))
    return [
        [
            python, str(scripts / "plot_mean_force.py"),
            "--curve", f"file={mean_force},dataset={dataset},label=MeanForce,marker=o",
            "--output", str(out / "mean_force.png"),
            "--rc-order", direction,
            "--confirm-parameters",
        ],
        [
            python, str(scripts / "plot_free_energy.py"),
            "--curve", f"file={free_energy},dataset={dataset},label=FreeEnergy,marker=o",
            "--output", str(out / "free_energy.png"),
            "--rc-order", direction,
            "--free-energy-unit-label", str(config.get("free_energy_plot_unit_label", "au")),
            "--confirm-parameters",
        ],
    ]


def build_tst_cmd(python: str, scripts: Path, config: dict[str, Any], free_energy: Path, rates: Path) -> list[str]:
    cmd = [
        python,
        str(scripts / "compute_tst_rates.py"),
        "--input", str(free_energy),
        "--output", str(rates),
        "--elementary-step", str(require(config, "elementary_step")),
        "--dataset-label", str(require(config, "dataset_label")),
        "--rc-index", str(config.get("rc_index", 0)),
        "--temperature", str(require(config, "temperature_K")),
        "--free-energy-column", str(config.get("free_energy_column", "free_energy_au")),
        "--free-energy-unit", str(config.get("free_energy_unit", "auto")),
        "--reactant-mode", str(require(config, "reactant_mode")),
        "--ts-mode", str(require(config, "ts_mode")),
        "--prefactor-model", str(config.get("prefactor_model", "kBT_over_h")),
        "--prefactor-units", str(config.get("prefactor_units", "s^-1")),
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

    config_dir = config_path.parent
    repo_root = Path(__file__).resolve().parents[2]
    root = path_from(config_dir, require(config, "sampling_output_root"))
    out = path_from(config_dir, config.get("output_dir", "nqe-postprocess-output"))
    scripts = script_paths(config, config_dir)
    python = str(config.get("python", sys.executable))
    input_file = str(config.get("input_file", "energy.dat"))
    windows = discover_windows(root, input_file, str(config.get("window_glob", "*")))
    run_convergence = as_bool(config, "run_convergence_diagnostics", False)
    convergence_dir = path_from(config_dir, config.get("convergence_output_dir", out / "convergence"))

    out.mkdir(parents=True, exist_ok=True)
    if run_convergence and not args.dry_run:
        convergence_dir.mkdir(parents=True, exist_ok=True)
    mean_force = out / "mean_force_table.csv"
    free_energy = out / "free_energy_profile.csv"
    rates = out / "tst_rates.csv"
    summary = out / "summary.json"
    unlink_outputs([mean_force, free_energy, rates, summary], args.dry_run)

    commands: list[list[str]] = []
    if run_convergence:
        for window in windows:
            run(build_convergence_cmd(python, repo_root, config, window, convergence_dir, input_file), args.dry_run, commands)
    for window in windows:
        run(build_extract_cmd(python, scripts, config, window, mean_force, input_file), args.dry_run, commands)
    run(build_integrate_cmd(python, scripts, config, mean_force, free_energy), args.dry_run, commands)
    if as_bool(config, "plots", True):
        for cmd in build_plot_cmds(python, scripts, config, mean_force, free_energy, out):
            run(cmd, args.dry_run, commands)
    if as_bool(config, "compute_tst", True):
        run(build_tst_cmd(python, scripts, config, free_energy, rates), args.dry_run, commands)

    payload = {
        "config": str(config_path),
        "dataset_label": str(require(config, "dataset_label")),
        "window_count": len(windows),
        "windows": [{"sample_label": window.name, "input": str(window / input_file)} for window in windows],
        "outputs": {
            "convergence_dir": str(convergence_dir) if run_convergence else None,
            "mean_force_table": str(mean_force),
            "free_energy_profile": str(free_energy),
            "tst_rates": str(rates) if as_bool(config, "compute_tst", True) else None,
            "mean_force_plot": str(out / "mean_force.png") if as_bool(config, "plots", True) else None,
            "free_energy_plot": str(out / "free_energy.png") if as_bool(config, "plots", True) else None,
        },
        "commands": commands,
        "notes": [
            "All numerical choices come from the confirmed config.",
            "Convergence diagnostics remain screening outputs; review plots and do not treat suggested cutoffs as proof of equilibration.",
            "Inspect reactant and transition-state selections before treating rates as final.",
        ],
    }
    if not args.dry_run:
        summary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote summary to {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
