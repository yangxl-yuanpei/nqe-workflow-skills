# ABACUS Failure Cases

Use this reference when an ABACUS input check or run fails before labels are produced. These cases explain common file/path failures; they do not prove that a calculation is physically valid after the error is fixed.

## Missing Pseudopotential File

Typical symptoms:

- ABACUS reports that a pseudopotential file cannot be opened or found.
- A run stops soon after reading `STRU` or initializing atom types.
- The file named in the `ATOMIC_SPECIES` block is absent from `pseudo_dir`.

Likely causes:

- `INPUT` has the wrong `pseudo_dir` path.
- `STRU` contains a pseudopotential filename that differs from the real file by spelling, version tag, extension, or case.
- The pseudopotential file exists locally but was not copied to the run directory or compute node.
- A relative `pseudo_dir` was interpreted from a different working directory than expected.

Agent response:

1. Check `INPUT` for `pseudo_dir`.
2. Check `STRU` `ATOMIC_SPECIES` pseudopotential filenames.
3. Verify each referenced file exists under `pseudo_dir`.
4. Do not substitute a different pseudopotential automatically; ask the user to approve the exact file and source/version.

## Missing Numerical Orbital File

Typical symptoms:

- ABACUS reports that an orbital file cannot be opened or found.
- The run uses `basis_type lcao` or another setting that requires numerical atomic orbitals.
- `STRU` has a `NUMERICAL_ORBITAL` section but files are absent from `orbital_dir`.

Likely causes:

- `INPUT` has no `orbital_dir` or points to the wrong directory.
- The orbital filenames in `STRU` do not match files on disk.
- The orbital set was not copied to the run directory or compute node.
- The selected orbital file is from a different element, cutoff, functional family, or basis convention than the user intended.

Agent response:

1. Check `basis_type` in `INPUT`.
2. Check `orbital_dir` in `INPUT`.
3. Check `NUMERICAL_ORBITAL` filenames in `STRU`.
4. Verify each file exists under `orbital_dir`.
5. Do not choose replacement orbital files automatically; ask the user to confirm the intended basis files.

## STRU Or KPT Path Mismatch

Typical symptoms:

- ABACUS cannot locate the structure or k-point file.
- `INPUT` sets `stru_file` or `kpoint_file` to a filename different from the files present in the run directory.

Likely causes:

- The project uses non-default filenames but the files were renamed or not copied.
- Relative paths are resolved from a different run directory.
- The template names `STRU` and `KPT` were changed in `INPUT` but not in the actual directory.

Agent response:

1. Check `stru_file` and `kpoint_file` in `INPUT`.
2. Verify those exact paths exist relative to the run directory.
3. Do not rename files silently; report the mismatch and ask the user which name should be authoritative.

## How This Connects To The Checker

Run the minimal static checker before submitting ABACUS jobs:

```bash
python common/scripts/check_workflow_files.py --software abacus --path PATH_TO_ABACUS_RUN
```

The checker can catch missing `INPUT`, `STRU`, `KPT`, missing `pseudo_dir`, missing `orbital_dir`, and missing pseudopotential/orbital files referenced by `STRU`. It cannot validate convergence, physical parameter quality, or whether a pseudopotential/orbital choice is scientifically appropriate.
