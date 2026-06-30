# Boundary Rules

This reference condenses the canonical statements for the NQE H2 formation workflow. Use it to keep explanations and generated workflow text consistent.

## NQE

- NQE means nuclear quantum effects, mainly for H-related nuclei/protons: zero-point energy, nuclear delocalization, and tunneling-related quantum statistical effects.
- Electronic quantum effects are handled by DFT under the Born-Oppenheimer framework and should not be called NQE.
- ABACUS DFT produces energy, force, and related labels for the approximate Born-Oppenheimer potential energy surface.
- DeePMD-kit learns an approximate Born-Oppenheimer potential energy surface from DFT labels.
- CPIHMC/path-integral sampling introduces nuclear quantum statistical effects in nuclear degrees of freedom.

## Initial Dataset

- The workflow starts from an initial DFT-labeled dataset prepared or curated by the user.
- Initial DFT dataset preparation is not currently automated by the agent.
- The agent may explain strategies and checklists, but should not choose the dataset strategy, DFT settings, reaction paths, or initial structures automatically.
- Common strategies are user-provided/downloaded labeled data, chemically guided CINEB or transition-state searches, and AIMD combined with enhanced sampling.
- Do not claim that an initial dataset is sufficient unless validation criteria and checks are documented.

## DP-GEN

- DP-GEN is the outer-loop workflow manager for automated MLFF training.
- Describe each DP-GEN iteration as training -> exploration -> labeling.
- Training uses the current DFT-labeled dataset to train an ensemble of DeePMD-kit models.
- Exploration uses trained models to sample configuration space and evaluate model deviation.
- Labeling uses ABACUS to label selected candidate configurations.
- Model-deviation-based selection is an internal filtering mechanism within or immediately after exploration, not a fourth main step.
- The first training step starts from the user-prepared initial DFT-labeled dataset.
- Trust-level thresholds such as `tol_lo` and `tol_hi` are user-defined and should not be chosen by the agent.
- DP-GEN convergence is judged by trust-level distribution in exploration trajectories, not by a fixed iteration count.

## Component Handoff

- CPIHMC does not directly output final H2 formation efficiency.
- CHMC/CPIHMC output mean force along reaction coordinates.
- Thermodynamic integration converts mean force into free-energy profiles and activation free energies.
- TST converts activation free energies into elementary rate constants.
- KMC uses elementary rate constants to simulate large-scale H2 formation efficiency.

## LAMMPS, CHMC, and CPIHMC

- LAMMPS is a simulation package and should not be equated with classical MD only.
- LAMMPS can be used for classical MD and, with appropriate methods, path-integral-related simulations such as PIMD/RPMD.
- The in-house code can be used as CHMC without path-integral beads or CPIHMC with beads.
- Classical versus quantum sampling is determined by whether nuclear quantum effects are included through path-integral beads, not by the software name alone.
- LAMMPS and CHMC/CPIHMC are not strict substitutes. The choice depends on research stage, configuration space, reaction coordinate, constraints, sampling efficiency, and interface convenience.
- Do not describe CPIHMC as more accurate than LAMMPS or as the quantum replacement of LAMMPS.
