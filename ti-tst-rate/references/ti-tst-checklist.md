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

TI integrates mean force along the reaction coordinate to obtain a free-energy profile.

Before accepting F(xi):

- check smoothness of neighboring windows
- check numerical integration method is documented
- check error propagation or bootstrap/block statistics if available
- check reference zero of free energy is documented
- check classical and quantum profiles use compatible RC definitions

## Activation Free Energy

Delta F dagger should be extracted from the free-energy profile as the difference between transition-state/saddle-region free energy and reactant free energy.

Check:

- reactant reference state is documented
- transition-state location is physically reasonable
- uncertainty is reported or TODO
- comparison between classical and quantum barriers is labelled clearly

## TST Rate Constants

TST converts activation free energy into an elementary rate constant. The teaching workflow uses the conceptual form k(T) = (k_B T / h) exp(-Delta F dagger / k_B T), with special handling for adsorption prefactors only when documented by the user.

Check:

- temperature is documented
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
