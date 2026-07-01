# Supported Conversion Routes

This repository focuses on the following practical conversion routes first. Always verify exact format names against the installed dpdata version.

## Priority Routes

- ABACUS output -> DeePMD raw/npy labeled data
- DeePMD raw/npy -> inspection before training or DP-GEN reuse
- LAMMPS dump/data -> structure or trajectory inspection
- xyz/ASE-readable structures -> intermediate structure inspection
- DP-GEN labeled outputs -> DeePMD dataset inspection

## Commonly Useful Format Families

- `deepmd/npy`
- `deepmd/raw`
- `abacus/*`
- `lammps/*`
- `xyz`
- `ase/structure`

The exact suffixes and accepted arguments are dpdata-version-specific.

## What To Avoid

- Do not use VASP examples as defaults for this repository's open DFT backend. ABACUS is the documented DFT labeling backend here.
- Do not assume every LAMMPS dump has enough information for DeePMD training.
- Do not assume every ABACUS output contains forces and virials.
- Do not convert unlabeled trajectories into labeled DeePMD training data.
