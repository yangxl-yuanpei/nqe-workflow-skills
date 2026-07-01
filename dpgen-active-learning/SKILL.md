---
name: dpgen-active-learning
description: Guidance and checks for the DP-GEN active-learning stage in the NQE H2 formation workflow. Use when a user asks about DP-GEN train-explore-label iterations, model deviation, trust levels, candidate selection, convergence diagnostics, param.json or machine.json planning, DeePMD training handoff, ABACUS labeling handoff, or whether a DP-GEN run is ready or converged.
---

# DP-GEN Active Learning

Use this skill for the DP-GEN stage that turns a user-prepared initial DFT-labeled dataset into a converged MLFF dataset and frozen DeePMD models.

## Scope

- General: Use the train -> exploration -> labeling loop, model-deviation, `param.json`, `machine.json`, and convergence-diagnostic checks for other DP-GEN/MLFF workflows.
- NQE H2-specific: Keep candidate selection and model validation connected to reaction-coordinate coverage needed for CHMC/CPIHMC free-energy sampling.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining DP-GEN loop structure, model deviation, trust levels, or convergence.
- Use `initial-dft-dataset` when the question concerns the first training dataset.
- Use `deepmd-training` when the question concerns DeePMD-kit `input.json`, training logs, freeze, or model testing.
- Use `lammps-exploration` when the question concerns LAMMPS input scripts, exploration trajectories, LAMMPS variables, `model_devi_jobs` templates, or LAMMPS output sanity checks.
- Use `abacus-dft-labeling` when the question concerns first-principles labeling tasks.
- Use `dpdata-format-conversion` when preparing, inspecting, or converting labeled data between ABACUS, DeePMD raw/npy, LAMMPS, or other dpdata-readable formats.
- Use `nqe-h2-workflow` when the user asks how DP-GEN connects to CHMC/CPIHMC, TI, TST, or KMC.

## Core Loop

Describe each DP-GEN iteration as exactly three main stages:
Describe the canonical DP-GEN loop as `training -> exploration -> labeling`.


1. Training: train an ensemble of DeePMD-kit models on the current DFT-labeled dataset.
2. Exploration: use trained models to explore configuration space and evaluate model deviation.
3. Labeling: use ABACUS to label selected uncertain candidate configurations and add them to the dataset.

Treat model-deviation selection as an internal filtering mechanism within or immediately after exploration, not as a fourth main stage.

## What This Skill May Do

- Explain why DP-GEN is needed before CHMC/CPIHMC production sampling.
- Map required DP-GEN inputs: initial data, structure configs, DeePMD training template, exploration settings, ABACUS labeling settings, and machine resources.
- Help inspect `param.json` and `machine.json` for missing fields and consistency, using official DP-GEN documentation as the source of parameter meanings.
- Summarize iteration outputs such as `iter.000000`, model files, exploration trajectories, model-deviation reports, candidate structures, and newly labeled data.
- Explain trust levels, candidate selection, convergence concepts, and staged exploration strategy.
- Route detailed LAMMPS script generation or review to `lammps-exploration`.
- Create TODO lists for human approval before a DP-GEN run.

## What This Skill Must Not Do

- Do not choose `tol_lo`, `tol_hi`, exploration engine, exploration temperature, ensemble, sampling length, LAMMPS timestep, dump frequency, or candidate selection strategy automatically.
- Do not choose ABACUS DFT settings for labeling.
- Do not choose DeePMD architecture, learning rate, batch size, loss weights, or training steps.
- Do not claim DP-GEN is converged without documented convergence criteria and user confirmation.
- Do not invent DP-GEN commands, paths, scheduler settings, queue names, or JSON fields.
- Do not present the loop as exploration -> labeling -> training or as training -> exploration -> model-deviation selection -> labeling.

- Use `../common/scripts/check_workflow_files.py --software dpgen --path PATH_TO_RUN` for a minimal static check of `param.json`/`run_param.json`, `machine.json`, placeholders, and obvious schema issues. Treat warnings as prompts for human review, not as convergence proof.

## Checks Before Running DP-GEN

- Confirm the initial DFT-labeled dataset exists and passed the `initial-dft-dataset` checklist.
- Confirm DFT metadata consistency between the initial dataset and future ABACUS labeling.
- Confirm `type_map` and atom ordering are consistent with DeePMD data and exploration structures.
- Confirm converted datasets have been checked with `dpdata-format-conversion` when DP-GEN inputs came from another software format.
- Confirm `param.json` and `machine.json` are present or explicitly marked TODO.
- Confirm DeePMD training template ownership belongs to `deepmd-training`, not this skill.
- Confirm ABACUS labeling template ownership belongs to `abacus-dft-labeling`, not this skill.
- Confirm all human-approved numerical parameters are recorded.

## Convergence And Output Review

- Inspect model-deviation distributions across exploration trajectories.
- Check whether candidate counts decrease across iterations, but do not treat this alone as proof of convergence.
- Check whether selected candidates are chemically meaningful and relevant to downstream reaction-coordinate sampling.
- Check DeePMD training did not diverge or produce NaN logs.
- Check ABACUS labeling tasks converged and produced complete energy, force, and virial labels.
- Report unresolved TODOs instead of filling them silently.

## Templates

- Use `templates/param.json.template` and `templates/machine.json.template` as teaching scaffolds for DP-GEN planning.
- Treat every `TODO_USER_APPROVAL` token as a required user-approved value.
- Do not treat template JSON fields as guaranteed for every DP-GEN version; check official DP-GEN documentation for the installed version.
- Delegate DeePMD training details to `deepmd-training/templates/input.json.template` and ABACUS label inputs to `abacus-dft-labeling/templates/`.
- Read `templates/reference-examples/README.md` and `references/dpgen-real-input-transfer-notes.md` when the user provides or asks about real DP-GEN `param.json`/`machine.json` files from another project.

## References

- Read `references/dpgen-failure-cases.md` when DP-GEN runs fail or logs are ambiguous. This placeholder should be expanded with real observed failures before relying on it for diagnosis.

- Read `../common/references/command-help.md` when an executable name, command option, subcommand, or version-specific syntax is missing; use official docs and local `-h`/`--help`/`help` output instead of guessing.

- Read `references/dpgen-exploration-strategy.md` when the user asks how to design exploration jobs, stage temperatures/trajectory lengths, or interpret `model_devi_jobs`.

- Read `references/dpgen-official-notes.md` for official DP-GEN documentation entry points for `dpgen run`, `param.json`, and `machine.json`.
- Read `references/dpgen-run-checklist.md` for local workflow-specific checks.
- Use the official DP-GEN documentation for `dpgen run`, `param.json`, and `machine.json` parameter meanings: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/index.html
