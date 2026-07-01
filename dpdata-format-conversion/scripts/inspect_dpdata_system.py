#!/usr/bin/env python3
"""Inspect a dpdata-readable System or LabeledSystem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_type_map(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


def load_system(path: str, fmt: str, labeled: bool, type_map: list[str] | None):
    try:
        import dpdata
    except ImportError as exc:
        raise SystemExit("dpdata is not installed in this Python environment.") from exc

    cls = dpdata.LabeledSystem if labeled else dpdata.System
    kwargs: dict[str, Any] = {"fmt": fmt}
    if type_map:
        kwargs["type_map"] = type_map
    try:
        return cls(path, **kwargs)
    except TypeError:
        if type_map:
            raise
        return cls(path, fmt=fmt)


def safe_len(value: Any) -> int | None:
    try:
        return len(value)
    except Exception:
        return None


def shape_of(value: Any) -> list[int] | str | None:
    if value is None:
        return None
    shape = getattr(value, "shape", None)
    if shape is not None:
        return [int(x) for x in shape]
    length = safe_len(value)
    return [length] if length is not None else type(value).__name__


def summarize(system: Any) -> dict[str, Any]:
    data = getattr(system, "data", {})
    coords_shape = shape_of(data.get("coords"))
    summary: dict[str, Any] = {
        "frames": None,
        "natoms": None,
        "atom_names": data.get("atom_names"),
        "atom_numbs": data.get("atom_numbs"),
        "available_arrays": sorted(data.keys()),
        "shapes": {},
        "has_energies": "energies" in data,
        "has_forces": "forces" in data,
        "has_virials": "virials" in data,
        "has_cells": "cells" in data,
        "has_coords": "coords" in data,
    }
    try:
        summary["frames"] = int(system.get_nframes())
    except Exception:
        summary["frames"] = coords_shape[0] if isinstance(coords_shape, list) and coords_shape else None
    try:
        summary["natoms"] = int(system.get_natoms())
    except Exception:
        atom_numbs = data.get("atom_numbs")
        if atom_numbs is not None:
            summary["natoms"] = int(sum(atom_numbs))
    for key in ["coords", "cells", "energies", "forces", "virials", "atom_types"]:
        if key in data:
            summary["shapes"][key] = shape_of(data[key])
    warnings: list[str] = []
    if not summary["has_coords"]:
        warnings.append("coords array is missing")
    if not summary["has_cells"]:
        warnings.append("cells array is missing; confirm whether downstream needs periodic cell information")
    if "energies" not in data or "forces" not in data:
        warnings.append("energy/force labels are incomplete for DeePMD labeled training data")
    if "virials" not in data:
        warnings.append("virials are absent; acceptable only if downstream does not require virial labels")
    summary["warnings"] = warnings
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a dpdata-readable System or LabeledSystem.")
    parser.add_argument("--input", required=True, help="Input file or directory.")
    parser.add_argument("--format", required=True, help="Explicit dpdata format string, e.g. deepmd/npy or abacus/scf.")
    parser.add_argument("--labeled", action="store_true", help="Use dpdata.LabeledSystem instead of dpdata.System.")
    parser.add_argument("--type-map", help="Optional comma-separated element/type map. Use only when the input format needs external element names or type ordering.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    if not Path(args.input).exists():
        raise SystemExit(f"Input does not exist: {args.input}")
    system = load_system(args.input, args.format, args.labeled, parse_type_map(args.type_map))
    summary = summarize(system)
    print(json.dumps(summary, indent=2))
    if not args.json:
        print("Boundary: this inspection checks file shape only; it does not certify physical correctness or readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
