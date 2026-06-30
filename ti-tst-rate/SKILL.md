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

- Thermodynamic integration converts mean force along a reaction coordinate into a free-energy profile F(xi). Mean force is treated as dF/dRC under the user-provided convention.
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

## Postprocessing Logic

- For one CHMC/CPIHMC reaction coordinate, map `MeanForce` to `RxnCoord`. For multiple reaction coordinates, map each `MeanForce_i` column to the corresponding `RxnCoord_i` column; `MeanForce_0` corresponds to the first reaction coordinate.
- Treat multiple mean-force columns as multidimensional free-energy-surface data. Do not collapse them to one dimension unless the user provides a path, projection, or marginalization rule.
- Use atomic units for reaction coordinates and mean forces unless the user documents a conversion.
- Support user-approved prefactor models by elementary step. Use `k_B T / h` only for the original/simple TST prefactor when requested or documented; allow custom prefactors such as hydrogen adsorption `n v S` when the user provides density, mean speed, site area, and units.
- Treat postprocessing scripts as a future execution layer. Until a validated script is provided, this skill should explain table schemas and readiness checks, not claim production execution.

## TI Readiness Checks

- Confirm mean force is available for every required reaction-coordinate window.
- Confirm the RC grid and window ordering are documented.
- Confirm units and sign conventions for mean force and reaction coordinate are documented.
- Confirm uncertainty estimates, block statistics, or convergence diagnostics are available or explicitly TODO.
- Confirm failed or missing CHMC/CPIHMC windows are flagged.

## TST Readiness Checks

- Confirm Delta F dagger has been extracted from the free-energy profile with uncertainty if available.
- Confirm temperature, prefactor model, prefactor units, and unit conversion are documented.
- Confirm whether the rate is classical or quantum/NQE-corrected.
- Confirm recrossing or transmission-coefficient assumptions are documented or TODO.
- Confirm the rate corresponds to a single elementary step and is not the full KMC observable.

## Scripts

- Use `scripts/extract_mean_force.py` to extract one sampling output/window into one row of `mean_force_table.csv`. Use external loops to collect many reaction-coordinate windows. Require `--confirm-parameters` because columns, skip rows, unit scales, and output units can differ between CHMC/CPIHMC runs.
- Use `scripts/integrate_free_energy.py` to integrate a completed `mean_force_table.csv` into `free_energy_profile.csv`. Require `--confirm-parameters` because integration direction, sign convention, zero reference, unit compatibility, and optional `--free-energy-scale`/`--free-energy-unit-label` conversion need user confirmation. Ask for integration direction before invoking the script if the user has not explicitly specified it. Default ordering is `--integration-direction ascending`, from small reaction coordinate to large reaction coordinate; use `descending` when the large-RC side is the initial/reference side. `free_energy_au` always remains atomic units; optional conversion is written to `free_energy_converted`.
- Use `scripts/run_smoke_test.py` only as a bundled demo smoke test for the TI/TST script chain. It is not a production workflow runner.
- Do not use these scripts for temperature-directory discovery, production orchestration, or KMC. Those remain separate layers.

## Script Usage

Use these scripts only for the TI preprocessing and integration layer. They do not compute TST rates, KMC outputs, or plots. Use `scripts/compute_tst_rates.py` only after a free-energy barrier or a validated `free_energy_profile.csv` is available.

### Extract One Mean-Force Row

Use `scripts/extract_mean_force.py` for one sampling output/window. It appends one row to `mean_force_table.csv`. Run it repeatedly, or from an external loop, to collect multiple reaction-coordinate windows.

Example for a `PHY_QUANT` file:

```bash
python scripts/extract_mean_force.py \
  --input path/to/PHY_QUANT \
  --output mean_force_table.csv \
  --dataset-label cpihmc_100K \
  --sample-label rc_0.40 \
  --rc-index 0 \
  --rc-column RxnCoord \
  --force-column MeanForce \
  --skiprows 0 \
  --rc-scale 1.0 \
  --force-scale 1.0 \
  --rc-raw-unit-label au \
  --force-raw-unit-label au \
  --confirm-parameters
```

