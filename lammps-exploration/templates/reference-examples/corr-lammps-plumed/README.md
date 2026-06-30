# CORR LAMMPS/PLUMED Reference Example

This directory contains real LAMMPS and PLUMED exploration inputs from a CORR-related DP-GEN workflow. They are included as reference examples for file organization, DP-GEN variable substitution, and PLUMED coupling style.

They are not H2/graphene production templates. Do not copy atom IDs, group definitions, masses, fixed layers, thermostat parameters, restraint centers, force constants, PLUMED atom indices, or run length settings without user approval and validation.

## Files

| File | Role in the original CORR example |
|---|---|
| `input.lammps` | LAMMPS exploration script using DP-GEN variables, DeePMD pair style, fixed substrate groups, NVT, restart logic, and PLUMED coupling. |
| `input.plumed_1` | PLUMED input defining units, a distance collective variable, harmonic restraint, printed distance output, and flush stride. |
| `README.md` | This transfer summary. |

## Transferable Patterns

- Use DP-GEN-substituted variables such as `V_NSTEPS`, `V_TEMP`, `V_PRES`, and `V_STRIDE` to drive exploration jobs.
- Keep LAMMPS and PLUMED inputs separate so DP-GEN can combine LAMMPS templates with multiple PLUMED templates.
- Use LAMMPS restart logic deliberately when continuing exploration.
- Record thermo output rich enough to diagnose temperature, energies, pressure, cell, and instability.
- Use PLUMED `PRINT`/`FLUSH` output to monitor collective variables or restraints during biased exploration.

## System-Specific Content Not To Transfer Blindly

- atom IDs in groups and PLUMED `DISTANCE ATOMS`
- Cu/C/O/H masses and type ordering
- fixed-bottom layer definitions and `setforce` choices
- thermostat damping, timestep, and run length
- `RESTRAINT AT`, `KAPPA`, and collective-variable choice
- boundary conditions and triclinic box handling
- whether to use NVT, NPT, reflective walls, or PLUMED biasing

Use this example as a realism check, not a default schedule.
