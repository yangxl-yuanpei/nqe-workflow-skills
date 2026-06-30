# TI/TST Script Parameters

Use this reference when a user asks how to call the TI/TST scripts, what a parameter means, what defaults are assumed, or whether an index starts from 0 or 1.

## Global Conventions

- All script indices are 0-based.
- `--rc-index 0` means the first reaction coordinate.
- For one CHMC/CPIHMC reaction coordinate, the default headers are `RxnCoord` and `MeanForce`.
- For multiple reaction coordinates, `RxnCoord_0` and `MeanForce_0` are the first reaction-coordinate/mean-force pair; `RxnCoord_1` and `MeanForce_1` are the second pair.
- `--rc-col-index 0` and `--force-col-index 0` mean the first numeric table column.
- Atomic units are assumed unless the user provides a conversion or the input file documents another unit.
- `--confirm-parameters` is a required guardrail, not a nuisance flag. Use it only after the user confirms columns, units, scales, ordering, and physical interpretation.
- Use `--print-defaults` or `--help` to inspect current defaults before production-like use.

## extract_mean_force.py

Purpose: read one CHMC/CPIHMC sampling output/window and append one row to `mean_force_table.csv`.

| Parameter | Default | Meaning |
|---|---:|---|
| `--input` | required | One sampling output file, such as `PHY_QUANT` or one window data file. |
| `--output` | `mean_force_table.csv` | CSV file to create or append to. |
| `--format` | `auto` | Parser mode: `auto`, `phy_quant`, or `table`. |
| `--dataset-label` | required | Dataset label, such as `classical_100K` or `cpihmc_100K`. |
| `--sample-label` | empty | Optional window/sample label, such as `rc_0.40`. |
| `--rc-index` | `0` | 0-based reaction-coordinate index. |
| `--rc-column` | `RxnCoord` | Header column for reaction coordinate in `phy_quant` mode. Single-RC CHMC output usually uses `RxnCoord`; multi-RC output uses names such as `RxnCoord_0`. |
| `--force-column` | `MeanForce` | Header column for mean force in `phy_quant` mode. Single-RC CHMC output usually uses `MeanForce`; multi-RC output uses names such as `MeanForce_0`. |
| `--rc-col-index` | none | 0-based numeric column index for reaction coordinate in `table` mode. |
| `--force-col-index` | none | 0-based numeric column index for mean force in `table` mode. Required in `table` mode. |
| `--window-rc` | none | Use a user-provided window reaction coordinate instead of averaging an RC column. |
| `--skiprows` | `0` | Number of data rows to skip after header/comment handling; usually equilibration discard. |
| `--rc-scale` | `1.0` | Multiply `reaction_coordinate_raw` by this factor to produce `reaction_coordinate_au`. Default assumes raw input already atomic units. |
| `--force-scale` | `1.0` | Multiply `mean_force_raw` samples by this factor to produce `mean_force_au`. Default assumes raw input already atomic units. |
| `--uncertainty` | `sem` | Uncertainty estimate: `sem`, `std`, or `none`. Written for both raw and au-scaled force samples. |
| `--rc-raw-unit-label` | `input` | Unit label for `reaction_coordinate_raw`. |
| `--force-raw-unit-label` | `input` | Unit label for `mean_force_raw`. |
| `--notes` | empty | Free-form note preserved in the output CSV. |
| `--confirm-parameters` | false | Required confirmation that columns, units, scales, and skip settings are appropriate. |
| `--print-defaults` | false | Print default assumptions and exit. |

Important notes:

- Use this script once per sampling window. Collect many windows by running it repeatedly from an external loop.
- In `phy_quant` mode with one reaction coordinate, the default column pair is `RxnCoord` and `MeanForce`.
- In `phy_quant` mode with multiple reaction coordinates, `MeanForce_i` should correspond to `RxnCoord_i`; pass explicit names such as `--rc-column RxnCoord_0 --force-column MeanForce_0`.
- If you prefer numeric columns for a file like `Steps KinEng PotEng TotEng dE_dN ElecNum RxnCoord MeanForce`, pass `--format table --rc-col-index 6 --force-col-index 7` to use 0-based numeric columns.
- In `table` mode, text headers are ignored because only numeric rows are parsed; `--skiprows` then skips numeric data rows, not the header.
- In `table` mode, either provide `--rc-col-index` or `--window-rc`; always provide `--force-col-index`.

## integrate_free_energy.py

