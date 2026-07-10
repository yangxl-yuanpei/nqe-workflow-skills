# Config Schema

Use a flat YAML or JSON config. Paths are resolved relative to the config file.

A runnable config must contain only user-confirmed values. When creating a new config, ask about each parameter before writing it to YAML. If a value is not yet confirmed, use a question checklist or a non-runnable draft with `parameters_confirmed: false` and `TODO_USER_APPROVAL` placeholders.

Required guardrail:

- `parameters_confirmed`: must be `true`.
- Set `parameters_confirmed: true` only after every included parameter has been explicitly approved by the user or copied from a user-provided config.
- Use `parameters_confirmed: false` for drafts, examples, or partially filled configs.
- `parameters_confirmed: true` is necessary but not sufficient. The runner also refuses runnable configs that still rely on implicit parser, column, unit, integration, state-selection, temperature, or prefactor defaults.

Before outputting a runnable YAML and before setting `parameters_confirmed: true`, the user must confirm every applicable parameter:

- input window directory and window discovery pattern
- input file name, window discovery pattern, and parser mode
- reaction-coordinate and mean-force columns or numeric indices
- whether indices are zero-based
- unit labels and scale factors for reaction coordinate and mean force
- equilibration/skip-row handling
- integration direction and free-energy zero reference
- free-energy conversion factor and unit label, if used
- whether plots should be generated
- whether TST should be computed
- elementary-step label, temperature, free-energy column/unit, reactant state, transition-state selection, prefactor model, and prefactor units when TST is enabled

Window discovery:

- `sampling_output_root`: directory containing reaction-coordinate window subdirectories.
- `input_file`: confirmed file name inside each window directory. Required in runnable configs; do not rely on `energy.dat` as an implicit default.
- `window_glob`: confirmed direct-child glob for window directories. Required in runnable configs; do not rely on `*` as an implicit default.
- `dataset_label`: label written to output CSVs.
- `output_dir`: output directory. Default: `nqe-postprocess-output`.

Optional convergence screening before TI:

- `run_convergence_diagnostics`: `true` or `false`. If omitted, convergence screening is disabled, but set it explicitly in reviewed configs when this choice matters.
- `convergence_columns`: confirmed columns or zero-based numeric indices to inspect, as a comma-separated string in YAML or an array in JSON. Examples: `PotEng,MeanForce` or `PotEng,MeanForce_0`.
- `convergence_output_dir`: optional directory for per-window diagnostic plots and CSV summaries. Default: `output_dir/convergence`.
- `convergence_skiprows`: numeric rows to discard before the diagnostic script. Required when convergence screening is enabled.
- `convergence_step_column`, `convergence_step_col_index`: optional step-axis settings for the diagnostic script.
- `convergence_running_window`: optional rolling-average window for convergence plots. Default: `0`.
- `convergence_x_scale`, `convergence_y_scale`: optional axis scaling for the diagnostic script.
- `convergence_xlabel`, `convergence_ylabel`: optional axis labels for the diagnostic script.
- `convergence_auto_equilibration`: `true` or `false`. Required when convergence screening is enabled.

Convergence-screening boundary:

- These diagnostics call `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py` once per window before mean-force extraction.
- The generated plot/CSV outputs are screening aids only. They do not automatically rewrite `skiprows`, do not prove equilibration, and still require user review before TI handoff.

Mean-force extraction:

- `format`: `phy_quant` or `table`. Required in runnable configs; the runner preflight refuses `auto`.
- `rc_index`: confirmed reaction-coordinate index.
- `rc_column`, `force_column`: required header names for `phy_quant`/headered data.
- `rc_col_index`, `force_col_index`: required zero-based numeric columns for `table` data.
- `skiprows`: confirmed numeric rows to discard after header/comment handling.
- `rc_scale`, `force_scale`: confirmed raw-to-atomic-unit conversion factors.
- `rc_raw_unit_label`, `force_raw_unit_label`: confirmed raw unit labels preserved in CSV.
- `uncertainty`: confirmed policy, `sem`, `std`, or `none`.

Thermodynamic integration:

- `integration_direction`: required; use `ascending`, `descending`, or `input`.
- `zero`: confirmed reference-zero convention, `first`, `last`, `min`, or `none`.
- `free_energy_scale`: confirmed conversion factor for `free_energy_converted`.
- `free_energy_unit_label`: confirmed label for converted free energy.

Plotting:

- `plots`: `true` or `false`. Required in runnable configs.
- `free_energy_plot_unit_label`: optional y-axis unit label for the free-energy plot. If omitted, the runner uses `free_energy_unit_label`.

TST:

- `compute_tst`: `true` or `false`. Required in runnable configs.
- `elementary_step`: required when `compute_tst` is true.
- `temperature_K`: required when `compute_tst` is true.
- `reactant_mode`: `first`, `last`, `min`, `rc`, or `value`.
- `ts_mode`: `max`, `rc`, or `value`.
- `reactant_rc`, `ts_rc`, `reactant_value`, `ts_value`: required only for matching state-selection modes.
- `free_energy_column`: required when `compute_tst` is true.
- `free_energy_unit`: required when `compute_tst` is true.
- `prefactor_model`: `kBT_over_h`, `custom_numeric`, or `adsorption_flux_n_v_S`.
- `prefactor_units`: required when `compute_tst` is true.
- `prefactor_value`, `density`, `mean_speed`, `site_area`: required only for matching prefactor models.

Optional:

- `python`: Python executable used for child scripts. Default: current interpreter.
- `ti_tst_scripts_dir`: override path to `ti-tst-rate/scripts`.
- `notes`: text added to generated CSV rows.
- CLI `--dry-run`: print generated child commands without executing them. Use this first for smoke testing and config review.

Agent execution rule:

1. Read this schema and the config file.
2. When creating YAML, ask for every parameter before writing a runnable config; otherwise write only a non-runnable draft with `parameters_confirmed: false`.
3. Refuse dry-run and real execution if required explicit fields are missing, if `format: auto` is used, if placeholders remain, or if `parameters_confirmed` is not true.
4. Run the runner with `--dry-run` first.
5. Ask for user confirmation if the dry-run commands reveal unexpected paths, units, ordering, convergence columns, state selection, temperature, or prefactor.
6. Run without `--dry-run` only after the dry-run is accepted.
