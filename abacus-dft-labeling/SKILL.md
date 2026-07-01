---
name: abacus-dft-labeling
description: Guidance and checks for ABACUS DFT labeling in the NQE H2 formation workflow. Use when a user asks about ABACUS INPUT/STRU/KPT files, initial DFT label generation, DP-GEN labeling backend setup, SCF/force/virial output checks, label consistency, or whether ABACUS results are ready for DP-GEN/DeePMD training.
---

# ABACUS DFT Labeling

Use this skill for ABACUS-specific first-principles labeling tasks in the NQE H2 formation workflow. ABACUS is the documented DFT backend for this teaching workflow.

## Scope

- General: Use the ABACUS input/output and labeling checks for any workflow that needs DFT energies, forces, and virials for MLFF training or validation.
- NQE H2-specific: Keep labeling settings consistent with the initial dataset and DP-GEN labeling stages that feed CHMC/CPIHMC free-energy sampling.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining DFT settings or judging label quality.
- Use `initial-dft-dataset` when ABACUS is used to generate or check starting labels before DP-GEN.
- Use `dpgen-active-learning` when ABACUS labeling occurs inside DP-GEN iterations.
- Use `deepmd-training` when ABACUS labels are being checked for DeePMD training readiness.
- Use `dpdata-format-conversion` when ABACUS outputs need to be inspected or converted into DeePMD raw/npy data or another atomistic data format.

## Roles In This Workflow

- Initial dataset role: ABACUS may label user-prepared structures before the first DP-GEN training step.
- DP-GEN labeling role: ABACUS labels uncertain candidate configurations selected by model-deviation filtering.
- Settings consistency role: ABACUS settings used for initial labels and DP-GEN labels must be consistent unless the user explicitly documents and approves a change.

## What This Skill May Do

- Explain the purpose of ABACUS `INPUT`, `STRU`, and `KPT` files.
- Help inspect whether ABACUS input templates include all required user-approved settings.
- Help inspect ABACUS outputs for obvious missing labels, SCF failures, force/virial availability, or unit/format issues.
- Produce TODO lists for missing functional, pseudopotential, basis, k-point, dispersion, spin, charge, slab, and convergence settings.
- Explain how ABACUS labels hand off to DP-GEN and DeePMD-kit data preparation.
- Route actual ABACUS-output-to-DeePMD conversion commands to `dpdata-format-conversion`.

## What This Skill Must Not Do

- Do not choose exchange-correlation functional, pseudopotential, basis set, cutoff, k-point mesh, smearing, dispersion correction, spin, charge, slab settings, or SCF/force convergence thresholds without user approval.
- Do not claim an ABACUS calculation converged unless logs and output files demonstrate convergence.
- Do not claim labels are ready for DP-GEN/DeePMD unless energy, force, virial, units, atom ordering, and metadata checks pass.
- Do not invent ABACUS commands, file names, keywords, or output fields; use official ABACUS documentation or existing project templates.
- Do not change physical assumptions to make a calculation easier without user approval.
- Do not relax or alter DP-GEN candidate structures when the task is single-point labeling; discuss fixed/free atoms only for explicit optimization workflows.

- Use `../common/scripts/check_workflow_files.py --software abacus --path PATH_TO_CALC` for a minimal static check of ABACUS `INPUT`/`STRU`/`KPT` files, INPUT-declared STRU/KPT paths, pseudopotential/orbital file existence, and obvious output/log issues. Treat warnings as prompts for human review, not as convergence proof.

## Input Checks

- Confirm `INPUT`, `STRU`, and `KPT` are present or explicitly TODO.
- Confirm all physical settings are user-provided or marked TODO.
- Confirm structure, cell, vacuum, PBC, atom order, and element labels match the target system.
- For single-point labeling, preserve candidate coordinates and atom order; do not treat movable flags as a default labeling strategy.
- Confirm pseudopotential and basis references are documented and accessible to the execution environment.
- Confirm initial dataset labeling and DP-GEN labeling use consistent ABACUS settings.

## Output Checks

- Check SCF convergence and calculation termination status.
- Check energy, force, and virial/stress labels are present when required.
- Check units and sign conventions before conversion to DP-GEN/DeePMD data.
- Check atom ordering and cell information remain consistent with input structures.
- Before conversion, confirm the dpdata input format string, target output format, type map, labels, and units with `dpdata-format-conversion`.
- Flag broken structures, unconverged calculations, missing labels, or abnormal forces for human review.

## Templates

- Use `templates/INPUT.template`, `templates/STRU.template`, and `templates/KPT.template` as teaching scaffolds when the user asks how ABACUS input files should be organized.
- Treat every `TODO_USER_APPROVAL` token in the templates as a required human decision, not a default.
- Verify all keywords and file syntax against the official ABACUS documentation for the user's installed version before running.
- Read `templates/reference-examples/corr/README.md` and `references/abacus-corr-transfer-notes.md` when a real ABACUS project example is useful for file organization or style. Treat the CORR files as reference examples, not H2/graphene production settings.

## References

- Read `references/abacus-failure-cases.md` when ABACUS input checks or logs mention missing pseudopotential files, missing numerical orbital files, missing STRU/KPT paths, or path-resolution failures.

- Read `../common/references/command-help.md` when an executable name, command option, subcommand, or version-specific syntax is missing; use official docs and local `-h`/`--help`/`help` output instead of guessing.

- Read `references/abacus-official-notes.md` for official ABACUS documentation entry points and file/command meanings.
- Read `references/abacus-labeling-checklist.md` for local workflow-specific checks.
- Use official ABACUS documentation for input/output file syntax and keyword meanings: https://abacus.deepmodeling.com/en/latest/
