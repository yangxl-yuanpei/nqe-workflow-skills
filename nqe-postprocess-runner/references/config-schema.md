# Config Schema

Use a flat YAML or JSON config. Paths are resolved relative to the config file.

A runnable config must contain only user-confirmed values. When creating a new config, ask about each parameter before writing it to YAML. If a value is not yet confirmed, use a question checklist or a non-runnable draft with `parameters_confirmed: false` and `TODO_USER_APPROVAL` placeholders.

Required guardrail:

- `parameters_confirmed`: must be `true`.
- Set `parameters_confirmed: true` only after every included parameter has been explicitly approved by the user or copied from a user-provided config.
- Use `parameters_confirmed: false` for drafts, examples, or partially filled configs.
- `parameters_confirmed: true` is necessary but not sufficient. The runner also refuses runnable configs that still rely on implicit parser, column, unit, integration, state-selection, temperature, or prefactor defaults.
- Optional fields with documented defaults may be omitted. If an optional field is written explicitly in a runnable config, it is still a config parameter and must be user-confirmed or copied from a user-provided config.

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
- optional `stop_after` stage when intentionally stopping before integration, plotting, or TST, or when plotting only from existing CSVs

Window discovery:

- `sampling_output_root`: directory containing reaction-coordinate window subdirectories.
- `input_file`: confirmed file name inside each window directory. Required in runnable configs; do not rely on `energy.dat` as an implicit default.
- `window_glob`: confirmed direct-child glob for window directories. Required in runnable configs; do not rely on `*` as an implicit default.
- `dataset_label`: provenance label written to output CSVs and summaries. It does not by itself choose `output_dir` or file-name prefixes unless a specific config field or script option uses it.
- `output_dir`: output directory. Default: `nqe-postprocess-output`.
- `allow_existing_output_dir`: optional safety override, `true` or `false`. Default: `false`. Real execution refuses to write into a non-empty `output_dir` unless this is explicitly set to `true` after inspecting old outputs and approving reuse or cleanup. Do not add this field as the first remedy or as a convenience fix. Dry-run does not write outputs and does not require this field.
- `stop_after`: optional stage boundary, one of `convergence`, `extraction`, `integration`, `plot`, or `all`. Default: `all`.
- Directories discovered during workspace inspection are candidates only. Do not silently promote a discovered directory such as `demo/` or `results/` to `sampling_output_root`; ask the user to confirm the intended root before writing a runnable config or running commands. Do not describe a discovered candidate as the user's dataset until the user confirms it.

Stage boundary:

- `stop_after: convergence` generates or runs only convergence-screening commands and requires `run_convergence_diagnostics: true`.
- `stop_after: extraction` generates or runs convergence screening, if enabled, and mean-force extraction. It does not require TI, plot, or TST fields.
- `stop_after: integration` generates or runs through TI integration but skips plot and TST commands.
- `stop_after: plot` plots existing user-confirmed CSV files only. It does not discover windows, run convergence diagnostics, extract mean force, integrate free energy, or run TST.
- `stop_after: all` preserves the full runner behavior and requires explicit plot and TST choices.
- For broad user requests such as "postprocess this batch", do not infer a full pipeline. Default to `stop_after: convergence` or `stop_after: extraction` until the user separately confirms integration direction, zero reference, unit conversion, and mean-force sign convention.
- When asking for `sampling_output_root`, state the intended first stop stage and the downstream confirmation gates. Do not ask for the path as if it were enough to authorize TI or TST.
- If candidate directories are found before the user confirms `sampling_output_root`, list them as candidates and ask which one is intended. Discovery is not confirmation; a bundled `demo/` or previous real-case record is not the user's new batch just because it exists in the repository.
- Read-only inventory is allowed before a runnable config exists. Counting windows, checking row counts, detecting short rows, and comparing `INPUT`/`ALL_INPUT` files are inspection tasks, not runner execution; they do not require `parameters_confirmed: true` and do not authorize child scripts or downstream TI/TST.

Optional convergence screening before TI:

