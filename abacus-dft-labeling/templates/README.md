# ABACUS DFT Labeling Templates

These files are teaching templates for ABACUS DFT labeling in the NQE workflow. They are intentionally incomplete: values that control scientific meaning are marked `TODO_USER_APPROVAL` and must be set by the user before any calculation is run.

Use these templates for two roles:

- Initial DFT-labeled dataset generation, when ABACUS is used to label user-prepared starting structures.
- DP-GEN labeling, when ABACUS labels candidate configurations selected by model-deviation filtering.

## Files

| File | Purpose |
|---|---|
| `INPUT.template` | ABACUS main input template for single-point energy/force/virial labeling. |
| `STRU.template` | ABACUS structure template with placeholders for lattice, species, pseudopotentials, basis files, and coordinates. |
| `KPT.template` | ABACUS k-point template with a user-approved mesh placeholder. |

## Required Before Use

- Replace every `TODO_USER_APPROVAL` token with a documented, user-approved value.
- Confirm ABACUS keyword syntax against the official ABACUS documentation for the target version.
- Confirm pseudopotential and basis files exist in the runtime environment.
- Keep settings consistent between initial labels and DP-GEN labeling unless the user explicitly approves a change.
- Run a small validation calculation before batch labeling.

## Real-World Reference Example

The directory `reference-examples/corr/` contains real ABACUS input files from a CORR-related calculation. Use it to understand ABACUS file organization and input style. Do not use its numerical parameters, structure, k-point mesh, solvation, field, gate, charge, or cell settings as defaults for H2/graphene.
