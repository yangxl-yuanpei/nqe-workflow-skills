# NQE Workflow Skills Current Status Report

Last updated: 2026-07-11

## Overall Status

This repository is currently a teaching, checking, and semi-automated post-processing skills library for an atomistic NQE workflow. It is not a one-click production pipeline.

The workflow coverage is broad and internally coherent:

```text
initial DFT-labeled dataset
  -> DP-GEN active learning
    -> LAMMPS/PLUMED exploration
      -> ABACUS DFT labeling
        -> DeePMD/MLFF training
          -> CHMC/CPIHMC mean-force sampling
            -> thermodynamic integration
              -> activation free energy
                -> TST elementary rates
                  -> KMC event-network reasoning
```

## Repository Snapshot

| Area | Current state |
|---|---|
| Skills | 12 skills total |
| Skill maturity | Most skills are ready for teaching/checking; `nqe-postprocess-runner` remains experimental; `kmc-h2-efficiency` remains teaching-ready |
| Scripts | 14 Python helper scripts |
| Templates | 19 `.template` files |
| Failure references | 9 `*failure-cases.md` files; 8 populated, 1 still placeholder |
| Manual prompts | Broad prompt coverage exists in `tests/manual_prompts.md`; recorded fresh-agent batches pass, while deeper failure-driven and real-data validation remains open |
| Open DFT backend | ABACUS is the documented open backend; do not reintroduce VASP as the default |
| Production status | Not production-ready without target-system parameters, convergence evidence, and user-approved physical choices |

## What Is Working

- The 12 skills cover the full teaching workflow from initial DFT data through KMC reasoning.
- The README, quickstart, testing guide, and major skills now agree on the repository boundary: useful for teaching, guarded checking, and deterministic post-processing helpers, not automatic production.
- The TI/TST script chain exists and is split into extraction, integration, plotting, and TST-rate computation.
- `nqe-postprocess-runner` can dry-run or execute a confirmed config in guarded stages. It now includes a preflight guard that rejects runnable configs relying on implicit parser, column, unit, integration, state-selection, temperature, prefactor, or convergence-plot defaults.
- `nqe-postprocess-runner` now has `stop_after` stage control, optional convergence-screening mode, plot-only mode for existing CSV outputs, and an explicit `per_window_skiprows_file` mechanism for user-reviewed per-window extraction discard overrides. `convergence_plot: false` enables CSV summary-only mode when plotting dependencies are unavailable.
- `analyze_phy_quant_convergence.py` supports single-RC demo files and real multi-column `PHY_QUANT` shapes such as `PotEng` plus `MeanForce_0`.
- `check_chmc_window.py` exists as a CHMC/CPIHMC window health-check helper for acceptance, physical-output row integrity, initial RC adjustment, final RC consistency, convergence screening, and `INPUT`/`ALL_INPUT` comparison. It now resolves relative input/log/physical-output paths under `--window-dir`, reports explicit `Header Inference` warnings when a numeric-first `energy.dat` header is inferred from a sibling window, and fails parsing when no reliable header source is available.
- `dpdata-format-conversion` provides inspect, convert, and compare helpers for dpdata-readable systems.
- `dpdata-format-conversion/README.md` documents a user-confirmed local mini example, `../00`, for labeled `abacus/scf -> deepmd/npy` inspection/comparison boundaries. This example is for local file-shape testing only and is not a reusable production default.
- Recorded fresh-agent and smoke batches currently pass: Batch A/B minimal smoke and failure prompts, Batch C changed-skill deep tests, Batch D script-interface smoke, and the targeted dpdata/TI/TST/runner retest.
- Script-level checks on 2026-07-10 passed for Python syntax across all 14 helper scripts, runner positive dry-run, runner implicit-default refusal, and `check_chmc_window.py --print-defaults`.
- The targeted runner preflight fresh-agent record is `tests/fresh_agent_records/2026-07-10_runner-preflight-targeted_opencode.md`. It passed for implicit-default refusal, `format: auto` refusal, TST default refusal, missing convergence columns, and bundled-config boundary behavior.
- The real-data runner staged execution record is `tests/real_case_records/2026-07-10_demo_runner_dry_run_record.md`. It validates dry-run plus real execution through convergence CSV summaries and mean-force extraction on the 13-window `../demo` dataset with explicit table columns and no TI/TST commands.
- The real-data runner output review is `tests/real_case_records/2026-07-11_demo_runner_output_review.md`. It records plot-axis correction, output completeness, TI-handoff risks, and discard sensitivity for windows `0.0` and `1.8`.
- A candidate per-window discard dry-run fixture exists at `tests/runner_configs/demo_multi_window_candidate_skiprows.yaml`, with its CSV override in `tests/runner_configs/demo_multi_window_candidate_skiprows.csv`. This is for command review and sensitivity testing only, not a production discard policy.
- The reviewed per-window extraction record is `tests/real_case_records/2026-07-11_reviewed_skiprows_execution_record.md`. It uses the user-accepted `10000`-row discard for `0.0` and `1.8` in the `../demo` review only and explicitly requires plot/CSV review before any production reuse.
- The guarded TI-only record is `tests/real_case_records/2026-07-11_reviewed_ti_only_record.md`. It integrates the reviewed mean-force table with ascending RC order, zero at the most-negative RC endpoint, eV conversion for `free_energy_converted`, and no TST.
- A plot-only dry-run fixture exists at `tests/runner_configs/demo_multi_window_plot_only.yaml`. It generates plot commands from the reviewed mean-force and free-energy CSV files without rerunning extraction, integration, or TST.
- Real-case attachments are now indexed by `tests/real_case_records/MANIFEST.md`. Duplicate convergence CSV directories and non-representative per-window PNG plots were pruned while retaining canonical CSV summaries, final outputs, and representative plots.
- The targeted dpdata/TI/TST/runner record is `tests/fresh_agent_records/2026-07-03_dpdata-ti-runner-targeted_opencode.md`. It passed after retesting the TI/TST anti-inference guardrail.
- Real-data diagnostic records exist for a single large `PHY_QUANT` case and for a 13-window `../demo` CHMC/CPIHMC dataset. The multi-window record is `tests/real_case_records/2026-07-03_demo_multi_window_test_record.md`.
- Real or semi-real reference examples exist for ABACUS, DP-GEN, LAMMPS/PLUMED, DeePMD, CHMC/CPIHMC, TI/TST handoff, and KMC event-network shape.