- `run_convergence_diagnostics`: `true` or `false`. If omitted, convergence screening is disabled, but set it explicitly in reviewed configs when this choice matters.
- `convergence_columns`: confirmed columns or zero-based numeric indices to inspect, as a comma-separated string in YAML or an array in JSON. Examples: `PotEng,MeanForce` or `PotEng,MeanForce_0`.
- `convergence_output_dir`: optional directory for per-window diagnostic plots and CSV summaries. Default: `output_dir/convergence`.
- `convergence_skiprows`: numeric rows to discard before the diagnostic script. Required when convergence screening is enabled.
- `convergence_step_column`, `convergence_step_col_index`: optional step-axis settings for the diagnostic script.
- `convergence_use_row_index_as_step`: optional `true` or `false`. Use `true` only when the sampling output has no real step/iteration column and the user has approved row/sample index as the diagnostic x-axis. Do not combine it with `convergence_step_column` or `convergence_step_col_index`.
- `convergence_running_window`: optional rolling-average window for convergence plots. Default: `0`.
- `convergence_x_scale`, `convergence_y_scale`: optional axis scaling for the diagnostic script.
- `convergence_xlabel`, `convergence_ylabel`: optional axis labels for the diagnostic script.
- `convergence_auto_equilibration`: `true` or `false`. Required when convergence screening is enabled.
- `convergence_plot`: `true` or `false`. Required when convergence screening is enabled. Use `false` for CSV summary-only mode, for example in environments without `matplotlib`.

Convergence-screening boundary:

- These diagnostics call `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py` once per window before mean-force extraction.
- The generated plot/CSV outputs are screening aids only. They do not automatically rewrite `skiprows`, do not prove equilibration, and still require user review before TI handoff.
- Convergence screening and mean-force extraction are separate stages. Screening plots/CSVs diagnose time-series behavior; extraction produces `mean_force_table.csv` for TI only after parser, column, unit, and discard choices are confirmed.
- If `convergence_plot: false`, the runner generates only per-window CSV summaries via `--no-plot`; this avoids adding plotting dependencies but removes the visual inspection artifact.
- If the sampling output has no step/iteration column, do not use a physical observable such as kinetic energy as a fake x-axis. Ask the user to confirm `convergence_use_row_index_as_step: true`; then any reported `equilibration_step` is a row index after `convergence_skiprows`, not a simulation step.
- Do not set `convergence_auto_equilibration: true` in a runnable config unless the user has explicitly confirmed that suggested equilibration indices are screening hints only. For drafts, prefer `TODO_USER_APPROVAL` or `false` until the user decides.
- After real convergence screening, prepare a human-review checklist before extraction when any window has nonzero suggested equilibration, strong drift, sign changes, suspicious energy behavior, or user uncertainty. Use the checklist to record whether a window is accepted, assigned a user-approved discard, rerun, excluded, or left unresolved.

Mean-force extraction:

- `format`: `phy_quant` or `table`. Required in runnable configs; the runner preflight refuses `auto`.
- `rc_index`: confirmed reaction-coordinate index.
- `rc_column`, `force_column`: required header names for `phy_quant`/headered data.
- `rc_col_index`, `force_col_index`: required zero-based numeric columns for `table` data.
- `skiprows`: confirmed numeric rows to discard after header/comment handling.
- `per_window_skiprows_file`: optional CSV path for confirmed per-window extraction discard overrides. Required columns: `sample_label`, `skiprows`; optional column: `reason`. Values in this file override global `skiprows` for matching windows only.
- `rc_scale`, `force_scale`: confirmed raw-to-atomic-unit conversion factors.
- `rc_raw_unit_label`, `force_raw_unit_label`: confirmed raw unit labels preserved in CSV.
- `uncertainty`: confirmed policy, `sem`, `std`, or `none`.
- If a legacy sampling output has left/right mean-force components, such as `mfl` and `mfr`, the current runner extraction config still selects one force column per run. Do not invent runnable combine fields. For these legacy outputs, require either a user-confirmed single component or a documented, user-approved preprocessing step that writes a combined force column before runner extraction.

Parser and skip-row boundaries:

