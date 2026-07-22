# Convergence Review Checklist

Use this checklist after CHMC/CPIHMC convergence diagnostics have been generated and before mean-force extraction or thermodynamic integration.

This checklist is a human-review handoff artifact. It records what the diagnostic scripts found, what the user inspected, and what decision was made for each suspicious reaction-coordinate window. It does not prove convergence by itself.

## Required Sections

### Run Context

- dataset label
- sampling root
- temperature or condition label, if relevant
- input file name
- diagnostic output directory
- columns inspected, including names or zero-based indices
- step-axis source: real step column/index or row/sample index after skiprows
- global diagnostic skiprows used before plotting
- whether auto-equilibration was enabled, and that it was screening only
- window-health check coverage: whether `check_chmc_window.py` or equivalent checks were run for every intended window
- acceptance-rate source and review policy: log/user-provided value, `energy-delta-inferred` fallback, missing/TODO, and the user-approved interpretation range if one exists

### Inventory Summary

Report, at minimum:

- number of expected windows
- number of discovered windows
- reaction-coordinate range
- per-window row-count consistency
- column-count consistency
- missing, truncated, or short-row windows
- `INPUT`/`ALL_INPUT` consistency if checked
- `OUTPUT` column definition if available
- acceptance-rate coverage summary: number from log/user value, number inferred from energy deltas, number missing/TODO, and any windows outside the user-approved review range

### Per-Window Diagnostic Summary

Provide a compact table with one row per window and at least:

- window label / reaction-coordinate value
- row count
- largest suggested `eq_index` among inspected columns
- columns that triggered nonzero `eq_index`
- potential-energy status
- reaction-coordinate status
- mean-force status
- acceptance-rate status and source, for example `log`, `user-provided`, `energy-delta-inferred`, `missing`, or `not checked`
- notes

Use `eq_index` to mean row/sample index after diagnostic `skiprows` when row-index mode was used. Do not call it simulation step unless a real step column was used.

### Suspicious Window Detail

For every window with a large suggested cutoff, sign change, large drift, missing output, or unusual neighboring-window behavior, include:

- observed issue
- affected columns
- all-sample mean and production mean for the relevant columns
- whether potential energy, total energy, reaction coordinate, and mean force drift together
- whether the late-time platform is visually stable
- comparison with neighboring reaction-coordinate windows
- if left/right mean-force components are present, whether the two components agree in mean, sign, drift, and neighboring-window trend
- user decision: use all, use user-approved discard, rerun, exclude, or unresolved
- user rationale

The rationale should record scientific reasoning without converting it into a general default. For example, if the user chooses to rerun rather than accept a large cutoff, record whether the decision was based on a lower late-time potential-energy platform, a mean-force sign change, consistency or inconsistency with neighboring windows, too little remaining production data, or unclear visual stability. These are evidence categories, not reusable rules.

### Candidate Skiprows Draft

If useful, provide a non-runnable candidate discard table:

```csv
sample_label,skiprows,reason,status
WINDOW_LABEL,NUMERIC_ROWS,USER_REVIEW_REQUIRED,NON_RUNNABLE
```

Rules:

- Use only numeric `skiprows` values in the draft table.
- Mark the draft as `NON_RUNNABLE` until the user explicitly approves it for extraction.
- Do not copy automatic `SUGGESTED` values into production `skiprows` without user review.
- Missing windows should fall back only to a user-confirmed global `skiprows`, not to inferred values.

### Handoff Decision

End with one of:

- `READY_FOR_EXTRACTION_WITH_USER_APPROVED_SKIPROWS`
- `RERUN_REQUIRED_FOR_LISTED_WINDOWS`
- `WINDOW_EXCLUSION_REQUIRES_USER_APPROVAL`
- `UNRESOLVED_REVIEW_REQUIRED`

Also list the exact remaining questions before extraction, such as which mean-force column to use, how to combine multiple mean-force columns, unit scaling, and whether the chosen discard policy has been approved.

If acceptance-rate coverage is missing or only partially reviewed, choose `UNRESOLVED_REVIEW_REQUIRED` unless the user explicitly documents why downstream diagnostic-only extraction may proceed with that limitation. Do not describe the sampling batch as converged or TI-ready from potential-energy and mean-force plots alone.

For left/right mean-force outputs, list the pending or approved extraction policy explicitly:

- `force_source = left_component`
- `force_source = right_component`
- `force_source = user_precomputed_combined_column`
- legacy-output workaround: a documented preprocessing step that writes a user-approved combined force column

Do not assume that left/right components should be averaged. Averaging is a user-approved combine policy. If it is selected, record the formula, for example `mean_force = (mfl + mfr) / 2`, the source columns, units, and any observed left-right discrepancy.

## Required Agent Behavior

- Generate this checklist after a convergence diagnostic run when the user asks whether to proceed to extraction, or when any window has nonzero suggested equilibration, strong drift, sign change, suspicious energy behavior, missing data, or truncated output.
- Ask the user to inspect the relevant plots before accepting nonzero discard or declaring a window usable.
- If the user chooses to rerun a window, record that as the handoff decision and stop before extraction for the affected dataset.
- Do not treat a stable late-time platform, lower potential energy, or neighboring-window trend consistency as automatic proof of convergence. These can support a documented user decision, but they do not replace user approval or additional sampling when needed.
