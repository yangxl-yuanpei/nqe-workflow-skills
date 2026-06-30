# LAMMPS Official Documentation Notes

Use official documentation when explaining LAMMPS syntax or DeePMD/LAMMPS coupling. Do not invent command syntax from memory.

## Official Entry Points

- LAMMPS command reference: https://docs.lammps.org/Commands_all.html
- LAMMPS variable command: https://docs.lammps.org/variable.html
- DeePMD-kit LAMMPS command guide: https://docs.deepmodeling.com/projects/deepmd/en/latest/third-party/lammps-command.html

## What To Verify In Official Docs

- command syntax for `units`, `atom_style`, `boundary`, `read_data`, `read_restart`, `pair_style`, `pair_coeff`, `fix`, `thermo`, `thermo_style`, `dump`, `restart`, `timestep`, `velocity`, and `run`
- variable syntax and command-line variable substitution
- whether the installed LAMMPS build supports the needed DeePMD pair style
- whether optional packages or plugins are required for the intended pair style, fix style, or PLUMED integration

## Version Sensitivity

LAMMPS and DeePMD-kit command syntax can vary with build options and versions. Ask for the installed versions and verify syntax before claiming a script is runnable.