- Do not infer `format: phy_quant` for the whole batch from one file or one representative header. Use `phy_quant` only when all included windows have reliable compatible headers containing the confirmed `rc_column` and `force_column`.
- If headers are missing, inconsistent, truncated, or only partially inspected, do not guess column names. Ask the user whether to use `format: table` with explicit zero-based `rc_col_index` and `force_col_index`, or stop for manual inspection.
- `skiprows` is not a header-skip parameter. It discards numeric data rows after header/comment parsing. Do not set `skiprows: 1` to skip a text header; use `skiprows: 0` unless the user has confirmed an equilibration or data-row discard length.

Thermodynamic integration:

- Required only when `stop_after` reaches `integration` or `all`.
- `integration_direction`: required; use `ascending`, `descending`, or `input`.
- `zero`: confirmed reference-zero convention, `first`, `last`, `min`, or `none`.
- `free_energy_scale`: confirmed conversion factor for `free_energy_converted`.
- `free_energy_unit_label`: confirmed label for converted free energy.

Plotting:

- Required when `stop_after: all` uses generated plots, or when `stop_after: plot` plots existing CSVs.
- `plots`: `true` or `false`. Required for `stop_after: all`; not required for `stop_after: plot` because plot-only mode is already explicit.
- `free_energy_plot_unit_label`: optional y-axis unit label for the free-energy plot. If omitted, the runner uses `free_energy_unit_label`.

Plot-only mode:

- Use `stop_after: plot` when mean-force and/or free-energy CSV files already exist and the user only wants plots.
- `sampling_output_root`, `input_file`, `window_glob`, parser fields, extraction fields, and TI fields are not required in plot-only mode because no sampling-output parsing or integration is performed.
- `plot_mean_force`: `true` or `false`. Required in plot-only mode.
- `plot_free_energy`: `true` or `false`. Required in plot-only mode.
- At least one of `plot_mean_force` or `plot_free_energy` must be `true`.
- `mean_force_table`: existing `mean_force_table.csv` path. Required when `plot_mean_force: true`.
- `free_energy_profile`: existing `free_energy_profile.csv` path. Required when `plot_free_energy: true`.
- `plot_rc_order`: confirmed plotting order, `ascending`, `descending`, or `input`. For free-energy plots, this must be consistent with the user-confirmed integration direction or intended initial-to-final RC direction; do not infer it from CSV row order or use it as a visual styling default.
- When `plot_rc_order: descending` is passed to the plotting scripts and no explicit x-axis limits are supplied, the scripts invert the x-axis so larger reaction coordinate values appear on the left. If explicit x-axis limits are supplied, their order controls the visual axis direction.
- If a config contains both `integration_direction` and `plot_rc_order`, they must not conflict. Updating a plot direction means updating `plot_rc_order`; changing only `integration_direction` has no effect in plot-only mode when `plot_rc_order` is present.
- `mean_force_y_column`: confirmed mean-force column to plot, for example `mean_force_au`. Required when `plot_mean_force: true`.
- `free_energy_y_column`: confirmed free-energy column to plot, for example `free_energy_converted`. Required when `plot_free_energy: true`.
- `free_energy_plot_unit_label`: confirmed plotted free-energy unit label. Required when `plot_free_energy: true`.
- Observed CSV headers, row ordering, and unit-label columns are candidates only. They can help form a checklist, but they do not authorize setting `parameters_confirmed: true` unless the user explicitly confirms the selected y-columns, plotted unit label, and `plot_rc_order`, or those values are copied from a user-provided config.
- `mean_force_plot_output`, `free_energy_plot_output`: optional output image paths. If omitted, the runner writes `mean_force.png` and `free_energy.png` under `output_dir`.
- Optional style fields use the prefixes `mean_force_plot_` or `free_energy_plot_`: `xlabel`, `ylabel`, `title`, `width`, `height`, `dpi`, `linewidth`, `markersize`, and `grid`.
- The runner writes `plot_summary.json` in `output_dir` by default, so plot-only provenance does not overwrite an existing postprocessing `summary.json`.
- Plot-only mode is visualization only. It does not certify convergence, approve TI conventions, choose TST states, or compute rates.

