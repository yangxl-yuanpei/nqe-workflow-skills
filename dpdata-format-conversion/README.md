# dpdata Format Conversion Scripts

These scripts provide guarded helpers around dpdata for atomistic file inspection, explicit format conversion, and simple source/converted consistency checks.

They are intentionally conservative. They do not decide whether a dataset is physically correct, whether a DFT calculation converged, or whether converted data are production-ready for DeePMD, DP-GEN, LAMMPS, ABACUS, or CHMC/CPIHMC.

## Anti-Guessing Rule

Do not turn examples in this file into defaults for a new system.

- Do not invent dpdata format strings. Use only user-confirmed strings or strings verified against the installed dpdata documentation/version.
- Do not invent optional flags. Add `--labeled`, `--set-size`, `--overwrite`, or `--type-map` only when the user has confirmed that the flag applies.
- Do not replace `TODO_*` tokens with plausible-looking values just to make a command runnable.
- Do not treat a successful conversion as proof of ABACUS convergence, label quality, unit correctness, DeePMD readiness, or DP-GEN readiness.
- If the user has not confirmed exact input/output formats and label requirements, answer with a checklist or non-runnable skeleton rather than a runnable command.

## Required User Confirmation

Before conversion, confirm:

- source software and exact dpdata input format string
- target software and exact dpdata output format string
- whether labels are required, which determines `System` versus `LabeledSystem`
- element order/type map as reported by source inspection
- coordinate, cell, energy, force, virial, and unit conventions
- whether missing virials or cells are acceptable for the downstream task
- output path and overwrite policy

## Confirmed Local Mini Example

The user-provided `../00` directory is a small maintainer-local example for this workspace. It may not exist in a fresh public clone. It has ABACUS SCF-style input/output files and a converted DeePMD NPY directory:

- source path from the repository root: `..\00`
- source format, confirmed for this example only: `abacus/scf`
- target path from the repository root: `..\00\deepmd`
- target format, confirmed for this example only: `deepmd/npy`
- label mode, confirmed for this example only: labeled data, so use `--labeled`
- observed DeePMD files: `type.raw`, `type_map.raw`, `set.000\box.npy`, `coord.npy`, `energy.npy`, and `force.npy`

Use this example to test script interfaces and file-shape checks when dpdata is installed. Do not treat it as a public reproducibility fixture, and do not use its element list, ABACUS settings, labels, units, frame count, or output layout as defaults for another system.

From the repository root, inspect the ABACUS source:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input ../00 \
  --format abacus/scf \
  --labeled
```

Inspect the converted DeePMD NPY data:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input ../00/deepmd \
  --format deepmd/npy \
  --labeled
```

Compare the confirmed source and converted data:

```bash
python dpdata-format-conversion/scripts/compare_converted_system.py \
  --source ../00 \
  --source-format abacus/scf \
  --converted ../00/deepmd \
  --converted-format deepmd/npy \
  --labeled
```

To regenerate the converted output, choose a new output directory and confirm overwrite policy explicitly. Do not overwrite `../00/deepmd` unless the user asks for that.

```bash
python dpdata-format-conversion/scripts/convert_with_dpdata.py \
  --input ../00 \
  --input-format abacus/scf \
  --output ../00/deepmd-regenerated \
  --output-format deepmd/npy \
  --labeled \
  --confirm
```

Boundary: these commands are runnable only because the user confirmed this exact local example as `abacus/scf -> deepmd/npy` labeled data. For any other path, return to the Required User Confirmation checklist first.

## Inspect Data

Use this before conversion or before trusting an existing dataset shape:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input PATH_TO_DATA \
  --format TODO_USER_CONFIRMED_INPUT_FORMAT \
  TODO_ADD_--labeled_ONLY_IF_LABELS_ARE_REQUIRED
```

Key arguments:

- `--input`: input file or directory.
- `--format`: explicit dpdata format string confirmed by the user or official dpdata docs for the installed version.
- `--labeled`: use `dpdata.LabeledSystem`; include it only when labels are required and present.
- `--type-map`: optional comma-separated element/type map. Do not use it for ordinary inspection unless the source format lacks element names or the user explicitly needs to test a specific external type ordering.
- `--json`: print only JSON.

## Convert Data

Use this only after formats, labels, units, atom ordering, and output path are confirmed:

```bash
python dpdata-format-conversion/scripts/convert_with_dpdata.py \
  --input TODO_USER_CONFIRMED_INPUT_PATH \
  --input-format TODO_USER_CONFIRMED_INPUT_FORMAT \
  --output TODO_USER_CONFIRMED_OUTPUT_PATH \
  --output-format TODO_USER_CONFIRMED_OUTPUT_FORMAT \
  TODO_ADD_--labeled_ONLY_IF_LABELS_ARE_REQUIRED \
  --confirm
```

Key arguments:

- `--input-format` and `--output-format`: explicit dpdata format strings. Do not guess them.
- `--labeled`: required when converting energy/force/virial labels for training.
- `--set-size`: optional set size for `deepmd/npy` output when supported by installed dpdata and requested by the user.
- `--overwrite`: allow existing output path to be replaced; use only after explicit user approval.
- `--confirm`: required by the script, but it is not a substitute for real confirmation. Add it only after formats, labels, units, atom order, and output path are approved.

## Compare Converted Data

After conversion, compare source and converted data shape:

```bash
python dpdata-format-conversion/scripts/compare_converted_system.py \
  --source TODO_USER_CONFIRMED_INPUT_PATH \
  --source-format TODO_USER_CONFIRMED_INPUT_FORMAT \
  --converted TODO_USER_CONFIRMED_OUTPUT_PATH \
  --converted-format TODO_USER_CONFIRMED_OUTPUT_FORMAT \
  TODO_ADD_--labeled_ONLY_IF_LABELS_ARE_REQUIRED
```

This checks frame count, atom count, atom names/counts, label presence, array shapes, and optional max absolute numeric differences when NumPy is installed. Passing this comparison means the data shapes are consistent; it does not certify physical correctness.

The `TODO_*` tokens are intentional. Do not replace them with plausible format strings unless the user has confirmed those exact strings or they have been verified against official dpdata documentation for the installed version.

## Common Failure Modes

- wrong dpdata format string for the installed dpdata version
- using `System` for data that need energy/force labels
- missing virials when downstream training expects virials
- changed type map or atom order
- missing cell/PBC information
- assuming conversion proves ABACUS convergence or DeePMD readiness
