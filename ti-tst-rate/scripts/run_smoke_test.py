#!/usr/bin/env python3
"""Run a small TI/TST postprocessing smoke test.

This script uses the bundled user-tested demo windows. It exercises:
extract_mean_force.py -> integrate_free_energy.py -> optional plotting -> compute_tst_rates.py.
It is a syntax and file-shape smoke test, not a production scientific validation.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def default_demo_dir() -> Path:
    return script_dir().parent / "templates" / "reference-examples" / "user-tested-ti-tst-chain" / "demo"


def parse_window_name(name: str) -> float:
    if name.startswith("_"):
        return -float(name[1:])
    return float(name)


def window_dirs(demo_dir: Path) -> list[Path]:
    dirs = [p for p in demo_dir.iterdir() if p.is_dir() and (p / "energy.dat").exists()]
    return sorted(dirs, key=lambda p: parse_window_name(p.name))


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bundled TI/TST demo smoke test.")
    parser.add_argument("--demo-dir", default=str(default_demo_dir()), help="Directory containing RC-window subdirectories with energy.dat files.")
    parser.add_argument("--output-dir", default="smoke-test-output", help="Directory for generated smoke-test outputs.")
    parser.add_argument("--dataset-label", default="test", help="Dataset label written to output CSV files.")
    parser.add_argument("--skiprows", type=int, default=1, help="Numeric data rows to discard from each energy.dat. Default: 1.")
    parser.add_argument("--integration-direction", choices=["ascending", "descending", "input"], default="descending", help="RC ordering for integration. Default follows the user-tested chain: descending.")
    parser.add_argument("--free-energy-scale", type=float, default=27.211386245988, help="Conversion factor for free_energy_converted. Default: Hartree to eV.")
    parser.add_argument("--free-energy-unit-label", default="eV", help="Unit label for free_energy_converted. Default: eV.")
    parser.add_argument("--temperature", type=float, default=100.0, help="Temperature for TST rate. Default: 100 K.")
    parser.add_argument("--elementary-step", default="CHO", help="Elementary-step label for TST output.")
    parser.add_argument("--use-table-columns", action="store_true", help="Use --format table --rc-col-index 6 --force-col-index 7 instead of header names.")
    parser.add_argument("--skip-plots", action="store_true", help="Skip matplotlib plotting scripts.")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use. Default: current interpreter.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scripts = script_dir()
    demo = Path(args.demo_dir).resolve()
    out = Path(args.output_dir).resolve()
    if not demo.exists():
        raise FileNotFoundError(f"Demo directory not found: {demo}")
    windows = window_dirs(demo)
    if len(windows) < 2:
        raise ValueError(f"Need at least two demo windows in {demo}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    mean_force = out / "mean_force_table.csv"
    free_energy = out / "free_energy_profile.csv"
    rates = out / "tst_rates.csv"

    for window in windows:
        cmd = [
            args.python, str(scripts / "extract_mean_force.py"),
            "--input", str(window / "energy.dat"),
            "--output", str(mean_force),
            "--dataset-label", args.dataset_label,
            "--sample-label", window.name,
            "--skiprows", str(args.skiprows),
            "--rc-raw-unit-label", "au",
            "--force-raw-unit-label", "au",
            "--confirm-parameters",
        ]
        if args.use_table_columns:
            cmd += ["--format", "table", "--rc-col-index", "6", "--force-col-index", "7"]
        run(cmd)

    run([
        args.python, str(scripts / "integrate_free_energy.py"),
        "--input", str(mean_force),
        "--output", str(free_energy),
        "--dataset-label", args.dataset_label,
        "--integration-direction", args.integration_direction,
        "--free-energy-scale", str(args.free_energy_scale),
        "--free-energy-unit-label", args.free_energy_unit_label,
        "--confirm-parameters",
    ])

    if not args.skip_plots:
        run([
            args.python, str(scripts / "plot_mean_force.py"),
            "--curve", f"file={mean_force},dataset={args.dataset_label},label=MeanForce,marker=o",
            "--output", str(out / "mean_force.png"),
            "--rc-order", args.integration_direction,
            "--confirm-parameters",
        ])
        run([
            args.python, str(scripts / "plot_free_energy.py"),
            "--curve", f"file={free_energy},dataset={args.dataset_label},label=FreeEnergy,marker=o",
            "--output", str(out / "free_energy.png"),
            "--rc-order", args.integration_direction,
            "--free-energy-unit-label", "au",
            "--confirm-parameters",
        ])

    run([
        args.python, str(scripts / "compute_tst_rates.py"),
        "--input", str(free_energy),
        "--output", str(rates),
        "--elementary-step", args.elementary_step,
        "--dataset-label", args.dataset_label,
        "--temperature", str(args.temperature),
        "--confirm-parameters",
    ])

    print(f"Smoke-test outputs written to {out}")
    print("Reminder: inspect reactant/TS state selection before treating rates as final.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
