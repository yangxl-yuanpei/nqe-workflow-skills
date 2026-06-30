# CHMC/CPIHMC Real Output Notes

Use these notes when interpreting real files like the `corr-gc-cpihmc` reference example.

## INPUT Versus ALL_INPUT

- `INPUT` is the user-provided parameter file.
- `ALL_INPUT` is generated after the run and records all parameters actually used, including defaults or expanded values. Prefer `ALL_INPUT` when auditing what the code really ran.
- If `INPUT` and `ALL_INPUT` differ, ask whether defaults or code normalization changed the run settings before reusing the example.
- In `corr-gc-cpihmc`, `INPUT` contains `Hybrid_Monte_Cralo_Ratio 0.95` while `ALL_INPUT` records `Hybrid_Monte_Carlo_Ratio 0.8`; keep the raw files unchanged, but ask the user which value/code spelling should govern any reproduced run.
- When explaining that ratio, use the workflow-specific move split: MC can include electron-number sampling, path-integral bead sampling, and reaction-coordinate-related angular/free-degree sampling; HMC mainly samples 3D degrees of freedom of atoms not directly tied to the reaction coordinate. For this workflow, about 30-50% acceptance is often useful, and higher temperature can increase acceptance.

## BEADS

- `BEADS` contains initial bead coordinates for path-integral sampling.
- The public documentation warns that `BEADS` coordinates are in Bohr. Confirm units before comparing with `STRU` or other structure files.
- The number of lines and columns should be checked against `N_Bead` and `Bead_Index`.
- Treat bead coordinates as initialization data, not physical observables.

## PHY_QUANT

In the real reference example, `PHY_QUANT` contains columns like:

- `Steps`
- `KinEng`, `PotEng`, `TotEng`
- `dE_dN` and `ElecNum` for grand-canonical diagnostics
- `RxnCoord_0`, `RxnCoord_1`
- `MeanForce_0`, `MeanForce_1`

For TI handoff, identify the reaction-coordinate column(s), mean-force column(s), units, sign convention, sampling window, and uncertainty/block statistics. A raw `PHY_QUANT` file shape is not enough to claim a converged free-energy profile.

## Grand-Canonical Diagnostics

When `dE_dN` and `ElecNum` are present, explain them as grand-canonical/electrochemical diagnostics. Do not use them in a target workflow unless the user explicitly adds constant-potential or variable-electron-number physics.
