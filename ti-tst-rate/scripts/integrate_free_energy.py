#!/usr/bin/env python3
"""Integrate a collected mean-force CSV into a free-energy profile CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Sequence

REQUIRED_COLUMNS = ["dataset_label", "rc_index", "reaction_coordinate_au", "mean_force_au"]
FIELDNAMES = [
    "dataset_label",
    "rc_index",
    "reaction_coordinate_au",
    "free_energy_au",
    "free_energy_converted",
    "free_energy_converted_unit",
    "free_energy_relative_to",
    "uncertainty_au",
    "integration_method",
    "source_mean_force_table",
    "parameters_confirmed",
    "free_energy_scale",
    "free_energy_unit",
    "notes",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Integrate mean-force CSV rows into relative free-energy profiles.")
    parser.add_argument("--input", required=True, help="Collected mean_force_table.csv.")
    parser.add_argument("--output", default="free_energy_profile.csv", help="Output free-energy profile CSV.")
    parser.add_argument("--dataset-label", default=None, help="Only integrate this dataset label. Default: all labels separately.")
    parser.add_argument("--rc-index", type=int, default=0, help="Reaction-coordinate index to integrate. Default: 0.")
    parser.add_argument("--method", choices=["trapezoid"], default="trapezoid", help="Numerical integration method. Default: trapezoid.")
    parser.add_argument("--zero", choices=["first", "last", "min", "none"], default="first", help="Reference-zero convention. Default: first point.")
    parser.add_argument("--free-energy-scale", type=float, default=1.0, help="Conversion factor applied only to free_energy_converted. free_energy_au always remains atomic units. Default: 1.0.")
    parser.add_argument("--free-energy-unit-label", default="au", help="Unit label for free_energy_converted. Default: au.")
    parser.add_argument("--sort", action="store_true", help="Legacy alias for --integration-direction ascending.")
    parser.add_argument("--integration-direction", choices=["ascending", "descending", "input"], default="ascending", help="Ordering of reaction-coordinate windows before integration. Default: ascending, from small RC to large RC. Use descending when the large-RC end is the initial/reference side.")
    parser.add_argument("--confirm-parameters", action="store_true", help="Required confirmation that units, sign convention, sorting, and zero reference are appropriate.")
    parser.add_argument("--notes", default="", help="Notes to preserve in the output CSV.")
    parser.add_argument("--print-defaults", action="store_true", help="Print default assumptions and exit.")
    return parser


def print_defaults() -> None:
    print("Default assumptions requiring user confirmation:")
    print("  rc_index: 0")
    print("  integration method: trapezoid")
    print("  zero reference: first")
    print("  integration_direction: ascending (small reaction coordinate to large reaction coordinate)")
    print("  legacy --sort: same as --integration-direction ascending")
    print("  units: input reaction_coordinate_au and mean_force_au are already compatible")
    print("  free_energy_scale: 1.0 (applies to free_energy_converted only)")
    print("  free_energy_unit_label: au")
    print("  sign: mean_force_au is dF/dRC under the user-confirmed convention")
    print("  use --integration-direction descending when the larger reaction coordinate is the initial/reference side")
    print("  free_energy_au is always atomic units; converted values are written to free_energy_converted")


def is_repeated_header(row: dict[str, str]) -> bool:
    return all(row.get(col) == col for col in REQUIRED_COLUMNS)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {missing}")
        rows: list[dict[str, str]] = []
        skipped_headers = 0
        for line_number, row in enumerate(reader, start=2):
            if is_repeated_header(row):
                skipped_headers += 1
                continue
            row["_line_number"] = str(line_number)
            rows.append(row)
        if skipped_headers:
            print(f"Skipped {skipped_headers} repeated CSV header row(s) in {path}", file=sys.stderr)
        return rows


def parse_int_field(row: dict[str, str], field: str) -> int:
    try:
        return int(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        line = row.get("_line_number", "unknown")
        raise ValueError(f"Invalid integer in column {field!r} at CSV line {line}: {row.get(field)!r}") from exc


def parse_float_field(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        line = row.get("_line_number", "unknown")
        raise ValueError(f"Invalid number in column {field!r} at CSV line {line}: {row.get(field)!r}") from exc


def group_key(row: dict[str, str]) -> tuple[str, int]:
    return row["dataset_label"], parse_int_field(row, "rc_index")


def integrate_trapezoid(points: list[tuple[float, float]]) -> list[float]:
    free = [0.0]
    for idx in range(len(points) - 1):
        x0, f0 = points[idx]
        x1, f1 = points[idx + 1]
        free.append(free[-1] + (x1 - x0) * (f0 + f1) / 2.0)
    return free


def shift(values: list[float], zero: str) -> tuple[list[float], str]:
    if zero == "none":
        return values, "unshifted_first_point_zero_from_integration"
    if zero == "first":
        ref = values[0]
        label = "first_grid_point"
    elif zero == "last":
        ref = values[-1]
        label = "last_grid_point"
    elif zero == "min":
        ref = min(values)
        label = "minimum_free_energy_point"
    else:
        raise ValueError(zero)
    return [value - ref for value in values], label


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.print_defaults:
        print_defaults()
        return 0
    if not args.confirm_parameters:
        print_defaults()
        print("\nRefusing to integrate until --confirm-parameters is supplied.", file=sys.stderr)
        return 2

    source = Path(args.input)
    rows = read_rows(source)
    grouped: dict[tuple[str, int], list[dict[str, str]]] = {}
    for row in rows:
        key = group_key(row)
        if args.dataset_label is not None and key[0] != args.dataset_label:
            continue
        if key[1] != args.rc_index:
            continue
        grouped.setdefault(key, []).append(row)

    output_rows: list[dict[str, str]] = []
    for (dataset_label, rc_index), group in grouped.items():
        direction = "ascending" if args.sort else args.integration_direction
        if direction == "ascending":
            group = sorted(group, key=lambda row: parse_float_field(row, "reaction_coordinate_au"))
        elif direction == "descending":
            group = sorted(group, key=lambda row: parse_float_field(row, "reaction_coordinate_au"), reverse=True)
        elif direction == "input":
            group = list(group)
        points = [(parse_float_field(row, "reaction_coordinate_au"), parse_float_field(row, "mean_force_au")) for row in group]
        if len(points) < 2:
            raise ValueError(f"Need at least two windows to integrate {dataset_label}/rc_index={rc_index}")
        free = integrate_trapezoid(points)
        free, ref_label = shift(free, args.zero)
        for row, (rc, _force), free_value in zip(group, points, free):
            output_rows.append({
                "dataset_label": dataset_label,
                "rc_index": str(rc_index),
                "reaction_coordinate_au": f"{rc:.12g}",
                "free_energy_au": f"{free_value:.12g}",
                "free_energy_converted": f"{free_value * args.free_energy_scale:.12g}",
                "free_energy_converted_unit": args.free_energy_unit_label,
                "free_energy_relative_to": ref_label,
                "uncertainty_au": "TODO_NOT_PROPAGATED",
                "integration_method": f"{args.method};direction={direction}",
                "source_mean_force_table": str(source),
                "parameters_confirmed": "true",
                "free_energy_scale": f"{args.free_energy_scale:.12g}",
                "free_energy_unit": "au",
                "notes": args.notes,
            })

    if not output_rows:
        raise ValueError("No rows matched the requested dataset label and reaction-coordinate index")
    write_rows(Path(args.output), output_rows)
    print(f"Wrote {len(output_rows)} free-energy rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
