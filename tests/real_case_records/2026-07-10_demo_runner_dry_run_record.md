# 2026-07-10 Demo Runner Staged Execution Record

Dataset location: `../demo` relative to the repository root

Runner config: `tests/runner_configs/demo_multi_window_dry_run.yaml`

Scope: `nqe-postprocess-runner` staged validation on the real 13-window CHMC/CPIHMC-style `energy.dat` dataset.

Boundary: this record verifies config parsing, window discovery, convergence CSV summary command generation/execution, and mean-force extraction. It does not execute TI integration, plotting, or TST. It does not certify sampling convergence, integration direction, units, free-energy interpretation, or production readiness.

## Config Rationale

The `../demo` dataset contains 13 windows:

```text
_1.6 _1.2 _0.8 _0.4 0.0 0.4 0.8 1.2 1.4 1.8 2.2 2.6 3.0
```

Some `energy.dat` files start with numeric rows and do not contain a reliable header. Therefore the runner fixture uses explicit table columns rather than `format: auto` or `format: phy_quant`:

- `format: table`
- `convergence_columns: 2,6,7`
- `convergence_step_col_index: 0`
- `rc_col_index: 6`
- `force_col_index: 7`
- `skiprows: 0`
- `rc_scale: 1.0`
- `force_scale: 1.0`
- `rc_raw_unit_label: au`
- `force_raw_unit_label: au`

The fixture intentionally stops before TI:

- `stop_after: extraction`
- `convergence_plot: false`

`convergence_plot: false` was used because the local runtime did not provide `matplotlib`; the runner therefore passed `--no-plot` and generated CSV summaries only.

## Commands Exercised

Dry-run command:

```text
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  tests/runner_configs/demo_multi_window_dry_run.yaml \
  --dry-run
```

Dry-run outcome:

- Exit code: `0`
- Generated commands: `26`
- Executed commands: `0`
- Output files written: `0`

Dry-run command categories:

- `13` convergence-screening commands using `analyze_phy_quant_convergence.py --no-plot`
- `13` mean-force extraction commands using `extract_mean_force.py`
- `0` integration commands
- `0` plot commands
- `0` TST commands

Real execution command:

```text
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  tests/runner_configs/demo_multi_window_dry_run.yaml
```

Real execution outcome:

- Exit code: `0`
- Generated and executed commands: `26`
- Generated convergence summaries: `13` CSV files in `tests/real_case_records/2026-07-10_demo_runner_dry_run/convergence/`
- Generated mean-force table: `tests/real_case_records/2026-07-10_demo_runner_dry_run/output/mean_force_table.csv`
- Generated runner summary: `tests/real_case_records/2026-07-10_demo_runner_dry_run/output/summary.json`
- No `free_energy_profile.csv`, TST rates, or plots were generated.

## Expected Command Shape

Convergence-screening commands used explicit numeric columns and summary-only mode:

```text
--col-index 2 --col-index 6 --col-index 7 --step-col-index 0 --running-window 1000 --auto-equilibration --no-plot
```

Mean-force extraction commands used explicit table columns:

```text
--format table --rc-col-index 6 --force-col-index 7 --skiprows 0
```

No `integrate_free_energy.py`, `plot_mean_force.py`, `plot_free_energy.py`, or `compute_tst_rates.py` commands were generated because `stop_after: extraction`.

## Output Notes

The extracted mean-force table contains 13 data rows. Most extracted reaction coordinates match the window labels. Two rows show small runtime-adjusted coordinates rather than exact label values:

- window `1.8`: extracted `reaction_coordinate_raw = 1.83857238572`
- window `3.0`: extracted `reaction_coordinate_raw = 2.99996399964`

This is consistent with CHMC/CPIHMC runs where the initial structure can be adjusted toward the constrained reaction coordinate. These observations are diagnostics only; they do not decide skiprows or TI readiness.

The convergence summaries contain `SUGGESTED` auto-equilibration statuses. These are screening hints only and must not be treated as proof of convergence or automatically converted into production discard lengths.

## Interpretation

This staged run validates that `nqe-postprocess-runner` can discover the real `../demo` windows and execute explicit convergence-screening CSV summaries plus mean-force extraction without relying on parser, column, unit, plotting, integration, or TST defaults.

It does not validate whether the extracted data should be integrated. Before any TI execution, the user must review:

- whether numeric columns `2`, `6`, and `7` are the intended diagnostic columns for every window,
- whether startup-adjustment windows require discard or explicit window-RC treatment,
- whether convergence-screening output is sufficient to proceed to TI,
- whether integration direction, zero reference, units, and sign convention are physically confirmed,
- whether TST should remain disabled until elementary-step, state-selection, temperature, and prefactor choices are confirmed.

## Follow-Up

- Preserve this fixture as a runner real-data staged execution test, not as a production config template.
- If integrating later, create a separate config with `stop_after: integration` only after TI direction, zero reference, units, and sign convention are confirmed.
- Keep TST disabled until elementary step, state selection, temperature, and prefactor are explicitly confirmed.
