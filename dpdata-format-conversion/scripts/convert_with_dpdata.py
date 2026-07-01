#!/usr/bin/env python3
"""Guarded dpdata conversion wrapper."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from inspect_dpdata_system import load_system, summarize


def write_system(system: Any, output: str, output_format: str, set_size: int | None) -> None:
    if output_format == "deepmd/npy" and hasattr(system, "to_deepmd_npy"):
        kwargs = {}
        if set_size is not None:
            kwargs["set_size"] = set_size
        system.to_deepmd_npy(output, **kwargs)
        return
    if output_format == "deepmd/raw" and hasattr(system, "to_deepmd_raw"):
        system.to_deepmd_raw(output)
        return
    if hasattr(system, "to"):
        system.to(output_format, output)
        return
    raise RuntimeError("Loaded dpdata object does not expose a supported writer for this format.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert atomistic data using explicit dpdata formats.")
    parser.add_argument("--input", required=True, help="Input file or directory.")
    parser.add_argument("--input-format", required=True, help="Explicit dpdata input format.")
    parser.add_argument("--output", required=True, help="Output file or directory.")
    parser.add_argument("--output-format", required=True, help="Explicit dpdata output format.")
    parser.add_argument("--labeled", action="store_true", help="Use dpdata.LabeledSystem instead of dpdata.System.")
    parser.add_argument("--set-size", type=int, help="Optional set size for deepmd/npy output when supported.")
    parser.add_argument("--overwrite", action="store_true", help="Allow writing to an existing output path.")
    parser.add_argument("--confirm", action="store_true", help="Required confirmation that formats, labels, units, atom order, and output path are user-approved.")
    args = parser.parse_args()

    if not args.confirm:
        raise SystemExit("Refusing conversion without --confirm. Confirm formats, labels, units, atom order, and output path first.")
    if not Path(args.input).exists():
        raise SystemExit(f"Input does not exist: {args.input}")
    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists: {args.output}. Use --overwrite only after user approval.")

    system = load_system(args.input, args.input_format, args.labeled, None)
    before = summarize(system)
    write_system(system, args.output, args.output_format, args.set_size)
    print("Conversion completed.")
    print(f"input_format={args.input_format}")
    print(f"output_format={args.output_format}")
    print(f"frames={before.get('frames')} natoms={before.get('natoms')}")
    print("Boundary: conversion does not certify DFT convergence, unit correctness, label quality, or downstream readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
