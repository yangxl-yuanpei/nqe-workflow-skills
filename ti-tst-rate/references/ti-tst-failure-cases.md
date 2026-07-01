# TI/TST Failure Cases

Use this reference when TI/TST postprocessing scripts fail, reject inputs, or produce surprising state selections. These cases are diagnostic patterns, not proof that a free-energy profile or rate is physically valid after the immediate issue is fixed.

Keep the stage boundary clear:

- CHMC/CPIHMC produces sampled reaction-coordinate and mean-force data.
- Thermodynamic integration converts user-approved mean-force tables into relative free-energy profiles.
- TST converts an activation free energy plus a user-approved prefactor model into one elementary-step rate.
- KMC consumes elementary rates. TI/TST scripts do not produce full H2 formation efficiency or any other KMC observable.
- Any fix involving reaction-coordinate definition, equilibration discard, integration direction, free-energy zero, transition-state selection, temperature, prefactor, or KMC handoff requires user approval.

## Mean-Force Extraction Uses The Wrong Columns

Typical symptoms:

- `extract_mean_force.py` reports a missing `RxnCoord`, `MeanForce`, `RxnCoord_0`, or `MeanForce_0` column.
- The file has numeric columns, but the command passes `--rc-col-index` and `--force-col-index` without `--format table`.
- A single-RC file uses `RxnCoord` and `MeanForce`, while the command requests multi-RC names such as `RxnCoord_0` and `MeanForce_0`.
- A multi-RC file is reduced to one dimension without a documented path, projection, or marginalization rule.

Likely causes:

- Header-name mode and numeric-column mode were mixed.
- Single-RC and multi-RC CHMC/CPIHMC conventions were confused.
- The wrong reaction-coordinate/mean-force pair was selected.
- A command copied from the smoke-test chain was reused without confirming this target file's header.

Agent response:

1. Inspect the input header and list available `RxnCoord*` and `MeanForce*` columns.
2. For single-RC output, map `MeanForce` to `RxnCoord`.
3. For multi-RC output, map `MeanForce_i` to `RxnCoord_i`.
4. If numeric columns are intended, require `--format table` and confirm 0-based column indices.
5. Do not collapse multidimensional mean-force data to 1D TI unless the user provides the path, projection, or marginalization rule.

Useful command shape for numeric-column mode:

```bash
python ti-tst-rate/scripts/extract_mean_force.py \
  --input energy.dat \
  --output mean_force_table.csv \
  --dataset-label USER_CONFIRMED_LABEL \
  --format table \
  --rc-col-index USER_CONFIRMED_0_BASED_INDEX \
  --force-col-index USER_CONFIRMED_0_BASED_INDEX \
  --confirm-parameters
```

## Mean-Force Table Has Too Few Or Mismatched Windows

Typical symptoms:

- `integrate_free_energy.py` reports `Need at least two windows to integrate`.
- `integrate_free_energy.py` reports that no rows matched the requested dataset label and reaction-coordinate index.
- The mean-force table contains multiple dataset labels or `rc_index` values, but the command filters the wrong one.
- Neighboring windows are missing or duplicated, causing gaps in the free-energy profile.

Likely causes:

- Only one CHMC/CPIHMC window has been extracted.
- Some failed windows were not rerun but were still expected in the integration grid.
- The user changed `dataset_label` or `rc_index` across extraction commands.
- Manual CSV editing or concatenation introduced inconsistent labels.

Agent response:

1. Count rows by `dataset_label` and `rc_index`.
2. Check that the intended reaction-coordinate grid has at least two valid windows.
3. Ask the user whether missing windows should be rerun, excluded with a documented reason, or left as TODO.
4. Do not interpolate, duplicate, or fabricate missing mean-force windows.
5. Do not continue to TST if the free-energy profile does not represent the user-approved grid.

## Repeated Headers Or Old Mean-Force Table Schema

Typical symptoms:

- `integrate_free_energy.py` reports an invalid integer such as `invalid literal for int() with base 10: 'rc_index'`.
- Appending with `extract_mean_force.py` fails because an existing CSV schema does not match the current script schema.
- A table created by an older script lacks raw columns, scale columns, or `parameters_confirmed`.
- The same CSV contains repeated header rows from manual concatenation.

Likely causes:

- Multiple single-window CSV files were concatenated with headers intact.
- A current script is appending to an old-format table.
- The user manually edited a CSV and changed column names or ordering.

Agent response:

1. Inspect the CSV header and look for repeated header rows in the body.
2. Prefer regenerating the mean-force table by appending all windows with the current `extract_mean_force.py`.
3. If a repeated-header row is skipped by the current script, still report it as a data-hygiene issue.
4. Do not silently merge old and new schemas.
5. Preserve raw source files so the table can be regenerated.