TST:

- Required only when `stop_after: all`.
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
- If the user says to use "defaults", do not mark TST choices as confirmed, even if the prompt also mentions candidate values such as `free_energy_converted`, `min`, `max`, or `kBT_over_h`. These are proposed settings until the user confirms their physical meaning and units.
- `reactant_mode: min` and `ts_mode: max` are mathematical selections from the profile, not automatic identification of the physical reactant and transition state. Require user confirmation that those selections match the intended elementary step.
- `kBT_over_h` is an allowed prefactor model, not a universal default. Require confirmation that it is appropriate for the elementary step and that the rate units are correct.

Optional:

- `python`: Python executable used for child scripts. Default: current interpreter.
- `ti_tst_scripts_dir`: override path to `ti-tst-rate/scripts`.
- `notes`: text added to generated CSV rows.
- CLI `--dry-run`: print generated child commands without executing them. Use this first for smoke testing and config review.

Output-directory reuse boundary:

- By default, a real runner execution refuses a non-empty `output_dir` before deleting or overwriting known outputs.
- Prefer a fresh `output_dir` for materially different configs or reruns after child-script failure.
- Set `allow_existing_output_dir: true` only after the user has inspected old outputs and explicitly approved reuse or cleanup. This flag is an operational override; it does not merge provenance or certify stale outputs.
- Do not suggest adding `allow_existing_output_dir: true` as the first remedy, do not auto-edit a config to add it, and do not describe reuse as a clean overwrite. Known CSV/JSON files may be regenerated, but old plots, convergence summaries, and other provenance-bearing files can remain.
- Do not state that a rerun with `allow_existing_output_dir: true` completed cleanly, that all windows are converged, or that old outputs are fully replaced unless the user separately reviewed the output directory, convergence evidence, and generated summaries. Script completion is not physical validation.
- Dry-run may be used to review commands even when the output directory contains old files, because it does not execute child scripts or write outputs.

Agent execution rule:

1. Read this schema and the config file.
2. When creating YAML, ask for every parameter before writing a runnable config; otherwise write only a non-runnable draft with `parameters_confirmed: false`.
3. Refuse dry-run and real execution if required explicit fields are missing, if `format: auto` is used, if placeholders remain, or if `parameters_confirmed` is not true.
4. If the user only asks generally to postprocess sampling results, stop at convergence or extraction unless TI choices are explicitly confirmed. If the user only asks to plot already generated CSV outputs, use `stop_after: plot` rather than rerunning extraction or integration.
5. If more path information is needed, ask for `sampling_output_root` while also explaining the staged stop point and the TI/TST confirmations that are still missing.
6. If local inspection finds plausible directories, treat them as candidates and ask the user to confirm the intended `sampling_output_root`; do not choose a candidate silently and do not rank which candidate is "probably" the real dataset.
7. Before proposing `format: phy_quant`, verify or ask the user to confirm that every included window has reliable compatible headers. Otherwise require explicit table column indices.
8. Before proposing any nonzero `skiprows`, state that it discards numeric data rows, not headers, and require user approval of the discard length.
9. If a TST request includes the word "default", respond with a confirmation checklist rather than a runnable config. Mentioned min/max/free-energy-column/prefactor choices are candidates only until explicitly confirmed.
10. Run the runner with `--dry-run` first.
11. Ask for user confirmation if the dry-run commands reveal unexpected paths, units, ordering, convergence columns, state selection, temperature, or prefactor.
12. Run without `--dry-run` only after the dry-run is accepted.

Per-window discard boundary:

- Use `per_window_skiprows_file` only after the user has reviewed convergence plots/CSVs and approved the per-window discard choices.
- Do not generate or apply this file automatically from `auto_status: SUGGESTED`; suggested equilibration indices are screening aids, not production cutoffs.
- If a per-window discard file is used, review the dry-run commands and confirm that only intended windows receive non-global `--skiprows` values.
- In production-facing prompts or records, remind the user to inspect the convergence plots directly and personally approve whether the proposed discard length is reasonable for the physical system.
