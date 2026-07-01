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
- Do not claim conversion proves DFT convergence, label quality, training readiness, or physical correctness.
- Do not silently reorder atom types, change type maps, drop virials, or discard cells without reporting it.
- Do not treat unlabeled structures as DeePMD training labels.
- Do not assume a converted dataset is ready for DP-GEN or DeePMD without downstream checks.

## Core Rules

- Use `LabeledSystem` when energies, forces, or virials are required.
- Use `System` for unlabeled structures, trajectories, or geometry-only conversions.
- Require explicit `--input-format` and `--output-format` before conversion.
- Confirm atom names/type map, atom count, frame count, cell/PBC, coordinates, energies, forces, virials, and units after conversion.
- Treat all script warnings as prompts for human review.

## Scripts

- Use `scripts/inspect_dpdata_system.py` to summarize a dpdata-readable file or directory.
- Use `scripts/convert_with_dpdata.py` to perform an explicit dpdata conversion.
- Use `scripts/compare_converted_system.py` to compare source and converted data after conversion.
- For inspection, omit `--type-map` unless the input format lacks element names or the user explicitly needs to test a specific external type ordering. Prefer reading the type map reported by the data itself.
- For conversion, do not pass a type map through `convert_with_dpdata.py`; inspect the source data first and let dpdata preserve the reported atom names/order. If a source format lacks reliable element names, stop and ask the user how to prepare or inspect that source before conversion.
- For comparison, do not pass external type maps; compare the atom names/order reported by the source and converted data themselves.

Example inspection:

```bash
python scripts/inspect_dpdata_system.py \
  --input PATH_TO_DATA \
  --format abacus/scf \
  --labeled
```

Example conversion:

```bash
python scripts/convert_with_dpdata.py \
  --input PATH_TO_ABACUS_OUTPUT \
  --input-format abacus/scf \
  --output deepmd_data \
  --output-format deepmd/npy \
  --labeled \
  --confirm
```

Example comparison:

```bash
python scripts/compare_converted_system.py \
  --source PATH_TO_ABACUS_OUTPUT \
  --source-format abacus/scf \
  --converted deepmd_data \
  --converted-format deepmd/npy \
  --labeled
```

## References

- Read `references/dpdata-failure-cases.md` when dpdata inspection, conversion, comparison, reloading, type-map checks, or labeled/unlabeled handoffs fail.

- Read `README.md` for script usage, required confirmations, key arguments, and common failure modes.
- Read `references/dpdata-official-notes.md` for official documentation entry points and basic API concepts.
- Read `references/conversion-checklist.md` before converting workflow data.
- Read `references/supported-conversions.md` when choosing conversion routes for this repository.
- Read `../common/references/command-help.md` when command syntax or installed-version behavior is missing.