## Unit Conversion Is Applied To The Wrong Column

Typical symptoms:

- The user expects `free_energy_au` to be in eV after passing `--free-energy-scale`.
- Downstream TST reads `free_energy_au` while the user intended `free_energy_converted`.
- A plot label says eV, but the plotted column is `free_energy_au`.
- A rate changes by orders of magnitude because the selected free-energy unit does not match the selected column.

Likely causes:

- `free_energy_au` and `free_energy_converted` were confused.
- The Hartree-to-eV scale was copied without confirming atomic-unit compatibility.
- A plotting or TST command selected a converted column but left the unit at `auto` or `au`.

Agent response:

1. State that `free_energy_au` remains atomic units.
2. State that `--free-energy-scale` writes converted values to `free_energy_converted`.
3. For TST, ask whether to read `free_energy_au` as `au` or `free_energy_converted` with its matching `free_energy_converted_unit`.
4. For plotting, require `--y-column` and the displayed unit label to describe the same column.
5. Do not overwrite atomic-unit columns with converted values.

## Integration Direction Or Free-Energy Zero Is Wrong

Typical symptoms:

- The profile is integrated from small RC to large RC, but the user says the large-RC side is the initial/reference state.
- `--zero first` is used without realizing that "first" is applied after ordering.
- A profile looks reversed relative to the intended initial-to-final direction.
- TST uses the first point as reactant even though the first point is not the physical reactant under the chosen ordering.

Likely causes:

- The agent used the default `ascending` direction without asking.
- A command copied from a demo used `descending`, but the current system requires `ascending`, or the reverse.
- The free-energy zero was chosen as a plotting convenience and then reused as a state definition.

Agent response:

1. Ask the user to confirm `ascending`, `descending`, or `input` before production-like integration.
2. Explain that `ascending` means small RC to large RC and `descending` means large RC to small RC.
3. Explain that `zero=first`, `zero=last`, and `zero=min` are applied after ordering.
4. If state selection seems wrong, check integration direction and zero reference before recomputing a TST rate.
5. Do not infer the physical initial state from directory order or CSV order alone.

## Mean-Force Sign Convention Is Ambiguous

Typical symptoms:

- The integrated free-energy profile has the opposite slope from the user's expectation.
- Classical and CPIHMC profiles use opposite apparent signs.
- The user asks the agent to "flip the force sign" to make a barrier positive.
- The source code or workflow notes define mean force differently from `dF/dRC`.

Likely causes:

- The sampled quantity may be force, negative gradient, constraint force, or an already sign-adjusted derivative.
- A legacy plotting/integration script used the opposite sign convention.
- Mean-force columns from different sources were combined without documenting convention.

Agent response:

1. Ask the user to confirm whether the column is `dF/dRC` under this workflow convention.
2. Compare against documented workflow notes, not against the desired barrier shape.
3. Reintegrate only after the user approves the sign convention.
4. Record the sign convention in notes or config.
5. Do not flip signs just to obtain a positive activation barrier.

## TST Barrier Selection Gives A Negative Or Surprising Barrier

Typical symptoms:

- `compute_tst_rates.py` raises `Computed activation free energy is negative`.
- The default `--reactant-mode first --ts-mode max` selects a reactant or transition state the user does not accept.
- The selected transition-state RC is at an endpoint rather than a saddle-like region.
- The script prints selected reactant and transition-state RC values that do not match the intended elementary step.

Likely causes:

- The free-energy profile is ordered in the wrong direction.
- The reactant/reference state was not the first filtered row.
- The transition state is not simply the maximum point on the filtered 1D profile.
- The wrong dataset label, `rc_index`, or free-energy column was selected.

Agent response:

1. Report the selected reactant RC and transition-state RC.
2. Ask the user to confirm or revise `reactant-mode`, `reactant-rc`, `ts-mode`, or `ts-rc`.
3. If the selected states are wrong, ask whether integration direction and zero reference should be checked first.
4. Confirm the elementary-step identity before treating the barrier as a rate input.
5. Do not treat script defaults as automatic physical state identification.

## TST Prefactor Or Temperature Is Missing Or Incompatible

Typical symptoms:

- `compute_tst_rates.py` refuses to run without `--temperature`.
- `custom_numeric` is selected without `--prefactor-value`.
- `adsorption_flux_n_v_S` is selected without density, mean speed, or site area.
- The rate unit label does not match the prefactor model or supplied inputs.

Likely causes:

- The user has a free-energy barrier but has not approved a TST prefactor model.
- `kBT_over_h` was assumed when a step-specific prefactor is required.
- Adsorption-flux inputs were copied from another system without unit review.
- Temperature or environmental assumptions were not tied to the sampled dataset.

