# CHMC/CPIHMC Templates

These templates are teaching scaffolds for the public GC-Constrained-PIHMC / CHMC-CPIHMC style workflow. They are not production inputs.

Use official documentation and local executable help before running. Replace every `TODO_USER_APPROVAL` token with a documented value.

## Files

| File | Purpose |
|---|---|
| `INPUT.template` | Simulation parameter scaffold for CHMC/CPIHMC-style sampling. |
| `STRU.template` | Initial structure scaffold in ABACUS-like format. |
| `BEADS.template` | Optional path-integral bead-coordinate scaffold for CPIHMC. |
| `PHY_QUANT.template` | Example output-shape scaffold for physical quantities / mean-force diagnostics. |
| `MODEL_DEVI.template` | Example output-shape scaffold for model-deviation diagnostics. |
| `reference-examples/` | Place redacted real inputs/outputs here when available. |

## Use Boundaries

- CHMC means classical constrained sampling without path-integral beads.
- CPIHMC means path-integral constrained sampling with bead-related settings.
- Reaction coordinate, bead number, window grid, temperature, timestep, steps, walls, electron-number controls, and output intervals are scientific choices that require user approval.
- The public README states current potential support is DP-only; require an accepted DeePMD/DP frozen model unless the installed code version documents otherwise.
