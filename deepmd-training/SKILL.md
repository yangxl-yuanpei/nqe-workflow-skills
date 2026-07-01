---
name: deepmd-training
description: Guidance and checks for DeePMD-kit training in the NQE H2 formation workflow. Use when a user asks about DeePMD-kit input.json, training data format, DP-GEN model ensembles, final optional DeePMD training, freeze/test/model-deviation checks, training logs such as lcurve.out, or whether a DeePMD frozen model is ready for CHMC/CPIHMC production sampling.
---

# DeePMD Training

Use this skill for DeePMD-kit training and model validation within the NQE H2 formation workflow. DeePMD-kit learns an approximate Born-Oppenheimer potential energy surface from DFT labels.

## Scope

- General: Use the DeePMD-kit data, `input.json`, train/freeze/test, ensemble, and model-readiness checks for other MLFF workflows.
- NQE H2-specific: Require validation evidence for reaction-coordinate regions before a frozen model is accepted for CHMC/CPIHMC sampling.

## Required Boundary Skills

- Apply `nqe-boundaries` before judging model reliability or training settings.
- Use `dpgen-active-learning` when DeePMD training is part of the DP-GEN train-explore-label loop.
- Use `initial-dft-dataset` when the question concerns training data origin or label consistency.
- Use `dpdata-format-conversion` when training data must be inspected as DeePMD raw/npy or converted from ABACUS, LAMMPS, xyz, ASE, or another dpdata-readable source.
- Use `nqe-h2-workflow` when the user asks how the model is used by CHMC/CPIHMC, TI, TST, or KMC.

## Roles In This Workflow

- In DP-GEN, DeePMD-kit trains an ensemble of models on the current DFT-labeled dataset; model disagreement later drives model-deviation-based candidate selection.
- After DP-GEN convergence is accepted by the user, the user may either select one final DP-GEN frozen model or run optional specialized DeePMD training on the accumulated dataset.
- The selected frozen model is an intermediate tool for CHMC/CPIHMC free-energy sampling, not the final scientific observable.

## What This Skill May Do

- Explain DeePMD-kit training inputs, data-format expectations, training/freeze/test concepts, and model-deviation use.
- Inspect a DeePMD dataset description for expected files, type maps, units, label completeness, and train/test split assumptions.
- Route file-format conversion and source/converted shape comparison to `dpdata-format-conversion`.
- Inspect `input.json` for missing or undocumented sections using official DeePMD-kit documentation for field meanings.
- Inspect training logs such as `lcurve.out` for obvious divergence, NaNs, or missing metrics. Use `scripts/parse_lcurve.py` for deterministic first-pass log summaries when a log file is available.
- Explain how ensemble models from different random seeds support DP-GEN model-deviation estimates.
- Use `dp test` results to compare multiple final models only when the test dataset, metrics, and user-approved selection criteria are documented.
- Produce TODO lists for user-approved training settings and validation criteria.

## What This Skill Must Not Do

- Do not choose descriptor type, cutoff radius, fitting network architecture, embedding network architecture, loss weights, learning-rate schedule, batch size, training steps, validation split, or random seeds without user approval.
- Do not claim a DeePMD model is reliable without documented test errors, model-deviation checks, and reaction-relevant validation.
- Do not claim the MLFF is an exact Born-Oppenheimer PES.
- Do not skip user approval before choosing a final production model for CHMC/CPIHMC.
- Do not invent DeePMD commands, paths, JSON fields, or output filenames; use official documentation or existing project files.

- Use `../common/scripts/check_workflow_files.py --software deepmd --path PATH_TO_TRAINING` for a minimal static check of `input.json`, `lcurve.out`, logs, placeholders, and obvious NaN/Inf markers. Treat warnings as prompts for human review, not as model-readiness proof.

## Checks Before Training

- Confirm the DFT-labeled dataset passed initial dataset and ABACUS labeling checks.
- Confirm energy, force, and virial labels are present if required by the training setup.
- Confirm `type_map`, atom ordering, units, coordinates, cells, and PBC are consistent.
- If the dataset was converted, confirm `dpdata-format-conversion` inspected frame count, atom count, type map, cells, labels, and source/converted shape consistency.
- Confirm training and validation data selection is documented.
- Confirm all training hyperparameters are user-provided or explicitly TODO.

## Checks After Training

- Check training logs for NaNs, divergence, missing metrics, or abnormal loss behavior.
- Check energy, force, and virial test errors if available.
- Check consistency across ensemble models if used for DP-GEN.
- Check whether validation includes configurations relevant to CHMC/CPIHMC reaction-coordinate sampling.
- Check the frozen model path and format are documented before downstream use.
- Report unresolved TODOs rather than declaring production readiness.

## Templates

- Use `templates/input.json.template` as a teaching scaffold for DeePMD-kit training input.
- Read `templates/reference-examples/corr-deepmd/README.md` when a real DeePMD training example is useful for file organization, lcurve shape, or train.log interpretation.
- Treat every `TODO_USER_APPROVAL` token as a required user-approved value.
- Verify field names, descriptor options, and command behavior against the official DeePMD-kit documentation for the installed version before running.

## References

- Read `references/deepmd-failure-cases.md` when DeePMD-kit training, freeze, test, or model-deviation steps fail. This placeholder should be expanded with real observed failures before relying on it for diagnosis.

- Read `../common/references/command-help.md` when an executable name, command option, subcommand, or version-specific syntax is missing; use official docs and local `-h`/`--help`/`help` output instead of guessing.

- Read `references/deepmd-official-notes.md` for official DeePMD-kit documentation entry points for data, train, freeze, test, and model deviation.
- Read `references/deepmd-training-checklist.md` for local workflow-specific checks.
- Use `scripts/parse_lcurve.py` to summarize DeePMD-kit `lcurve.out`-style training logs; treat its output as diagnostics, not model certification.
- Read `references/deepmd-freeze-test-selection.md` when the user asks about freeze/export, `dp test`, final model selection, or DP-GEN model-deviation categories.
- Use the official DeePMD-kit documentation for data, train, freeze, test, and model-deviation command meanings: https://docs.deepmodeling.com/projects/deepmd/en/latest/
