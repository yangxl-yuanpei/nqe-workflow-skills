# TI/TST Checklist

This reference summarizes thermodynamic integration and TST checks for the NQE H2 formation workflow.

## Handoff From CHMC/CPIHMC

Inputs from sampling:

- reaction-coordinate grid
- mean force for each window
- classical or quantum/NQE label for each dataset
- units and sign conventions
- sampling uncertainty or TODO marker
- failed/missing window flags

## Thermodynamic Integration

TI integrates mean force along the reaction coordinate to obtain a free-energy profile. In this workflow, single-RC output maps `MeanForce` to `RxnCoord`; multi-RC output maps `MeanForce_i` to `RxnCoord_i`, with `MeanForce_0` the derivative of free energy with respect to the first reaction coordinate. Reaction coordinates and mean forces are atomic units unless the user documents otherwise.

Before accepting F(xi):

- check smoothness of neighboring windows
- check numerical integration method is documented
- check error propagation or bootstrap/block statistics if available
- check reference zero of free energy is documented
- check classical and quantum profiles use compatible RC definitions
- For high-dimensional scans, check the user has provided a path/projection rule before reducing to a one-dimensional profile

## Activation Free Energy

Delta F dagger should be extracted from the free-energy profile as the difference between transition-state/saddle-region free energy and reactant free energy.

Check:

- reactant reference state is documented
- transition-state location is physically reasonable
- uncertainty is reported or TODO
- comparison between classical and quantum barriers is labelled clearly

## TST Rate Constants

TST converts activation free energy into an elementary rate constant. Use the conceptual form `k(T) = prefactor * exp(-Delta F dagger / k_B T)`. The original/simple TST prefactor can be `k_B T / h`, but prefactors should be customizable by elementary step. For hydrogen adsorption, a documented option is `n v S`, where `n` is hydrogen atom density, `v` is mean hydrogen atom speed, and `S` is average adsorption-site area. Transmission coefficients, recrossing corrections, or other prefactor models require user documentation.

Check:

- temperature is documented
- prefactor model and units are documented
- units are compatible
- elementary step identity is documented
- classical versus quantum/NQE rate label is preserved
- recrossing or transmission coefficient assumptions are documented or TODO

## Handoff To KMC

KMC should receive elementary step rate constants, not mean force or trajectory data.

Before handoff:

- each rate has an elementary-step label
- temperature and environmental assumptions are recorded
- uncertainties or TODOs are preserved
- missing rates for other elementary steps are listed rather than invented
