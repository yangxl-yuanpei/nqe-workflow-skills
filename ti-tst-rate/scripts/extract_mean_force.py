#!/usr/bin/env python3
"""Extract one sampling output into a mean-force CSV row.

This script handles one sampling/window at a time. Use shell loops or workflow
managers outside this script to collect many reaction-coordinate windows.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path
from typing import Iterable, Sequence

DEFAULTS = {
    "format": "auto",
    "rc_column": "RxnCoord",
    "force_column": "MeanForce",
    "rc_index": 0,
    "skiprows": 0,
    "rc_scale": 1.0,
    "force_scale": 1.0,
    "rc_raw_unit_label": "input",
    "force_raw_unit_label": "input",
    "equilibration_discard": "0 rows",
}

FIELDNAMES = [
    "dataset_label",
    "sample_label",
    "rc_index",
    "reaction_coordinate_raw",
    "reaction_coordinate_raw_unit",
    "mean_force_raw",
    "mean_force_raw_unit",
    "uncertainty_raw",
    "reaction_coordinate_au",
    "mean_force_au",
    "uncertainty_au",
    "n_samples",
    "equilibration_discard",
    "source_file",
    "rc_column",
    "force_column",
    "rc_scale",
    "force_scale",
    "parameters_confirmed",
    "notes",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract reaction coordinate and mean force from one CHMC/CPIHMC sampling output."
    )
    parser.add_argument("--input", required=True, help="Single sampling output file, e.g. PHY_QUANT or one window dat file.")
    parser.add_argument("--output", default="mean_force_table.csv", help="CSV file to create or append to.")
    parser.add_argument("--format", choices=["auto", "phy_quant", "table"], default=DEFAULTS["format"], help="Input parser. phy_quant uses header names; table uses numeric columns.")
    parser.add_argument("--dataset-label", required=True, help="Dataset label, e.g. classical_100K or cpihmc_100K.")
    parser.add_argument("--sample-label", default="", help="Optional sampling/window label.")
    parser.add_argument("--rc-index", type=int, default=DEFAULTS["rc_index"], help="Reaction-coordinate index. Default: 0.")
    parser.add_argument("--rc-column", default=DEFAULTS["rc_column"], help="Header column for reaction coordinate. Default: RxnCoord for one RC; use RxnCoord_0, RxnCoord_1, ... for multi-RC output.")
    parser.add_argument("--force-column", default=DEFAULTS["force_column"], help="Header column for mean force. Default: MeanForce for one RC; use MeanForce_0, MeanForce_1, ... for multi-RC output.")
    parser.add_argument("--rc-col-index", type=int, default=None, help="Zero-based numeric column index for reaction coordinate in table format.")
    parser.add_argument("--force-col-index", type=int, default=None, help="Zero-based numeric column index for mean force in table format.")
    parser.add_argument("--window-rc", type=float, default=None, help="Use this reaction coordinate instead of averaging an RC column.")
    parser.add_argument("--skiprows", type=int, default=DEFAULTS["skiprows"], help="Rows to skip after the header/comment handling. Default: 0.")
    parser.add_argument("--rc-scale", type=float, default=DEFAULTS["rc_scale"], help="Multiply raw extracted/window RC by this factor to produce reaction_coordinate_au. Default: 1.0, raw input already atomic units.")
    parser.add_argument("--force-scale", type=float, default=DEFAULTS["force_scale"], help="Multiply raw extracted force by this factor to produce mean_force_au. Default: 1.0, raw input already atomic units.")
    parser.add_argument("--rc-raw-unit-label", default=DEFAULTS["rc_raw_unit_label"], help="Unit label for reaction_coordinate_raw. Default: input.")
    parser.add_argument("--force-raw-unit-label", default=DEFAULTS["force_raw_unit_label"], help="Unit label for mean_force_raw. Default: input.")
    parser.add_argument("--uncertainty", choices=["none", "sem", "std"], default="sem", help="Uncertainty estimate from samples. Default: sem.")
    parser.add_argument("--notes", default="", help="Notes to preserve in the output CSV.")
    parser.add_argument("--confirm-parameters", action="store_true", help="Required confirmation that columns, units, scales, and skip settings are appropriate for this run.")
    parser.add_argument("--print-defaults", action="store_true", help="Print default assumptions and exit.")
    return parser


def print_defaults() -> None:
    print("Default assumptions requiring user confirmation:")
    for key, value in DEFAULTS.items():
        print(f"  {key}: {value}")
    print("  uncertainty: sem")
    print("  units: raw columns preserve extracted values; rc_scale/force_scale convert raw values to *_au columns")


def numeric_tokens(line: str) -> list[float] | None:
    parts = line.split()
    if not parts:
        return None
    vals: list[float] = []
    try:
        for part in parts:
            vals.append(float(part))
    except ValueError:
        return None
    return vals


def detect_format(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            return "table" if numeric_tokens(stripped) is not None else "phy_quant"
    raise ValueError(f"No data found in {path}")


def read_phy_quant(path: Path, rc_column: str, force_column: str, skiprows: int) -> tuple[list[float], list[float]]:
    with path.open("r", encoding="utf-8") as handle:
        header: list[str] | None = None
        rows: list[list[str]] = []
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if header is None:
                header = stripped.split()
            else:
                rows.append(stripped.split())
    if header is None:
        raise ValueError(f"No header found in {path}")
    try:
        rc_pos = header.index(rc_column)
        force_pos = header.index(force_column)
    except ValueError as exc:
        raise ValueError(
            f"Missing requested column in {path}; header={header}. "
            f"Requested rc_column={rc_column!r}, force_column={force_column!r}. "
            "For one-RC CHMC/CPIHMC output the default headers are 'RxnCoord' and 'MeanForce'. "
            "For multi-RC output, pass explicit names such as --rc-column RxnCoord_0 --force-column MeanForce_0. "
            "If you want to use numeric column indices, pass --format table; "
            "--rc-col-index/--force-col-index are only used in table mode."
        ) from exc
    rc_vals: list[float] = []
    force_vals: list[float] = []
    for row in rows[skiprows:]:
        if max(rc_pos, force_pos) >= len(row):
            continue
        rc_vals.append(float(row[rc_pos]))
        force_vals.append(float(row[force_pos]))
    return rc_vals, force_vals


def read_table(path: Path, rc_col_index: int | None, force_col_index: int | None, window_rc: float | None, skiprows: int) -> tuple[list[float], list[float]]:
    if force_col_index is None:
        raise ValueError("--force-col-index is required for --format table")
    if rc_col_index is None and window_rc is None:
        raise ValueError("Provide --rc-col-index or --window-rc for --format table")
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = numeric_tokens(stripped)
            if vals is not None:
                rows.append(vals)
    rows = rows[skiprows:]
    force_vals: list[float] = []
    rc_vals: list[float] = []
    for row in rows:
        if force_col_index >= len(row):
            continue
        force_vals.append(row[force_col_index])
        if window_rc is not None:
            rc_vals.append(window_rc)
        elif rc_col_index is not None and rc_col_index < len(row):
            rc_vals.append(row[rc_col_index])
    return rc_vals, force_vals


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("No numeric samples were extracted")
    return sum(values) / len(values)


def uncertainty(values: Sequence[float], method: str) -> str:
    if method == "none":
        return "TODO_NOT_ESTIMATED"
    if len(values) < 2:
        return "TODO_INSUFFICIENT_SAMPLES"
    std = statistics.stdev(values)
    if method == "std":
        return f"{std:.12g}"
    return f"{std / math.sqrt(len(values)):.12g}"


def append_row(output: Path, row: dict[str, str]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output.exists() or output.stat().st_size == 0
    if not write_header:
        with output.open("r", newline="", encoding="utf-8") as existing:
            reader = csv.reader(existing)
            header = next(reader, [])
        if header != FIELDNAMES:
            raise ValueError(
                f"Existing output CSV schema does not match current schema: {output}. "
                "Write to a new output file or regenerate the table with the current script."
            )
    with output.open("a", newline="", encoding="utf-8") as handle:
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
        print("\nRefusing to extract data until --confirm-parameters is supplied.", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    fmt = detect_format(input_path) if args.format == "auto" else args.format
    if fmt == "phy_quant":
        rc_vals, force_vals = read_phy_quant(input_path, args.rc_column, args.force_column, args.skiprows)
        rc_column_label = args.rc_column
        force_column_label = args.force_column
    else:
        rc_vals, force_vals = read_table(input_path, args.rc_col_index, args.force_col_index, args.window_rc, args.skiprows)
        rc_column_label = "window_rc" if args.window_rc is not None else f"col_{args.rc_col_index}"
        force_column_label = f"col_{args.force_col_index}"

    rc_raw_mean = mean(rc_vals)
    force_raw_mean = mean(force_vals)
    raw_uncertainty = uncertainty(force_vals, args.uncertainty)
    rc_mean = rc_raw_mean * args.rc_scale
    force_samples = [value * args.force_scale for value in force_vals]
    force_mean = mean(force_samples)
    row = {
        "dataset_label": args.dataset_label,
        "sample_label": args.sample_label,
        "rc_index": str(args.rc_index),
        "reaction_coordinate_raw": f"{rc_raw_mean:.12g}",
        "reaction_coordinate_raw_unit": args.rc_raw_unit_label,
        "mean_force_raw": f"{force_raw_mean:.12g}",
        "mean_force_raw_unit": args.force_raw_unit_label,
        "uncertainty_raw": raw_uncertainty,
        "reaction_coordinate_au": f"{rc_mean:.12g}",
        "mean_force_au": f"{force_mean:.12g}",
        "uncertainty_au": uncertainty(force_samples, args.uncertainty),
        "n_samples": str(len(force_samples)),
        "equilibration_discard": f"{args.skiprows} rows",
        "source_file": str(input_path),
        "rc_column": rc_column_label,
        "force_column": force_column_label,
        "rc_scale": f"{args.rc_scale:.12g}",
        "force_scale": f"{args.force_scale:.12g}",
        "parameters_confirmed": "true",
        "notes": args.notes,
    }
    append_row(Path(args.output), row)
    print(f"Wrote one mean-force row to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
