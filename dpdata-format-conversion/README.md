# dpdata Format Conversion Scripts

These scripts provide guarded helpers around dpdata for atomistic file inspection, explicit format conversion, and simple source/converted consistency checks.

They are intentionally conservative. They do not decide whether a dataset is physically correct, whether a DFT calculation converged, or whether converted data are production-ready for DeePMD, DP-GEN, LAMMPS, ABACUS, or CHMC/CPIHMC.

## Required User Confirmation

Before conversion, confirm:

- source software and exact dpdata input format string
- target software and exact dpdata output format string
- whether labels are required, which determines `System` versus `LabeledSystem`
- element order/type map as reported by source inspection
- coordinate, cell, energy, force, virial, and unit conventions
- whether missing virials or cells are acceptable for the downstream task
- output path and overwrite policy

## Inspect Data

Use this before conversion or before trusting an existing dataset shape:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input PATH_TO_DATA \
  --format deepmd/npy \
  --labeled
```

Key arguments:

- `--input`: input file or directory.
- `--format`: explicit dpdata format string, such as `deepmd/npy`, `deepmd/raw`, or a version-supported ABACUS/LAMMPS format.
- `--labeled`: use `dpdata.LabeledSystem`; use this for DFT-labeled data intended for DeePMD training.
- `--type-map`: optional comma-separated element/type map. Do not use it for ordinary inspection unless the source format lacks element names or needs an external type ordering.
- `--json`: print only JSON.

## Convert Data

Use this only after formats, labels, units, atom ordering, and output path are confirmed:

```bash
python dpdata-format-conversion/scripts/convert_with_dpdata.py \
  --input PATH_TO_ABACUS_OUTPUT \
  --input-format abacus/scf \
  --output deepmd_data \
  --output-format deepmd/npy \
  --labeled \
  --confirm
```

Key arguments:

- `--input-format` and `--output-format`: explicit dpdata format strings. Do not guess them.
- `--labeled`: required when converting energy/force/virial labels for training.
- `--set-size`: optional set size for `deepmd/npy` output when supported by installed dpdata.
- `--overwrite`: allow existing output path to be replaced; use only after user approval.
- `--confirm`: required. The script refuses conversion without it.

## Compare Converted Data

After conversion, compare source and converted data shape:

```bash
python dpdata-format-conversion/scripts/compare_converted_system.py \
  --source PATH_TO_ABACUS_OUTPUT \
  --source-format abacus/scf \
  --converted deepmd_data \
  --converted-format deepmd/npy \
  --labeled
```

This checks frame count, atom count, atom names/counts, label presence, array shapes, and optional max absolute numeric differences when NumPy is installed. Passing this comparison means the data shapes are consistent; it does not certify physical correctness.

## Common Failure Modes

- wrong dpdata format string for the installed dpdata version
- using `System` for data that need energy/force labels
- missing virials when downstream training expects virials
- changed type map or atom order
- missing cell/PBC information
- assuming conversion proves ABACUS convergence or DeePMD readiness
