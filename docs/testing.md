# Testing Guide

This guide explains how to test the NQE workflow skills repository. The goal is to check whether an agent uses the skills conservatively, follows documented references, and preserves scientific guardrails. Passing these tests does not mean a calculation is production-ready.

## Test Order

Run tests in this order:

1. Minimal smoke prompts
2. Minimal failure prompts
3. Stage-specific manual prompts
4. Script-level smoke tests
5. Optional TI/TST demo chain

The manual prompts live in [tests/manual_prompts.md](../tests/manual_prompts.md).

For dated fresh-agent test procedure and record format, see [fresh-agent-testing.md](fresh-agent-testing.md).

## Manual Behavior Tests

Use a fresh agent or fresh conversation for each prompt whenever possible. The point is to test whether the repository files are sufficient, not whether the agent remembers earlier context from this development thread.

A clean subagent can also be used for practical fresh-agent testing if it receives only the repository path, the relevant `SKILL.md` path, required reference paths, and the exact test prompt. Record this as `Freshness level: subagent-fresh`; do not provide the subagent with expected behavior or prior development context.

### 1. Minimal Smoke Prompts

Start with the `Minimal Smoke Prompts` section in [tests/manual_prompts.md](../tests/manual_prompts.md).

These prompts check whether each skill can answer a normal first-use question. A pass means the agent identifies the correct stage, uses the right vocabulary, and keeps the repository's teaching-workflow boundary.

### 2. Minimal Failure Prompts

Next run the `Minimal Failure Prompts` section.

These prompts intentionally ask the agent to do unsafe things such as invent production parameters, reuse unrelated reference examples, skip workflow stages, or treat a file name as proof of readiness. A pass means the agent corrects the premise, refuses to invent missing values, and explains what must be confirmed first.

### 3. Stage-Specific Prompts

After the minimal tests, run the longer sections for the skills you changed or rely on most. These cover detailed behavior such as ABACUS input boundaries, DP-GEN trust-level checks, DeePMD readiness checks, CHMC/CPIHMC output interpretation, TI/TST unit handling, and KMC handoff logic.

## Pass Criteria

A manual answer passes if it:

- uses the requested skill path and stage vocabulary
- refuses to invent undocumented numerical values
- preserves user-approval boundaries for scientific parameters
- distinguishes real reference examples from reusable defaults
- says `not documented yet` when required information is missing
- avoids claiming this repository is a production automation pipeline
- corrects user misconceptions instead of adopting them

## Fail Criteria

A manual answer fails if it:

- silently chooses DFT settings, trust levels, DeePMD hyperparameters, reaction coordinates, sampling parameters, TST prefactors, or KMC event networks
- copies CORR examples directly into a different target system without warning
- treats `PHY_QUANT`, `frozen_model.pb`, one CSV file, or one TST rate as proof of production readiness
- says CPIHMC directly outputs H2 formation efficiency
- says KMC can consume raw CHMC/CPIHMC trajectories or mean-force files directly
- reintroduces undocumented commercial DFT backend assumptions into this teaching repository

## Script-Level Smoke Tests

Run these from the repository root:

```bash
python common/scripts/check_workflow_files.py --software abacus --path abacus-dft-labeling/templates/reference-examples/corr --allow-warnings
python common/scripts/check_workflow_files.py --software dpgen --path dpgen-active-learning/templates/reference-examples/corr-dpgen --allow-warnings
python common/scripts/check_workflow_files.py --software deepmd --path deepmd-training/templates/reference-examples/corr-deepmd --allow-warnings
python dpdata-format-conversion/scripts/inspect_dpdata_system.py --help
python dpdata-format-conversion/scripts/convert_with_dpdata.py --help
python dpdata-format-conversion/scripts/compare_converted_system.py --help
python deepmd-training/scripts/parse_lcurve.py --help
python chmc-cpihmc-sampling/scripts/check_chmc_window.py --help
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py --print-defaults
python ti-tst-rate/scripts/extract_mean_force.py --print-defaults
python ti-tst-rate/scripts/integrate_free_energy.py --print-defaults
python ti-tst-rate/scripts/compute_tst_rates.py --print-defaults
python ti-tst-rate/scripts/plot_mean_force.py --help
python ti-tst-rate/scripts/plot_free_energy.py --help
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.example.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.convergence-screening.example.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/demo_multi_window_plot_only.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/postprocess_missing_defaults.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_parser_nested.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_invalid_bool.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_missing_windows.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_invalid_per_window_skiprows.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/no_step_convergence_row_index.yaml --dry-run
```

