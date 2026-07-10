# 2026-07-10 Demo Runner Dry-Run Record

Dataset location: `../demo` relative to the repository root

Runner config: `tests/runner_configs/demo_multi_window_dry_run.yaml`

Scope: `nqe-postprocess-runner` command-generation validation on the real 13-window CHMC/CPIHMC-style `energy.dat` dataset.

Boundary: this record verifies config parsing, window discovery, and child-command generation. It does not execute convergence screening, mean-force extraction, TI integration, plotting, or TST. It does not certify sampling convergence, integration direction, units, free-energy interpretation, or production readiness.

## Config Rationale

The `../demo` dataset contains 13 windows:

```text
_1.6 _1.2 _0.8 _0.4 0.0 0.4 0.8 1.2 1.4 1.8 2.2 2.6 3.0
```

Some `energy.dat` files start with numeric rows and do not contain a header. Therefore the runner fixture uses explicit table columns rather than `format: auto` or `format: phy_quant`:

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

The fixture disables plot and TST command generation:

- `plots: false`
- `compute_tst: false`

The runner still generates an integration command after extraction because that is the current runner pipeline shape. The config uses explicit integration fields only so dry-run can expose the command for review:

- `integration_direction: input`
- `zero: "none"`
- `free_energy_scale: 1.0`
- `free_energy_unit_label: au`

These are not production TI approvals.

## Commands Exercised

Initial dry-run command:

```text
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  tests/runner_configs/demo_multi_window_dry_run.yaml \
  --dry-run
```

Initial outcome:

- `FAIL`, because `zero: none` was parsed by the runner's simple YAML parser as a null value.
- Fix: quote the value as `zero: "none"`.

Retest outcome:

- Exit code: `0`
- Generated commands: `27`
- Executed commands: `0`
- Output files written: `0`

Command categories:

- `13` convergence-screening commands using `analyze_phy_quant_convergence.py`
- `13` mean-force extraction commands using `extract_mean_force.py`
- `1` integration command using `integrate_free_energy.py`
- `0` plot commands
- `0` TST commands

## Expected Command Shape

Convergence-screening commands used explicit numeric columns:

```text
--col-index 2 --col-index 6 --col-index 7 --step-col-index 0 --running-window 1000 --auto-equilibration
```

Mean-force extraction commands used explicit table columns:

```text
--format table --rc-col-index 6 --force-col-index 7 --skiprows 0
```

The integration command was generated for review only:

```text
--integration-direction input --zero none --free-energy-scale 1.0 --free-energy-unit-label au
```

No `plot_mean_force.py`, `plot_free_energy.py`, or `compute_tst_rates.py` commands were generated.

## Interpretation

This dry-run validates that `nqe-postprocess-runner` can discover the real `../demo` windows and generate explicit convergence-screening and extraction commands without relying on parser, column, unit, plotting, or TST defaults.

It does not validate whether the generated commands should be executed for production analysis. Before any real execution, the user must review:

- whether numeric columns `2`, `6`, and `7` are the intended diagnostic columns for every window,
- whether startup-adjustment windows require discard or explicit `--window-rc`,
- whether convergence-screening output is sufficient to proceed to TI,
- whether integration direction, zero reference, units, and sign convention are physically confirmed,
- whether TST should remain disabled until elementary-step, state-selection, temperature, and prefactor choices are confirmed.

## Follow-Up

- Consider running only the convergence-screening and extraction portions for `../demo` after user review.
- If integrating later, treat it as a guarded TI-only test unless the user explicitly confirms TST assumptions.
- Preserve this fixture as a runner real-data command-generation test, not as a production config template.