Agent response:

1. Ask for temperature and its relationship to the sampled dataset.
2. Ask the user to choose and document the prefactor model.
3. For `custom_numeric`, require value and units.
4. For `adsorption_flux_n_v_S`, require density, mean speed, site area, and unit consistency.
5. Do not compute or invent a prefactor from an unrelated reference example.

## Classical And CPIHMC Profiles Are Compared Without Compatible Metadata

Typical symptoms:

- Classical and CPIHMC curves are plotted together but use different RC definitions, directions, or units.
- NQE enhancement is computed from two rates without matching elementary-step labels.
- A CPIHMC profile is assumed to have a lower barrier without inspecting data.
- Classical and quantum datasets have different missing-window patterns.

Likely causes:

- Dataset labels were treated as cosmetic rather than provenance.
- Different equilibration discard, sign convention, or integration direction was used for each dataset.
- A comparison was made before both profiles had complete and compatible metadata.

Agent response:

1. Compare RC definitions, units, sign conventions, window grids, and integration direction.
2. Check that elementary-step labels and state selections match before comparing TST rates.
3. Preserve classical versus CPIHMC provenance in output tables.
4. List missing metadata as TODOs instead of forcing a comparison.
5. Do not assume the NQE-inclusive barrier is lower unless the confirmed data show that.

## Plot Direction Or Axis Label Does Not Match The Analysis

Typical symptoms:

- `plot_mean_force.py` or `plot_free_energy.py` uses `--rc-order ascending` while integration used descending.
- The free-energy plot axis says eV but the y-column is `free_energy_au`.
- Curves from different datasets are visually compared with different RC order conventions.
- The user wants the axis reversed for appearance without documenting the analysis convention.

Likely causes:

- Plotting was treated as cosmetic rather than part of the analysis record.
- The plotting command was written independently of the integration/TST command.
- The wrong `--y-column` or unit label was selected.

Agent response:

1. Reuse the same RC order convention confirmed for integration and TST.
2. Confirm `--y-column` and y-axis unit label together.
3. Label dataset, method, and units explicitly.
4. If the plot is for presentation and uses a reversed axis, document that it is a display choice.
5. Do not let plotting order silently redefine the physical initial or final state.

## Rate Table Is Handed To KMC Without Event-Network Context

Typical symptoms:

- The user asks to treat one TST rate as final H2 formation efficiency.
- A `tst_rates.csv` row lacks a clear elementary-step label.
- KMC state definitions, event preconditions, reverse events, or output metrics are missing.
- Rates from different temperatures or environments are combined in one KMC table.

Likely causes:

- The TI/TST-to-KMC boundary was skipped.
- TST rate constants were mistaken for grain-scale observables.
- The event network has not been defined or checked.

Agent response:

1. State that a TST rate is one elementary-step rate constant, not the KMC observable.
2. Ask for KMC states, event network, rate table, temperature/environment labels, stopping rule, trajectory count, and output metrics.
3. Route event-network validation to `kmc-h2-efficiency`.
4. Preserve missing rates as TODOs.
5. Do not infer adsorption, desorption, hopping, or association rates from a single TI/TST calculation.

## How These Cases Connect To Scripts

Use `extract_mean_force.py` only after columns, units, scales, and equilibration discard are confirmed:

```bash
python ti-tst-rate/scripts/extract_mean_force.py \
  --input PATH_TO_PHY_QUANT_OR_ENERGY_DAT \
  --output mean_force_table.csv \
  --dataset-label USER_CONFIRMED_LABEL \
  --confirm-parameters
```

Use `integrate_free_energy.py` only after a complete multi-window table, unit compatibility, sign convention, ordering, and zero reference are confirmed:

```bash
python ti-tst-rate/scripts/integrate_free_energy.py \
  --input mean_force_table.csv \
  --output free_energy_profile.csv \
  --integration-direction USER_CONFIRMED_DIRECTION \
  --zero USER_CONFIRMED_ZERO \
  --confirm-parameters
```

Use `compute_tst_rates.py` only after the reactant/reference state, transition state, free-energy unit, temperature, prefactor model, and elementary-step identity are confirmed:

```bash
python ti-tst-rate/scripts/compute_tst_rates.py \
  --input free_energy_profile.csv \
  --output tst_rates.csv \
  --elementary-step USER_CONFIRMED_STEP \
  --dataset-label USER_CONFIRMED_LABEL \
  --temperature USER_CONFIRMED_TEMPERATURE \
  --confirm-parameters
```

All script outputs remain diagnostics or deterministic postprocessing products. They do not prove sampling convergence, barrier correctness, prefactor validity, or KMC readiness.
