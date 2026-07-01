# Quick Start

This repository is a teaching and guidance skills library for an atomistic NQE workflow. It helps an agent explain stages, inspect files, draft guarded templates, and run a few deterministic post-processing helpers. It does not replace expert judgment or become a one-click production pipeline by itself.

## Start Here

If you are new to the repository, use the skills in this order:

1. `nqe-boundaries`
2. `nqe-h2-workflow`
3. the stage-specific skill you actually need

Suggested first prompts:

```text
Use the skill at nqe-workflow-skills-release/nqe-boundaries.
Summarize what NQE means here and what the agent must not overclaim.
```

```text
Use the skill at nqe-workflow-skills-release/nqe-h2-workflow.
Map the workflow stages from initial dataset preparation to H2 formation efficiency.
```

## Which Skill To Use

Use `initial-dft-dataset` when you are deciding how to build or validate the first labeled structures.

Use `abacus-dft-labeling` when you need ABACUS input templates, file-shape guidance, labeling checks, or official-input references.

Use `dpgen-active-learning` when you need the DP-GEN loop order, `param.json` versus `machine.json`, trust-level boundaries, or staged exploration guidance.

Use `lammps-exploration` when you need the exploration layer, LAMMPS input shape, DeePMD coupling, PLUMED CV or bias setup, or model-deviation handoff context.

Use `deepmd-training` when you need to inspect `input.json`, `lcurve.out`, `train.log`, freeze/test boundaries, or final-model selection logic.

Use `dpdata-format-conversion` when data must move between software formats, such as ABACUS output to DeePMD raw/npy data, LAMMPS trajectory inspection, or checking whether labels/cells/type maps survived conversion.

Use `chmc-cpihmc-sampling` when you need CHMC/CPIHMC input structure, `INPUT` or `BEADS` or `PHY_QUANT` guidance, or mean-force sampling boundaries.

Use `ti-tst-rate` when you need to convert mean-force data into free-energy profiles, activation barriers, plots, or TST rate constants.

Use `nqe-postprocess-runner` when the TI/TST postprocessing assumptions have already been confirmed and you want a config-driven dry run or reproducible wrapper around the existing TI/TST scripts.

Use `kmc-h2-efficiency` when you need KMC input concepts, event-network logic, rate-table expectations, or the boundary between elementary rates and final observables.

## What The Agent Can Reliably Do

- explain what each workflow stage is for
- distinguish reusable patterns from project-specific numerical settings
- point to templates, references, and real example file shapes
- explain what extra information is still needed before a stage is runnable
- run a few guarded diagnostic, conversion, or post-processing scripts when file format and assumptions are confirmed

## What The Agent Must Not Guess

- DFT convergence settings
- trust levels and production exploration schedules
- DeePMD hyperparameters
- dpdata format strings, type maps, or unit interpretations
- reaction coordinates, bead counts, or HMC/MC settings
- TI integration direction, free-energy zero, or sign convention
- TST prefactors and physical state selection
- complete KMC event networks

If one of these is missing, the correct behavior is to ask for confirmation or say that the repository does not document the value yet.

## Common Starting Tasks

For ABACUS labeling:

```text
Use the skill at nqe-workflow-skills-release/abacus-dft-labeling.
Read the templates and references, then tell me what information I still need before generating INPUT, STRU, and KPT.
```

For DP-GEN:

```text
Use the skill at nqe-workflow-skills-release/dpgen-active-learning.
Explain the loop order and tell me what evidence I need before claiming convergence.
```

For DeePMD:

```text
Use the skill at nqe-workflow-skills-release/deepmd-training.
Read the references and tell me what I must check before using a trained model in downstream sampling.
```

For dpdata conversion:

```text
Use the skill at nqe-workflow-skills-release/dpdata-format-conversion.
Tell me how to inspect ABACUS output and convert it to DeePMD data without guessing format names or losing labels.
```

For CHMC/CPIHMC:

```text
Use the skill at nqe-workflow-skills-release/chmc-cpihmc-sampling.
Explain what the output means and what must happen before TI, TST, and KMC.
```

For TI/TST:

```text
Use the skill at nqe-workflow-skills-release/ti-tst-rate.
Read the script references and tell me how to go from mean-force windows to a TST rate without guessing missing physics.
```

For config-driven postprocessing:

```text
Use the skill at nqe-workflow-skills-release/nqe-postprocess-runner.
Read the config schema and example, then tell me what must be confirmed before running the postprocessing runner.
```

## Testing The Repository

Use [tests/manual_prompts.md](../tests/manual_prompts.md) for manual behavior tests. Start with the `Minimal Smoke Prompts` section when you want a quick pass over all skills. See [testing.md](testing.md) for the full test order and pass/fail criteria.

Useful script-level checks:

```bash
python deepmd-training/scripts/parse_lcurve.py --help
python dpdata-format-conversion/scripts/inspect_dpdata_system.py --help
python dpdata-format-conversion/scripts/convert_with_dpdata.py --help
python dpdata-format-conversion/scripts/compare_converted_system.py --help
python ti-tst-rate/scripts/extract_mean_force.py --print-defaults
python ti-tst-rate/scripts/integrate_free_energy.py --print-defaults
python ti-tst-rate/scripts/compute_tst_rates.py --print-defaults
python ti-tst-rate/scripts/run_smoke_test.py --skip-plots
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.example.yaml --dry-run
```

The TI/TST smoke test checks that the bundled demo chain runs through expected file shapes and script interfaces. It does not certify convergence or physical correctness.
