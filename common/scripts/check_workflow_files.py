#!/usr/bin/env python3
"""Minimal static file-shape checks for the NQE workflow skills repository.

These checks are intentionally simple. They look for missing files, obvious
placeholders, malformed JSON/CSV, missing headers/keywords, and common error
markers. They do not perform deep software validation, convergence analysis,
parameter-quality review, physical interpretation, or production-readiness
certification.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass
class Finding:
    level: str
    scope: str
    message: str


class CheckContext:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[Finding] = []

    def add(self, level: str, scope: str, message: str) -> None:
        self.findings.append(Finding(level.upper(), scope, message))

    def pass_(self, scope: str, message: str) -> None:
        self.add("PASS", scope, message)

    def warn(self, scope: str, message: str) -> None:
        self.add("WARN", scope, message)

    def fail(self, scope: str, message: str) -> None:
        self.add("FAIL", scope, message)

    def existing(self, *names: str) -> list[Path]:
        return [self.root / name for name in names if (self.root / name).exists()]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_file(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    lowered = {name.lower() for name in names}
    children = root.iterdir() if root.exists() and root.is_dir() else []
    for child in children:
        if child.name.lower() in lowered:
            return child
    return None


def check_required_files(ctx: CheckContext, names: Iterable[str], scope: str) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for name in names:
        path = find_file(ctx.root, [name])
        if path is None:
            ctx.fail(scope, f"Missing required file: {name}")
        else:
            found[name] = path
            ctx.pass_(scope, f"Found {name}")
    return found


def warn_placeholders(ctx: CheckContext, paths: Iterable[Path]) -> None:
    for path in paths:
        if path.exists() and path.is_file():
            text = read_text(path)
            if "TODO_USER_APPROVAL" in text:
                ctx.warn(path.name, "Contains TODO_USER_APPROVAL placeholders; replace or explicitly approve before running.")
            if "REDACTED_" in text:
                ctx.warn(path.name, "Contains REDACTED_* placeholders; do not treat as runnable production input.")


def warn_error_markers(ctx: CheckContext, paths: Iterable[Path]) -> None:
    markers = ["error", "fatal", "nan", "segmentation fault", "traceback", "not converged", "failed"]
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = read_text(path).lower()
        hits = sorted({m for m in markers if m in text})
        if hits:
            ctx.warn(path.name, f"Found possible error markers: {', '.join(hits)}")


def parse_key_value_lines(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            result[parts[0]] = " ".join(parts[1:])
    return result



def first_path_token(value: str | None) -> str | None:
    if value is None:
        return None
    token = value.split()[0].strip().strip("'\"") if value.split() else ""
    return token or None


def resolve_declared_path(root: Path, value: str | None) -> Path | None:
    token = first_path_token(value)
    if token is None:
        return None
    path = Path(token).expanduser()
    if not path.is_absolute():
        path = root / path
    return path


def parse_abacus_stru_resources(path: Path) -> dict[str, list[str]]:
    sections = {
        "ATOMIC_SPECIES",
        "NUMERICAL_ORBITAL",
        "LATTICE_CONSTANT",
        "LATTICE_VECTORS",
        "ATOMIC_POSITIONS",
        "NUMERICAL_DESCRIPTOR",
    }
    result: dict[str, list[str]] = {"pseudopotentials": [], "orbitals": [], "sections": []}
    current: str | None = None
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        upper = line.split()[0].upper()
        if upper in sections:
            current = upper
            result["sections"].append(upper)
            continue
        parts = line.split()
        if current == "ATOMIC_SPECIES" and len(parts) >= 3:
            result["pseudopotentials"].append(parts[2])
        elif current == "NUMERICAL_ORBITAL" and parts:
            result["orbitals"].append(parts[0])
    return result


def check_declared_file(ctx: CheckContext, base: Path, filename: str, scope: str, kind: str, missing_level: str = "FAIL") -> None:
    if "TODO_USER_APPROVAL" in filename or filename.startswith("REDACTED_"):
        ctx.warn(scope, f"{kind} file is still a placeholder: {filename}")
        return
    candidate = Path(filename)
    if not candidate.is_absolute():
        candidate = base / candidate
    if candidate.exists() and candidate.is_file():
        ctx.pass_(scope, f"Found {kind} file: {filename}")
    else:
        message = f"Missing {kind} file referenced by STRU: {candidate}"
        if missing_level.upper() == "WARN":
            ctx.warn(scope, message)
        else:
            ctx.fail(scope, message)


def load_json(ctx: CheckContext, path: Path, scope: str) -> Any | None:
    try:
        data = json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001 - report parser failure to user.
        ctx.fail(scope, f"Invalid JSON in {path.name}: {exc}")
        return None
    ctx.pass_(scope, f"JSON parsed: {path.name}")
    return data


def require_json_keys(ctx: CheckContext, data: Any, keys: Iterable[str], scope: str) -> None:
    if not isinstance(data, dict):
        ctx.fail(scope, "Expected top-level JSON object.")
        return
    for key in keys:
        if key in data:
            ctx.pass_(scope, f"Found JSON key: {key}")
        else:
            ctx.warn(scope, f"Missing or version-specific JSON key: {key}")


def check_csv_header(ctx: CheckContext, path: Path, required: Iterable[str], scope: str) -> None:
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as handle:
            reader = csv.reader(handle)
            header = next(reader)
    except StopIteration:
        ctx.fail(scope, f"Empty CSV: {path.name}")
        return
    except Exception as exc:  # noqa: BLE001
        ctx.fail(scope, f"Could not read CSV {path.name}: {exc}")
        return
    normalized = [item.strip() for item in header]
    for col in required:
        if col in normalized:
            ctx.pass_(scope, f"Found CSV column: {col}")
        else:
            ctx.fail(scope, f"Missing CSV column: {col}")


def check_abacus(ctx: CheckContext) -> None:
    files = check_required_files(ctx, ["INPUT", "STRU", "KPT"], "ABACUS input")
    warn_placeholders(ctx, files.values())
    input_path = files.get("INPUT")
    kv: dict[str, str] = {}
    if input_path:
        kv = parse_key_value_lines(input_path)
        common_keywords = ["calculation", "suffix", "basis_type", "pseudo_dir", "stru_file", "kpoint_file", "ecutwfc", "scf_thr"]
        basis_type = kv.get("basis_type", "").lower()
        if basis_type and basis_type not in {"pw", "plane_wave", "plane-wave"}:
            common_keywords.append("orbital_dir")
        for key in common_keywords:
            if key in kv:
                ctx.pass_("INPUT", f"Found keyword: {key}")
            else:
                ctx.warn("INPUT", f"Missing commonly required keyword: {key}")
        if kv.get("cal_force") == "1":
            ctx.pass_("INPUT", "Force output requested with cal_force 1")
        else:
            ctx.warn("INPUT", "cal_force is not explicitly 1; DFT labeling usually needs forces.")
        if "cal_stress" not in kv:
            ctx.warn("INPUT", "cal_stress not documented; virial/stress labels may be missing for MLFF training.")

        for key, expected_name in [("stru_file", "STRU"), ("kpoint_file", "KPT")]:
            declared = resolve_declared_path(ctx.root, kv.get(key, expected_name))
            if declared is None:
                ctx.warn("INPUT", f"Could not resolve {key}")
            elif declared.exists():
                ctx.pass_("INPUT", f"{key} resolves to existing path: {declared.name}")
            else:
                ctx.fail("INPUT", f"{key} points to missing path: {declared}")

    stru_path = files.get("STRU")
    if stru_path:
        resources = parse_abacus_stru_resources(stru_path)
        for section in ["ATOMIC_SPECIES", "LATTICE_CONSTANT", "LATTICE_VECTORS", "ATOMIC_POSITIONS"]:
            if section in resources["sections"]:
                ctx.pass_("STRU", f"Found section: {section}")
            else:
                ctx.fail("STRU", f"Missing section: {section}")
        if resources["pseudopotentials"]:
            ctx.pass_("STRU", f"Found {len(resources['pseudopotentials'])} pseudopotential reference(s).")
        else:
            ctx.warn("STRU", "No pseudopotential files parsed from ATOMIC_SPECIES.")
        pseudo_dir = resolve_declared_path(ctx.root, kv.get("pseudo_dir")) if kv else None
        if resources["pseudopotentials"]:
            pseudo_missing_level = "FAIL"
            if pseudo_dir is None:
                ctx.warn("INPUT", "pseudo_dir is not documented; checking the run directory as a fallback.")
                pseudo_dir = ctx.root
                pseudo_missing_level = "WARN"
            elif not pseudo_dir.exists() or not pseudo_dir.is_dir():
                ctx.fail("INPUT", f"pseudo_dir does not exist or is not a directory: {pseudo_dir}")
                pseudo_dir = None
            else:
                ctx.pass_("INPUT", f"pseudo_dir exists: {pseudo_dir}")
            if pseudo_dir is not None:
                for pseudo in resources["pseudopotentials"]:
                    check_declared_file(ctx, pseudo_dir, pseudo, "STRU", "pseudopotential", pseudo_missing_level)

        if resources["orbitals"]:
            ctx.pass_("STRU", f"Found {len(resources['orbitals'])} numerical orbital reference(s).")
            orbital_dir = resolve_declared_path(ctx.root, kv.get("orbital_dir")) if kv else None
            orbital_missing_level = "FAIL"
            if orbital_dir is None:
                ctx.warn("INPUT", "STRU references NUMERICAL_ORBITAL files but INPUT has no orbital_dir keyword; checking the run directory as a fallback.")
                orbital_dir = ctx.root
                orbital_missing_level = "WARN"
            elif not orbital_dir.exists() or not orbital_dir.is_dir():
                ctx.fail("INPUT", f"orbital_dir does not exist or is not a directory: {orbital_dir}")
                orbital_dir = None
            else:
                ctx.pass_("INPUT", f"orbital_dir exists: {orbital_dir}")
            if orbital_dir is not None:
                for orbital in resources["orbitals"]:
                    check_declared_file(ctx, orbital_dir, orbital, "STRU", "orbital", orbital_missing_level)
        else:
            basis_type = kv.get("basis_type", "").lower() if kv else ""
            if basis_type and basis_type not in {"pw", "plane_wave", "plane-wave"}:
                ctx.warn("STRU", "No NUMERICAL_ORBITAL files parsed; confirm whether this basis requires orbital files.")

    kpt_path = files.get("KPT")
    if kpt_path:
        kpt_lines = [line.strip() for line in read_text(kpt_path).splitlines() if line.strip() and not line.strip().startswith("#")]
        if kpt_lines:
            ctx.pass_("KPT", "KPT file is non-empty.")
        else:
            ctx.fail("KPT", "KPT file has no non-comment content.")

    output_candidates = list(ctx.root.glob("*.log")) + list(ctx.root.glob("OUT.*/*")) + list(ctx.root.glob("running*"))
    if output_candidates:
        warn_error_markers(ctx, output_candidates)
    else:
        ctx.warn("ABACUS output", "No obvious ABACUS output/log files found; input-only check performed.")


def check_dpgen(ctx: CheckContext) -> None:
    param = find_file(ctx.root, ["param.json", "run_param.json"])
    machine = find_file(ctx.root, ["machine.json"])
    if param is None:
        ctx.fail("DP-GEN input", "Missing param.json or run_param.json")
    else:
        warn_placeholders(ctx, [param])
        data = load_json(ctx, param, "DP-GEN param")
        if data is not None:
            require_json_keys(ctx, data, ["type_map", "mass_map", "model_devi_jobs"], "DP-GEN param")
            if "model_devi_f_trust_lo" in str(data) or "trust_lo" in str(data):
                ctx.pass_("DP-GEN param", "Trust-level fields appear to be documented.")
            else:
                ctx.warn("DP-GEN param", "No obvious trust-level fields found; confirm version-specific field names.")
    if machine is None:
        ctx.warn("DP-GEN input", "Missing machine.json; local/manual checks only.")
    else:
        warn_placeholders(ctx, [machine])
        data = load_json(ctx, machine, "DP-GEN machine")
        if data is not None:
            require_json_keys(ctx, data, ["api_version"], "DP-GEN machine")


def check_deepmd(ctx: CheckContext) -> None:
    input_json = find_file(ctx.root, ["input.json"])
    if input_json is None:
        ctx.warn("DeePMD input", "Missing input.json; checking logs only if present.")
    else:
        warn_placeholders(ctx, [input_json])
        data = load_json(ctx, input_json, "DeePMD input")
        if data is not None:
            require_json_keys(ctx, data, ["model", "learning_rate", "loss", "training"], "DeePMD input")
    lcurve = find_file(ctx.root, ["lcurve.out"])
    if lcurve is None:
        ctx.warn("DeePMD output", "Missing lcurve.out; cannot inspect training curve shape.")
    else:
        lines = [line.split() for line in read_text(lcurve).splitlines() if line.strip()]
        if len(lines) < 2:
            ctx.fail("lcurve.out", "Not enough rows for header plus data.")
        else:
            ctx.pass_("lcurve.out", "Found header and data rows.")
            final = lines[-1]
            bad = [x for x in final if x.lower() in {"nan", "inf", "-inf"}]
            if bad:
                ctx.fail("lcurve.out", f"Final row contains non-finite values: {bad}")
            else:
                ctx.pass_("lcurve.out", "Final row has no literal NaN/Inf tokens.")
    logs = list(ctx.root.glob("*.log"))
    warn_error_markers(ctx, logs)


def check_lammps(ctx: CheckContext) -> None:
    script = find_file(ctx.root, ["input.lammps", "in.lammps", "in.lmp"])
    if script is None:
        ctx.fail("LAMMPS input", "Missing input.lammps/in.lammps/in.lmp")
        return
    warn_placeholders(ctx, [script])
    text = read_text(script).lower()
    for token in ["units", "atom_style", "read_data", "pair_style", "timestep", "thermo", "run"]:
        if token in text:
            ctx.pass_("LAMMPS input", f"Found command/token: {token}")
        else:
            ctx.warn("LAMMPS input", f"Missing common command/token: {token}")
    if "deepmd" in text:
        ctx.pass_("LAMMPS input", "DeepMD pair style/model coupling appears in script.")
    else:
        ctx.warn("LAMMPS input", "No deepmd token found; confirm intended force field.")
    logs = list(ctx.root.glob("log*")) + list(ctx.root.glob("*.log"))
    if logs:
        warn_error_markers(ctx, logs)
    else:
        ctx.warn("LAMMPS output", "No log files found; input-only check performed.")


def check_plumed(ctx: CheckContext) -> None:
    plumed = find_file(ctx.root, ["input.plumed", "plumed.dat", "input.plumed_1"])
    if plumed is None:
        ctx.fail("PLUMED input", "Missing input.plumed/plumed.dat/input.plumed_1")
        return
    warn_placeholders(ctx, [plumed])
    text = read_text(plumed).upper()
    if "UNITS" in text:
        ctx.pass_("PLUMED input", "Units are explicitly documented.")
    else:
        ctx.warn("PLUMED input", "No UNITS line found; confirm PLUMED/LAMMPS unit convention.")
    if "PRINT" in text:
        ctx.pass_("PLUMED input", "PRINT output is configured.")
    else:
        ctx.warn("PLUMED input", "No PRINT action found; CV diagnostics may be missing.")
    if re.search(r"ATOMS\s*=", text):
        ctx.pass_("PLUMED input", "Found atom-index based CV/action.")
    else:
        ctx.warn("PLUMED input", "No ATOMS= entry found; confirm CV definition.")
    if any(token in text for token in ["RESTRAINT", "UPPER_WALLS", "LOWER_WALLS", "METAD"]):
        ctx.warn("PLUMED input", "Bias/restraint action found; confirm center, force constant, stride, and units.")


def check_chmc(ctx: CheckContext) -> None:
    files = check_required_files(ctx, ["INPUT", "STRU"], "CHMC/CPIHMC input")
    beads = find_file(ctx.root, ["BEADS"])
    if beads:
        ctx.pass_("CHMC/CPIHMC input", "Found optional BEADS file.")
        files["BEADS"] = beads
    else:
        ctx.warn("CHMC/CPIHMC input", "No BEADS file found; acceptable only if not running path-integral mode or beads are generated elsewhere.")
    warn_placeholders(ctx, files.values())
    input_path = files.get("INPUT")
    if input_path:
        kv = parse_key_value_lines(input_path)
        for key in ["Simu_Type", "Steps", "Temp", "Deep_Pot_Model", "Rxn_Coord", "Hybrid_Monte_Carlo_Ratio"]:
            if key in kv:
                ctx.pass_("INPUT", f"Found keyword: {key}")
            else:
                ctx.warn("INPUT", f"Missing or version-specific keyword: {key}")
    phy = find_file(ctx.root, ["PHY_QUANT", "energy.dat"])
    if phy:
        header = read_text(phy).splitlines()[0].split()
        if {"RxnCoord", "MeanForce"}.issubset(set(header)) or any(h.startswith("RxnCoord_") for h in header):
            ctx.pass_("CHMC/CPIHMC output", "Found reaction-coordinate/mean-force style columns.")
        else:
            ctx.warn("CHMC/CPIHMC output", "No obvious RxnCoord/MeanForce columns in first row.")
    else:
        ctx.warn("CHMC/CPIHMC output", "No PHY_QUANT or energy.dat found; input-only check performed.")


def check_ti_tst(ctx: CheckContext) -> None:
    mean_force = find_file(ctx.root, ["mean_force_table.csv", "result.csv", "result.dat", "meanforce.csv"])
    free_energy = find_file(ctx.root, ["free_energy_profile.csv", "free_energy.csv", "free_energy.dat"])
    rates = find_file(ctx.root, ["tst_rates.csv", "rate.csv"])
    if mean_force:
        check_csv_header(ctx, mean_force, ["dataset_label", "rc_index", "reaction_coordinate_au", "mean_force_au"], "Mean-force table")
    else:
        ctx.warn("TI/TST", "No mean-force table found.")
    if free_energy:
        check_csv_header(ctx, free_energy, ["dataset_label", "rc_index", "reaction_coordinate_au", "free_energy_au"], "Free-energy profile")
        text = read_text(free_energy)
        if "free_energy_converted" in text:
            ctx.pass_("Free-energy profile", "Converted free-energy column is available.")
    else:
        ctx.warn("TI/TST", "No free-energy profile found.")
    if rates:
        check_csv_header(ctx, rates, ["elementary_step", "dataset_label", "temperature_K"], "TST rates")
    else:
        ctx.warn("TI/TST", "No TST rate table found.")


def check_kmc(ctx: CheckContext) -> None:
    events = find_file(ctx.root, ["kmc_events.json", "events.json"])
    params = find_file(ctx.root, ["kmc_parameters.json", "parameters.json"])
    if events is None:
        ctx.warn("KMC input", "Missing kmc_events.json/events.json.")
    else:
        warn_placeholders(ctx, [events])
        data = load_json(ctx, events, "KMC events")
        if isinstance(data, dict):
            if any(key in data for key in ["events", "event_list"]):
                ctx.pass_("KMC events", "Found event list container.")
            else:
                ctx.warn("KMC events", "No obvious events/event_list key found.")
    if params is None:
        ctx.warn("KMC input", "Missing kmc_parameters.json/parameters.json.")
    else:
        warn_placeholders(ctx, [params])
        data = load_json(ctx, params, "KMC parameters")
        if isinstance(data, dict):
            if isinstance(data.get("environment"), dict) and "temperature_K" in data["environment"]:
                ctx.pass_("KMC parameters", "Found environment.temperature_K.")
            else:
                ctx.warn("KMC parameters", "Missing environment.temperature_K.")
            if isinstance(data.get("simulation_controls"), dict) and "stopping_rule" in data["simulation_controls"]:
                ctx.pass_("KMC parameters", "Found simulation_controls.stopping_rule.")
            else:
                ctx.warn("KMC parameters", "Missing simulation_controls.stopping_rule.")


def summarize(ctx: CheckContext, output: str) -> int:
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for finding in ctx.findings:
        counts[finding.level] = counts.get(finding.level, 0) + 1
    if output == "json":
        print(json.dumps({"root": str(ctx.root), "counts": counts, "findings": [finding.__dict__ for finding in ctx.findings]}, indent=2))
    else:
        print(f"Checked: {ctx.root}")
        print(f"Summary: PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
        for finding in ctx.findings:
            print(f"[{finding.level}] {finding.scope}: {finding.message}")
    return 2 if counts["FAIL"] else (1 if counts["WARN"] else 0)


CHECKS: dict[str, Callable[[CheckContext], None]] = {
    "abacus": check_abacus,
    "dpgen": check_dpgen,
    "deepmd": check_deepmd,
    "lammps": check_lammps,
    "plumed": check_plumed,
    "chmc": check_chmc,
    "ti-tst": check_ti_tst,
    "kmc": check_kmc,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run minimal static input/output file-shape checks for NQE workflow software stages.")
    parser.add_argument("--software", choices=sorted(CHECKS), required=True, help="Software/stage-specific checker to run.")
    parser.add_argument("--path", default=".", help="Directory containing the files to check. Default: current directory.")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format. Default: text.")
    parser.add_argument("--allow-warnings", action="store_true", help="Return exit code 0 when only warnings are present.")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    ctx = CheckContext(root)
    if not root.exists() or not root.is_dir():
        ctx.fail("path", "Path does not exist or is not a directory.")
    else:
        CHECKS[args.software](ctx)
    code = summarize(ctx, args.output)
    if args.allow_warnings and code == 1:
        return 0
    return code


if __name__ == "__main__":
    raise SystemExit(main())
