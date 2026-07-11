# 2026-07-11 Candidate Per-Window Skiprows Dry-Run Record

Runner config: `tests/runner_configs/demo_multi_window_candidate_skiprows.yaml`

Override CSV: `tests/runner_configs/demo_multi_window_candidate_skiprows.csv`

Raw dataset: `../demo`, a 13-window CHMC/CPIHMC-style `energy.dat` dataset outside the repository

Boundary: this record verifies runner config parsing and dry-run command generation for explicit per-window extraction discard overrides. It does not execute extraction and does not certify convergence, TI readiness, or production correctness.

## Config Intent

The baseline staged runner fixture remains `tests/runner_configs/demo_multi_window_dry_run.yaml` with `skiprows: 0` for all windows.

This candidate fixture is intentionally separate. It keeps global `skiprows: 0` but adds:

```yaml
per_window_skiprows_file: demo_multi_window_candidate_skiprows.csv
```

The CSV currently contains only two candidate overrides:

```csv
sample_label,skiprows,reason
0.0,10000,MeanForce convergence screen suggested eq_index=10000; candidate for sensitivity review only
1.8,10000,RxnCoord adjustment is visually obvious and convergence screen suggested eq_index=10000; candidate for sensitivity review only
```

These values come from diagnostic review and discard sensitivity screening. The user later accepted them for this demo review only; they are not production-approved discard lengths for any new target system.

## Dry-Run Result

Status: `PASS`

The dry-run generated 26 child commands:

- 13 convergence-screening commands
- 13 mean-force extraction commands

The convergence-screening commands continue to use `--skiprows 0`, because they are meant to inspect the full trajectory.

The extraction commands use:

- `--skiprows 10000` for sample `0.0`
- `--skiprows 10000` for sample `1.8`
- `--skiprows 0` for all other samples

The dry-run command notes include the per-window discard reason for the two overridden windows.

## Interpretation

The runner can now route reviewed per-window discard choices into extraction commands without modifying the baseline fixture and without auto-promoting convergence-screening `SUGGESTED` indices.

Before using this pattern for a production target, the user must inspect the convergence plots/CSVs directly and approve whether the proposed discard is scientifically reasonable.