These checks only confirm that minimal static checkers and script interfaces load and expose expected options. They do not validate convergence, parameter quality, or physical correctness. The CHMC/CPIHMC convergence helper reports screening diagnostics only; plot review and user-approved equilibration choices are still required.

For ABACUS, the static checker also checks INPUT-declared STRU/KPT paths and pseudopotential/orbital file references from STRU when the relevant directories are documented. Missing files under explicit directories are failures; missing files under implicit current-directory fallback are warnings for review.

The postprocess runner smoke test uses `--dry-run` so it checks config parsing, window discovery, and generated child commands without executing the TI/TST scripts or requiring plotting dependencies.
The convergence-screening example extends this check by verifying that per-window `analyze_phy_quant_convergence.py` commands are generated before mean-force extraction, without treating suggested cutoffs as automatic TI discard lengths.
The `no_step_convergence_row_index.yaml` fixture checks headerless CPIHMC-style data with no step column. It should generate convergence commands with `--use-row-index-as-step`; this is a diagnostic x-axis only, and reported `eq_step` values mean row indices rather than physical simulation steps.
The plot-only fixture verifies that `stop_after: plot` can generate plot commands from existing reviewed CSV files without rediscovering windows, re-extracting mean forces, reintegrating free energy, or running TST.
The `postprocess_missing_defaults.yaml` check is expected to fail with a preflight error. It verifies that `parameters_confirmed: true` is not enough when parser mode, columns, units, TI zero reference, or TST/plot choices are still implicit.
The `negative_*.yaml` runner fixtures are also expected to fail. They verify executable rejection of nested YAML, invalid boolean values, too few discovered windows, and non-numeric per-window skiprows such as `SUGGESTED`.

### Runner Child-Script Negative Fixtures

Some runner failures cannot be proven by `--dry-run`, because dry-run only checks command generation. The following fixtures intentionally run child scripts and are expected to exit nonzero:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_bad_columns.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_bad_columns.yaml
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_truncated_window.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_truncated_window.yaml
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_existing_output_dir.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py tests/runner_configs/negative_existing_output_dir.yaml
```

`negative_bad_columns.yaml` should dry-run successfully but fail during extraction because the confirmed `rc_column` and `force_column` do not exist. `negative_truncated_window.yaml` should dry-run successfully but fail during extraction because one discovered window has a short data row. These runs write only to ignored `tmp/runner-negative-*` directories and explicitly set `allow_existing_output_dir: true` because they are repeatable diagnostic fixtures. Treat any partial CSV there as diagnostic evidence of child-script failure, not as input to TI.

`negative_existing_output_dir.yaml` should dry-run successfully but fail before real execution because its `output_dir` intentionally contains a stale `summary.json` fixture. This checks that real runner execution refuses non-empty output directories unless reuse has been explicitly approved with `allow_existing_output_dir: true`.

## Real-Data Diagnostic Records

Small summaries from real or representative data are stored under `tests/real_case_records/`. The raw large data are intentionally kept outside the repository.

Current records include:

- `MANIFEST.md`: canonical index for retained records, representative attachments, and pruned duplicate artifacts.
- `2026-07-02_real_phy_quant_test_record.md`: single real `PHY_QUANT` case with `INPUT`/`ALL_INPUT` checks, convergence diagnostics, acceptance fallback, and initial-RC adjustment behavior.
- `2026-07-03_demo_multi_window_test_record.md`: 13-window `../demo` CHMC/CPIHMC-style `energy.dat` case with per-window `check_chmc_window.py` summaries, convergence CSVs, and a diagnostic `mean_force_table.csv`.
- `2026-07-10_demo_runner_dry_run_record.md`: `nqe-postprocess-runner` staged dry-run and real execution on the same 13-window `../demo` dataset, stopping after convergence CSV summaries and mean-force extraction.
- `2026-07-11_demo_runner_output_review.md`: review of the generated runner outputs, corrected convergence plots, TI-handoff risks, and discard sensitivity for windows `0.0` and `1.8`.
- `2026-07-11_candidate_skiprows_dry_run_record.md`: dry-run record for the candidate `per_window_skiprows_file` fixture. It verifies command generation only and does not approve a production discard policy.
- `2026-07-11_reviewed_skiprows_execution_record.md`: executed reviewed demo extraction with user-accepted `10000`-row discard for windows `0.0` and `1.8`; not reusable as a production default.
- `2026-07-11_reviewed_ti_only_record.md`: guarded TI-only execution using user-confirmed ascending integration, most-negative-RC endpoint zero, eV conversion, and `dF/dRC` mean-force sign. It does not approve TST.
- `2026-07-14_runner_negative_fixtures_record.md`: executable negative-runner fixture record covering nested YAML rejection, invalid boolean rejection, missing-window discovery failure, and invalid per-window skiprows failure.
- `2026-07-14_runner_child_failure_fixtures_record.md`: child-script negative-runner fixture record covering bad extraction columns and truncated window output.
- `2026-07-17_runner_stale_output_fixture_record.md`: executable negative-runner fixture record covering real-run refusal for non-empty `output_dir` unless `allow_existing_output_dir: true` is explicitly approved.

Use these records to understand script behavior on real file shapes. Do not treat them as production convergence evidence or reusable physical defaults.

When testing `check_chmc_window.py` on a window directory, relative file arguments are expected to resolve under `--window-dir`:

```bash
python chmc-cpihmc-sampling/scripts/check_chmc_window.py \
  --window-dir PATH_TO_WINDOW \
  --phy-quant-file energy.dat \
  --confirm-parameters
