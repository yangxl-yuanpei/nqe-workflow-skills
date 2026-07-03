---
name: dpdata-format-conversion
description: Guidance and guarded scripts for using dpdata to inspect and convert atomistic data formats between ABACUS, LAMMPS, DeePMD, DP-GEN, xyz/ASE-like structures, and related workflow files. Use when a user asks about format conversion, DeepMD raw/npy data generation, System versus LabeledSystem, preserving energies/forces/virials/cells/type maps, or checking whether converted atomistic data are ready for downstream DeePMD, DP-GEN, LAMMPS, ABACUS, or CHMC/CPIHMC stages.
---

# dpdata Format Conversion

Use this skill for atomistic data format inspection and conversion between software stages. dpdata is a format-conversion and atomistic-data handling layer, not a physical validation layer.

## Required Boundary Skills

- Apply `nqe-boundaries` before judging whether converted data are scientifically ready.
- Use `abacus-dft-labeling` when the source is ABACUS DFT output.
- Use `deepmd-training` when the target is DeePMD raw/npy training data.
- Use `dpgen-active-learning` when conversion prepares DP-GEN initial data or labeled iterations.
- Use `lammps-exploration` when converting or inspecting LAMMPS structures, dumps, or trajectories.

## What This Skill May Do

- Explain when to use dpdata `System` versus `LabeledSystem`.
- Inspect frame count, atom count, atom names/type map, cell presence, and available labels such as energies, forces, and virials.
- Convert between explicitly provided input and output formats using dpdata.
- Compare source and converted systems for basic shape consistency.
- Produce TODOs when format names, units, atom ordering, type maps, labels, or cell information are not documented.

## What This Skill Must Not Do

- Do not guess dpdata format strings. Ask the user or consult official dpdata docs.
- Do not provide runnable conversion commands with invented format strings, paths, labels, or flags when the user has not confirmed them.
- Do not include optional flags such as `--labeled`, `--type-map`, `--set-size`, `--overwrite`, or `--confirm` merely because they exist. Mention them only as conditional choices after explaining when they apply.
- Do not answer a first-use or smoke prompt with a complete command line unless the prompt already contains confirmed paths, exact format strings, and labeled/unlabeled requirements.
- Do not claim conversion proves DFT convergence, label quality, training readiness, or physical correctness.
- Do not silently reorder atom types, change type maps, drop virials, or discard cells without reporting it.
- Do not treat unlabeled structures as DeePMD training labels.
- Do not assume a converted dataset is ready for DP-GEN or DeePMD without downstream checks.

## Response Protocol

When the user asks how to inspect or convert data but has not provided exact dpdata format strings:

1. Do not produce a runnable command.
2. Say that exact `--format`, `--input-format`, and `--output-format` values must be user-confirmed or verified against official dpdata documentation for the installed version.
3. Ask for source software/version, source path shape, target format, whether labels are required, expected frame/atom counts, cells/PBC, energies, forces, virials, and type-map expectations.
4. Offer a non-runnable command skeleton only if useful, and keep placeholders visibly non-executable.
5. Explain that after the user confirms formats, the workflow is inspect -> convert -> reload/compare -> downstream DeePMD/DP-GEN checks.

When the user asks the agent to guess an unknown format:

1. Refuse to guess.
2. Ask for the source software and a small directory/file listing.
3. Suggest checking official dpdata docs or local script `--help` before choosing a format string.
4. Do not try multiple plausible parser names until one happens to load.

## Core Rules

- Use `LabeledSystem` when energies, forces, or virials are required.
- Use `System` for unlabeled structures, trajectories, or geometry-only conversions.
- Require explicit `--input-format` and `--output-format` before conversion.
- If the exact format strings are unknown, stop at a TODO checklist or ask the user to confirm them; do not fill in plausible strings such as `abacus/scf` or `deepmd/npy` unless they are documented for this specific source and installed dpdata version.
- Confirm atom names/type map, atom count, frame count, cell/PBC, coordinates, energies, forces, virials, and units after conversion.
- Treat all script warnings as prompts for human review.

## Scripts

- Use `scripts/inspect_dpdata_system.py` to summarize a dpdata-readable file or directory.
- Use `scripts/convert_with_dpdata.py` to perform an explicit dpdata conversion.
- Use `scripts/compare_converted_system.py` to compare source and converted data after conversion.
- For inspection, omit `--type-map` unless the input format lacks element names or the user explicitly needs to test a specific external type ordering. Prefer reading the type map reported by the data itself.
- For conversion, do not pass a type map through `convert_with_dpdata.py`; inspect the source data first and let dpdata preserve the reported atom names/order. If a source format lacks reliable element names, stop and ask the user how to prepare or inspect that source before conversion.
- For comparison, do not pass external type maps; compare the atom names/order reported by the source and converted data themselves.

Non-runnable inspection skeleton:

```text
python scripts/inspect_dpdata_system.py
  --input TODO_USER_CONFIRMED_INPUT_PATH
  --format TODO_USER_CONFIRMED_INPUT_FORMAT
  [--labeled only if the user confirms labels are required and present]
```

Non-runnable conversion skeleton:

```text
python scripts/convert_with_dpdata.py
  --input TODO_USER_CONFIRMED_INPUT_PATH
  --input-format TODO_USER_CONFIRMED_INPUT_FORMAT
  --output TODO_USER_CONFIRMED_OUTPUT_PATH
  --output-format TODO_USER_CONFIRMED_OUTPUT_FORMAT
  [--labeled only if the user confirms labels are required and present]
  [--confirm only after the user approves formats, labels, units, atom order, and output path]
```

Non-runnable comparison skeleton:

```text
python scripts/compare_converted_system.py
  --source TODO_USER_CONFIRMED_INPUT_PATH
  --source-format TODO_USER_CONFIRMED_INPUT_FORMAT
  --converted TODO_USER_CONFIRMED_OUTPUT_PATH
  --converted-format TODO_USER_CONFIRMED_OUTPUT_FORMAT
  [--labeled only if the user confirms labels are required and present]
```

The skeletons are intentionally non-runnable. Replace placeholders and optional bracketed flags only after the user confirms the installed dpdata format names, label requirements, paths, units, and output policy.

## References

- Read `references/dpdata-failure-cases.md` when dpdata inspection, conversion, comparison, reloading, type-map checks, or labeled/unlabeled handoffs fail.

- Read `README.md` for script usage, required confirmations, key arguments, and common failure modes.
- Read `references/dpdata-official-notes.md` for official documentation entry points and basic API concepts.
- Read `references/conversion-checklist.md` before converting workflow data.
- Read `references/supported-conversions.md` when choosing conversion routes for this repository.
- Read `../common/references/command-help.md` when command syntax or installed-version behavior is missing.