## Current Gaps

- `1/9` failure-case reference file is still a placeholder: `kmc-h2-efficiency/references/kmc-failure-cases.md`. `abacus-dft-labeling/references/abacus-failure-cases.md`, `chmc-cpihmc-sampling/references/chmc-cpihmc-failure-cases.md`, `ti-tst-rate/references/ti-tst-failure-cases.md`, `dpdata-format-conversion/references/dpdata-failure-cases.md`, `nqe-postprocess-runner/references/postprocess-runner-failure-cases.md`, `deepmd-training/references/deepmd-failure-cases.md`, `dpgen-active-learning/references/dpgen-failure-cases.md`, and `lammps-exploration/references/lammps-failure-cases.md` currently contain populated cases.
- Recorded fresh-agent batches pass, but deeper failure-driven and real-data validation remains incomplete. Do not claim production readiness or exhaustive test coverage.
- `dpgen-active-learning/templates/reference-examples/placeholder-real-example/` contains placeholder-shaped `param.json`, `machine.json`, and README files. It is not a real DP-GEN production example.
- `nqe-postprocess-runner` is still experimental because it needs deeper fresh-agent behavior tests for config/failure cases and a user-approved guarded TI-only review after convergence/extraction, not because basic staged execution is missing.
- `kmc-h2-efficiency` is still teaching-ready because it lacks an executable schema checker for event networks and rate tables.
- The repository still lacks target-system-specific production inputs, validated physical parameters, convergence evidence, and provenance records.

## Script Inventory

The current 14 Python helper scripts are:

- `common/scripts/check_workflow_files.py`
- `deepmd-training/scripts/parse_lcurve.py`
- `dpdata-format-conversion/scripts/inspect_dpdata_system.py`
- `dpdata-format-conversion/scripts/convert_with_dpdata.py`
- `dpdata-format-conversion/scripts/compare_converted_system.py`
- `chmc-cpihmc-sampling/scripts/check_chmc_window.py`
- `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py`
- `ti-tst-rate/scripts/extract_mean_force.py`
- `ti-tst-rate/scripts/integrate_free_energy.py`
- `ti-tst-rate/scripts/compute_tst_rates.py`
- `ti-tst-rate/scripts/plot_mean_force.py`
- `ti-tst-rate/scripts/plot_free_energy.py`
- `ti-tst-rate/scripts/run_smoke_test.py`
- `nqe-postprocess-runner/scripts/nqe_postprocess_runner.py`

Script output remains diagnostic or post-processing output. It is not proof of physical correctness or production convergence.

## Highest-Priority Next Work

1. Review the guarded TI-only free-energy profile before any TST handoff, especially the zero convention, reactant/transition-state definition, free-energy column/unit, temperature, and prefactor model.
2. Continue deeper fresh-agent tests for runner config/failure behavior beyond the targeted preflight pass, especially missing windows, bad columns, unexpected dry-run commands, child-script failures, `stop_after`, `convergence_plot`, and `per_window_skiprows_file`.
3. Keep dpdata repeatable checks deferred until an environment with dpdata is available; the skill, README example, and populated failure reference already cover the teaching/checking boundary.
4. Defer KMC failure cases and any KMC checker until the final specialized postprocessing pass.
5. Keep README, quickstart, testing guide, status report, and pending-work documents synchronized after every script or skill change.

## Scientific Guardrails

- Real reference examples show file shape, organization, and migration boundaries. They are not defaults for a new target system.
- DFT settings, DP-GEN trust levels, DeePMD hyperparameters, reaction coordinates, sampling lengths, CPIHMC beads, TST prefactors, and KMC event networks require user confirmation.
- From CHMC/CPIHMC to TI, inspect `PHY_QUANT` potential-energy and mean-force convergence evidence first.
- From free energy to TST, confirm integration direction, initial state, transition state, units, and prefactor.
- From rates to KMC, confirm event network, state definitions, rate table, and output metrics.
- ABACUS remains the documented open DFT backend in this teaching repository.
