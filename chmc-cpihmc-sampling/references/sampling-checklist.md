# CHMC/CPIHMC Sampling Checklist

This reference summarizes constrained sampling checks for the NQE H2 formation workflow. It is not a production input template for the in-house code.

## Concepts

- CHMC: constrained HMC/MC sampling without path-integral beads; nuclei are treated classically.
- CPIHMC: constrained path-integral HMC/MC sampling with beads; includes nuclear quantum statistical effects.
- Both modes output mean force along a reaction coordinate for thermodynamic integration.
- CPIHMC does not directly output final H2 formation efficiency.

## Software / Method / Physics Layers

- Software: LAMMPS versus in-house CHMC/CPIHMC code.
- Sampling method: MD-based sampling versus MC/HMC-based sampling.
- Physical approximation: classical nuclei versus path-integral nuclei.

Do not collapse these layers. Do not call CPIHMC a quantum replacement for LAMMPS.

## Required Inputs

- accepted DeePMD frozen model path
- initial structure
- reaction-coordinate definition
- temperature
- sampling window positions
- HMC/MC step size and step count
- `Hybrid_Monte_Carlo_Ratio` interpretation: MC can include electron-number sampling, path-integral bead sampling, and reaction-coordinate-related angular/free-degree sampling; HMC mainly samples 3D degrees of freedom of atoms not directly tied to the reaction coordinate
- equilibration and production lengths
- output format for mean force
- for CPIHMC: bead number and bead convergence plan

## Reaction Coordinate Notes

Reaction coordinates are physical decisions and require user approval. In the project background, common examples include:

- two-H association: H-H distance
- adsorption/desorption: distance between H and adsorption site
- hopping: signed distance difference between neighboring sites
- path-integral calculations: use centroids of quantized atoms for reaction-coordinate definitions

These examples should not be treated as automatic defaults for new systems.

## Diagnostics To Request

- HMC acceptance rate; about 30-50% is often a useful range for this workflow, and temperature can shift acceptance
- autocorrelation of mean force
- trajectory mixing quality
- convergence of mean force with sampling length
- smoothness across neighboring windows
- bead-number convergence for CPIHMC
- abnormal wall/restriction rejection events if walls are used


## Template And Output File Boundaries

- `INPUT`, `STRU`, and optional `BEADS` are input-side files.
- `PHY_QUANT`, `ALL_INPUT`, `ALL_STRU`, and `MODEL_DEVI` are output or diagnostic files documented by the public README.
- Use `PHY_QUANT` as a source for mean-force/TI handoff only after units, sign convention, reaction-coordinate grid, and uncertainty/block information are documented.
- Use `MODEL_DEVI` as a diagnostic for MLFF uncertainty, not as convergence proof by itself.

## Grand-Canonical / Constant-Potential Feature

The public GC-Constrained-PIHMC repository documents grand-canonical ensemble support for CHMC/CPIHMC and includes electron-number controls such as `Elec_Num_Ratio`, `Mu`, `Elec_Num_Range`, and `Elec_Num_Width`. This is an important software capability, especially for electrochemical or constant-potential-like simulations.

For any target workflow, do not assume grand-canonical or constant-potential conditions by default. Use this feature only when the user explicitly documents the electrochemical context and approves electron-number controls.

Before using grand-canonical/constant-potential-like sampling, confirm:

- whether the target physics requires variable electron number or electrochemical potential control
- `Mu` and its units/sign convention
- electron-number range, width, and initial electron number in `STRU` if used
- whether CHMC or CPIHMC is intended
- how mean force and electron-number fluctuations should be interpreted downstream


## Real File Interpretation

- Prefer `ALL_INPUT` over memory or partial `INPUT` snippets when auditing parameters actually used in a completed run.
- For `PHY_QUANT`, identify `RxnCoord_*` and `MeanForce_*` pairs, then confirm units, sign convention, window/grid identity, and uncertainty before TI.
- Treat `dE_dN` and `ElecNum` as grand-canonical/electrochemical diagnostics when present.
- Treat `BEADS` as path-integral initialization data; confirm coordinate units and consistency with `N_Bead`/`Bead_Index`.

## Handoff To TI

Before thermodynamic integration:

- mean force is available for each window
- reaction-coordinate grid is documented
- uncertainties or block statistics are available or marked TODO
- output units and sign conventions are documented
- missing windows or failed sampling runs are flagged