Confirm before running: RC column, mean-force column, skipped/equilibration rows, raw unit labels, input-to-au scale factors, dataset label, and whether downstream TI should consume the au-scaled columns. For multi-RC output, use explicit columns such as `RxnCoord_0` and `MeanForce_0`.

### Integrate Collected Windows

Use `scripts/integrate_free_energy.py` only after `mean_force_table.csv` contains multiple windows for the same dataset label and reaction-coordinate index. It writes `free_energy_profile.csv`. Before calling `scripts/integrate_free_energy.py`, ask the user whether integration should proceed from small reaction coordinate to large reaction coordinate (`ascending`) or from large reaction coordinate to small reaction coordinate (`descending`).

Example from small RC to large RC, output in atomic units:

```bash
python scripts/integrate_free_energy.py \
  --input mean_force_table.csv \
  --output free_energy_profile.csv \
  --rc-index 0 \
  --integration-direction ascending \
  --zero first \
  --confirm-parameters
```

Example when the larger reaction coordinate is the initial/reference side and the user wants eV:

```bash
python scripts/integrate_free_energy.py \
  --input mean_force_table.csv \
  --output free_energy_profile.csv \
  --rc-index 0 \
  --integration-direction descending \
  --zero first \
  --free-energy-scale 27.211386245988 \
  --free-energy-unit-label eV \
  --confirm-parameters
```

Confirm before running: at least two windows are present, explicit user choice of integration direction (`ascending` or `descending`), sign convention, zero reference, unit compatibility, and output unit conversion. Keep `free_energy_au` in atomic units; if converting, use `free_energy_converted` and `free_energy_converted_unit`. Do not infer the direction from file order alone.

### Compute One TST Rate

Use `scripts/compute_tst_rates.py` to extract one activation free-energy barrier from `free_energy_profile.csv` or use an explicit barrier, then compute one elementary TST rate. It appends one row to `tst_rates.csv`.

Before running this script, remind the user that barrier extraction is a physical state-selection choice, not a purely technical default. Ask the user to confirm:

- which point is the reactant/reference state: `first`, `last`, `min`, a specified RC via `rc`, or an explicit value via `value`
- which point is the transition state: `max`, a specified RC via `rc`, or an explicit value via `value`
- whether the free-energy profile has already been ordered from initial state to final state
- whether the integration direction and zero reference should be checked before rate calculation
- which free-energy column and unit to use, especially `free_energy_au` versus `free_energy_converted`
- temperature, elementary-step identity, prefactor model, prefactor units, and whether the rate is intended for KMC

Default barrier extraction is `--reactant-mode first --ts-mode max`: the first filtered free-energy point is treated as the reactant/reference state and the highest free-energy point is treated as the transition state. Do not present this as automatic physical identification.

Example using a profile, the first point as reactant, the maximum as transition state, and the original/simple `kBT_over_h` prefactor:

    python scripts/compute_tst_rates.py \
      --input free_energy_profile.csv \
      --output tst_rates.csv \
      --elementary-step TODO_USER_APPROVAL_STEP \
      --dataset-label cpihmc_100K \
      --rc-index 0 \
      --temperature 100 \
      --free-energy-unit auto \
      --reactant-mode first \
      --ts-mode max \
      --prefactor-model kBT_over_h \
      --confirm-parameters

Example using a hydrogen adsorption prefactor `n v S`:

    python scripts/compute_tst_rates.py \
      --input free_energy_profile.csv \
      --output tst_rates.csv \
      --elementary-step H_adsorption \
      --dataset-label cpihmc_100K \
      --temperature 100 \
      --reactant-mode first \
      --ts-mode max \
      --prefactor-model adsorption_flux_n_v_S \
      --density TODO_USER_APPROVAL_N \
      --mean-speed TODO_USER_APPROVAL_V \
      --site-area TODO_USER_APPROVAL_S \
      --prefactor-units TODO_USER_APPROVAL_UNITS \
      --confirm-parameters

