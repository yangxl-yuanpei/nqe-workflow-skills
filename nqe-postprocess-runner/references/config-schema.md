# Config Schema

Use a flat YAML or JSON config. Paths are resolved relative to the config file.

Required guardrail:

- `parameters_confirmed`: must be `true`.

Window discovery:

- `sampling_output_root`: directory containing reaction-coordinate window subdirectories.
- `input_file`: file name inside each window directory. Default: `energy.dat`.
- `window_glob`: direct-child glob for window directories. Default: `*`.
- `dataset_label`: label written to output CSVs.
- `output_dir`: output directory. Default: `nqe-postprocess-output`.

Mean-force extraction:

- `format`: `auto`, `phy_quant`, or `table`. Default: `auto`.
- `rc_index`: reaction-coordinate index. Default: `0`.
- `rc_column`, `force_column`: header names for `phy_quant`/headered data.
- `rc_col_index`, `force_col_index`: zero-based numeric columns for `table` data.
- `skiprows`: numeric rows to discard after header/comment handling.
- `rc_scale`, `force_scale`: raw-to-atomic-unit conversion factors.
- `rc_raw_unit_label`, `force_raw_unit_label`: raw unit labels preserved in CSV.
- `uncertainty`: `sem`, `std`, or `none`. Default: `sem`.

Thermodynamic integration:

- `integration_direction`: required; use `ascending`, `descending`, or `input`.
- `zero`: `first`, `last`, `min`, or `none`. Default: `first`.
- `free_energy_scale`: conversion factor for `free_energy_converted`.
- `free_energy_unit_label`: label for converted free energy.

Plotting:

- `plots`: `true` or `false`. Default: `true`.

TST:

- `compute_tst`: `true` or `false`. Default: `true`.
- `elementary_step`: required when `compute_tst` is true.
- `temperature_K`: required when `compute_tst` is true.
- `reactant_mode`: `first`, `last`, `min`, `rc`, or `value`.
- `ts_mode`: `max`, `rc`, or `value`.
- `reactant_rc`, `ts_rc`, `reactant_value`, `ts_value`: required only for matching state-selection modes.
- `free_energy_column`: default `free_energy_au`.
- `free_energy_unit`: default `auto`.
- `prefactor_model`: `kBT_over_h`, `custom_numeric`, or `adsorption_flux_n_v_S`.
- `prefactor_value`, `prefactor_units`, `density`, `mean_speed`, `site_area`: required only for matching prefactor models.

Optional:

- `python`: Python executable used for child scripts. Default: current interpreter.
- `ti_tst_scripts_dir`: override path to `ti-tst-rate/scripts`.
- `notes`: text added to generated CSV rows.
