# Runner Stale Output Fixture Record

Date: 2026-07-17

Purpose: verify that `nqe-postprocess-runner` refuses real execution into a non-empty `output_dir` unless reuse has been explicitly approved.

These checks are expected to distinguish dry-run command review from real execution. A PASS means dry-run can still show intended commands, while a real run refuses stale output reuse before deleting or overwriting any files.

## Fixture

- Config: `tests/runner_configs/negative_existing_output_dir.yaml`
- Stale output directory: `tests/runner_configs/fixtures/stale_output_dir`
- Stale file: `summary.json`

The fixture uses the existing two-window test data in `tests/runner_configs/fixtures/two_windows`.

## Dry-Run Command

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_existing_output_dir.yaml --dry-run
```

Observed result:

```text
DRY RUN: generated 2 command(s); no commands were executed and no output files were written.
```

Status: PASS. Dry-run remains available for command review even when the output directory contains stale files.

## Real-Run Command

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_existing_output_dir.yaml
```

Observed result:

```text
ERROR: Refusing to write into non-empty output_dir: ...\tests\runner_configs\fixtures\stale_output_dir. Existing entries: summary.json. Use a fresh output_dir, inspect and clean the old outputs, or set allow_existing_output_dir: true only after user-approved reuse/cleanup.
```

Status: PASS. The runner refused before deleting `summary.json`, creating `mean_force_table.csv`, or running child scripts.

## Regression Checks

The following checks were run to ensure the new stale-output guard did not break unrelated behavior:

```bash
python -m py_compile nqe-postprocess-runner/scripts/nqe_postprocess_runner.py
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.example.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_bad_columns.yaml
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_truncated_window.yaml
```

Observed results:

- Script compilation passed.
- The bundled config dry-run passed.
- `negative_bad_columns.yaml` still failed during `extract_mean_force.py` because the requested header columns are absent.
- `negative_truncated_window.yaml` still failed during `extract_mean_force.py` because one row has too few numeric columns.

## Boundary

`allow_existing_output_dir: true` is an operational override for user-approved reuse or cleanup. It is not a scientific approval, does not merge provenance, and does not make stale outputs valid inputs for TI/TST.
