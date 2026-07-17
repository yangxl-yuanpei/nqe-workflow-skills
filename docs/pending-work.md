# Pending Work

Last updated: 2026-07-17

This file tracks work that remains after the current repository consistency pass. It intentionally separates documented repository state from production readiness.

## Current Repository State

- 12 skills exist.
- 14 Python helper scripts exist.
- 19 `.template` files exist.
- 9 failure-case references exist; all 9 are populated.
- `nqe-postprocess-runner` has a basic config example, a convergence-screening config example, staged `stop_after` control for convergence/extraction/integration/plot/all, and a user-reviewed `per_window_skiprows_file` mechanism for per-window extraction discard overrides.
- `check_chmc_window.py` exists; it is no longer a future script placeholder.
- `dpgen-active-learning/templates/reference-examples/placeholder-real-example/` contains placeholder-shaped files, but it is not a real DP-GEN example.
- Manual prompts exist. Recorded fresh-agent and script-smoke batches currently pass; remaining testing work is deeper failure-driven behavior and real-data validation, not a missing baseline pass.
- Runner negative smoke fixtures exist at `tests/runner_configs/postprocess_missing_defaults.yaml` and `tests/runner_configs/negative_*.yaml`; they are expected to fail and verify implicit-default refusal, nested YAML rejection, invalid boolean rejection, missing-window discovery failure, and invalid per-window skiprows rejection.
- Runner child-script negative fixtures also exist for bad header columns and truncated table rows. They dry-run successfully but fail during real extraction, demonstrating that dry-run command generation is not a guarantee of child-script success.
- A targeted runner preflight fresh-agent record exists at `tests/fresh_agent_records/2026-07-10_runner-preflight-targeted_opencode.md`; it passed the current implicit-default and bundled-config boundary prompts.
- A targeted runner plot-only fresh-agent record exists at `tests/fresh_agent_records/2026-07-12_runner-plot-only-targeted_subagent.md`; it passed the current existing-CSV plotting boundary prompt.
- A targeted runner/TI-TST boundary retest exists at `tests/fresh_agent_records/2026-07-14_runner-ti-tst-boundary-retest_opencode.md`; it passed candidate-path handling, optional `output_dir` omission, plot-only-to-default-TST refusal, and path-confirmation-versus-TI/TST-approval prompts.
- A targeted runner deeper failure-case retest exists at `tests/fresh_agent_records/2026-07-14_runner-deeper-failure-targeted_opencode.md`; it passed Tests 9-17 for missing windows, bad columns, unexpected dry-run commands, partial outputs, per-window skiprows errors, parser failures, existing output directories, summary-without-review, and truncated window outputs.
- A targeted upstream DeepModeling boundary retest exists at `tests/fresh_agent_records/2026-07-17_upstream-deepmodeling-boundary_opencode.md`; it passed dpdata, DeePMD, DP-GEN, and LAMMPS/PLUMED prompts that check upstream skills are software-operation references rather than target-system default sources.
- KMC boundary prompts now cover default convergence-threshold refusal, historical KMC note threshold refusal, and association-only networks with confirmed initial coverage. The latest reported fresh-agent answers passed these checks, but a dedicated KMC fresh-agent record file has not yet been added.
- An executable runner negative-fixture record exists at `tests/real_case_records/2026-07-14_runner_negative_fixtures_record.md`; it confirms expected failures for nested YAML, invalid boolean values, too few discovered windows, and invalid `per_window_skiprows_file` values.
- A runner child-script failure fixture record exists at `tests/real_case_records/2026-07-14_runner_child_failure_fixtures_record.md`; it confirms expected failures for bad extraction columns and truncated window rows.
- A runner stale-output fixture record exists at `tests/real_case_records/2026-07-17_runner_stale_output_fixture_record.md`; it confirms dry-run command review remains available while real execution refuses non-empty `output_dir` reuse unless `allow_existing_output_dir: true` is explicitly approved.
- A user-confirmed local dpdata mini example exists outside the repository at `../00` for labeled `abacus/scf -> deepmd/npy` inspection/comparison boundaries. It is documented in `dpdata-format-conversion/README.md` and is not a reusable production default.
- A real 13-window CHMC/CPIHMC-style dataset exists outside the repository at `../demo`; summaries and diagnostics are recorded under `tests/real_case_records/2026-07-03_demo_multi_window*`.
- A runner staged fixture for `../demo` exists at `tests/runner_configs/demo_multi_window_dry_run.yaml`; the record is `tests/real_case_records/2026-07-10_demo_runner_dry_run_record.md`. It has been dry-run and executed through convergence CSV summaries plus mean-force extraction, without TI/TST.
- The staged runner outputs have been reviewed in `tests/real_case_records/2026-07-11_demo_runner_output_review.md`, including corrected convergence plots and discard sensitivity for `0.0` and `1.8`.
- A separate per-window discard fixture exists at `tests/runner_configs/demo_multi_window_candidate_skiprows.yaml` with `tests/runner_configs/demo_multi_window_candidate_skiprows.csv`. The user accepted `10000` discarded rows for `0.0` and `1.8` in this demo review only; production use still requires direct convergence plot/CSV review.
- A guarded TI-only fixture exists at `tests/runner_configs/demo_multi_window_reviewed_ti_only.yaml`; its execution record is `tests/real_case_records/2026-07-11_reviewed_ti_only_record.md`.
- A plot-only fixture exists at `tests/runner_configs/demo_multi_window_plot_only.yaml`; it verifies command generation and execution from reviewed CSV outputs without rerunning extraction, integration, or TST. The execution record is `tests/real_case_records/2026-07-12_plot_only_execution_record.md`.
- Real-case test records are indexed by `tests/real_case_records/MANIFEST.md`. Duplicate convergence CSV attachments and non-representative per-window PNG plots have been pruned; canonical summaries, final outputs, and representative plots remain.

