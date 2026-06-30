---
name: kmc-h2-efficiency
description: Guidance and checks for kinetic Monte Carlo simulation of H2 formation efficiency in the NQE H2 workflow. Use when a user asks how TST elementary rates enter KMC, how to build event lists, lattice or surface models, adsorption/desorption/hopping/association networks, gas-dust assumptions, temperature/density grids, statistical convergence, or whether KMC outputs can be interpreted as H2 formation rate or efficiency.
---

# KMC H2 Efficiency

Use this skill for the final kinetic Monte Carlo stage that converts elementary step rate constants into grain-scale H2 formation rates and efficiencies.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining what KMC consumes or what CPIHMC outputs.
- Use `ti-tst-rate` when the question concerns rate constants derived from activation free energies.
- Use `nqe-h2-workflow` when the user asks where KMC fits in the full pipeline.

## Roles In This Workflow

- KMC consumes elementary step rate constants derived from TI/TST, not raw CHMC/CPIHMC trajectories or mean-force data.
- KMC evolves a lattice/surface reaction network over long timescales.
- KMC outputs H2 formation rate, formation efficiency, coverage statistics, and rate-limiting behavior when the event network and simulation assumptions are complete.

## What This Skill May Do

- Explain why a single elementary rate is insufficient for full H2 formation efficiency.
- Help inspect an event list for missing adsorption, desorption, hopping, and association steps.
- Help inspect whether rate constants are labelled by elementary step, temperature, density/environment assumption, and classical/quantum treatment.
- Explain thermalization versus gas-dust decoupling assumptions when documented by the user.
- Produce TODO lists for missing lattice model, event network, rates, simulation length, trajectory count, and normalization method.
- Help design checks for steady state and statistical convergence once KMC outputs exist.

## What This Skill Must Not Do

- Do not invent event lists, lattice models, adsorption sites, rate constants, temperature/density grids, simulation lengths, trajectory counts, or formation-efficiency definitions.
- Do not claim a meta two-H association rate alone is enough for full KMC.
- Do not claim KMC directly uses CPIHMC mean force or trajectories.
- Do not claim KMC outputs are statistically converged without documented trajectory statistics and steady-state checks.
- Do not decide physical assumptions such as thermalization, gas-dust decoupling, coverage independence, or adiabatic adsorption without user approval.

## Input Checks

- Confirm each elementary rate has an elementary-step label, temperature, units, and classical/quantum label.
- Confirm required elementary steps are present or explicitly TODO: adsorption, desorption, hopping, association channels, and any system-specific events.
- Confirm the lattice/surface model, adsorption sites, boundary conditions, and initial coverage are documented.
- Confirm environmental assumptions are documented, including gas temperature, dust temperature, density grid, and thermalization/adiabatic assumptions if used.
- Confirm simulation length, number of trajectories, random seeds, and normalization method are documented.

## Output Checks

- Check steady-state behavior or justify transient interpretation.
- Check statistical convergence across independent trajectories.
- Check H2 formation event counts and physical time normalization.
- Check coverage statistics and rate-limiting step identification.
- Check uncertainty estimates and sensitivity to missing or uncertain elementary rates.
- Preserve missing-rate TODOs instead of filling them silently.

## References

- Read `references/kmc-checklist.md` for local workflow-specific checks.
- Read repository file `templates/kmc/README.md` for the current placeholder template plan and KMC handoff boundaries.
- Read repository files `docs/overview.md` and `workflow.yaml` for the full workflow context.
