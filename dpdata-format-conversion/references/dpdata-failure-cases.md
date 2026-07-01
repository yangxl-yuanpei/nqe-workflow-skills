# dpdata Failure Cases

Use this reference when dpdata inspection, conversion, or comparison fails, or when converted data look inconsistent with the source. These cases are diagnostic patterns, not proof that a conversion is scientifically valid after the immediate issue is fixed.

Some patterns below are informed by public upstream dpdata issues. Treat those issues as examples of file-shape, parser, and version-boundary problems. Do not copy their physical systems, software settings, or format choices as defaults for this repository.

## Upstream Issue References

These public GitHub issues are useful as searchable examples of real parser, writer, and shape failures. Use them to understand symptoms and version boundaries, not to infer production settings for this repository:

- Search all upstream dpdata issues: [deepmodeling/dpdata issues](https://github.com/deepmodeling/dpdata/issues).
- Search closed and open issues by symptom, format string, and error text: [deepmodeling/dpdata issue search](https://github.com/deepmodeling/dpdata/issues?q=is%3Aissue).
- ABACUS parser/version behavior: [deepmodeling/dpdata#949](https://github.com/deepmodeling/dpdata/issues/949), [deepmodeling/dpdata#951](https://github.com/deepmodeling/dpdata/issues/951).
- VASP OUTCAR parser behavior: [deepmodeling/dpdata#359](https://github.com/deepmodeling/dpdata/issues/359), [deepmodeling/dpdata#611](https://github.com/deepmodeling/dpdata/issues/611), [deepmodeling/dpdata#894](https://github.com/deepmodeling/dpdata/issues/894).
- ASE stress / labeled-system compatibility: [deepmodeling/dpdata#975](https://github.com/deepmodeling/dpdata/issues/975).
- DeepMD mixed/HDF5 optional-array shape issues: [deepmodeling/dpdata#831](https://github.com/deepmodeling/dpdata/issues/831), [deepmodeling/dpdata#996](https://github.com/deepmodeling/dpdata/issues/996).
- ABACUS `STRU` writing behavior: [deepmodeling/dpdata#998](https://github.com/deepmodeling/dpdata/issues/998).
- CP2K parser file-argument behavior: [deepmodeling/dpdata#673](https://github.com/deepmodeling/dpdata/issues/673).

Keep the stage boundary clear:

- dpdata inspects and converts atomistic data arrays.
- It does not prove DFT convergence, label quality, force/energy correctness, type-map suitability, or downstream DeePMD/DP-GEN readiness.
- Any fix involving format strings, labeled versus unlabeled data, atom ordering, type maps, units, cells, virials, or dropped labels requires user confirmation.

## Unknown Or Wrong Format String

Typical symptoms:

- `dpdata.System` or `dpdata.LabeledSystem` cannot load the input path.
- A command uses a plausible-looking format string that is not supported by the installed dpdata version.
- A script works on one machine but fails on another with a different dpdata version.
- The agent is tempted to guess between formats such as `abacus/scf`, `abacus/pw/scf`, `abacus/lcao/relax`, `deepmd/raw`, or `deepmd/npy`.

Likely causes:

- dpdata format strings are version-specific.
- The source directory is not the shape expected by that reader.
- A format name was copied from another project or a newer dpdata release.
- The data are unlabeled, but the command uses `LabeledSystem`, or the reverse.

Agent response:

1. Check the installed script help or official dpdata documentation before choosing a format string.
2. Ask the user to confirm source software, calculation type, and exact input/output formats.
3. Run `inspect_dpdata_system.py` before conversion when possible.
4. Do not try a list of guessed formats until one happens to load.
5. Record the dpdata version and the exact command that worked or failed.

Useful command shape:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input PATH_TO_DATA \
  --format USER_CONFIRMED_FORMAT \
  --labeled
```

## System Used Where LabeledSystem Is Required

Typical symptoms:

- The converted output contains coordinates and cells but no energies, forces, or virials.
- DeePMD training data are generated from unlabeled structures.
- `inspect_dpdata_system.py` reports missing labels needed by downstream DeePMD or DP-GEN.
- The user asks whether unlabeled LAMMPS/XYZ/ASE structures are ready for training.

Likely causes:

- `System` was used for data that need labels.
- The source format does not contain DFT labels.
- The output route discards optional labels that were not available or not supported.

Agent response:

1. Use `LabeledSystem` when DeePMD/DP-GEN labels are required.
2. Check for energies, forces, virials, cells, atom names, atom count, and frame count after loading.
3. If labels are missing, route back to DFT labeling or a user-provided labeled source.
4. Do not treat unlabeled geometry conversion as DeePMD training data.
5. Do not fabricate missing labels or fill them with zeros.

## Source Parser Breaks On Software-Version Output Changes

Typical symptoms:

- Loading a previously supported format fails after the source code version changes.
- The parser reports missing energies, missing frames, or cannot convert a token to a number.
- A labeled trajectory loads only part of the expected frames.
- ABACUS, VASP, CP2K, QE, or ASE outputs differ from the parser's expected keywords or stress/virial shape.

Likely causes:

- The source software changed output keywords or table layout.
- The calculation mode is not the one expected by the selected dpdata reader.
- A parser supports one branch/version of a code but not another.
- Optional data such as stress, virial, spin, or frame parameters have changed shape.

Observed upstream examples:

- ABACUS MD energy keywords changed, causing an energy/frame mismatch in `abacus/pw/md`: [deepmodeling/dpdata#949](https://github.com/deepmodeling/dpdata/issues/949).
- ABACUS LCAO relax parsing reported only the first frame instead of the full trajectory: [deepmodeling/dpdata#951](https://github.com/deepmodeling/dpdata/issues/951).
- VASP OUTCAR parsing has reported `LabeledSystem` failures and numeric parsing failures across versions/files: [deepmodeling/dpdata#359](https://github.com/deepmodeling/dpdata/issues/359), [deepmodeling/dpdata#611](https://github.com/deepmodeling/dpdata/issues/611).
- ASE stress shape compatibility has caused `ase/structure` to `LabeledSystem` failures: [deepmodeling/dpdata#975](https://github.com/deepmodeling/dpdata/issues/975).

Agent response:

1. Record source software name, version or branch, calculation mode, and dpdata version.
2. Inspect raw logs for the expected energy, force, cell, virial, and frame markers.
3. Compare the loaded frame count with the expected trajectory length.
4. If parser support is unclear, ask the user whether to update dpdata, use another official format route, or export through a verified intermediate format.
5. Do not assume that a partially loaded trajectory is acceptable.

## Wrong Input Path Or Directory Shape

Typical symptoms:

- A directory conversion returns zero frames or empty `MultiSystems`.
- A multi-directory conversion misses single-point calculation files.
- The CLI or script reports that required files are missing even though they exist in subdirectories.
- Relative and absolute paths behave differently for a helper route.

Likely causes:

- The chosen reader expects a file, but the command passed a parent directory.
- The chosen reader expects a directory, but the command passed one output file.
- Multi-directory aggregation requires a specific directory depth or file naming pattern.
- A helper path was interpreted relative to the current working directory.

Observed upstream examples:

- Multi-directory conversion of OUTCAR single-point calculations has reported failures when aggregating nested directories: [deepmodeling/dpdata#894](https://github.com/deepmodeling/dpdata/issues/894).
- `MultiSystems.from_dir` has had path-shape issues around directory discovery behavior: [deepmodeling/dpdata#986](https://github.com/deepmodeling/dpdata/issues/986).

Agent response:

1. List the expected input files and compare them with the actual directory tree.
2. Try inspection on one known-good file or one leaf calculation directory before aggregating many directories.
3. Ask the user to confirm whether the conversion target is one system, many systems, or a mixed dataset.
4. Do not flatten or regroup directories without preserving provenance.
5. Do not treat zero-frame output as a successful conversion.

## Atom Names Or Type Map Changes Unexpectedly

Typical symptoms:

- Source and converted systems have the same atom count but different atom-name order.
- `type.raw`, `type_map.raw`, `atom_names`, or element counts do not match the source.
- A downstream DeePMD model reads the wrong element mapping.
- A comparison script reports type-map or atom-name mismatch.

Likely causes:

- A type map was supplied externally and did not match the source data.
- The source format lacks reliable element names.
- Atom names were sorted or padded differently during conversion.
- Multiple systems with different element sets were combined without an explicit policy.

Agent response:

1. Inspect the source first and prefer the atom names/order reported by dpdata.
2. Do not pass a type map through `convert_with_dpdata.py`.
3. Use `compare_converted_system.py` to compare source and converted atom names/order.
4. If the source lacks reliable element names, stop and ask how the type map should be defined.
5. Do not silently reorder atom types or accept type-map drift for training data.

## Frame Count, Atom Count, Or Optional Array Shape Mismatch

Typical symptoms:

- Source and converted systems have different frame counts or atom counts.
- Loading a converted mixed dataset reports shape mismatch for optional arrays such as `fparam`.
- DeepMD HDF5/raw/npy routes disagree about empty optional arrays.
- A conversion succeeds, but reloading the output fails.

Likely causes:

- Multi-system aggregation mixed incompatible systems.
- Optional frame-level or atom-level arrays were present for some systems but not others.
- A writer emitted empty optional arrays that a loader could not reshape.
- The target format requires consistent shape across frames or systems.

Observed upstream examples:

- `deepmd/npy/mixed` loading has reported `fparam` shape mismatch in `MultiSystems`: [deepmodeling/dpdata#831](https://github.com/deepmodeling/dpdata/issues/831).
- DeepMD HDF5 optional empty arrays have been reported as writable but not reloadable: [deepmodeling/dpdata#996](https://github.com/deepmodeling/dpdata/issues/996).

Agent response:

1. Compare frame count and atom count before and after conversion.
2. Reload the converted output with the intended output format.
3. Check optional arrays such as virials, `fparam`, `aparam`, spin, or custom labels if they are required downstream.
4. Split incompatible systems rather than forcing them into one mixed dataset.
5. Do not continue to training until the converted output can be reloaded and compared.

## Labels, Virials, Cells, Or PBC Disappear

Typical symptoms:

- `inspect_dpdata_system.py` reports that energies or forces are missing after conversion.
- Virials are absent even though downstream training expects them.
- Cells or PBC are missing for periodic data.
- Coordinate arrays survive, but label arrays do not.

Likely causes:

- The source was unlabeled or only partially labeled.
- The selected output format does not preserve a label type.
- The parser could not find a label because of source-version output differences.
- The user converted through an intermediate geometry-only format.

Agent response:

1. Check label availability before conversion and after conversion.
2. Ask which labels are required downstream: energies, forces, virials, cells, PBC, or custom arrays.
3. If virials are required but missing, stop and route to the target-stage training requirements.
4. Do not fill missing virials or labels with placeholder values.
5. Document labels that are intentionally absent as TODOs.

## ABACUS STRU Or Input-Like Output Is Malformed

Typical symptoms:

- A converted ABACUS `STRU` file cannot be parsed by ABACUS.
- Position lines, move flags, spin constraints, pseudopotential names, or basis entries look malformed.
- The user asks whether a generated `STRU` is ready for DFT labeling.

Likely causes:

- The writer route has a format-specific bug or version mismatch.
- Required ABACUS metadata such as masses, pseudopotentials, basis files, constraints, or spin settings were not supplied.
- The source structure lacks ABACUS-specific fields.

Observed upstream example:

- ABACUS `STRU` writing with scalar spin-constraint flags has produced malformed position lines in one reported issue: [deepmodeling/dpdata#998](https://github.com/deepmodeling/dpdata/issues/998).

Agent response:

1. Inspect generated `STRU` text before using it as an ABACUS input.
2. Route ABACUS input-readiness questions to `abacus-dft-labeling`.
3. Ask the user to confirm masses, pseudopotentials, basis files, constraints, and spin settings.
4. Do not assume a geometry conversion produces a production-ready ABACUS input.
5. Do not repair ABACUS physical settings without user approval.

## CP2K Or Other Parser Reports NoneType Or Missing Auxiliary Files

Typical symptoms:

- A parser raises a `NoneType` path error while looking for trajectory, cell, force, or output-log files.
- The source directory contains a main output log but not the auxiliary files expected by the selected reader.
- The user says forces or trajectories were enabled, but dpdata still cannot find them.

Likely causes:

- The selected format requires multiple files with specific names.
- The command passed a directory without the expected keyword arguments.
- The source software did not print one of the required sections.
- File names differ from the reader's defaults.

Observed upstream example:

- A CP2K-to-DeepMD conversion reported a `NoneType` path failure when the parser could not locate an expected file argument: [deepmodeling/dpdata#673](https://github.com/deepmodeling/dpdata/issues/673).

Agent response:

1. Check the selected format's required files and keyword arguments.
2. Ask the user to provide the output log, force file, cell file, trajectory file, and exact command.
3. Do not assume a main output log alone contains all labels.
4. If a format requires custom file-name arguments, ask the user to confirm them.
5. Prefer official examples or local `--help` over guessed parser keywords.

## Output Already Exists Or Conversion Would Overwrite Data

Typical symptoms:

- The conversion target directory already contains `set.*`, `type.raw`, `type_map.raw`, or prior output.
- A rerun would mix old and new converted frames.
- The user asks to overwrite output without checking what is there.

Likely causes:

- A previous conversion attempt partially completed.
- The same output path is reused for different source data.
- Old and new dpdata versions wrote different schemas.

Agent response:

1. Refuse to overwrite existing output unless the user explicitly approves.
2. Inspect the existing output and record whether it is complete or partial.
3. Prefer a new output directory for a new source or new conversion policy.
4. Do not merge outputs from different source systems without a documented aggregation rule.
5. Preserve failed outputs for audit unless the user approves cleanup.

## How These Cases Connect To Scripts

Use `inspect_dpdata_system.py` before conversion:

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py \
  --input PATH_TO_DATA \
  --format USER_CONFIRMED_INPUT_FORMAT \
  --labeled
```

Use `convert_with_dpdata.py` only with explicit input and output formats:

```bash
python dpdata-format-conversion/scripts/convert_with_dpdata.py \
  --input PATH_TO_DATA \
  --input-format USER_CONFIRMED_INPUT_FORMAT \
  --output PATH_TO_OUTPUT \
  --output-format USER_CONFIRMED_OUTPUT_FORMAT \
  --labeled \
  --confirm
```

Use `compare_converted_system.py` after conversion:

```bash
python dpdata-format-conversion/scripts/compare_converted_system.py \
  --source PATH_TO_DATA \
  --source-format USER_CONFIRMED_INPUT_FORMAT \
  --converted PATH_TO_OUTPUT \
  --converted-format USER_CONFIRMED_OUTPUT_FORMAT \
  --labeled
```

Script output is a file-shape and metadata diagnostic. It is not a production-readiness certificate for DeePMD, DP-GEN, ABACUS, LAMMPS, CHMC/CPIHMC, TI/TST, or KMC.
