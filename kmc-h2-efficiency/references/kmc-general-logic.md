# General KMC Logic

Use this reference when explaining KMC as a general event-based simulation method. Do not limit KMC to H2 formation unless the user explicitly asks for that case.

## Basic Principle

Kinetic Monte Carlo evolves a discrete state by repeatedly selecting one allowed event according to its rate constant and advancing the simulation clock. The event network, state representation, rate constants, and observable definitions determine what KMC means for a specific problem.

## Required Inputs

- State model: lattice, graph, sites, species, coverages, or any other discrete representation.
- Event list: allowed transitions, preconditions, postconditions, and rate constants.
- Environment: temperature, pressure/density, boundary conditions, reservoirs, or external fields when relevant.
- Simulation controls: stopping rule, random seeds, number of trajectories, output interval, and convergence criteria.
- Observable definitions: what to count, how to normalize, and how to postprocess.

## Event Selection Logic

For a state with event rates `k_i`, compute `K_total = sum_i k_i`. Select event `i` with probability `k_i / K_total`. Advance time using the standard stochastic waiting-time relation, usually `dt = -ln(u) / K_total` for uniform random number `u`.

## Inputs From TI/TST

TI/TST usually supplies elementary rate constants. KMC should not directly consume `PHY_QUANT`, CHMC/CPIHMC trajectories, or free-energy profiles unless a postprocessing layer has converted them into event rates.

## Outputs

Common KMC outputs include event counts, simulated physical time, coverage/state histories, product formation rates, selectivity/efficiency metrics, uncertainty across trajectories, and sensitivity to rate constants. The exact output schema should be user-defined or handled by a dedicated postprocessing script.

## Generality Boundary

This skill may explain KMC logic, validate event tables, and prepare generic templates. It must not invent a system-specific lattice, event network, or efficiency formula. For special cases such as H2 formation, keep custom observables in a separate output/postprocessing layer.
