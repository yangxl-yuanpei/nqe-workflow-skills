# NQE H2 Workflow Map

This reference summarizes the teaching workflow for H2 formation with nuclear quantum effects. The current documented DFT backend is ABACUS.

## High-Level Pipeline

Initial DFT-labeled dataset -> DP-GEN active learning -> DeePMD/MLFF -> CHMC/CPIHMC mean-force sampling -> thermodynamic integration -> TST rate constants -> KMC H2 formation efficiency.

## Stage Table

| Stage | Purpose | Main Inputs | Main Outputs | Approval |
|---|---|---|---|---|
| initial dataset | Provide DFT labels for first DP-GEN training | user-prepared structures, ABACUS settings | energy/force/virial labels | required |
| DP-GEN | Iteratively improve MLFF | initial dataset, training/exploration/labeling configs | converged dataset and frozen models | required |
| final DeePMD | Optional model specialization | converged dataset or DP-GEN models | custom frozen model | required |
| CHMC | Classical constrained sampling | MLFF, RC, windows, HMC settings | classical mean force | required |
| CPIHMC | Path-integral constrained sampling | MLFF, RC, bead number, windows, HMC settings | quantum/NQE mean force | required |
| TI | Integrate mean force | CHMC/CPIHMC mean force, RC grid | F(xi), Delta F dagger | required |
| TST | Convert barriers to elementary rates | Delta F dagger, temperature | k(T), NQE enhancement | required |
| KMC | Simulate formation efficiency | elementary rates, lattice/event model | H2 formation rate and efficiency | required |
| report | Summarize teaching results | all previous outputs and TODOs | report with figures/tables | required |

## Graphene Meta 50 K Teaching Example

Documented:

- surface: graphene
- elementary step: meta two-H association
- temperature: 50 K
- classical free energy: CHMC without beads
- quantum free energy: CPIHMC with path-integral beads
- DFT backend: ABACUS
- MLFF framework: DP-GEN and DeePMD-kit

Not documented yet:

- real ABACUS production input files
- initial geometry files
- DP-GEN param.json and machine.json
- DeePMD input.json
- DP-GEN exploration engine choice for this example
- trust-level thresholds for this example
- reaction-coordinate grid and number of windows
- CPIHMC bead number for this example
- HMC step size, step count, equilibration, and convergence criteria
- TI integration method
- full KMC lattice model, event list, rates, and simulation parameters

## Correct Handoff Logic

- ABACUS produces DFT labels.
- DP-GEN uses DeePMD training, exploration, and ABACUS labeling to improve the MLFF.
- DeePMD frozen models approximate the Born-Oppenheimer PES learned from DFT labels.
- CHMC/CPIHMC use the MLFF to sample mean force along reaction coordinates.
- TI converts mean force into free-energy profiles and activation free energies.
- TST converts activation free energies into elementary rate constants.
- KMC uses elementary rate constants to estimate grain-scale H2 formation efficiency.
