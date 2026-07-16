# Runner Child-Script Failure Fixtures Record

Date: 2026-07-14

Purpose: verify runner failure families that cannot be proven by `--dry-run` alone. These fixtures intentionally let the runner generate valid child commands, then fail during real `extract_mean_force.py` execution.

These checks are expected to exit nonzero. A PASS means the runner or child script refused the bad input before integration.

## Bad Header Columns

Fixture: `tests/runner_configs/negative_bad_columns.yaml`

Dry-run command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_bad_columns.yaml --dry-run
```

Observed dry-run result: PASS. The runner generated two extraction commands and wrote no output files.

Real command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_bad_columns.yaml
```

Observed real-run result:

```text
ValueError: Missing requested column in ...\tests\runner_configs\fixtures\two_windows\0.0\energy.dat; header=['Steps', 'RxnCoord', 'MeanForce']. Requested rc_column='MissingRxnCoord', force_column='MissingMeanForce'.
```

Status: PASS. Bad columns are not silently accepted.

## Truncated Window Row

Fixture: `tests/runner_configs/negative_truncated_window.yaml`

Dry-run command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_truncated_window.yaml --dry-run
```

Observed dry-run result: PASS. The runner generated two extraction commands and wrote no output files.

Real command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_truncated_window.yaml
```

Observed real-run result:

```text
Wrote one mean-force row to ...\tmp\runner-negative-truncated-window-output\mean_force_table.csv
ValueError: Row 3 in ...\tests\runner_configs\fixtures\truncated_windows\0.4\energy.dat has 2 numeric column(s), but requested force_col_index=2. This may indicate a truncated or corrupt sampling output.
```

Status: PASS. The first window can leave a partial diagnostic CSV, but the truncated second window is rejected before TI.

## Boundary

These fixtures demonstrate why dry-run review is necessary but not sufficient. Dry-run checks paths, staging, and command generation. Real execution can still fail in child scripts due to bad columns, truncated rows, corrupt sampling output, schema mismatch, or other stage-specific issues.

Partial outputs under ignored `tmp/runner-negative-*` directories are diagnostic artifacts only. They must not be reused for TI.

