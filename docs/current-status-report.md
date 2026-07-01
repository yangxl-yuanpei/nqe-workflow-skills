# NQE Workflow Skills Current Status Report

Last updated: 2026-07-01

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
| Failure references | 9 `*failure-cases.md` files; 2 populated, 7 still placeholders |
| Manual prompts | Broad prompt coverage exists in `tests/manual_prompts.md`; fresh-agent pass status is not fully recorded |
| Open DFT backend | ABACUS is the documented open backend; do not reintroduce VASP as the default |
| Production status | Not production-ready without target-system parameters, convergence evidence, and user-approved physical choices |

## What Is Working

- The 12 skills cover the full teaching workflow from initial DFT data through KMC reasoning.
- The README, quickstart, testing guide, and major skills now agree on the repository boundary: useful for teaching, guarded checking, and deterministic post-processing helpers, not automatic production.
- The TI/TST script chain exists and is split into extraction, integration, plotting, and TST-rate computation.
- `nqe-postprocess-runner` can dry-run a confirmed config and generate child commands for the TI/TST chain.
- `nqe-postprocess-runner` now has an optional convergence-screening mode that generates per-window `analyze_phy_quant_convergence.py` commands before mean-force extraction.
- `analyze_phy_quant_convergence.py` supports single-RC demo files and real multi-column `PHY_QUANT` shapes such as `PotEng` plus `MeanForce_0`.
- `check_chmc_window.py` exists as a CHMC/CPIHMC window health-check helper for acceptance, physical-output row integrity, RC consistency, convergence screening, and `INPUT`/`ALL_INPUT` comparison.
- `dpdata-format-conversion` provides inspect, convert, and compare helpers for dpdata-readable systems.
- Real or semi-real reference examples exist for ABACUS, DP-GEN, LAMMPS/PLUMED, DeePMD, CHMC/CPIHMC, TI/TST handoff, and KMC event-network shape.

## Current Gaps

- `7/9` failure-case reference files are still placeholders. `abacus-dft-labeling/references/abacus-failure-cases.md` and `chmc-cpihmc-sampling/references/chmc-cpihmc-failure-cases.md` currently contain populated cases.
- Fresh-agent manual test results are not fully recorded. Do not claim that all manual prompts have passed unless a dated test record is added.
- `dpgen-active-learning/templates/reference-examples/placeholder-real-example/` contains placeholder-shaped `param.json`, `machine.json`, and README files. It is not a real DP-GEN production example.
- `nqe-postprocess-runner` is still experimental because it needs more failure cases, fresh-agent behavior tests, and more real multi-window validation.
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

1. Populate the next high-value failure references, starting with TI/TST, dpdata, and postprocess-runner.
2. Add dated fresh-agent test records for the changed skills and prompts, especially `nqe-postprocess-runner`, `dpdata-format-conversion`, and `kmc-h2-efficiency`.
3. Continue validating `analyze_phy_quant_convergence.py` and runner convergence screening on real multi-window `PHY_QUANT` data.
4. Add a minimal KMC event-network checker such as `check_kmc_network.py` or `check_kmc_events.py`.
5. Add small real dpdata conversion examples and failure cases.
6. Keep README, quickstart, testing guide, status report, and pending-work documents synchronized after every script or skill change.

## Scientific Guardrails

- Real reference examples show file shape, organization, and migration boundaries. They are not defaults for a new target system.
- DFT settings, DP-GEN trust levels, DeePMD hyperparameters, reaction coordinates, sampling lengths, CPIHMC beads, TST prefactors, and KMC event networks require user confirmation.
- From CHMC/CPIHMC to TI, inspect `PHY_QUANT` potential-energy and mean-force convergence evidence first.
- From free energy to TST, confirm integration direction, initial state, transition state, units, and prefactor.
- From rates to KMC, confirm event network, state definitions, rate table, and output metrics.
- ABACUS remains the documented open DFT backend in this teaching repository.