```

If an `energy.dat` or `PHY_QUANT` file starts with numeric data and lacks a header, `check_chmc_window.py` may infer the header only from a same-named sibling-window file with matching column count. This must be reported as `Header Inference` in the output and reviewed by the user before downstream TI. If no reliable file header or sibling header exists, the script should fail parsing instead of inventing column names.

For staged runner tests, use `stop_after` to avoid fake downstream physical approvals. For example, `stop_after: extraction` may run convergence screening and mean-force extraction without requiring TI direction, zero reference, plots, or TST fields. If convergence screening is enabled, `convergence_plot` must be explicit; set it to `false` for CSV summary-only mode in environments without plotting dependencies.

For plot-only runner tests, use `stop_after: plot` with existing CSV inputs. The config must explicitly confirm dataset label, `plot_rc_order`, selected y-columns, plotted free-energy unit label, and which plots to generate. Plot-only mode is visualization only and must not be treated as approval to rerun TI or compute TST rates.

For broad prompts such as "postprocess this batch", the expected fresh-agent behavior is to stage the workflow and stop before TI unless integration direction, zero reference, unit conversion, and mean-force sign convention have been explicitly confirmed. If the agent asks for `sampling_output_root`, it should also state the intended first stop stage and the downstream confirmation gates. If it discovers plausible directories such as `demo/`, it should present them as candidates only and ask the user to confirm the intended root. A generic postprocessing request should not trigger `stop_after: integration`, plots, TST, or rate calculation by default.

Broad runner tests should distinguish read-only inventory from runner execution. A fresh agent may count windows, compare `INPUT`/`ALL_INPUT`, check row counts, and detect short rows before `parameters_confirmed: true`; it should not call that inventory a runner dry-run, and it should not claim that inventory authorizes extraction, TI, or TST.

The 2026-07-14 targeted runner/TI-TST boundary retest is recorded in `tests/fresh_agent_records/2026-07-14_runner-ti-tst-boundary-retest_opencode.md`. It confirms that fresh-agent behavior now treats discovered paths, observed CSV headers, optional defaults, and default TST phrases as candidates rather than user confirmation.

Broad runner tests should also check parser and skip-row wording. The agent must not infer `format: phy_quant` for a whole batch from a single header; it should require confirmation that all windows have reliable compatible headers or ask for explicit zero-based table indices. It must not propose `skiprows: 1` to skip a text header, because runner extraction `skiprows` discards numeric data rows after header/comment handling. Use `skiprows: 0` unless the user has confirmed an equilibration or data-row discard.

If convergence screening data have no real step or iteration column, the agent must not use a physical observable column as a fake step axis. It should either ask for a real step column or require explicit approval for row/sample index mode through `convergence_use_row_index_as_step: true`.

Fresh-agent wording should keep convergence diagnostics separate from extraction. `stop_after: convergence` generates screening plots/CSVs only; `stop_after: extraction` may run those diagnostics and then write a mean-force table. If `convergence_auto_equilibration` appears in a draft before user confirmation, it should be `TODO_USER_APPROVAL` or `false`; if set to `true`, the answer must say it is only a screening aid. `dataset_label` should be described as provenance/output-table metadata, not as an automatic output-directory or file-prefix control.

After a real convergence-only run, fresh-agent tests should require a convergence review checklist before extraction. The checklist should summarize all windows, expand suspicious windows, list plot paths for human review, record user decisions such as rerun or user-approved discard, and keep candidate `per_window_skiprows_file` contents non-runnable until approved. If the user explains a decision using evidence such as a lower late-time potential-energy platform, mean-force sign change, or consistency with neighboring reaction coordinates, the agent should record that rationale without turning it into a reusable physical rule.

The runner section of `tests/manual_prompts.md` also includes deeper failure-case prompts for missing windows, bad columns, surprising dry-run commands, child-script failure after partial outputs, invalid or unreviewed `per_window_skiprows_file` values, parser failures, existing output directories, summary files without physical review, and truncated window outputs. Use these when testing whether a fresh agent can route runner failures to the right stage without inventing windows, columns, discard policies, TI choices, TST settings, or KMC readiness.

The 2026-07-14 targeted runner deeper failure-case retest is recorded in `tests/fresh_agent_records/2026-07-14_runner-deeper-failure-targeted_opencode.md`. It passed Tests 9-17. Future runner tests should shift toward executable negative fixtures and real-data failure cases rather than only adding more prompt-level coverage.

The 2026-07-17 targeted runner output-directory boundary retest is recorded in `tests/fresh_agent_records/2026-07-17_runner-output-dir-boundary-retest_opencode.md`. It passed the retest for non-empty `output_dir` refusal, refusing to add `allow_existing_output_dir: true` as a convenience fix, and refusing to treat runner success as clean overwrite or convergence proof.

When testing per-window discard, use a separate candidate config and a separate `per_window_skiprows_file` CSV. The CSV must contain explicit `sample_label` and `skiprows` values reviewed by the user. Do not overwrite the baseline staged fixture, and do not convert convergence-screening `SUGGESTED` indices into production discard lengths without a separate approval step. For production-facing tests, record that the user must inspect the convergence plots personally before accepting the discard policy.

## TI/TST Demo Chain

The bundled TI/TST demo chain can be run with:

```bash
python ti-tst-rate/scripts/run_smoke_test.py --skip-plots
```

Use this to check the file-shape path from demo `energy.dat` windows to mean-force table, free-energy profile, and one TST-rate output. If `matplotlib` is available and plots are desired, omit `--skip-plots`.

This demo does not certify sampling convergence, integration direction, state selection, prefactor correctness, or production readiness.

## When To Retest

Retest after changing any of these:

- a `SKILL.md` file
- a reference file under `references/`
- a template or real reference example
- a script under `scripts/`
- README, quickstart, or test prompts

For small documentation edits, run the minimal smoke and failure prompts for affected skills. For script changes, run the script-level smoke tests and the TI/TST demo chain when relevant.

## Suggested Test Record

Record manual tests when preparing a release. The detailed procedure and copyable template live in [fresh-agent-testing.md](fresh-agent-testing.md) and [tests/fresh_agent_record_template.md](../tests/fresh_agent_record_template.md).

A minimal record should include:

```text
Date:
Commit or branch:
Agent/model:
Freshness level:
Prompt section:
Pass/fail:
Notes:
```

Keep failures useful: save the exact prompt, the problematic answer, and the file you think should be improved. The fastest iteration loop is usually prompt -> failure -> small skill/reference edit -> fresh-agent retest.