## 1. Failure-Case References

All failure-case reference files are now populated:

- `abacus-dft-labeling/references/abacus-failure-cases.md`
- `chmc-cpihmc-sampling/references/chmc-cpihmc-failure-cases.md`
- `ti-tst-rate/references/ti-tst-failure-cases.md`
- `dpdata-format-conversion/references/dpdata-failure-cases.md`
- `nqe-postprocess-runner/references/postprocess-runner-failure-cases.md`
- `deepmd-training/references/deepmd-failure-cases.md`
- `dpgen-active-learning/references/dpgen-failure-cases.md`
- `lammps-exploration/references/lammps-failure-cases.md`
- `kmc-h2-efficiency/references/kmc-failure-cases.md`

Future work should refine these with additional real observed failures as they appear, not convert reference examples into production defaults.

## 2. CHMC/CPIHMC Window Checking

`chmc-cpihmc-sampling/scripts/check_chmc_window.py` exists and has been exercised on single-window and 13-window real data records.

Current state:

- Relative file arguments are resolved under `--window-dir`.
- Numeric-first physical-output files can infer missing headers from same-named sibling-window files with matching column count, but fail parsing when no reliable header source is available.
- Header inference is reported explicitly as a warning.
- Real multi-window diagnostics are recorded for `../demo`.

Remaining work:

- Validate acceptance-rate parsing on real logs or outputs.
- Validate final-RC and target-RC checks against more real `INPUT`/`ALL_INPUT` examples when `ALL_INPUT` is available.
- Continue validating initial-RC adjustment diagnostics on more real windows, including multi-RC cases.
- Connect recurring diagnostic outcomes to `chmc-cpihmc-failure-cases.md`.
- Decide which checks should remain in `check_chmc_window.py` and which should remain in `analyze_phy_quant_convergence.py`.

Boundary: `check_chmc_window.py` can screen file and diagnostic consistency. It must not certify sampling convergence by itself.

## 3. nqe-postprocess-runner Experimental To Ready

Current state:

