# CORR ABACUS Reference Example

This directory stores real ABACUS input files from a CORR-related calculation. These files are included as a reference example for file organization and ABACUS input style.

They are not H2/graphene production templates. Do not copy numerical settings, element choices, cell vectors, k-point mesh, charge settings, solvation settings, or field/gate settings into another system without explicit user approval and convergence checks.

## Files

| File | Role in the original CORR example |
|---|---|
| `INPUT_aimd` | ABACUS molecular-dynamics input using `calculation md`. |
| `INPUT_opt` | ABACUS cell-relaxation input using `calculation cell-relax`. |
| `INPUT_sp` | ABACUS single-point input using `calculation scf`. |
| `STRU_opt` | ABACUS structure file with species, pseudopotentials, numerical orbitals, cell, coordinates, movable flags, and magnetic tags. |
| `KPT` | Gamma-centered k-point mesh used in the CORR example. |

## How To Use This Example

- Use it to learn how a real ABACUS project separates task types into multiple INPUT files.
- Use it to recognize common sections such as `INPUT_PARAMETERS`, `ATOMIC_SPECIES`, `NUMERICAL_ORBITAL`, `LATTICE_VECTORS`, `ATOMIC_POSITIONS`, and `K_POINTS`.
- Use it to inspect how slab-like settings, movable flags, pseudopotential names, basis names, and optional electrochemical/field settings may appear.
- Keep the minimal templates as the starting point for new systems; use this CORR example as a realism check, not as default settings.
