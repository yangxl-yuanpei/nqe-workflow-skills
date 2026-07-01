# NQE Workflow Skills

This repository contains agent-readable skills for teaching, inspecting, and partially post-processing an atomistic NQE workflow. The workflow runs from structure/DFT preparation through DP-GEN, DeePMD, CHMC/CPIHMC sampling, thermodynamic integration, TST rate estimation, and KMC reasoning.

The current repository is a teaching and guidance skills library. It is not yet a one-click production automation pipeline.

Quick entry points:

- [Quick Start](docs/quickstart.md)
- [Manual Skill Tests](tests/manual_prompts.md)
- [Testing Guide](docs/testing.md)

## Workflow Scope

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

ABACUS is the documented open DFT backend in this teaching repository. DeePMD-kit and DP-GEN provide the MLFF and active-learning layer. LAMMPS and PLUMED are documented as exploration/CV tools. GC-Constrained-PIHMC is the public reference implementation for the CHMC/CPIHMC sampling layer.

## Completed Skills

| Skill | Current role | Status |
|---|---|---|
| `nqe-boundaries` | Shared terminology, scientific boundaries, and anti-overclaiming rules | ready |
| `nqe-h2-workflow` | End-to-end workflow routing and stage map | ready |
| `initial-dft-dataset` | Initial DFT-labeled dataset preparation strategy and checks | ready |
| `abacus-dft-labeling` | ABACUS input scaffolds, labeling checks, and official-doc references | ready |
| `dpgen-active-learning` | DP-GEN training, exploration, labeling loop, trust-region boundaries, and staged exploration guidance | ready |
| `lammps-exploration` | LAMMPS/PLUMED exploration templates, model-deviation handoff, and transfer boundaries | ready |
| `deepmd-training` | DeePMD-kit training, freeze/test/model-selection boundaries, and diagnostics | ready |
| `dpdata-format-conversion` | dpdata-based atomistic data inspection, explicit format conversion, and converted-data shape comparison | ready |
| `chmc-cpihmc-sampling` | CHMC/CPIHMC input/output templates, mean-force sampling checks, and grand-canonical notes | ready |
| `ti-tst-rate` | Mean-force extraction, TI integration, free-energy barrier extraction, TST rate calculation, and plotting guidance | ready |
| `nqe-postprocess-runner` | Config-driven wrapper for confirmed sampling-output -> mean-force -> free-energy -> TST CSV/plot/summary runs | experimental |
| `kmc-h2-efficiency` | General KMC event-network logic and H2-efficiency-specific boundaries | teaching-ready |

## Current Progress

Current repository state:

- 12 skills cover the full teaching workflow from initial DFT data through KMC reasoning.
- 14 Python helper scripts are available for static checks, data conversion, diagnostics, and guarded post-processing.
- 19 `.template` files provide input or handoff scaffolds with explicit `TODO_USER_APPROVAL` placeholders.
- `nqe-postprocess-runner` now has both a basic demo config and an optional convergence-screening config.
- `check_chmc_window.py` and `analyze_phy_quant_convergence.py` support the current CHMC/CPIHMC pre-TI checking path.
- 9 failure-case reference files exist; 4 are still placeholders and should not be treated as reliable diagnosis guides yet.
- Manual prompt coverage exists, but complete fresh-agent pass records are not yet documented.

The most up-to-date status and pending-work summaries live in [docs/current-status-report.md](docs/current-status-report.md) and [docs/pending-work.md](docs/pending-work.md).

## Real Reference Examples

These examples are included to show real file shapes, naming patterns, and transfer boundaries. They are not production defaults for a new H2/graphene calculation.

