---
name: ti-tst-rate
description: Guidance and checks for converting CHMC/CPIHMC mean-force data into free-energy profiles, activation free energies, and TST elementary rate constants in the NQE H2 formation workflow. Use when a user asks about thermodynamic integration, Delta F dagger, classical versus quantum free-energy profiles, TST rate constants, NQE enhancement factors, or handoff from mean-force sampling to KMC rates.
---

# TI/TST Rate

Use this skill for the thermodynamic-integration and transition-state-theory stages after CHMC/CPIHMC mean-force sampling.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining what CPIHMC outputs or what KMC consumes.
- Use `chmc-cpihmc-sampling` when the question concerns whether mean-force data are ready for integration.
- Use `kmc-h2-efficiency` when the question concerns how elementary rates enter the KMC model.
- Use `nqe-h2-workflow` when the user asks where TI/TST fits in the full pipeline.

## Roles In This Workflow

- Thermodynamic integration converts mean force along a reaction coordinate into a free-energy profile F(xi).
- Activation free energy Delta F dagger is extracted from the free-energy profile.
- TST converts Delta F dagger into elementary step rate constants k(T).
- KMC consumes elementary rate constants, not raw CHMC/CPIHMC trajectories or mean-force files.

## What This Skill May Do

- Explain how CHMC and CPIHMC mean forces become classical and quantum free-energy profiles.
- Check whether mean-force data are complete enough for TI.
- Explain the TST formula conceptually and identify required inputs.
- Compare classical and quantum activation free energies or rate constants when provided by the user.
- Compute or outline calculations only when all required numerical inputs, units, and sign conventions are provided.
- Produce TODO lists for missing RC grid, integration method, uncertainty estimates, temperature, or recrossing assumptions.

## What This Skill Must Not Do

- Do not invent mean-force values, reaction-coordinate grids, integration methods, uncertainties, activation barriers, temperatures, or rate constants.
- Do not assume the quantum barrier must be lower in every possible case without checking the documented system and data.
- Do not claim TST rates are final H2 formation efficiency; KMC is still required for the grain-scale observable.
- Do not ignore recrossing, variational TST, transmission coefficient, or other limitations when the user asks about rate accuracy.
- Do not pass incomplete or unlabelled mean-force data to KMC.

## TI Readiness Checks

- Confirm mean force is available for every required reaction-coordinate window.
- Confirm the RC grid and window ordering are documented.
- Confirm units and sign conventions for mean force and reaction coordinate are documented.
- Confirm uncertainty estimates, block statistics, or convergence diagnostics are available or explicitly TODO.
- Confirm failed or missing CHMC/CPIHMC windows are flagged.

## TST Readiness Checks

- Confirm Delta F dagger has been extracted from the free-energy profile with uncertainty if available.
- Confirm temperature and unit conversion are documented.
- Confirm whether the rate is classical or quantum/NQE-corrected.
- Confirm recrossing or transmission-coefficient assumptions are documented or TODO.
- Confirm the rate corresponds to a single elementary step and is not the full KMC observable.

## References

- Read `references/ti-tst-checklist.md` for local workflow-specific checks.
- Read repository files `docs/overview.md`, `workflow.yaml`, and `examples/graphene_meta_50K/README.md` for the documented teaching workflow.
