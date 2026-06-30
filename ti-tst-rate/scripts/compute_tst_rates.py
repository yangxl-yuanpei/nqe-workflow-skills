#!/usr/bin/env python3
"""Extract an activation free-energy barrier and compute a TST rate constant."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Sequence

KB_J_PER_K = 1.380649e-23
H_J_S = 6.62607015e-34
HARTREE_J = 4.3597447222071e-18
EV_J = 1.602176634e-19
AVOGADRO = 6.02214076e23

FIELDNAMES = [
    "elementary_step", "dataset_label", "temperature_K", "deltaF_dagger_au",
    "reactant_rc_au", "transition_state_rc_au",
    "reactant_free_energy", "transition_state_free_energy",
    "prefactor_model", "prefactor_expression", "prefactor_inputs",
    "prefactor_units", "prefactor_value", "rate_units", "rate_value",
    "barrier_source", "notes",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute one TST rate from a free-energy profile or explicit barrier.")
    parser.add_argument("--input", help="free_energy_profile.csv. Required unless --deltaF is provided.")
    parser.add_argument("--output", default="tst_rates.csv", help="CSV file to create or append to.")
    parser.add_argument("--elementary-step", required=True, help="Elementary-step label for the rate.")
    parser.add_argument("--dataset-label", required=True, help="Dataset label to select and write.")
    parser.add_argument("--rc-index", type=int, default=0, help="Reaction-coordinate index. Default: 0.")
    parser.add_argument("--temperature", type=float, required=True, help="Temperature in K.")
    parser.add_argument("--free-energy-column", default="free_energy_au", help="Free-energy column in profile CSV. Default: free_energy_au. Use free_energy_converted only with a matching converted-unit column.")
    parser.add_argument("--free-energy-unit", choices=["auto", "au", "hartree", "eV", "kJ/mol", "kcal/mol"], default="auto", help="Unit of free-energy values. Default: auto from CSV free_energy_unit column, else au.")
    parser.add_argument("--reactant-mode", choices=["first", "last", "min", "rc", "value"], default="first", help="How to choose reactant/reference free energy. Default: first row after filtering.")
    parser.add_argument("--reactant-rc", type=float, default=None, help="Reactant reaction coordinate for --reactant-mode rc.")
    parser.add_argument("--reactant-value", type=float, default=None, help="Reactant free energy for --reactant-mode value, in --free-energy-unit.")
    parser.add_argument("--ts-mode", choices=["max", "rc", "value"], default="max", help="How to choose transition-state free energy. Default: max of selected profile.")
    parser.add_argument("--ts-rc", type=float, default=None, help="Transition-state reaction coordinate for --ts-mode rc.")
    parser.add_argument("--ts-value", type=float, default=None, help="Transition-state free energy for --ts-mode value, in --free-energy-unit.")
    parser.add_argument("--deltaF", type=float, default=None, help="Explicit activation free energy. If set, profile extraction is skipped.")
    parser.add_argument("--deltaF-unit", choices=["au", "hartree", "eV", "kJ/mol", "kcal/mol"], default=None, help="Unit for --deltaF. Required with --deltaF.")
    parser.add_argument("--prefactor-model", choices=["kBT_over_h", "custom_numeric", "adsorption_flux_n_v_S"], default="kBT_over_h", help="Prefactor model. Default: kBT_over_h.")
    parser.add_argument("--prefactor-value", type=float, default=None, help="Numeric prefactor for custom_numeric.")
    parser.add_argument("--prefactor-units", default="s^-1", help="Prefactor/rate units label. Default: s^-1.")
    parser.add_argument("--density", type=float, default=None, help="n for adsorption_flux_n_v_S.")
    parser.add_argument("--mean-speed", type=float, default=None, help="v for adsorption_flux_n_v_S.")
    parser.add_argument("--site-area", type=float, default=None, help="S for adsorption_flux_n_v_S.")
    parser.add_argument("--notes", default="", help="Notes to preserve in the output CSV.")
    parser.add_argument("--confirm-parameters", action="store_true", help="Required confirmation of barrier extraction, units, prefactor model, and rate interpretation.")
    parser.add_argument("--print-defaults", action="store_true", help="Print default assumptions and exit.")
    return parser


def print_defaults() -> None:
    print("Default assumptions requiring user confirmation:")
    print("  rc_index: 0")
    print("  reactant_mode: first (default initial state is the first point in the chosen free-energy profile)")
    print("  ts_mode: max (default transition state is the highest free-energy point)")
    print("  free_energy_unit: auto uses au for free_energy_au, free_energy_converted_unit for free_energy_converted, else CSV free_energy_unit or au")
    print("  prefactor_model: kBT_over_h")
    print("  rate formula: k = prefactor * exp(-DeltaF_dagger / (k_B T))")
    print("  custom/adsorption prefactors require user-provided units and inputs")


def unit_to_joule(value: float, unit: str) -> float:
    if unit in ("au", "hartree"):
        return value * HARTREE_J
    if unit == "eV":
        return value * EV_J
    if unit == "kJ/mol":
        return value * 1000.0 / AVOGADRO
    if unit == "kcal/mol":
        return value * 4184.0 / AVOGADRO
    raise ValueError(f"Unsupported unit: {unit}")


def joule_to_hartree(value_j: float) -> float:
    return value_j / HARTREE_J


def read_profile(path: Path, dataset_label: str, rc_index: int, free_energy_column: str, unit_arg: str) -> tuple[list[dict[str, str]], str]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header")
        required = ["dataset_label", "rc_index", "reaction_coordinate_au", free_energy_column]
        missing = [col for col in required if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Input CSV is missing columns: {missing}")
        rows = [row for row in reader if row["dataset_label"] == dataset_label and int(row["rc_index"]) == rc_index]
    if not rows:
        raise ValueError("No rows matched dataset label and rc index")
    if unit_arg != "auto":
        unit = unit_arg
    elif free_energy_column == "free_energy_au":
        unit = "au"
    elif free_energy_column == "free_energy_converted" and "free_energy_converted_unit" in rows[0] and rows[0].get("free_energy_converted_unit"):
        unit = rows[0]["free_energy_converted_unit"]
    elif "free_energy_unit" in rows[0] and rows[0].get("free_energy_unit"):
        unit = rows[0]["free_energy_unit"]
    else:
        unit = "au"
    if unit == "hartree":
        unit = "au"
    return rows, unit


def closest_by_rc(rows: list[dict[str, str]], rc: float) -> dict[str, str]:
    return min(rows, key=lambda row: abs(float(row["reaction_coordinate_au"]) - rc))


def select_value(rows: list[dict[str, str]], mode: str, column: str, rc: float | None, explicit: float | None, label: str) -> tuple[float, str]:
    if mode == "first":
        row = rows[0]
        return float(row[column]), row["reaction_coordinate_au"], f"{label}=first(rc={row['reaction_coordinate_au']})"
    if mode == "last":
        row = rows[-1]
        return float(row[column]), row["reaction_coordinate_au"], f"{label}=last(rc={row['reaction_coordinate_au']})"
    if mode == "min":
        row = min(rows, key=lambda r: float(r[column]))
        return float(row[column]), row["reaction_coordinate_au"], f"{label}=min(rc={row['reaction_coordinate_au']})"
    if mode == "max":
        row = max(rows, key=lambda r: float(r[column]))
        return float(row[column]), row["reaction_coordinate_au"], f"{label}=max(rc={row['reaction_coordinate_au']})"
    if mode == "rc":
        if rc is None:
            raise ValueError(f"--{label}-rc is required for --{label}-mode rc")
        row = closest_by_rc(rows, rc)
        return float(row[column]), row["reaction_coordinate_au"], f"{label}=closest_rc(requested={rc}, used={row['reaction_coordinate_au']})"
    if mode == "value":
        if explicit is None:
            raise ValueError(f"--{label}-value is required for --{label}-mode value")
        return explicit, "TODO_EXPLICIT_VALUE_NO_RC", f"{label}=explicit_value"
    raise ValueError(mode)


def prefactor(args: argparse.Namespace) -> tuple[float, str, str]:
    if args.prefactor_model == "kBT_over_h":
        value = KB_J_PER_K * args.temperature / H_J_S
        return value, "k_B*T/h", f"T={args.temperature} K"
    if args.prefactor_model == "custom_numeric":
        if args.prefactor_value is None:
            raise ValueError("--prefactor-value is required for custom_numeric")
        return args.prefactor_value, "custom_numeric", "prefactor_value=user_provided"
    if args.prefactor_model == "adsorption_flux_n_v_S":
        if args.density is None or args.mean_speed is None or args.site_area is None:
            raise ValueError("--density, --mean-speed, and --site-area are required for adsorption_flux_n_v_S")
        value = args.density * args.mean_speed * args.site_area
        return value, "n*v*S", f"n={args.density}; v={args.mean_speed}; S={args.site_area}"
    raise ValueError(args.prefactor_model)


def append_row(path: Path, row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.print_defaults:
        print_defaults()
        return 0
    if not args.confirm_parameters:
        print_defaults()
        print("\nRefusing to compute TST rate until --confirm-parameters is supplied.", file=sys.stderr)
        return 2
    if args.deltaF is not None:
        if args.deltaF_unit is None:
            raise ValueError("--deltaF-unit is required with --deltaF")
        delta_j = unit_to_joule(args.deltaF, args.deltaF_unit)
        delta_au = joule_to_hartree(delta_j)
        barrier_source = f"explicit_deltaF={args.deltaF} {args.deltaF_unit}"
        reactant = float("nan")
        ts = float("nan")
        reactant_rc = "TODO_EXPLICIT_DELTAF_NO_REACTANT_RC"
        ts_rc = "TODO_EXPLICIT_DELTAF_NO_TS_RC"
    else:
        if args.input is None:
            raise ValueError("--input is required unless --deltaF is supplied")
        rows, unit = read_profile(Path(args.input), args.dataset_label, args.rc_index, args.free_energy_column, args.free_energy_unit)
        reactant, reactant_rc, reactant_src = select_value(rows, args.reactant_mode, args.free_energy_column, args.reactant_rc, args.reactant_value, "reactant")
        ts, ts_rc, ts_src = select_value(rows, args.ts_mode, args.free_energy_column, args.ts_rc, args.ts_value, "ts")
        delta_value = ts - reactant
        delta_j = unit_to_joule(delta_value, unit)
        delta_au = joule_to_hartree(delta_j)
        barrier_source = f"{args.input}; {reactant_src}; {ts_src}; unit={unit}"
    if delta_j < 0:
        raise ValueError("Computed activation free energy is negative; confirm reactant/TS selection and sign convention")
    pref_value, pref_expr, pref_inputs = prefactor(args)
    rate = pref_value * math.exp(-delta_j / (KB_J_PER_K * args.temperature))
    row = {
        "elementary_step": args.elementary_step,
        "dataset_label": args.dataset_label,
        "temperature_K": f"{args.temperature:.12g}",
        "deltaF_dagger_au": f"{delta_au:.12g}",
        "reactant_rc_au": str(reactant_rc),
        "transition_state_rc_au": str(ts_rc),
        "reactant_free_energy": f"{reactant:.12g}",
        "transition_state_free_energy": f"{ts:.12g}",
        "prefactor_model": args.prefactor_model,
        "prefactor_expression": pref_expr,
        "prefactor_inputs": pref_inputs,
        "prefactor_units": args.prefactor_units,
        "prefactor_value": f"{pref_value:.12g}",
        "rate_units": args.prefactor_units,
        "rate_value": f"{rate:.12g}",
        "barrier_source": barrier_source,
        "notes": args.notes,
    }
    append_row(Path(args.output), row)
    print(f"Selected reactant RC: {reactant_rc}; transition-state RC: {ts_rc}")
    print("Ask the user to confirm these states before treating the rate as final.")
    print(f"Wrote one TST rate row to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
