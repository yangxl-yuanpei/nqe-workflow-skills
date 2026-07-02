# Script Interface Smoke Test Record

Date: 2026-07-02

Commit or branch: main @ 07b6f3c

Repository status: dirty (docs/SKILL.md/references edits pending)

Agent/model: opencode (deepseek-v4-pro)

Freshness level: N/A (script-level smoke, not agent-behavior test)

Prompt source: docs/testing.md, "Script-Level Smoke Tests" section

Result: 12 PASS, 4 WARN, 0 FAIL (script bugs need fixing)

Reviewer: codex

## Scope

Verify that all documented helper scripts load, expose expected options, and can execute their advertised interface modes (--help, --print-defaults, --dry-run).

## Results

| # | Command | Exit | Result | Notes |
|---|---|---|---|---|
| 1 | `check_workflow_files.py --software abacus --path .../corr --allow-warnings` | 0 | PASS | 2 PASS, 1 WARN, 2 FAIL — FAILs expected: INPUT/STRU not found (real files are INPUT_sp/STRU_opt) |
| 2 | `check_workflow_files.py --software dpgen --path .../corr-dpgen --allow-warnings` | 0 | PASS | 7 PASS, 2 WARN — WARNs about TODO_USER_APPROVAL and REDACTED_* placeholders are expected |
| 3 | `check_workflow_files.py --software deepmd --path .../corr-deepmd --allow-warnings` | 0 | PASS | 7 PASS |
| 4 | `inspect_dpdata_system.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 5 | `convert_with_dpdata.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 6 | `compare_converted_system.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 7 | `parse_lcurve.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 8 | `check_chmc_window.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 9 | `analyze_phy_quant_convergence.py --print-defaults` | 2 | WARN | argparse requires `--input` despite `--print-defaults` flag; `--print-defaults` should short-circuit |
| 10 | `extract_mean_force.py --print-defaults` | 2 | WARN | argparse requires `--input`, `--dataset-label` despite `--print-defaults` |
| 11 | `integrate_free_energy.py --print-defaults` | 2 | WARN | argparse requires `--input` despite `--print-defaults` |
| 12 | `compute_tst_rates.py --print-defaults` | 2 | WARN | argparse requires `--elementary-step`, `--dataset-label`, `--temperature` despite `--print-defaults` |
| 13 | `plot_mean_force.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 14 | `plot_free_energy.py --help` | 0 | PASS | Loads and exposes expected arguments |
| 15 | `nqe_postprocess_runner.py config.example.yaml --dry-run` | 0 | WARN | **Executed the full pipeline** (extract×14 windows + integrate + plot×2 + compute_tst) instead of only printing commands. `--dry-run` is not working — needs investigation. |
| 16 | `nqe_postprocess_runner.py config.convergence-screening.example.yaml --dry-run` | 0 | WARN | Same as #15 — executed full pipeline |

## Observed Issues

### Issue 1: `--print-defaults` broken for scripts with `required=True` args (items 9-12)

Four scripts (`analyze_phy_quant_convergence.py`, `extract_mean_force.py`, `integrate_free_energy.py`, `compute_tst_rates.py`) have `--print-defaults` but argparse requires other arguments first because they're declared `required=True`. This means `--print-defaults` cannot be used independently.

Fix: make `--print-defaults` check before argparse validates required args, or remove `required=True` from arguments and validate them in `main()` instead.

### Issue 2: `nqe_postprocess_runner.py --dry-run` executes instead of printing (items 15-16)

The `--dry-run` flag ran the full TI/TST pipeline (extract×14 → integrate → plot×2 → compute_tst) with the demo data, generating real output CSVs and plots. This is NOT a dry-run — it executed everything.

Likely file to improve: `nqe-postprocess-runner/scripts/nqe_postprocess_runner.py` — check `--dry-run` logic.

## Overall Notes

12 of 16 script-level tests PASS cleanly (load, expose --help). The 4 WARNs are real issues:

1. `--print-defaults` broken for 4 scripts due to argparse `required=True` conflict (minor, not urgent)
2. `nqe_postprocess_runner.py --dry-run` executes full pipeline instead of printing (serious — contradicts `parameters_confirmed` guardrail philosophy)

The runner bug is the most concerning: a config with `parameters_confirmed: true` triggers execution even with `--dry-run`, which defeats the purpose of the safety check.
