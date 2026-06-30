# CORR GC-CPIHMC Real Reference Example

This directory contains real GC-Constrained-PIHMC style input/output files from a CORR-related path-integral constrained sampling calculation. It is a reference example for file organization, grand-canonical controls, bead initialization, and `PHY_QUANT` output shape.

This is not a production template for a new target system. Do not copy reaction coordinates, atom indices, bead settings, electrochemical potential, electron-number controls, timestep, steps, model path, or output settings without user approval and validation.

## Files

| File | Meaning |
|---|---|
| `INPUT` | User-provided sampling input. |
| `BEADS` | Initial path-integral bead coordinates for selected atoms. |
| `ALL_INPUT` | Code-generated summary of all input parameters actually used, including defaults. |
| `PHY_QUANT` | Physical-quantity output sample including energies, `dE_dN`, electron number, reaction coordinates, and mean forces. |

## Observed Shape

- `INPUT` non-empty lines: `30`
- `ALL_INPUT` non-empty lines: `37`
- `BEADS` lines: `32`
- `PHY_QUANT` rows including header: `32`
- `PHY_QUANT` header: ` Steps         KinEng         PotEng         TotEng          dE_dN        ElecNum     RxnCoord_0     RxnCoord_1    MeanForce_0    MeanForce_1`

## Important Features Demonstrated

- DP potential through `Deep_Pot_Model`
- CHMC simulation type with path-integral bead settings
- grand-canonical electron-number controls: `Elec_Num_Range`, `Elec_Num_Width`, `Elec_Num_Ratio`, `Mu`
- multiple reaction-coordinate outputs and mean-force columns: `rc_0`, `rc_1`, `mf_0`, `mf_1`
- `ALL_INPUT` as a useful audit trail for defaults and final parameter values
- `PHY_QUANT` as the key handoff file for TI after unit/sign/uncertainty checks

## Transfer Boundaries

- Atom indices in `Virt_Atom`, `Rxn_Coord`, and `Bead_Index` are system-specific.
- `Mu`, electron-number range/width/ratio, and any constant-potential interpretation are system-specific.
- `N_Bead`, `N_Change_Bead`, bead coordinates, and bead convergence assumptions are system-specific.
- Mean-force sign convention and units must be confirmed before TI.
- This short `PHY_QUANT` sample demonstrates shape, not convergence.

## Transfer Boundary

- `INPUT` and `ALL_INPUT` should be compared before reproduction. This example intentionally preserves a spelling/value mismatch around the hybrid Monte Carlo ratio so the agent learns to audit effective parameters rather than silently normalize raw files.