- Core runner exists.
- Config schema exists.
- Basic and convergence-screening example configs exist.
- Dry-run command generation has been exercised for the bundled demo.
- A preflight guard now rejects runnable configs that still rely on implicit parser, column, unit, TI, TST, or plot defaults.
- A negative smoke config exists to check that `parameters_confirmed: true` alone does not bypass preflight.
- Real-data dry-run command generation and staged execution through extraction have been exercised on the `../demo` 13-window dataset.
- Per-window discard command generation and reviewed demo execution have been exercised with explicit `10000`-row overrides for `0.0` and `1.8`.
- Plot-only command generation has been exercised on reviewed demo mean-force and free-energy CSV outputs.

Remaining work:

- Prompt-level runner failure routing has a targeted fresh-agent pass for missing windows, bad columns, unexpected dry-run commands, child-script failures, per-window discard errors, config parser failures, existing output directories, summary-without-physical-review, and truncated window outputs.
- Extend executable runner negative validation to the remaining practical failure families, especially stale partial-output handling and real-data recovery. Parser, missing-window, invalid-boolean, invalid-per-window-skiprows, bad-column, truncated-window, and stale-output-dir fixtures already exist.
- Review the guarded TI-only free-energy profile before any TST handoff. TST still requires explicit reactant/transition-state selection, free-energy column/unit, temperature, prefactor model, and prefactor units.
- Consider adding a `--generate-config` or draft-config mode only if it can preserve `parameters_confirmed: false` for unapproved values.

## 4. KMC Teaching-Ready To Ready

Current state:

- KMC concepts, state/event/rate-table boundaries, and generic examples exist.
- KMC failure cases are populated and cover single-rate misuse, missing state models, incomplete event networks, rate-table mismatch, invalid/degenerate rates, event-selection logic, incomplete new species/event types, output-count misinterpretation, missing statistical convergence, stale/mixed outputs, and code-specific notes treated as defaults.
- KMC prompts now explicitly forbid default convergence thresholds, historical code-note threshold migration, and automatic dismissal of association-only networks when user-defined initial coverage or reservoir assumptions may exist.

Remaining work:

- Define a minimal KMC event-network schema.
- Add a checker such as `check_kmc_network.py` or `check_kmc_events.py`.
- Refine KMC failure cases with future real observed failures when available.
- Keep H2 formation efficiency as one possible observable, not a hard-coded output.

## 5. dpdata Conversion Examples

Current state:

- `inspect_dpdata_system.py`, `convert_with_dpdata.py`, and `compare_converted_system.py` exist.
- `dpdata-format-conversion/README.md` documents the user-confirmed local `../00` example as labeled `abacus/scf -> deepmd/npy`.
- A targeted fresh-agent test record confirms the skill now refuses unknown-format guessing and handles the confirmed `../00` example conservatively.
- `dpdata-format-conversion/references/dpdata-failure-cases.md` is populated with failure patterns and upstream issue references.

Remaining work:

- Convert the local `../00` example into repeatable documented checks only when a test environment with dpdata is available.
- Optionally use the populated dpdata failure reference to design small executable or documented checks for wrong format strings, missing labels, element-order mismatch, cell-shape mismatch, and frame-count mismatch.
- Add a short recipe reference for ABACUS -> DeePMD raw/npy and LAMMPS dump inspection when format names are confirmed.

## 6. Optional Static Checkers For Other Stages

These are useful but lower priority than runner real-data validation and current failure-driven tests. They should be implemented only as conservative checkers or schema validators. They must not generate production inputs, recommend physical parameters, or convert examples into defaults.

Potential scripts:

