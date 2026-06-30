# KMC H2 Efficiency Checklist

This reference summarizes KMC checks for the NQE H2 formation workflow. It is not a production KMC input template.

## Required Upstream Inputs

- elementary TST rate constants from `ti-tst-rate`
- labels identifying each elementary step
- temperature and environment assumptions for each rate
- uncertainty or TODO marker for each rate

## Event Network

A full H2 formation KMC model generally needs more than one elementary step. Depending on the surface model, include or explicitly mark TODO for:

- adsorption
- desorption
- hopping/diffusion
- two-H association channels such as ortho, meta, para when relevant
- surface-specific events and constraints

A single meta two-H association rate is not enough for full H2 formation efficiency.

## Lattice And Environment Assumptions

Require user approval for:

- lattice or surface model
- adsorption-site definition
- boundary conditions
- initial hydrogen coverage
- gas temperature and dust temperature treatment
- density grid
- temperature grid
- coverage-dependence assumptions
- thermalization or adiabatic assumptions

## Simulation Parameters

Require documentation for:

- total KMC steps or physical-time stopping criterion
- number of independent trajectories
- random seeds
- output interval
- definition and normalization of H2 formation rate
- definition of H2 formation efficiency

## Output Review

- H2 event counts are sufficient for statistics.
- simulated physical time and surface area normalization are documented.
- steady state is reached or transient interpretation is stated.
- coverage statistics are physically plausible.
- dominant rate-limiting step is consistent with the rate network.
- uncertainty across trajectories is reported or TODO.

## Handoff From TI/TST

KMC receives rate constants. It does not directly consume:

- CPIHMC mean-force files
- CHMC/CPIHMC trajectories
- raw free-energy profiles without extracted elementary rates

Missing elementary rates should be listed as TODOs rather than invented.