| Area | Reference example | What it is useful for | What not to copy blindly |
|---|---|---|---|
| ABACUS | `abacus-dft-labeling/templates/reference-examples/corr/` | Real `INPUT_sp`, `INPUT_opt`, `INPUT_aimd`, `STRU_opt`, and `KPT` style examples from a CORR project | Structure, cell, pseudopotentials, basis files, k mesh, charge/electric-field settings, convergence thresholds |
| DP-GEN | `dpgen-active-learning/templates/reference-examples/corr-dpgen/` | Real `run_param.json` exploration scheduling pattern and redacted `machine.json` organization | Exact systems, trust levels, temperatures, run lengths, HPC resources, labels, paths |
| LAMMPS/PLUMED | `lammps-exploration/templates/reference-examples/corr-lammps-plumed/` | Real `input.lammps` and `input.plumed_1` coupling style | Atom indices, CV definitions, restraint centers, force constants, strides, units |
| DeePMD | `deepmd-training/templates/reference-examples/corr-deepmd/` | Real `input.json` and `lcurve.out` examples for training diagnostics | Architecture, cutoffs, learning rate schedule, data paths, stopping criteria |
| CHMC/CPIHMC | `chmc-cpihmc-sampling/templates/reference-examples/corr-gc-cpihmc/` | Real `INPUT`, `BEADS`, `ALL_INPUT`, and `PHY_QUANT` examples for GC-CPIHMC output shape | Reaction coordinates, bead count, HMC/MC settings, electron-number settings, units/sign conventions |
| TI/TST | `ti-tst-rate/templates/reference-examples/corr-phy-quant-handoff/` | Semi-real handoff CSVs: `mean_force_table.csv`, `free_energy_profile.csv`, `tst_rates.csv` | Final barriers/rates for a new target system |
| TI/TST | `ti-tst-rate/templates/reference-examples/user-tested-ti-tst-chain/` | Small user-tested demo windows, observed outputs, and smoke-test chain | Production convergence or final rates |
| KMC | `kmc-h2-efficiency/templates/reference-examples/generic-rate-network/` | Generic event-network input shape | A complete H2/graphene production KMC model |

There is also a `dpgen-active-learning/templates/reference-examples/placeholder-real-example/` folder kept as a placeholder/example shape. Prefer the documented CORR example when discussing real DP-GEN transfer.

## Available Scripts

The scripts are deterministic helpers for diagnostics and post-processing. They do not replace expert review. The shared file checker is intentionally minimal: it checks file presence, parseability, placeholders, expected columns/keywords, selected ABACUS resource-file paths, and obvious error markers, not convergence or physical parameter quality.

| Script | Purpose | Output |
|---|---|---|
| `common/scripts/check_workflow_files.py` | Minimal static checks for ABACUS, DP-GEN, DeePMD, LAMMPS, PLUMED, CHMC/CPIHMC, TI/TST, and KMC file shapes | PASS/WARN/FAIL report |
| `dpdata-format-conversion/scripts/inspect_dpdata_system.py` | Inspect frame/atom counts, type map, cell, and label availability in dpdata-readable data | JSON summary |
| `dpdata-format-conversion/scripts/convert_with_dpdata.py` | Convert atomistic data between explicit dpdata input/output formats | converted data |
| `dpdata-format-conversion/scripts/compare_converted_system.py` | Compare source and converted dpdata systems for basic shape consistency | JSON comparison |
| `deepmd-training/scripts/parse_lcurve.py` | Parse DeePMD `lcurve.out`-style logs for first-pass diagnostics | Summary of columns, final values, and basic warnings |
| `chmc-cpihmc-sampling/scripts/check_chmc_window.py` | Window health check: acceptance rate, output row integrity, RC consistency, convergence, INPUT/ALL_INPUT agreement | PASS/WARN/FAIL/SKIP report |
| `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py` | Plot and summarize `PHY_QUANT` potential-energy/mean-force convergence for one sampling window | convergence image and optional CSV summary |
| `ti-tst-rate/scripts/extract_mean_force.py` | Extract one CHMC/CPIHMC sampling output/window into one mean-force CSV row | `mean_force_table.csv` |
| `ti-tst-rate/scripts/integrate_free_energy.py` | Integrate collected mean-force windows into a relative free-energy profile | `free_energy_profile.csv` |
| `ti-tst-rate/scripts/compute_tst_rates.py` | Extract an activation free-energy barrier and compute one TST rate | `tst_rates.csv` |
| `ti-tst-rate/scripts/plot_mean_force.py` | Plot one or more mean-force curves versus reaction coordinate | image file |
| `ti-tst-rate/scripts/plot_free_energy.py` | Plot one or more free-energy curves versus reaction coordinate | image file |
| `ti-tst-rate/scripts/run_smoke_test.py` | Run the bundled TI/TST demo chain as a smoke test | mean-force/free-energy/rate CSVs and optional plots |
| `nqe-postprocess-runner/scripts/nqe_postprocess_runner.py` | Run the confirmed TI/TST postprocessing chain from a flat YAML/JSON config, optionally generating pre-TI convergence-screening commands | CSVs, plots, `summary.json` |

Most TI/TST scripts require `--confirm-parameters`. This is intentional. The agent or user must confirm columns, unit conversions, equilibration discard, mean-force sign convention, integration direction, free-energy zero, initial/transition-state selection, and prefactor model before treating the result as meaningful.

## Templates

