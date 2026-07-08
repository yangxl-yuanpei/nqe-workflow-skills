#!/usr/bin/env python3
"""Check CHMC/CPIHMC sampling window for common issues.

This script performs six diagnostic checks on a CHMC/CPIHMC sampling window:
1. Acceptance probability (from log or user-supplied value)
2. PHY_QUANT / energy.dat output integrity
3. Initial reaction-coordinate adjustment diagnostics
4. Final reaction coordinate consistency with INPUT constraints
5. Potential energy and mean force convergence
6. ALL_INPUT vs INPUT parameter consistency

The script is intentionally conservative. It reports diagnostic information but does not
certify production readiness. Users should review all warnings before using the data.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class CheckResult:
    name: str
    status: str  # PASS, WARN, FAIL, SKIP
    message: str
    details: Optional[str] = None


@dataclass
class InputParameters:
    raw: dict[str, str]
    normalized: dict[str, str]


@dataclass
class AcceptanceEstimate:
    rate: float
    source: str
    details: str


@dataclass
class TableData:
    header: List[str]
    rows: List[List[float]]
    header_source: str
    header_note: Optional[str] = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check CHMC/CPIHMC sampling window for acceptance rate, RC adjustment, convergence, and INPUT/ALL_INPUT agreement."
    )
    parser.add_argument("--window-dir", help="Directory containing INPUT, ALL_INPUT, and PHY_QUANT/energy.dat.")
    parser.add_argument("--input-file", default="INPUT", help="Input parameter file. Default: INPUT.")
    parser.add_argument("--all-input-file", default="ALL_INPUT", help="Parsed input file with defaults. Default: ALL_INPUT.")
    parser.add_argument("--phy-quant-file", default=None, help="Physical quantity output file. Default: auto-detect PHY_QUANT or energy.dat.")
    parser.add_argument("--log-file", default=None, help="Log file containing acceptance rate. Default: auto-detect log or stdout.")
    parser.add_argument("--acceptance-rate", type=float, default=None, help="Override acceptance rate if not found in log (0.0 to 1.0).")
    parser.add_argument("--acceptance-threshold", type=float, default=0.5, help="Minimum acceptable acceptance rate. Default: 0.5.")
    parser.add_argument(
        "--acceptance-energy-tolerance",
        type=float,
        default=0.0,
        help="Tolerance for inferring accepted moves from KinEng/PotEng changes when no log acceptance is available. Default: 0.0.",
    )
    parser.add_argument("--rc-tolerance", type=float, default=0.05, help="Tolerance for RC deviation from constraint (in RC units). Default: 0.05.")
    parser.add_argument("--skip-convergence-check", action="store_true", help="Skip potential energy and mean force convergence check.")
    parser.add_argument("--summary", default=None, help="Optional path to write summary report.")
    parser.add_argument("--confirm-parameters", action="store_true", help="Required acknowledgement that tolerance thresholds were reviewed.")
    parser.add_argument("--print-defaults", action="store_true", help="Print default assumptions and exit.")
    return parser


def print_defaults() -> None:
    print("Default assumptions:")
    print("  acceptance-threshold: 0.5 (50%)")
    print("  acceptance-energy-tolerance: 0.0 (exact energy-change inference when log acceptance is unavailable)")
    print("  rc-tolerance: 0.05 (in reaction coordinate units)")
    print("  output integrity check: enabled (detects truncated or nonnumeric PHY_QUANT/energy.dat rows)")
    print("  path resolution: relative input/log/physical-output paths are resolved under --window-dir")
    print("  missing header handling: numeric-only physical-output files may infer headers from same-named sibling-window files with matching column counts")
    print("  initial RC adjustment check: enabled (diagnostic only; initial mismatch is not an automatic failure)")
    print("  convergence check: enabled (uses PHY_QUANT or energy.dat)")
    print("  INPUT/ALL_INPUT comparison: all parameters")


def parse_input_file(path: Path) -> Tuple[InputParameters, dict[str, List[str]]]:
    """Parse INPUT or ALL_INPUT file into parameter dict and multi-value dict."""
    raw = {}
    normalized = {}
    multi = {}
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 1)
            if len(parts) < 2:
                continue
            key = parts[0]
            value = parts[1].split("#")[0].strip()
            raw[key] = value
            normalized[key.lower().replace("_", "")] = value
            if key not in multi:
                multi[key] = []
            multi[key].append(value)
    return InputParameters(raw=raw, normalized=normalized), multi


def resolve_window_path(window_dir: Path, raw_path: str) -> Path:
    """Resolve window file arguments relative to the window directory.

    Absolute paths are used as-is. Relative paths are interpreted as files inside
    the window directory, because this script checks one sampling window.
    """
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return window_dir / path


def infer_header_from_siblings(path: Path, window_dir: Optional[Path], expected_columns: int) -> Tuple[Optional[List[str]], Optional[str]]:
    """Infer a missing header from same-named files in sibling windows.

    This is only used when the current file starts with numeric data. The
    inferred header must come from a sibling file with the same name and the same
    number of columns. The caller must report the inference to the user.
    """
    if window_dir is None:
        return None, None
    parent = window_dir.parent
    if not parent.exists():
        return None, None
    for sibling in sorted(parent.iterdir(), key=lambda item: item.name):
        if not sibling.is_dir() or sibling.resolve() == window_dir.resolve():
            continue
        candidate = sibling / path.name
        if not candidate.exists():
            continue
        with candidate.open("r", encoding="utf-8") as handle:
            for raw in handle:
                stripped = raw.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if all(is_float(part) for part in parts):
                    break
                if len(parts) == expected_columns:
                    return parts, str(candidate)
                break
    return None, None


def extract_acceptance_from_log(log_path: Path) -> Optional[float]:
    """Try to extract acceptance rate from log file."""
    if not log_path.exists():
        return None
    with log_path.open("r", encoding="utf-8") as handle:
        content = handle.read().lower()
    patterns = [
        r"acceptance\s*rate[:\s]+([0-9.]+)",
        r"acceptance[:\s]+([0-9.]+)",
        r"accept[:\s]+([0-9.]+)",
        r"accepted[:\s]+([0-9]+)\s*/\s*([0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            if "/" in match.group(0):
                accepted = float(match.group(1))
                total = float(match.group(2))
                if total > 0:
                    return accepted / total
            else:
                value = float(match.group(1))
                if value > 1.0:
                    value = value / 100.0
                return value
    return None


def parse_table(path: Path, window_dir: Optional[Path] = None, infer_sibling_header: bool = False) -> TableData:
    """Parse a whitespace table with either a text header or numeric-only rows."""
    header: Optional[List[str]] = None
    rows: List[List[float]] = []
    header_source = "file"
    header_note = None
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if header is None:
                if all(is_float(part) for part in parts):
                    inferred_header = None
                    inferred_source = None
                    if infer_sibling_header:
                        inferred_header, inferred_source = infer_header_from_siblings(path, window_dir, len(parts))
                    if inferred_header:
                        header = inferred_header
                        header_source = "sibling-inferred"
                        header_note = (
                            f"Current file starts with numeric data, so no header was read from this file. "
                            f"Inferred header from sibling file {inferred_source}: {' '.join(inferred_header)}"
                        )
                    else:
                        header = [f"col_{idx}" for idx in range(len(parts))]
                        header_source = "numeric-fallback"
                        header_note = (
                            "Current file starts with numeric data and no matching sibling header was found; "
                            "using numeric fallback columns col_0, col_1, ..."
                        )
                    rows.append([float(part) for part in parts])
                else:
                    header = parts
                    header_source = f"file:{line_no}"
                continue
            if len(parts) != len(header):
                raise ValueError(f"row {line_no} has {len(parts)} columns, expected {len(header)}")
            try:
                rows.append([float(part) for part in parts])
            except ValueError as exc:
                raise ValueError(f"row {line_no} contains nonnumeric data") from exc
    if header is None:
        raise ValueError("no table header or numeric data rows found")
    return TableData(header=header, rows=rows, header_source=header_source, header_note=header_note)


def parse_table_header_and_rows(path: Path) -> Tuple[List[str], List[List[float]]]:
    table = parse_table(path)
    return table.header, table.rows


def find_column_index(header: List[str], names: List[str], fallback: Optional[int] = None) -> Optional[int]:
    """Find a column by exact case-insensitive name, then by fallback index."""
    normalized = {name.lower(): idx for idx, name in enumerate(header)}
    for name in names:
        if name.lower() in normalized:
            return normalized[name.lower()]
    if fallback is not None and fallback < len(header):
        return fallback
    return None


def infer_acceptance_from_energy_table(path: Optional[Path], tolerance: float = 0.0) -> Optional[AcceptanceEstimate]:
    """Infer acceptance from KinEng/PotEng changes when log acceptance is unavailable.

    The rule follows the user-provided legacy script:
    - changed KinEng between neighboring rows indicates an HMC attempt
    - unchanged KinEng indicates an MC attempt
    - changed PotEng indicates the attempted move was accepted
    """
    if path is None or not path.exists():
        return None
    try:
        header, rows = parse_table_header_and_rows(path)
    except ValueError:
        return None
    numeric_only_table = all(name.startswith("col_") for name in header)
    kin_idx = find_column_index(header, ["KinEng", "KineticEnergy", "kinetic_energy"], fallback=1 if numeric_only_table else None)
    pot_idx = find_column_index(header, ["PotEng", "PotentialEnergy", "potential_energy"], fallback=2 if numeric_only_table else None)
    if kin_idx is None or pot_idx is None:
        return None
    if len(rows) < 2:
        return None

    hmc_attempts = 0
    mc_attempts = 0
    hmc_accepts = 0
    mc_accepts = 0
    for current, previous in zip(rows[1:], rows[:-1]):
        kin_changed = abs(current[kin_idx] - previous[kin_idx]) > tolerance
        pot_changed = abs(current[pot_idx] - previous[pot_idx]) > tolerance
        if kin_changed:
            hmc_attempts += 1
            if pot_changed:
                hmc_accepts += 1
        else:
            mc_attempts += 1
            if pot_changed:
                mc_accepts += 1

    attempts = hmc_attempts + mc_attempts
    if attempts == 0:
        return None
    rate = (hmc_accepts + mc_accepts) / attempts
    hmc_rate = hmc_accepts / hmc_attempts if hmc_attempts else None
    mc_rate = mc_accepts / mc_attempts if mc_attempts else None
    details = (
        "Inferred from neighboring-row KinEng/PotEng changes; "
        f"HMC {hmc_accepts}/{hmc_attempts}"
        f"{f' ({hmc_rate:.3f})' if hmc_rate is not None else ''}; "
        f"MC {mc_accepts}/{mc_attempts}"
        f"{f' ({mc_rate:.3f})' if mc_rate is not None else ''}; "
        f"tolerance={tolerance:g}. This is a fallback diagnostic, not an internal log counter."
    )
    return AcceptanceEstimate(rate=rate, source="energy-delta-inferred", details=details)


def auto_detect_phy_quant(window_dir: Path) -> Optional[Path]:
    """Auto-detect PHY_QUANT or energy.dat file."""
    candidates = ["PHY_QUANT", "energy.dat", "phy_quant.dat"]
    for name in candidates:
        path = window_dir / name
        if path.exists():
            return path
    return None


def auto_detect_log(window_dir: Path) -> Optional[Path]:
    """Auto-detect log file."""
    candidates = ["log", "stdout", "output.log", "run.log"]
    for name in candidates:
        path = window_dir / name
        if path.exists():
            return path
    return None


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def check_phy_quant_integrity(phy_quant_path: Optional[Path]) -> CheckResult:
    """Check whether PHY_QUANT/energy.dat has complete numeric rows."""
    if phy_quant_path is None:
        return CheckResult(
            name="PHY_QUANT Integrity",
            status="FAIL",
            message="No PHY_QUANT/energy.dat file was found for this window.",
            details="The sampling task may have failed before writing physical-quantity output.",
        )
    if not phy_quant_path.exists():
        return CheckResult(
            name="PHY_QUANT Integrity",
            status="FAIL",
            message=f"Physical-quantity output file does not exist: {phy_quant_path}",
        )
    text = phy_quant_path.read_text(encoding="utf-8")
    if not text.strip():
        return CheckResult(
            name="PHY_QUANT Integrity",
            status="FAIL",
            message=f"Physical-quantity output file is empty: {phy_quant_path}",
            details="The sampling task may have ended before writing data rows.",
        )

    lines = text.splitlines()
    header: Optional[List[str]] = None
    expected_columns: Optional[int] = None
    data_rows = 0
    first_data_line_no: Optional[int] = None

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if header is None:
            if all(is_float(part) for part in parts):
                header = [f"col_{idx}" for idx in range(len(parts))]
                expected_columns = len(parts)
                data_rows += 1
                first_data_line_no = line_no
            else:
                header = parts
                expected_columns = len(parts)
            continue
        if expected_columns is not None and len(parts) != expected_columns:
            return CheckResult(
                name="PHY_QUANT Integrity",
                status="FAIL",
                message=(
                    f"Row {line_no} has {len(parts)} columns, expected {expected_columns}; "
                    "physical-quantity output appears truncated or malformed."
                ),
                details=(
                    "This commonly happens when a job is killed while writing a row, "
                    "for example due to scheduler termination, wall-time limits, or exhausted allocation."
                ),
            )
        bad_tokens = [part for part in parts if not is_float(part)]
        if bad_tokens:
            return CheckResult(
                name="PHY_QUANT Integrity",
                status="FAIL",
                message=f"Row {line_no} contains nonnumeric token(s): {', '.join(bad_tokens[:3])}",
                details="Treat this window as failed or incomplete until the raw output is audited.",
            )
        data_rows += 1
        if first_data_line_no is None:
            first_data_line_no = line_no

    if data_rows == 0:
        return CheckResult(
            name="PHY_QUANT Integrity",
            status="FAIL",
            message="Physical-quantity output has a header but no numeric data rows.",
            details="The sampling task may have stopped before production output began.",
        )

    if not text.endswith(("\n", "\r")):
        return CheckResult(
            name="PHY_QUANT Integrity",
            status="WARN",
            message="Final data row is complete, but the file has no trailing newline.",
            details=(
                "This is not automatically a failure, but it can indicate an interrupted write. "
                "Confirm the scheduler/log status before production TI handoff."
            ),
        )

    return CheckResult(
        name="PHY_QUANT Integrity",
        status="PASS",
        message=f"Found {data_rows} complete numeric data row(s).",
        details=f"First data row: {first_data_line_no}; columns: {expected_columns}.",
    )


def parse_phy_quant_rc(path: Path, window_dir: Optional[Path] = None) -> Tuple[List[str], List[int], List[float], List[float], Optional[str]]:
    """Parse PHY_QUANT file to extract RC columns plus first and final values."""
    if not path.exists():
        raise FileNotFoundError(f"PHY_QUANT file not found: {path}")
    rc_columns = []
    rc_indices = []
    first_values = []
    final_values = []
    table = parse_table(path, window_dir=window_dir, infer_sibling_header=True)
    for i, col in enumerate(table.header):
        if col.lower().startswith("rxncoord") or col.lower().startswith("rc"):
            rc_columns.append(col)
            rc_indices.append(i)
    for row in table.rows:
        if rc_indices:
            current_values = [row[i] for i in rc_indices if i < len(row)]
            if not first_values:
                first_values = current_values
            final_values = current_values
    return rc_columns, rc_indices, first_values, final_values, table.header_note


def parse_input_file_multi(path: Path) -> Tuple[dict[str, str], dict[str, List[str]]]:
    """Parse INPUT file, handling multi-line parameters like Rxn_Coord."""
    raw = {}
    multi = {}
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 1)
            if len(parts) < 2:
                continue
            key = parts[0]
            value = parts[1].split("#")[0].strip()
            raw[key] = value
            if key not in multi:
                multi[key] = []
            multi[key].append(value)
    return raw, multi


def extract_rc_from_input_multi(multi_params: dict[str, List[str]]) -> List[Tuple[str, float]]:
    """Extract all reaction coordinate constraints from INPUT, handling multiple Rxn_Coord lines."""
    rc_constraints = []
    rxn_coord_lines = multi_params.get("Rxn_Coord", [])
    for line in rxn_coord_lines:
        parts = line.split()
        if len(parts) >= 2:
            rc_type = parts[0]
            if rc_type == "DIST" and len(parts) >= 4:
                try:
                    target = float(parts[3])
                    rc_constraints.append((f"DIST_{parts[1]}_{parts[2]}", target))
                except ValueError:
                    pass
            elif rc_type == "DIFF" and len(parts) >= 5:
                try:
                    target = float(parts[4])
                    rc_constraints.append((f"DIFF_{parts[1]}_{parts[2]}_{parts[3]}", target))
                except ValueError:
                    pass
    return rc_constraints


def check_acceptance_rate(acceptance: Optional[float], threshold: float, source: Optional[str] = None, details: Optional[str] = None) -> CheckResult:
    """Check if acceptance rate meets threshold."""
    if acceptance is None:
        return CheckResult(
            name="Acceptance Rate",
            status="SKIP",
            message="Acceptance rate not found in log or energy-table fallback; provide --acceptance-rate or check log/output files.",
        )
    source_text = f" from {source}" if source else ""
    if acceptance < threshold:
        return CheckResult(
            name="Acceptance Rate",
            status="FAIL",
            message=f"Acceptance rate{source_text} {acceptance:.3f} below threshold {threshold:.3f}.",
            details=details or "Low acceptance may indicate timestep too large or poor equilibration.",
        )
    return CheckResult(
        name="Acceptance Rate",
        status="PASS",
        message=f"Acceptance rate{source_text} {acceptance:.3f} meets the user-reviewed threshold {threshold:.3f}.",
        details=details,
    )


def check_rc_consistency(final_rcs: List[float], rc_constraints: List[Tuple[str, float]], tolerance: float) -> CheckResult:
    """Check if final RC values match INPUT constraints."""
    if not rc_constraints:
        return CheckResult(
            name="RC Consistency",
            status="SKIP",
            message="No reaction coordinate constraints found in INPUT.",
        )
    if not final_rcs:
        return CheckResult(
            name="RC Consistency",
            status="FAIL",
            message="No reaction coordinate values found in PHY_QUANT output.",
            details="Check that PHY_QUANT file contains RxnCoord columns.",
        )
    deviations = []
    for i, (label, target) in enumerate(rc_constraints):
        if i < len(final_rcs):
            deviation = abs(final_rcs[i] - target)
            deviations.append((label, target, final_rcs[i], deviation))
    if not deviations:
        return CheckResult(
            name="RC Consistency",
            status="SKIP",
            message="Could not match RC constraints to output columns.",
        )
    failures = [(label, target, actual, dev) for label, target, actual, dev in deviations if dev > tolerance]
    if failures:
        details = "\n".join([f"  {label}: target={target:.4f}, actual={actual:.4f}, deviation={dev:.4f}" for label, target, actual, dev in failures])
        return CheckResult(
            name="RC Consistency",
            status="FAIL",
            message=f"{len(failures)} RC constraint(s) violated (tolerance={tolerance}).",
            details=details,
        )
    details = "\n".join([f"  {label}: target={target:.4f}, actual={actual:.4f}, deviation={dev:.4f}" for label, target, actual, dev in deviations])
    return CheckResult(
        name="RC Consistency",
        status="PASS",
        message=f"All {len(deviations)} RC constraint(s) satisfied.",
        details=details,
    )


def check_initial_rc_adjustment(first_rcs: List[float], final_rcs: List[float], rc_constraints: List[Tuple[str, float]], tolerance: float) -> CheckResult:
    """Report whether the initial RC differs from the target and later adjusts."""
    if not rc_constraints:
        return CheckResult(
            name="Initial RC Adjustment",
            status="SKIP",
            message="No reaction coordinate constraints found in INPUT.",
        )
    if not first_rcs or not final_rcs:
        return CheckResult(
            name="Initial RC Adjustment",
            status="SKIP",
            message="Could not read both first and final reaction-coordinate values.",
        )

    diagnostics = []
    adjusted = []
    initially_on_target = []
    still_off_target = []
    for i, (label, target) in enumerate(rc_constraints):
        if i >= len(first_rcs) or i >= len(final_rcs):
            continue
        first = first_rcs[i]
        final = final_rcs[i]
        first_dev = abs(first - target)
        final_dev = abs(final - target)
        diagnostics.append((label, target, first, final, first_dev, final_dev))
        if first_dev <= tolerance:
            initially_on_target.append(label)
        elif final_dev <= tolerance:
            adjusted.append(label)
        else:
            still_off_target.append(label)

    if not diagnostics:
        return CheckResult(
            name="Initial RC Adjustment",
            status="SKIP",
            message="Could not match RC constraints to first/final output columns.",
        )

    details = "\n".join(
        [
            (
                f"  {label}: target={target:.4f}, first={first:.4f}, final={final:.4f}, "
                f"first_deviation={first_dev:.4f}, final_deviation={final_dev:.4f}"
            )
            for label, target, first, final, first_dev, final_dev in diagnostics
        ]
    )
    if adjusted:
        return CheckResult(
            name="Initial RC Adjustment",
            status="WARN",
            message=(
                f"{len(adjusted)} RC value(s) started outside tolerance and ended near target. "
                "This can be expected when CHMC/CPIHMC adjusts the initial structure, but review startup behavior."
            ),
            details=details,
        )
    if still_off_target:
        return CheckResult(
            name="Initial RC Adjustment",
            status="WARN",
            message=(
                f"{len(still_off_target)} RC value(s) started outside tolerance and did not end near target. "
                "Final RC consistency check should determine whether the window target failed."
            ),
            details=details,
        )
    return CheckResult(
        name="Initial RC Adjustment",
        status="PASS",
        message=f"All {len(initially_on_target)} matched RC value(s) started within tolerance of the target.",
        details=details,
    )


def check_convergence(phy_quant_path: Path, window_dir: Optional[Path] = None) -> CheckResult:
    """Check potential energy and mean force convergence using simple heuristics."""
    if not phy_quant_path or not phy_quant_path.exists():
        return CheckResult(
            name="Convergence",
            status="SKIP",
            message="PHY_QUANT file not found; skipping convergence check.",
        )
    try:
        pot_eng_values = []
        mean_force_values = []
        table = parse_table(phy_quant_path, window_dir=window_dir, infer_sibling_header=True)
        if "PotEng" in table.header:
            idx = table.header.index("PotEng")
            pot_eng_values = [row[idx] for row in table.rows if idx < len(row)]
        mean_force_column = None
        if "MeanForce_0" in table.header:
            mean_force_column = "MeanForce_0"
        elif "MeanForce" in table.header:
            mean_force_column = "MeanForce"
        if mean_force_column:
            idx = table.header.index(mean_force_column)
            mean_force_values = [row[idx] for row in table.rows if idx < len(row)]
        if len(pot_eng_values) < 10:
            return CheckResult(
                name="Convergence",
                status="WARN",
                message=f"Insufficient samples for convergence check ({len(pot_eng_values)} < 10).",
                details=table.header_note,
            )
        n = len(pot_eng_values)
        first_half = pot_eng_values[: n // 2]
        second_half = pot_eng_values[n // 2 :]
        mean_first = sum(first_half) / len(first_half)
        mean_second = sum(second_half) / len(second_half)
        rel_diff = abs(mean_first - mean_second) / max(abs(mean_second), 1e-10)
        if rel_diff > 0.01:
            return CheckResult(
                name="Convergence",
                status="WARN",
                message=f"Potential energy shows {rel_diff * 100:.2f}% drift between first and second half.",
                details="\n".join(filter(None, [table.header_note, "Consider longer equilibration or production run."])),
            )
        if mean_force_values and len(mean_force_values) >= 10:
            n_mf = len(mean_force_values)
            first_half_mf = mean_force_values[: n_mf // 2]
            second_half_mf = mean_force_values[n_mf // 2 :]
            mean_first_mf = sum(first_half_mf) / len(first_half_mf)
            mean_second_mf = sum(second_half_mf) / len(second_half_mf)
            rel_diff_mf = abs(mean_first_mf - mean_second_mf) / max(abs(mean_second_mf), 1e-10)
            if rel_diff_mf > 0.05:
                return CheckResult(
                    name="Convergence",
                    status="WARN",
                    message=f"Mean force shows {rel_diff_mf * 100:.2f}% drift.",
                    details="\n".join(filter(None, [table.header_note, "Consider longer production run for mean force convergence."])),
                )
        return CheckResult(
            name="Convergence",
            status="PASS",
            message="Potential energy and mean force show reasonable stability.",
            details=table.header_note,
        )
    except Exception as exc:
        return CheckResult(
            name="Convergence",
            status="SKIP",
            message=f"Could not parse PHY_QUANT for convergence check: {exc}",
        )


def check_input_all_input_agreement(input_params: InputParameters, all_input_params: InputParameters, input_multi: Optional[dict[str, List[str]]] = None) -> CheckResult:
    """Check if INPUT parameters are consistent with ALL_INPUT (parsed with defaults)."""
    if not all_input_params.raw:
        return CheckResult(
            name="INPUT/ALL_INPUT Agreement",
            status="SKIP",
            message="ALL_INPUT file is empty or not found.",
        )
    discrepancies = []
    for key, value in input_params.raw.items():
        normalized_key = key.lower().replace("_", "")
        if normalized_key in all_input_params.normalized:
            all_input_value = all_input_params.normalized[normalized_key]
            if input_multi and key in input_multi and len(input_multi[key]) > 1:
                combined_input = " ".join(input_multi[key])
                if combined_input != all_input_value:
                    discrepancies.append((key, combined_input, all_input_value))
            elif value != all_input_value:
                discrepancies.append((key, value, all_input_value))
    if discrepancies:
        details = "\n".join([f"  {key}: INPUT={value}, ALL_INPUT={all_value}" for key, value, all_value in discrepancies[:10]])
        if len(discrepancies) > 10:
            details += f"\n  ... and {len(discrepancies) - 10} more"
        return CheckResult(
            name="INPUT/ALL_INPUT Agreement",
            status="FAIL",
            message=f"{len(discrepancies)} parameter(s) differ between INPUT and ALL_INPUT.",
            details=details,
        )
    return CheckResult(
        name="INPUT/ALL_INPUT Agreement",
        status="PASS",
        message=f"All {len(input_params.raw)} INPUT parameters match ALL_INPUT.",
    )


def write_summary(path: Path, results: List[CheckResult]) -> None:
    """Write summary report to file."""
    with path.open("w", encoding="utf-8") as handle:
        handle.write("CHMC/CPIHMC Window Check Summary\n")
        handle.write("=" * 50 + "\n\n")
        for result in results:
            handle.write(f"[{result.status}] {result.name}\n")
            handle.write(f"  {result.message}\n")
            if result.details:
                handle.write(f"  Details:\n{result.details}\n")
            handle.write("\n")
        pass_count = sum(1 for r in results if r.status == "PASS")
        warn_count = sum(1 for r in results if r.status == "WARN")
        fail_count = sum(1 for r in results if r.status == "FAIL")
        skip_count = sum(1 for r in results if r.status == "SKIP")
        handle.write(f"Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL, {skip_count} SKIP\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.print_defaults:
        print_defaults()
        return 0
    if not args.window_dir:
        parser.error("--window-dir is required unless --print-defaults is used")
    if not args.confirm_parameters:
        print_defaults()
        print("\nRefusing to run checks until --confirm-parameters is supplied.", file=sys.stderr)
        return 2
    window_dir = Path(args.window_dir)
    if not window_dir.is_dir():
        print(f"Error: {window_dir} is not a directory.", file=sys.stderr)
        return 1
    input_path = resolve_window_path(window_dir, args.input_file)
    all_input_path = resolve_window_path(window_dir, args.all_input_file)
    if args.phy_quant_file:
        phy_quant_path = resolve_window_path(window_dir, args.phy_quant_file)
    else:
        phy_quant_path = auto_detect_phy_quant(window_dir)
    if args.log_file:
        log_path = resolve_window_path(window_dir, args.log_file)
    else:
        log_path = auto_detect_log(window_dir)
    results: List[CheckResult] = []
    try:
        input_params, input_multi = parse_input_file(input_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    try:
        all_input_params, _ = parse_input_file(all_input_path)
    except FileNotFoundError:
        all_input_params = InputParameters(raw={}, normalized={})
    acceptance = args.acceptance_rate
    acceptance_source = "user-provided" if acceptance is not None else None
    acceptance_details = None
    if acceptance is None and log_path:
        acceptance = extract_acceptance_from_log(log_path)
        if acceptance is not None:
            acceptance_source = f"log:{log_path.name}"
    phy_quant_integrity = check_phy_quant_integrity(phy_quant_path)
    if acceptance is None and phy_quant_integrity.status != "FAIL":
        acceptance_estimate = infer_acceptance_from_energy_table(phy_quant_path, args.acceptance_energy_tolerance)
        if acceptance_estimate is not None:
            acceptance = acceptance_estimate.rate
            acceptance_source = acceptance_estimate.source
            acceptance_details = acceptance_estimate.details
    results.append(check_acceptance_rate(acceptance, args.acceptance_threshold, acceptance_source, acceptance_details))
    results.append(phy_quant_integrity)
    if phy_quant_integrity.status == "FAIL":
        rc_columns, rc_indices, first_rcs, final_rcs = ([], [], [], [])
        header_note = None
    else:
        try:
            if phy_quant_path:
                rc_columns, rc_indices, first_rcs, final_rcs, header_note = parse_phy_quant_rc(phy_quant_path, window_dir=window_dir)
            else:
                rc_columns, rc_indices, first_rcs, final_rcs, header_note = ([], [], [], [], None)
        except Exception as exc:
            rc_columns, rc_indices, first_rcs, final_rcs = ([], [], [], [])
            header_note = None
            results.append(
                CheckResult(
                    name="PHY_QUANT Parse",
                    status="FAIL",
                    message=f"Could not parse reaction-coordinate columns: {exc}",
                    details="Treat this output as failed or incomplete before downstream TI.",
                )
            )
    if header_note:
        results.append(
            CheckResult(
                name="Header Inference",
                status="WARN",
                message="Header was not read directly from this physical-output file; review inferred column mapping.",
                details=header_note,
            )
        )
    rc_constraints = extract_rc_from_input_multi(input_multi)
    if phy_quant_integrity.status == "FAIL":
        results.append(
            CheckResult(
                name="RC Consistency",
                status="SKIP",
                message="Skipped because PHY_QUANT/energy.dat failed integrity checks.",
            )
        )
    else:
        results.append(check_initial_rc_adjustment(first_rcs, final_rcs, rc_constraints, args.rc_tolerance))
        results.append(check_rc_consistency(final_rcs, rc_constraints, args.rc_tolerance))
    if not args.skip_convergence_check and phy_quant_path and phy_quant_integrity.status != "FAIL":
        results.append(check_convergence(phy_quant_path, window_dir=window_dir))
    results.append(check_input_all_input_agreement(input_params, all_input_params, input_multi))
    for result in results:
        print(f"[{result.status}] {result.name}: {result.message}")
        if result.details:
            print(f"    {result.details}")
    if args.summary:
        write_summary(Path(args.summary), results)
        print(f"\nSummary written to {args.summary}")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARN")
    if fail_count > 0:
        print(f"\n{fail_count} check(s) FAILED. Review warnings before using this window's data.")
        return 1
    if warn_count > 0:
        print(f"\n{warn_count} check(s) produced warnings. Review before proceeding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
