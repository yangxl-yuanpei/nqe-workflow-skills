# TI/TST Postprocessing Logic

Use this reference when connecting CHMC/CPIHMC `PHY_QUANT` output to thermodynamic integration and TST rate tables. This file explains the data logic only; deterministic execution should be handled by a separate postprocessing script when the user provides one.

## PHY_QUANT To Mean Force

- The number of `MeanForce_*` columns should match the number of reaction-coordinate columns.
- For one reaction coordinate, `MeanForce` corresponds to `RxnCoord`. For multiple reaction coordinates, `MeanForce_0` corresponds to `RxnCoord_0`, `MeanForce_1` corresponds to `RxnCoord_1`, and so on.
- Multiple mean-force columns indicate a multidimensional free-energy surface scan. A single reaction coordinate and one mean-force column are sufficient for ordinary one-dimensional TI.
- Mean force is the derivative of free energy with respect to the corresponding reaction coordinate: `MeanForce_i = dF / dRC_i` under the workflow convention provided by the user.
- The sign follows the derivative sign: if the reaction coordinate increases and mean force is positive, the free energy increases along that coordinate; if mean force is negative, it decreases.
- Reaction coordinates and mean forces are in atomic units unless the user documents a conversion.

## One-Dimensional TI

For one-dimensional TI, collect one mean-force value per window:

```text
reaction_coordinate_raw, mean_force_raw, uncertainty_raw, reaction_coordinate_au, mean_force_au, uncertainty_au, source
```

Then integrate the mean force along the ordered reaction-coordinate grid to obtain a relative free-energy profile. The zero of free energy must be chosen and documented. `reaction_coordinate_au` and `free_energy_au` remain atomic-unit columns. If the user wants eV, write the converted values to a separate column such as `free_energy_converted` using Hartree-to-eV scale `27.211386245988` and label `free_energy_converted_unit = eV`. Do not integrate if window ordering, units, sign convention, equilibration discard, unit conversion, or uncertainty treatment is missing.

## Integration Direction

Default to integrating from smaller reaction coordinate to larger reaction coordinate only after the user confirms this is the intended direction. If the larger reaction coordinate corresponds to the initial/reference state, use a descending integration direction and document that choice. Do not call the integration script until the user confirms the direction (`ascending` or `descending`). The zero-reference option is applied after ordering; for example, `zero=first` means the first point in the chosen integration direction.

## Multidimensional Free-Energy Surface

For multiple reaction coordinates, treat `MeanForce_i` as the free-energy derivative along dimension `i`. Do not collapse multidimensional data to one dimension unless the projection, path, or marginalization rule is explicitly provided.

## TST Rate

Use a TST-like rate expression only when the user has provided the activation free energy, temperature, and prefactor model:

```text
k(T) = prefactor * exp(-DeltaF_dagger / (k_B T))
```

The original/simple TST prefactor can be `k_B T / h`, but the prefactor must be customizable by elementary step. For example, a hydrogen adsorption step may use `n v S`, where `n` is hydrogen atom density, `v` is mean hydrogen atom speed, and `S` is average adsorption-site area. Preserve whether `DeltaF_dagger` came from classical CHMC or NQE-inclusive CPIHMC. Do not add tunneling corrections, transmission coefficients, adsorption prefactors, or recrossing corrections unless the user provides the model and units.

## Default Barrier Selection

By default, treat the initial/reactant state as the first point in the free-energy profile and the transition state as the highest free-energy point. Always report the selected reactant reaction coordinate and transition-state reaction coordinate to the user for confirmation. If the user wants to change these states, ask whether the free-energy integration direction, initial/final-state convention, and zero reference should be checked before recomputing the rate.

## TST Rate Script

Use `scripts/compute_tst_rates.py` only after a free-energy profile or explicit activation free energy is available. Require the user to confirm reactant/reference state, transition-state selection, free-energy column and units, integration direction, zero reference, temperature, prefactor model, and prefactor units before running. The script computes one elementary-step rate per call and appends to `tst_rates.csv`. Default `reactant-mode first` and `ts-mode max` are script conventions only; they are not automatic physical identification of the reactant and transition state.

## Prefactor Models

Supported teaching categories:

- `kBT_over_h`: original/simple TST prefactor, computed from temperature.
- `custom_numeric`: user provides a numeric prefactor and units.
- `adsorption_flux_n_v_S`: user provides hydrogen atom density `n`, mean speed `v`, and average adsorption-site area `S`; the prefactor is `n v S`.

Require unit consistency before computing any rate. Do not treat the adsorption example as a universal prefactor for all elementary steps.

## Script Boundary

This skill may explain required columns and produce table scaffolds. It should not claim to execute production postprocessing until a validated script/notebook is provided and its assumptions are documented.

## Plotting Direction Consistency

Plotting scripts must preserve the same initial-to-final reaction-coordinate direction confirmed for integration and TST barrier selection. If direction was previously confirmed in the current task, reuse it. If not, ask before plotting. Multiple curves may be drawn on the same figure, but all curves in one plot should use the same direction convention unless the user explicitly requests otherwise.