Confirm before running: elementary-step identity, reactant/reference state, transition-state choice, free-energy unit, temperature, prefactor model, prefactor units, and whether the resulting rate is the correct input for KMC. Default barrier extraction treats the initial state as the first free-energy point and the transition state as the highest free-energy point. After computing or proposing a TST rate, report the selected reactant RC and transition-state RC to the user and ask whether they confirm or need to modify the state selection. If the user wants to modify the initial/final state selection, ask whether the free-energy integration direction and zero reference should be checked first.
### Plot Mean Force And Free Energy

Use `scripts/plot_mean_force.py` to plot `MeanForce` versus reaction coordinate from one or more `mean_force_table.csv` files. Use `scripts/plot_free_energy.py` to plot free energy versus reaction coordinate from one or more `free_energy_profile.csv` files.

Before calling either plotting script, keep the same initial-state and final-state convention used by `integrate_free_energy.py` and `compute_tst_rates.py`. If the user already confirmed `ascending` or `descending` earlier in the task, reuse it. If it has not been confirmed yet, ask before plotting. Do not reverse the x-axis or reorder curves silently.

Example mean-force plot with two curves:

    python scripts/plot_mean_force.py \
      --curve file=mean_force_table.csv,dataset=classical_100K,label=classical,color=black,linestyle=--,marker=o \
      --curve file=mean_force_table.csv,dataset=cpihmc_100K,label=CPIHMC,color=red,linestyle=-,marker=s \
      --rc-order ascending \
      --output mean_force_rc.png \
      --confirm-parameters

Example free-energy plot with two curves:

    python scripts/plot_free_energy.py \
      --curve file=free_energy_profile.csv,dataset=classical_100K,label=classical,color=black,linestyle=--,marker=o \
      --curve file=free_energy_profile.csv,dataset=cpihmc_100K,label=CPIHMC,color=red,linestyle=-,marker=s \
      --rc-order ascending \
      --free-energy-unit-label eV \
      --output free_energy_rc.png \
      --confirm-parameters

Each `--curve` may specify `file`, `dataset`, `label`, `rc_index`, `color`, `linestyle`, `marker`, `linewidth`, and `markersize`. Confirm units, labels, styles, and RC order before plotting.
## Templates

- Use `templates/mean_force_table.csv.template` for the `PHY_QUANT -> mean force table` handoff.
- Use `templates/free_energy_profile.csv.template` for the `mean force -> free energy profile` handoff.
- Use `templates/tst_rates.csv.template` for the `activation free energy -> TST rate` handoff.
- Use `templates/reference-examples/corr-phy-quant-handoff/` as a semi-real column-mapping example from the real CHMC/CPIHMC `PHY_QUANT`; it is not a computed free-energy profile.
- Use `templates/reference-examples/user-tested-ti-tst-chain/` as the bundled small demo and observed-output reference for the user-tested postprocessing chain.

## References

- Read `references/script-parameters.md` when the user asks what script parameters mean, what defaults are assumed, whether indices are 0-based or 1-based, or for the user-tested end-to-end command chain.
- Read `references/postprocessing-logic.md` when connecting `PHY_QUANT`, mean-force tables, TI, and TST rates.
- Read `references/legacy-mc-result-split-plan.md` when migrating the legacy `MC_result.py` plotting/integration script into maintainable postprocessing scripts.
- Read `references/ti-tst-checklist.md` for local workflow-specific checks.
- Read repository files `docs/overview.md`, `workflow.yaml`, and `examples/graphene_meta_50K/README.md` for the documented teaching workflow.