Purpose: integrate collected mean-force rows into a relative free-energy profile.

| Parameter | Default | Meaning |
|---|---:|---|
| `--input` | required | Collected `mean_force_table.csv`. |
| `--output` | `free_energy_profile.csv` | Output free-energy profile CSV. |
| `--dataset-label` | all labels | Integrate only this dataset label; otherwise process all labels separately. |
| `--rc-index` | `0` | 0-based reaction-coordinate index to integrate. |
| `--method` | `trapezoid` | Numerical integration method. Currently trapezoid only. |
| `--zero` | `first` | Free-energy zero: `first`, `last`, `min`, or `none`. |
| `--free-energy-scale` | `1.0` | Conversion factor applied to `free_energy_converted` only. `free_energy_au` always remains atomic units. |
| `--free-energy-unit-label` | `au` | Unit label for `free_energy_converted`. |
| `--sort` | false | Legacy alias for `--integration-direction ascending`. |
| `--integration-direction` | `ascending` | Window ordering before integration: `ascending`, `descending`, or `input`. |
| `--confirm-parameters` | false | Required confirmation of units, sign convention, direction, and zero reference. |
| `--notes` | empty | Free-form note preserved in the output CSV. |
| `--print-defaults` | false | Print default assumptions and exit. |

Important notes:

- The agent must ask the user to confirm integration direction before production-like use.
- `ascending` means small RC to large RC.
- `descending` means large RC to small RC.
- `--zero first` applies after ordering. In descending mode, the large-RC point becomes the first point.
- `reaction_coordinate_au` and `free_energy_au` remain atomic-unit columns. Unit conversion writes additional values to `free_energy_converted` and labels them with `free_energy_converted_unit`. For Hartree-to-eV conversion, use `--free-energy-scale 27.211386245988 --free-energy-unit-label eV` only after the user confirms the input is in Hartree-compatible atomic units.
- If `ValueError: invalid literal for int() with base 10: 'rc_index'` appears, the input CSV probably contains a repeated header row from manual concatenation. Current script versions skip repeated header rows; older copies require removing duplicated headers or regenerating the table with `extract_mean_force.py` appending to one output file.

## compute_tst_rates.py

Purpose: compute one elementary TST rate from a free-energy profile or explicit activation free energy.

| Parameter | Default | Meaning |
|---|---:|---|
| `--input` | required unless `--deltaF` | Input `free_energy_profile.csv`. |
| `--output` | `tst_rates.csv` | CSV file to create or append to. |
| `--elementary-step` | required | Label for the elementary step. |
| `--dataset-label` | required | Dataset label to select and write. |
| `--rc-index` | `0` | 0-based reaction-coordinate index. |
| `--temperature` | required | Temperature in K. |
| `--free-energy-column` | `free_energy_au` | Free-energy column in the profile CSV. `free_energy_au` is always atomic units; use `free_energy_converted` only with its matching `free_energy_converted_unit`. |
| `--free-energy-unit` | `auto` | Unit of profile values: `auto`, `au`, `hartree`, `eV`, `kJ/mol`, or `kcal/mol`. |
| `--reactant-mode` | `first` | Reactant/reference selection: `first`, `last`, `min`, `rc`, or `value`. |
| `--reactant-rc` | none | Requested reactant RC when `--reactant-mode rc`. |
| `--reactant-value` | none | Explicit reactant free energy when `--reactant-mode value`. |
| `--ts-mode` | `max` | Transition-state selection: `max`, `rc`, or `value`. |
| `--ts-rc` | none | Requested transition-state RC when `--ts-mode rc`. |
| `--ts-value` | none | Explicit transition-state free energy when `--ts-mode value`. |
| `--deltaF` | none | Explicit activation free energy. If set, profile extraction is skipped. |
| `--deltaF-unit` | none | Unit for `--deltaF`; required with `--deltaF`. |
| `--prefactor-model` | `kBT_over_h` | Prefactor model: `kBT_over_h`, `custom_numeric`, or `adsorption_flux_n_v_S`. |
| `--prefactor-value` | none | Numeric prefactor for `custom_numeric`. |
| `--prefactor-units` | `s^-1` | Prefactor and rate unit label. |
| `--density` | none | `n` for `adsorption_flux_n_v_S`. |
| `--mean-speed` | none | `v` for `adsorption_flux_n_v_S`. |
| `--site-area` | none | `S` for `adsorption_flux_n_v_S`. |
| `--notes` | empty | Free-form note preserved in the output CSV. |
| `--confirm-parameters` | false | Required confirmation of barrier extraction, units, prefactor model, and rate meaning. |
| `--print-defaults` | false | Print default assumptions and exit. |

