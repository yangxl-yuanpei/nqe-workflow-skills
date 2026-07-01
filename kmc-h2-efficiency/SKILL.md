---
name: kmc-h2-efficiency
description: Guidance and checks for kinetic Monte Carlo simulation and H2 formation-efficiency postprocessing in the NQE workflow. Use when a user asks how TST elementary rates enter KMC, how to build event lists, lattice or surface models, generic KMC state/event logic, adsorption/desorption/hopping/association networks, gas-dust assumptions, temperature/density grids, statistical convergence, custom observables, or whether KMC outputs can be interpreted as H2 formation rate or efficiency.
---

# KMC And Custom Efficiency Outputs

Use this skill for kinetic Monte Carlo as a general event-based simulation stage. In the H2 workflow, KMC converts elementary step rate constants into grain-scale H2 formation rates and efficiencies, but the KMC logic itself is not limited to H2.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining what KMC consumes or what CPIHMC outputs.
- Use `ti-tst-rate` when the question concerns rate constants derived from activation free energies.
- Use `nqe-h2-workflow` when the user asks where KMC fits in the full pipeline.

## General KMC Logic

- Represent the system as a discrete state model such as a lattice, graph, site list, coverage vector, or other user-approved state representation.
- Define an event network with preconditions, postconditions, and rate constants.
- Select events with probability proportional to their rates and advance the stochastic clock using the total rate.
- Treat observables such as formation efficiency, selectivity, or product rates as user-defined outputs or postprocessing scripts.

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

- Use `../common/scripts/check_workflow_files.py --software kmc --path PATH_TO_KMC_INPUTS` for a minimal static check of KMC event and parameter JSON files. Treat warnings as prompts for human review, not as event-network validation.

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

## Templates

- Use `templates/kmc_events.json.template` for a generic KMC event-list scaffold.
- Use `templates/kmc_parameters.json.template` for the state model, environment, stopping rules, seeds, and observable definitions.
- Use `templates/kmc_output_summary.csv.template` for generic or custom postprocessed outputs.
- Use `templates/reference-examples/generic-rate-network/` as a non-H2-specific example of event-network shape.

## References

- Read `references/kmc-failure-cases.md` when KMC setup, event networks, or output interpretation fails. This placeholder should be expanded with real observed failures before relying on it for diagnosis.

- Read `references/kmc-general-logic.md` when explaining KMC principles, generic event selection, custom observables, and non-H2 use cases.
- Read `references/kmc-checklist.md` for local workflow-specific checks.
- Read `templates/reference-examples/generic-rate-network/README.md` for the current example event-network shape and KMC handoff boundaries.
- Read repository files `README.md`, `docs/quickstart.md`, and `docs/testing.md` for the full workflow context.
