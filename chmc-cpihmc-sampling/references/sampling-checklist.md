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

- HMC acceptance rate
- autocorrelation of mean force
- trajectory mixing quality
- convergence of mean force with sampling length
- smoothness across neighboring windows
- bead-number convergence for CPIHMC
- abnormal wall/restriction rejection events if walls are used

## Handoff To TI

Before thermodynamic integration:

- mean force is available for each window
- reaction-coordinate grid is documented
- uncertainties or block statistics are available or marked TODO
- output units and sign conventions are documented
- missing windows or failed sampling runs are flagged