Important notes:

- Barrier extraction is `Delta F dagger = F_TS - F_reactant`.
- Default barrier selection is reactant = first free-energy point and transition state = maximum free-energy point.
- `--reactant-mode first` selects the first filtered row; `last` selects the last row; `min` selects the lowest free-energy row; `rc` selects the row closest to `--reactant-rc`; `value` uses `--reactant-value` directly.
- `--ts-mode max` selects the highest free-energy row; `rc` selects the row closest to `--ts-rc`; `value` uses `--ts-value` directly.
- Before running the script, the agent must remind the user to confirm reactant/reference state, transition-state choice, free-energy column/unit, integration direction, zero reference, temperature, prefactor model, and prefactor units.
- After running or proposing the command, report the selected reactant RC and transition-state RC to the user for confirmation.
- If the user rejects the selected states, ask whether the integration direction and zero reference should be checked first.
- Use `kBT_over_h` only as the original/simple TST prefactor when appropriate. Use custom prefactors per elementary step when the user provides a documented model and units.

## plot_mean_force.py

Purpose: plot one or more mean-force curves from `mean_force_table.csv` files.

| Parameter | Default | Meaning |
|---|---:|---|
| `--curve` | required, repeatable | Curve spec: `file=...,dataset=...,label=...,rc_index=0,color=...,linestyle=...,marker=...`. |
| `--output` | required | Output image path. |
| `--rc-order` | `ascending` | Plot order: `ascending`, `descending`, or `input`. Keep consistent with integration/TST convention. |
| `--xlabel` | `Reaction coordinate (au)` | X-axis label. |
| `--ylabel` | empty | Y-axis label override. |
| `--title` | empty | Plot title. |
| `--xlim` | none | X-axis limits as two numbers. |
| `--ylim` | none | Y-axis limits as two numbers. |
| `--width` | `6.0` | Figure width in inches. |
| `--height` | `4.0` | Figure height in inches. |
| `--dpi` | `300` | Figure resolution. |
| `--linewidth` | `2.0` | Default line width. |
| `--markersize` | `5.0` | Default marker size. |
| `--grid` | false | Show grid. |
| `--confirm-parameters` | false | Required confirmation of direction, units, datasets, and styles. |
| `--y-column` | `mean_force_au` | Column to plot on the y-axis. |

Curve-spec notes:

- `file` and `dataset` are required inside every `--curve`.
- `rc_index` inside `--curve` is 0-based and defaults to `0`.
- Style keys include `label`, `color`, `linestyle`, `marker`, `linewidth`, and `markersize`.

## plot_free_energy.py

Purpose: plot one or more free-energy curves from `free_energy_profile.csv` files.

| Parameter | Default | Meaning |
|---|---:|---|
| `--curve` | required, repeatable | Curve spec: `file=...,dataset=...,label=...,rc_index=0,color=...,linestyle=...,marker=...`. |
| `--output` | required | Output image path. |
| `--rc-order` | `ascending` | Plot order: `ascending`, `descending`, or `input`. Keep consistent with integration/TST convention. |
| `--xlabel` | `Reaction coordinate (au)` | X-axis label. |
| `--ylabel` | empty | Y-axis label override. |
| `--title` | empty | Plot title. |
| `--xlim` | none | X-axis limits as two numbers. |
| `--ylim` | none | Y-axis limits as two numbers. |
| `--width` | `6.0` | Figure width in inches. |
| `--height` | `4.0` | Figure height in inches. |
| `--dpi` | `300` | Figure resolution. |
| `--linewidth` | `2.0` | Default line width. |
| `--markersize` | `5.0` | Default marker size. |
| `--grid` | false | Show grid. |
| `--confirm-parameters` | false | Required confirmation of direction, units, datasets, and styles. |
| `--y-column` | `free_energy_au` | Column to plot on the y-axis. |
| `--free-energy-unit-label` | empty | Optional y-axis unit label, such as `eV` or `au`. |

Important notes:

- Plot from initial state to final state using the same convention confirmed during integration and TST.
- Do not reverse or reinterpret the x-axis silently.
- When plotting converted free energies, make sure `--y-column` and `--free-energy-unit-label` describe the same data.
