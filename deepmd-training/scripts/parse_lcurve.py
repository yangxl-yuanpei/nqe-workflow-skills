#!/usr/bin/env python3
"""Parse a DeePMD-kit lcurve.out-style training log.

This checker is intentionally conservative: it summarizes columns, detects
obvious NaN/Inf and step-order problems, and reports final values. It does not
judge whether a model is scientifically reliable.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Iterable


def _tokenize(line: str) -> list[str]:
    return line.strip().split()


def _is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def parse_lcurve(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")

    header: list[str] | None = None
    rows: list[list[float]] = []
    raw_header_lines: list[str] = []
    skipped_lines = 0

    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            raw_header_lines.append(stripped)
            candidate = stripped.lstrip("#").strip()
            tokens = _tokenize(candidate)
            if tokens and not all(_is_number(t) for t in tokens):
                header = tokens
            continue

        tokens = _tokenize(stripped)
        if not tokens:
            continue
        try:
            rows.append([float(t) for t in tokens])
        except ValueError:
            skipped_lines += 1
            if header is None and not all(_is_number(t) for t in tokens):
                header = tokens
            continue

    if not rows:
        return {
            "path": str(path),
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "warnings": ["no numeric rows found"],
        }

    max_cols = max(len(r) for r in rows)
    min_cols = min(len(r) for r in rows)
    if header is None or len(header) != max_cols:
        header = ["step"] + [f"col_{i}" for i in range(1, max_cols)]
    columns = header[:max_cols]

    warnings: list[str] = []
    if min_cols != max_cols:
        warnings.append(f"inconsistent column counts: min={min_cols}, max={max_cols}")
    if skipped_lines:
        warnings.append(f"skipped non-numeric data lines: {skipped_lines}")

    padded_rows: list[list[float]] = []
    for r in rows:
        padded = r + [math.nan] * (max_cols - len(r))
        padded_rows.append(padded)

    finite_counts = {name: 0 for name in columns}
    nan_counts = {name: 0 for name in columns}
    inf_counts = {name: 0 for name in columns}
    final_values: dict[str, float | None] = {}
    min_values: dict[str, float | None] = {}
    max_values: dict[str, float | None] = {}

    for idx, name in enumerate(columns):
        vals = [r[idx] for r in padded_rows]
        finite = [v for v in vals if math.isfinite(v)]
        finite_counts[name] = len(finite)
        nan_counts[name] = sum(1 for v in vals if math.isnan(v))
        inf_counts[name] = sum(1 for v in vals if math.isinf(v))
        final_values[name] = finite[-1] if finite else None
        min_values[name] = min(finite) if finite else None
        max_values[name] = max(finite) if finite else None
        if nan_counts[name]:
            warnings.append(f"column {name} contains NaN values: {nan_counts[name]}")
        if inf_counts[name]:
            warnings.append(f"column {name} contains Inf values: {inf_counts[name]}")

    step_col = 0
    step_name = columns[0]
    steps = [r[step_col] for r in padded_rows if math.isfinite(r[step_col])]
    if steps:
        if any(b < a for a, b in zip(steps, steps[1:])):
            warnings.append(f"step column {step_name} is not monotonically nondecreasing")
        if len(set(steps)) != len(steps):
            warnings.append(f"step column {step_name} contains duplicate values")

    suspicious_names = [name for name in columns if re.search(r"loss|rmse|error", name, re.I)]
    if not suspicious_names:
        warnings.append("no loss/rmse/error-like column names detected; check header interpretation")

    return {
        "path": str(path),
        "row_count": len(rows),
        "column_count": max_cols,
        "columns": columns,
        "raw_header_lines": raw_header_lines[-3:],
        "final_values": final_values,
        "min_values": min_values,
        "max_values": max_values,
        "finite_counts": finite_counts,
        "warnings": warnings,
        "note": "This parser reports obvious log issues only. It does not certify model readiness for CHMC/CPIHMC.",
    }


def format_text(summary: dict) -> str:
    lines = [
        f"File: {summary['path']}",
        f"Rows: {summary['row_count']}",
        f"Columns: {summary['column_count']} ({', '.join(summary['columns'])})",
        "",
        "Final values:",
    ]
    for key, value in summary.get("final_values", {}).items():
        lines.append(f"  {key}: {value}")
    warnings = summary.get("warnings", [])
    lines.append("")
    lines.append("Warnings:")
    if warnings:
        for w in warnings:
            lines.append(f"  - {w}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append(str(summary.get("note", "")))
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a DeePMD-kit lcurve.out-style log.")
    parser.add_argument("lcurve", type=Path, help="Path to lcurve.out or similar whitespace table")
    parser.add_argument("--json", action="store_true", help="Print JSON summary instead of text")
    args = parser.parse_args(argv)

    summary = parse_lcurve(args.lcurve)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(format_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
