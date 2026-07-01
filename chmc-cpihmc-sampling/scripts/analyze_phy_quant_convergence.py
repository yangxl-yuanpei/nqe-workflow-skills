#!/usr/bin/env python3
"""Plot and summarize convergence diagnostics for CHMC/CPIHMC PHY_QUANT-like files.

The script is intentionally conservative. It can suggest an equilibration cutoff from
simple block-stability heuristics, but that suggestion is not a proof of convergence.
Users should inspect the generated plots and approve the equilibration choice before
using the resulting mean force in thermodynamic integration.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


DEFAULT_COLUMN_CANDIDATES = ("PotEng", "MeanForce", "MeanForce_0")


@dataclass
class SeriesDiagnostic:
    column: str
    total_samples: int
    used_samples: int
    equilibration_index: int
    equilibration_step: Optional[float]
    mean: float
    std: float
    sem: float
    final_cumulative_mean: float
    auto_status: str
    auto_reason: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plot instantaneous, cumulative-average, and final-average diagnostics "
            "for selected columns in CHMC/CPIHMC PHY_QUANT or energy.dat outputs."
        )
    )
    parser.add_argument("--input", required=True, help="PHY_QUANT/energy.dat-like whitespace table.")
    parser.add_argument("--output", help="Output plot path, for example convergence.png.")
    parser.add_argument("--summary", help="Optional CSV summary path for numerical diagnostics.")
    parser.add_argument("--column", action="append", default=[], help="Column name to analyze. Repeat for multiple columns.")
    parser.add_argument("--col-index", action="append", type=int, default=[], help="Zero-based numeric column index to analyze. Repeat for multiple columns.")
    parser.add_argument("--step-column", default="Steps", help="Column name for x-axis steps.")
    parser.add_argument("--step-col-index", type=int, help="Zero-based step column index if no step-column header is available.")
    parser.add_argument("--skiprows", type=int, default=0, help="Number of numeric data rows to skip after the header.")
    parser.add_argument("--delimiter", default=None, help="Optional delimiter. Default: arbitrary whitespace.")
    parser.add_argument("--equilibration-index", type=int, help="Zero-based data-row index where production sampling starts after skiprows.")
    parser.add_argument("--equilibration-step", type=float, help="Step value where production sampling starts.")
    parser.add_argument("--auto-equilibration", action="store_true", help="Suggest an equilibration cutoff with conservative block-stability heuristics.")
    parser.add_argument("--auto-max-fraction", type=float, default=0.8, help="Largest fraction auto-equilibration may discard. Default: 0.8.")
    parser.add_argument("--auto-step-fraction", type=float, default=0.05, help="Fractional spacing between candidate burn-in cutoffs. Default: 0.05.")
    parser.add_argument("--min-production-samples", type=int, default=100, help="Minimum samples required after cutoff. Default: 100.")
    parser.add_argument("--block-count", type=int, default=8, help="Number of post-equilibration blocks for stability checks. Default: 8.")
    parser.add_argument("--sem-factor", type=float, default=2.0, help="Allowed early/late block-mean difference in combined SEM units. Default: 2.0.")
    parser.add_argument("--relative-tolerance", type=float, default=0.02, help="Relative tolerance for early/late block-mean agreement. Default: 0.02.")
    parser.add_argument("--absolute-tolerance", type=float, default=0.0, help="Absolute tolerance in selected column units. Default: 0.")
    parser.add_argument("--drift-tolerance", type=float, default=0.25, help="Allowed block-mean drift as a fraction of block scatter. Default: 0.25.")
    parser.add_argument("--running-window", type=int, default=0, help="Optional rolling-average window in samples. 0 disables rolling mean.")
    parser.add_argument("--x-scale", type=float, default=1.0, help="Multiply x-axis values by this factor.")
    parser.add_argument("--y-scale", type=float, default=1.0, help="Multiply selected y columns by this factor.")
    parser.add_argument("--xlabel", default="Step", help="X-axis label.")
    parser.add_argument("--ylabel", default="Value", help="Y-axis label base text.")
    parser.add_argument("--title", default=None, help="Optional figure title.")
    parser.add_argument("--width", type=float, default=8.0, help="Figure width in inches.")
    parser.add_argument("--height-per-panel", type=float, default=3.0, help="Figure height per analyzed column.")
    parser.add_argument("--dpi", type=int, default=160, help="Plot DPI. Default: 160.")
    parser.add_argument("--no-plot", action="store_true", help="Only write summary; do not create an image.")
    parser.add_argument("--confirm-parameters", action="store_true", help="Required acknowledgement that columns, units, and equilibration policy were reviewed.")
    parser.add_argument("--print-defaults", action="store_true", help="Print defaults and exit.")
    return parser


def print_defaults() -> None:
    print("Default behavior:")
    print("  input table: whitespace-delimited PHY_QUANT/energy.dat style")
    print("  default analyzed column: first available of PotEng, MeanForce, MeanForce_0")
    print("  column indices: zero-based")
    print("  step column: Steps")
    print("  skiprows: 0 numeric data rows after header")
    print("  y-scale: 1.0, x-scale: 1.0")
    print("  auto-equilibration: disabled unless --auto-equilibration is passed")
    print("  auto heuristic: block early/late mean agreement plus drift check")
    print("  convergence status: diagnostic only, not proof of production convergence")


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def split_line(line: str, delimiter: Optional[str]) -> List[str]:
    stripped = line.strip()
    if delimiter is None:
        return stripped.split()
    return [part.strip() for part in stripped.split(delimiter)]


def read_table(path: str, delimiter: Optional[str], skiprows: int) -> Tuple[List[str], List[List[float]]]:
    with open(path, "r", encoding="utf-8") as handle:
        raw_lines = [line.strip() for line in handle if line.strip() and not line.lstrip().startswith("#")]
    if not raw_lines:
        raise ValueError(f"No readable rows found in {path}")
    first = split_line(raw_lines[0], delimiter)
    if all(is_float(token) for token in first):
        header = [f"col_{i}" for i in range(len(first))]
        data_lines = raw_lines
        data_start_line = 1
    else:
        header = first
        data_lines = raw_lines[1:]
        data_start_line = 2
    rows: List[List[float]] = []
    for offset, line in enumerate(data_lines):
        line_no = data_start_line + offset
        parts = split_line(line, delimiter)
        if len(parts) != len(header):
            raise ValueError(f"Row {line_no} in {path} has {len(parts)} columns, expected {len(header)}; row={line!r}")
        try:
            rows.append([float(part) for part in parts])
        except ValueError as exc:
            raise ValueError(f"Non-numeric value on row {line_no} in {path}: {line!r}") from exc
    if skiprows < 0:
        raise ValueError("--skiprows must be non-negative")
    if skiprows >= len(rows):
        raise ValueError(f"--skiprows={skiprows} leaves no data rows; total rows={len(rows)}")
    return header, rows[skiprows:]


def resolve_index(header: Sequence[str], name: Optional[str], index: Optional[int], label: str) -> int:
    if index is not None:
        if index < 0 or index >= len(header):
            raise ValueError(f"{label} index {index} is outside available columns 0..{len(header)-1}")
        return index
    if name is not None and name in header:
        return header.index(name)
    if name is not None:
        raise ValueError(f"Missing {label} column {name!r}; available columns={list(header)}")
    raise ValueError(f"Missing {label} column/index")


def select_value_columns(header: Sequence[str], names: Sequence[str], indices: Sequence[int]) -> List[int]:
    selected: List[int] = []
    for name in names:
        if name not in header:
            raise ValueError(f"Missing requested column {name!r}; available columns={list(header)}")
        selected.append(header.index(name))
    for index in indices:
        if index < 0 or index >= len(header):
            raise ValueError(f"Requested column index {index} is outside available columns 0..{len(header)-1}")
        selected.append(index)
    if not selected:
        for candidate in DEFAULT_COLUMN_CANDIDATES:
            if candidate in header:
                selected.append(header.index(candidate))
                break
    if not selected:
        raise ValueError(f"No value column selected. Pass --column NAME or --col-index N. Available columns={list(header)}")
    unique: List[int] = []
    for item in selected:
        if item not in unique:
            unique.append(item)
    return unique


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def sample_std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def cumulative_mean(values: Sequence[float]) -> List[float]:
    out: List[float] = []
    total = 0.0
    for i, value in enumerate(values, start=1):
        total += value
        out.append(total / i)
    return out


def rolling_mean(values: Sequence[float], window: int) -> Tuple[List[int], List[float]]:
    if window <= 1 or window > len(values):
        return [], []
    out: List[float] = []
    indices: List[int] = []
    total = sum(values[:window])
    out.append(total / window)
    indices.append(window - 1)
    for i in range(window, len(values)):
        total += values[i] - values[i - window]
        out.append(total / window)
        indices.append(i)
    return indices, out


def make_blocks(values: Sequence[float], block_count: int) -> List[List[float]]:
    n = len(values)
    if block_count < 2 or n < block_count:
        return []
    block_size = n // block_count
    blocks: List[List[float]] = []
    for i in range(block_count):
        start = i * block_size
        end = (i + 1) * block_size if i < block_count - 1 else n
        block = list(values[start:end])
        if block:
            blocks.append(block)
    return blocks


def linear_slope(y: Sequence[float]) -> float:
    n = len(y)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = mean(y)
    denom = sum((i - x_mean) ** 2 for i in range(n))
    if denom == 0.0:
        return 0.0
    return sum((i - x_mean) * (value - y_mean) for i, value in enumerate(y)) / denom


def stability_check(values: Sequence[float], block_count: int, sem_factor: float, relative_tolerance: float, absolute_tolerance: float, drift_tolerance: float) -> Tuple[bool, str]:
    blocks = make_blocks(values, block_count)
    if len(blocks) < 4:
        return False, "not enough post-equilibration blocks"
    block_means = [mean(block) for block in blocks]
    mid = len(block_means) // 2
    early = block_means[:mid]
    late = block_means[mid:]
    early_mean = mean(early)
    late_mean = mean(late)
    diff = abs(early_mean - late_mean)
    early_sem = sample_std(early) / math.sqrt(len(early)) if len(early) > 1 else 0.0
    late_sem = sample_std(late) / math.sqrt(len(late)) if len(late) > 1 else 0.0
    combined_sem = math.sqrt(early_sem**2 + late_sem**2)
    scale = max(abs(late_mean), abs(early_mean), 1.0)
    tolerance = absolute_tolerance + relative_tolerance * scale
    sem_ok = combined_sem > 0 and diff <= sem_factor * combined_sem
    tol_ok = diff <= tolerance
    slope = linear_slope(block_means)
    total_drift = abs(slope) * max(len(block_means) - 1, 1)
    scatter = sample_std(block_means)
    drift_limit = absolute_tolerance + drift_tolerance * max(scatter, tolerance)
    drift_ok = total_drift <= drift_limit
    ok = (sem_ok or tol_ok) and drift_ok
    reason = f"early_late_diff={diff:.6g}, combined_sem={combined_sem:.6g}, rel_abs_tol={tolerance:.6g}, total_block_drift={total_drift:.6g}, drift_limit={drift_limit:.6g}"
    return ok, reason


def suggest_equilibration_index(values: Sequence[float], max_fraction: float, step_fraction: float, min_production_samples: int, block_count: int, sem_factor: float, relative_tolerance: float, absolute_tolerance: float, drift_tolerance: float) -> Tuple[int, str, str]:
    n = len(values)
    if n < min_production_samples:
        return 0, "UNDETERMINED", f"not enough samples: {n} < {min_production_samples}"
    if not (0.0 <= max_fraction < 1.0):
        raise ValueError("--auto-max-fraction must be >= 0 and < 1")
    if not (0.0 < step_fraction <= 0.5):
        raise ValueError("--auto-step-fraction must be > 0 and <= 0.5")
    candidate_count = int(max_fraction / step_fraction) + 1
    reasons: List[str] = []
    for i in range(candidate_count + 1):
        fraction = min(i * step_fraction, max_fraction)
        idx = int(round(n * fraction))
        post = values[idx:]
        if len(post) < min_production_samples:
            reasons.append(f"idx={idx}: insufficient post samples")
            continue
        ok, reason = stability_check(post, block_count, sem_factor, relative_tolerance, absolute_tolerance, drift_tolerance)
        if ok:
            return idx, "SUGGESTED", f"first stable candidate at fraction={fraction:.3f}; {reason}"
        reasons.append(f"idx={idx}: {reason}")
    tail = reasons[-1] if reasons else "no candidates evaluated"
    return 0, "WARN", f"no stable cutoff found within max_fraction={max_fraction}; last={tail}"


def index_from_step(steps: Sequence[float], equilibration_step: float) -> int:
    for i, value in enumerate(steps):
        if value >= equilibration_step:
            return i
    raise ValueError(f"--equilibration-step={equilibration_step} is beyond final step {steps[-1]}")


def analyze_series(column: str, steps: Sequence[float], values: Sequence[float], user_equilibration_index: Optional[int], auto_equilibration: bool, args: argparse.Namespace) -> SeriesDiagnostic:
    if user_equilibration_index is not None:
        eq_index = user_equilibration_index
        status = "USER_SET"
        reason = "user supplied equilibration cutoff"
    elif auto_equilibration:
        eq_index, status, reason = suggest_equilibration_index(values, args.auto_max_fraction, args.auto_step_fraction, args.min_production_samples, args.block_count, args.sem_factor, args.relative_tolerance, args.absolute_tolerance, args.drift_tolerance)
    else:
        eq_index = 0
        status = "NOT_RUN"
        reason = "auto-equilibration disabled; using full series for summary"
    if eq_index < 0 or eq_index >= len(values):
        raise ValueError(f"Equilibration index {eq_index} leaves no production data for column {column}")
    post = list(values[eq_index:])
    mu = mean(post)
    std = sample_std(post)
    sem = std / math.sqrt(len(post)) if post else float("nan")
    eq_step = steps[eq_index] if steps else None
    return SeriesDiagnostic(column=column, total_samples=len(values), used_samples=len(post), equilibration_index=eq_index, equilibration_step=eq_step, mean=mu, std=std, sem=sem, final_cumulative_mean=cumulative_mean(values)[-1], auto_status=status, auto_reason=reason)


def write_summary(path: str, diagnostics: Sequence[SeriesDiagnostic]) -> None:
    fieldnames = ["column", "total_samples", "used_samples", "equilibration_index_zero_based", "equilibration_step", "mean", "std", "sem", "final_cumulative_mean", "auto_status", "auto_reason"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in diagnostics:
            writer.writerow({"column": item.column, "total_samples": item.total_samples, "used_samples": item.used_samples, "equilibration_index_zero_based": item.equilibration_index, "equilibration_step": "" if item.equilibration_step is None else item.equilibration_step, "mean": item.mean, "std": item.std, "sem": item.sem, "final_cumulative_mean": item.final_cumulative_mean, "auto_status": item.auto_status, "auto_reason": item.auto_reason})


def make_plot(output: str, title: Optional[str], steps: Sequence[float], series: Sequence[Tuple[str, List[float], SeriesDiagnostic]], running_window: int, xlabel: str, ylabel: str, width: float, height_per_panel: float, dpi: int) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for plotting; use --no-plot for summary-only mode") from exc
    panel_count = len(series)
    fig, axes = plt.subplots(panel_count, 1, figsize=(width, max(height_per_panel * panel_count, 2.5)), dpi=dpi, sharex=True)
    if panel_count == 1:
        axes = [axes]
    fig.suptitle(title or "PHY_QUANT convergence diagnostics")
    for ax, (column, values, diagnostic) in zip(axes, series):
        cm = cumulative_mean(values)
        ax.plot(steps, values, color="0.65", linewidth=0.7, alpha=0.75, label="instantaneous")
        ax.plot(steps, cm, color="tab:red", linewidth=1.8, label="cumulative mean")
        if running_window and running_window > 1:
            rolling_indices, rolling_values = rolling_mean(values, running_window)
            if rolling_values:
                rolling_steps = [steps[i] for i in rolling_indices]
                ax.plot(rolling_steps, rolling_values, color="tab:blue", linewidth=1.3, label=f"rolling mean ({running_window})")
        ax.axhline(diagnostic.mean, color="black", linestyle="--", linewidth=1.3, label="production mean")
        if diagnostic.equilibration_index > 0:
            ax.axvline(steps[diagnostic.equilibration_index], color="tab:green", linestyle=":", linewidth=1.3, label="equilibration cutoff")
        ax.set_ylabel(f"{ylabel}: {column}")
        ax.grid(True, linewidth=0.4, alpha=0.35)
        ax.legend(loc="best", fontsize=8, frameon=False)
    axes[-1].set_xlabel(xlabel)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.print_defaults:
        print_defaults()
        return 0
    if not args.confirm_parameters:
        parser.error("--confirm-parameters is required after reviewing columns, units, and equilibration policy")
    if not args.output and not args.no_plot:
        parser.error("--output is required unless --no-plot is used")
    if not args.summary and args.no_plot:
        parser.error("--summary is required when --no-plot is used")
    header, rows = read_table(args.input, args.delimiter, args.skiprows)
    step_index = resolve_index(header, args.step_column, args.step_col_index, "step")
    value_indices = select_value_columns(header, args.column, args.col_index)
    raw_steps = [row[step_index] * args.x_scale for row in rows]
    user_eq_index: Optional[int] = None
    if args.equilibration_index is not None and args.equilibration_step is not None:
        parser.error("Use only one of --equilibration-index or --equilibration-step")
    if args.equilibration_index is not None:
        user_eq_index = args.equilibration_index
    elif args.equilibration_step is not None:
        user_eq_index = index_from_step(raw_steps, args.equilibration_step * args.x_scale)
    diagnostics: List[SeriesDiagnostic] = []
    plot_series: List[Tuple[str, List[float], SeriesDiagnostic]] = []
    for index in value_indices:
        column = header[index]
        values = [row[index] * args.y_scale for row in rows]
        diagnostic = analyze_series(column, raw_steps, values, user_eq_index, args.auto_equilibration, args)
        diagnostics.append(diagnostic)
        plot_series.append((column, values, diagnostic))
    if args.summary:
        write_summary(args.summary, diagnostics)
    if not args.no_plot:
        make_plot(args.output, args.title, raw_steps, plot_series, args.running_window, args.xlabel, args.ylabel, args.width, args.height_per_panel, args.dpi)
    for item in diagnostics:
        print(f"{item.column}: status={item.auto_status}, eq_index={item.equilibration_index}, eq_step={item.equilibration_step}, mean={item.mean:.10g}, sem={item.sem:.4g}, used={item.used_samples}/{item.total_samples}")
        print(f"  note: {item.auto_reason}")
    print("Diagnostic only: confirm the plot and equilibration cutoff before TI handoff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
