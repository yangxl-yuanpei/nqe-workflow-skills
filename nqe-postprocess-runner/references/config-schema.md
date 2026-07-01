# Config Schema

Use a flat YAML or JSON config. Paths are resolved relative to the config file.

A runnable config must contain only user-confirmed values. When creating a new config, ask about each parameter before writing it to YAML. If a value is not yet confirmed, use a question checklist or a non-runnable draft with `parameters_confirmed: false` and `TODO_USER_APPROVAL` placeholders.

Required guardrail:

- `parameters_confirmed`: must be `true`.
- Set `parameters_confirmed: true` only after every included parameter has been explicitly approved by the user or copied from a user-provided config.
- Use `parameters_confirmed: false` for drafts, examples, or partially filled configs.

Before outputting a runnable YAML and before setting `parameters_confirmed: true`, the user must confirm every applicable parameter:

- input window directory and window discovery pattern
- input file name and parser mode
- reaction-coordinate and mean-force columns or numeric indices
- whether indices are zero-based
- unit labels and scale factors for reaction coordinate and mean force
- equilibration/skip-row handling
- integration direction and free-energy zero reference
- free-energy conversion factor and unit label, if used
- whether plots should be generated
- whether TST should be computed
- elementary-step label, temperature, reactant state, transition-state selection, and prefactor model when TST is enabled

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
- `free_energy_plot_unit_label`: optional y-axis unit label for the free-energy plot. Default: `au`.

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
- CLI `--dry-run`: print generated child commands without executing them. Use this first for smoke testing and config review.

Agent execution rule:

1. Read this schema and the config file.
2. When creating YAML, ask for every parameter before writing a runnable config; otherwise write only a non-runnable draft with `parameters_confirmed: false`.
3. Refuse real execution if required fields are missing or `parameters_confirmed` is not true.
4. Run the runner with `--dry-run` first.
5. Ask for user confirmation if the dry-run commands reveal unexpected paths, units, ordering, state selection, temperature, or prefactor.
6. Run without `--dry-run` only after the dry-run is accepted.