- `dpgen-active-learning/scripts/check_dpgen_config.py`: inspect `param.json` and `machine.json` for required top-level sections, unresolved `TODO_USER_APPROVAL` or `REDACTED` values, missing init-data/training/exploration/labeling blocks, and whether ABACUS labeling is explicit when used. It should not choose trust levels, temperatures, run lengths, or machine resources.
- `deepmd-training/scripts/check_deepmd_training_config.py`: inspect DeePMD `input.json` for systems, type map, descriptor, fitting network, learning-rate, loss, train/validation data references, placeholders, and basic path consistency. It should not judge architecture, cutoff, learning-rate schedule, or stopping criteria as scientifically correct.
- `lammps-exploration/scripts/check_lammps_plumed_inputs.py`: inspect LAMMPS and PLUMED inputs for model paths, `pair_style deepmd`, PLUMED coupling, declared CVs, output/PRINT directives, unresolved placeholders, and obvious missing files. It should not decide CV definitions, atom indices, restraint strengths, bias parameters, or sampling length.
- `abacus-dft-labeling/scripts/check_abacus_inputs.py`: optionally split or deepen ABACUS-specific checks beyond `common/scripts/check_workflow_files.py`, including INPUT/STRU/KPT cross-references, pseudopotential/orbital path checks, placeholders, and obvious missing files. It should not recommend cutoff, k mesh, basis, smearing, convergence thresholds, or charge settings.
- `dpdata-format-conversion/scripts/check_dpdata_conversion_plan.py`: inspect a documented conversion plan for explicit input/output format strings, label requirements, type-map policy, units/provenance notes, and output overwrite policy. It should not guess dpdata format strings or claim converted data are training-ready.

Implementation boundary:

- Prefer small scripts with `--help`, `--print-defaults` when useful, and clear PASS/WARN/FAIL output.
- Check file shape, path existence, placeholders, required keys, and obvious contradictions.
- Route interpretation failures to the corresponding `references/*failure-cases.md` file.
- Keep examples and reference projects as file-shape evidence only, not reusable defaults.

## 7. Fresh-Agent Test Records

Manual prompts are available, and the recommended procedure is documented in `docs/fresh-agent-testing.md`. Recorded baseline fresh-agent, script-smoke, and targeted runner/TI-TST boundary batches pass. Future records should focus on newly changed behavior, deeper failure-driven prompts, and real-data workflow checks.

Recommended record fields:

```text
Date:
Commit or branch:
Repository status:
Agent/model:
Freshness level:
Prompt section:
Pass/fail:
Notes:
```

Use `tests/fresh_agent_record_template.md` as the copyable record template.

Highest-priority fresh-agent sections:

- `nqe-postprocess-runner` executable negative fixtures beyond the current parser/discovery/skiprows/bad-column/truncation/stale-output fixtures, especially stale partial-output and real-data failure recovery
- `chmc-cpihmc-sampling` only after further script/reference changes
- `ti-tst-rate` deeper prompts beyond the no-defaults retest
- `dpdata-format-conversion` only when adding new executable checks or changing the anti-guessing/reference behavior
- `kmc-h2-efficiency` only when adding the KMC checker or changing KMC boundary behavior again

## 8. Documentation Synchronization

After future changes, keep these files aligned:

- `README.md`
- `docs/quickstart.md`
- `docs/testing.md`
- `docs/upstream-community-skills.md`
- `docs/current-status-report.md`
- `docs/pending-work.md`
- affected `SKILL.md` files
- affected `references/*.md` files

Do not state that production readiness or exhaustive coverage has been achieved. It is acceptable to state that the currently recorded fresh-agent and script-smoke batches pass. Do not state that a placeholder example is a real production example.

## Suggested Priority Order

1. Implement the minimal KMC schema/static checker if the next pass continues KMC work.
2. Extend runner negative fixtures toward stale partial-output and real-data failure families now covered by prompt-level tests.
3. Review the guarded TI-only profile only if preparing a separate TST-confirmation checklist.
4. Keep dpdata repeatable checks deferred until a dpdata-enabled test environment is available.
5. Choose at most one optional static checker for DP-GEN, DeePMD, LAMMPS/PLUMED, ABACUS, or dpdata conversion only if it directly supports current validation needs.
6. Polish release-facing README and tutorial material after the evidence above is in place.