The repository includes templates for major workflow stages:

- ABACUS: `abacus-dft-labeling/templates/INPUT.template`, `STRU.template`, `KPT.template`
- DP-GEN: `dpgen-active-learning/templates/param.json.template`, `machine.json.template`
- LAMMPS/PLUMED: `lammps-exploration/templates/input.lammps.template`, `input.plumed.template`
- DeePMD: `deepmd-training/templates/input.json.template`
- CHMC/CPIHMC: `chmc-cpihmc-sampling/templates/INPUT.template`, `STRU.template`, `BEADS.template`, `PHY_QUANT.template`, `MODEL_DEVI.template`
- TI/TST: `ti-tst-rate/templates/mean_force_table.csv.template`, `free_energy_profile.csv.template`, `tst_rates.csv.template`
- KMC: `kmc-h2-efficiency/templates/kmc_events.json.template`, `kmc_parameters.json.template`, `kmc_output_summary.csv.template`

Templates use explicit placeholders and should be filled only with user-approved or project-documented choices.

dpdata helpers live under `dpdata-format-conversion/scripts/` rather than templates because format conversion should be performed with explicit input/output format strings, confirmed type maps, and post-conversion checks.

The postprocess runner also includes two config examples:

- `nqe-postprocess-runner/assets/config.example.yaml`: basic TI/TST demo wrapper
- `nqe-postprocess-runner/assets/config.convergence-screening.example.yaml`: same demo shape with optional per-window `PHY_QUANT` convergence screening before TI

## How To Test

Manual behavior tests live in:

```text
tests/manual_prompts.md
```

The full testing workflow is documented in [docs/testing.md](docs/testing.md).

Recommended manual test process:

1. Open a fresh agent or fresh conversation.
2. Ask the prompt exactly as written in `tests/manual_prompts.md`.
3. Check whether the answer follows the expected behavior.
4. Pay special attention to whether the agent invents numerical parameters, silently chooses production settings, or overclaims readiness.
5. Repeat after updating any `SKILL.md`, reference file, template, or script.

Useful script smoke tests:

```bash
python common/scripts/check_workflow_files.py --software abacus --path abacus-dft-labeling/templates/reference-examples/corr --allow-warnings
python common/scripts/check_workflow_files.py --software dpgen --path dpgen-active-learning/templates/reference-examples/corr-dpgen --allow-warnings
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
```

For production-like tests, use copies of real or mock data and keep the expected behavior conservative: the scripts can summarize, extract, integrate, compute, and plot, but the user still confirms physical interpretation.

## Current Boundaries

The skills can help an agent:

- explain each workflow stage and its physical meaning
- route questions to the correct stage
- inspect whether required inputs, outputs, metadata, or diagnostics are missing
- use official-documentation notes instead of inventing software behavior
- distinguish reusable patterns from project-specific numerical settings
- inspect and convert atomistic file formats with dpdata when the user confirms format names and labels
- generate TODO lists, readiness checklists, and conservative draft templates
- run available diagnostic/post-processing scripts when the user confirms assumptions

The skills must not let an agent:

- invent DFT settings, DP-GEN trust levels, DeePMD hyperparameters, reaction coordinates, CPIHMC bead counts, HMC/MC settings, TST prefactors, KMC event networks, or dpdata format strings
- copy CORR reference parameters directly into H2/graphene or another target system
- claim that a template, frozen model, `PHY_QUANT`, or one CSV file proves production readiness
- claim that CPIHMC directly outputs H2 formation efficiency
- claim that KMC can consume raw CHMC/CPIHMC trajectories or mean-force files directly
- describe this repository as a fully automated production workflow

## Not Yet A Production Automation Pipeline

This repository currently teaches the workflow and provides guarded scaffolds. A production pipeline would still need:

- target-system-specific ABACUS input files and convergence-tested settings
- validated initial structures and DFT-labeled datasets
- documented dpdata conversion commands, type maps, units, label availability, and converted-data shape checks
- project-approved DP-GEN exploration schedules, trust thresholds, and machine settings
- validated DeePMD model-selection criteria and frozen models
- confirmed CHMC/CPIHMC reaction coordinates, windows, units, signs, sampling length, and convergence evidence
- statistically checked TI uncertainty propagation
- project-specific TST prefactors and elementary-step definitions
- a complete KMC state model, event list, rate table, stopping rule, and output definitions
- executable orchestration that connects stages, checks failures, records provenance, and prevents accidental reuse of incompatible examples

The design goal is to make an agent careful and useful before making it automatic.
