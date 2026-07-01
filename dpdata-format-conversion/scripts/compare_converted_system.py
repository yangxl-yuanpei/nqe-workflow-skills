#!/usr/bin/env python3
"""Compare source and converted dpdata systems for simple shape consistency."""

from __future__ import annotations

import argparse
import json
from typing import Any

from inspect_dpdata_system import load_system, shape_of, summarize


def max_abs_diff(a: Any, b: Any) -> float | None:
    try:
        import numpy as np
    except ImportError:
        return None
    try:
        arr_a = np.asarray(a, dtype=float)
        arr_b = np.asarray(b, dtype=float)
        if arr_a.shape != arr_b.shape:
            return None
        return float(np.max(np.abs(arr_a - arr_b)))
    except Exception:
        return None


def compare(source: Any, converted: Any) -> dict[str, Any]:
    src = summarize(source)
    dst = summarize(converted)
    findings: list[str] = []
    for key in ["frames", "natoms", "atom_names", "atom_numbs", "has_energies", "has_forces", "has_virials", "has_cells"]:
        if src.get(key) != dst.get(key):
            findings.append(f"{key} differs: source={src.get(key)!r} converted={dst.get(key)!r}")
    src_data = getattr(source, "data", {})
    dst_data = getattr(converted, "data", {})
    numeric_diffs: dict[str, float | None] = {}
    for key in ["coords", "cells", "energies", "forces", "virials"]:
        if key in src_data and key in dst_data:
            if shape_of(src_data[key]) != shape_of(dst_data[key]):
                findings.append(f"{key} shape differs: source={shape_of(src_data[key])} converted={shape_of(dst_data[key])}")
            else:
                numeric_diffs[key] = max_abs_diff(src_data[key], dst_data[key])
        elif key in src_data or key in dst_data:
            findings.append(f"{key} presence differs between source and converted data")
    return {
        "source": src,
        "converted": dst,
        "numeric_max_abs_diff": numeric_diffs,
        "findings": findings,
        "shape_consistent": not findings,
        "boundary": "Shape consistency does not certify physical correctness or downstream readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare source and converted dpdata systems.")
    parser.add_argument("--source", required=True, help="Source file or directory.")
    parser.add_argument("--source-format", required=True, help="Explicit dpdata source format.")
    parser.add_argument("--converted", required=True, help="Converted file or directory.")
    parser.add_argument("--converted-format", required=True, help="Explicit dpdata converted format.")
    parser.add_argument("--labeled", action="store_true", help="Use LabeledSystem for both source and converted data.")
    args = parser.parse_args()

    source = load_system(args.source, args.source_format, args.labeled, None)
    converted = load_system(args.converted, args.converted_format, args.labeled, None)
    result = compare(source, converted)
    print(json.dumps(result, indent=2))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
