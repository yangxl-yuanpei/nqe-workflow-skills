# Runner Negative Fixtures Record

Date: 2026-07-14

Purpose: verify that selected `nqe-postprocess-runner` failure families are executable negative tests, not only prompt-level expectations.

These checks are expected to exit nonzero. A PASS means the runner refused the unsafe or malformed input at the intended guardrail.

## Commands And Results

### Nested YAML Rejection

Command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_parser_nested.yaml --dry-run
```

Observed result:

```text
ERROR: Unsupported indented or nested config line 13: '  title: nested_yaml_is_not_supported'. Use flat key: value YAML or JSON only.
```

Status: PASS.

### Invalid Boolean Rejection

Command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_invalid_bool.yaml --dry-run
```

Observed result:

```text
ERROR: compute_tst must be true or false
```

Status: PASS.

### Missing Windows Rejection

Command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_missing_windows.yaml --dry-run
```

Observed result:

```text
ERROR: Need at least two windows containing 'energy.dat' under ...\tests\runner_configs\fixtures\one_window
```

Status: PASS.

### Invalid Per-Window Skiprows Rejection

Command:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_invalid_per_window_skiprows.yaml --dry-run
```

Observed result:

```text
ERROR: Invalid skiprows value for sample_label '0.0' in ...\tests\runner_configs\negative_invalid_per_window_skiprows.csv: 'SUGGESTED'
```

Status: PASS.

## Positive Regression Checks

The parser hardening did not break representative flat-YAML dry-runs:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.example.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/demo_multi_window_plot_only.yaml --dry-run
```

Observed result: both commands exited successfully.

## Boundary

These fixtures cover parser, discovery, and per-window skiprows guardrails. They do not yet cover all deeper runner failures. In particular, bad extraction columns and truncated window contents may require child-script execution or CHMC/CPIHMC-level checks rather than runner dry-run alone.

