---
name: nqe-postprocess-runner
description: Configuration-driven runner for guarded NQE postprocessing. Use when a user wants to automate confirmed CHMC/CPIHMC sampling-output postprocessing into mean-force tables, free-energy profiles, TST rate CSVs, plots, and run summaries without inventing reaction coordinates, units, state selections, prefactors, or production scientific parameters.
---

# NQE Postprocess Runner

## Overview

Use this skill as the thin automation layer above `ti-tst-rate`. It discovers sampling windows from a confirmed config file, calls the existing TI/TST scripts, and writes reproducible CSV/plot/summary outputs.

## Boundaries

- Require `parameters_confirmed: true` in the config before running scripts.
- Treat `parameters_confirmed: true` as necessary but not sufficient: the script also performs preflight checks that reject implicit parser, column, unit, integration, state-selection, temperature, and prefactor defaults.
- Ask the user to confirm every config parameter before writing it into a runnable YAML file.
- Treat `assets/config.example.yaml` as a format example only, not as approved defaults for a new project.
- Do not choose reaction coordinates, units, integration direction, reactant/transition-state selection, temperature, prefactor model, or KMC event definitions.
- Do not describe the result as production-ready unless the user provides convergence, uncertainty, and physical validation evidence.
- Treat TST rates as elementary rates for later KMC use, not final H2 formation efficiency.

## Workflow

1. Read `references/config-schema.md` when creating or reviewing a runner config.
2. When the user needs a new config, use `assets/config.example.yaml` only as a field/layout example. Do not copy its values into the user's YAML unless the user explicitly approves each value.
3. Before writing a runnable YAML file, ask the user to confirm every parameter listed in `references/config-schema.md`. If values are unknown, produce a question checklist or non-runnable draft with TODOs instead of setting `parameters_confirmed: true`.
4. Inspect the config before running anything. Confirm that paths exist, `parameters_confirmed: true` is present, and all required scientific choices for the configured `stop_after` stage are explicit. Expect the runner to refuse configs that still rely on `format: auto`, missing extraction columns, missing unit/scale fields, missing TI zero references, or missing TST free-energy/prefactor fields.
5. If any required value is missing or ambiguous, ask the user before editing or running the config. Do not infer it from file order, directory names, or examples.
6. If the config enables convergence screening, confirm the selected `PHY_QUANT`/`energy.dat` diagnostic columns, skip policy, whether plots should be generated, and whether `--auto-equilibration` is only being used as a screening aid.
7. Run `--dry-run` first and show the generated child commands to the user unless the user explicitly says they already dry-ran the same config.
8. Only run without `--dry-run` after the user confirms the dry-run commands or explicitly asks for execution of an already confirmed config.
9. Report generated files and repeat the reactant/transition-state selection from `tst_rates.csv` for user confirmation.

Use this command for the first check:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py path/to/config.yaml --dry-run
```

Use this command only after the dry-run is accepted:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py path/to/config.yaml
```

## Broad Request Default Response

When the user broadly asks to "postprocess this batch" or "process these sampling results" and has not confirmed TI/TST choices, answer with this structure before asking for paths:

```text
Please provide sampling_output_root. If I discover candidate directories while inspecting the workspace, I will list them only as candidates and ask you to confirm which one is intended. I will first inspect the file shapes and prepare only a staged convergence/extraction plan, stopping at stop_after: convergence or stop_after: extraction. I will not proceed to TI until you confirm integration direction, zero reference, unit conversion, and mean-force sign convention. I will not run TST/rates until reactant/transition-state selection, temperature, and prefactor are confirmed.
```

This default response is a safety boundary, not just wording. Do not ask for the path as if it were enough to authorize integration, plotting, TST, or rate calculation.

## Agent Invocation Protocol

When the user asks an agent to run this postprocessing workflow:

- If the user asks to create a YAML file, ask for each parameter first. Do not output a runnable YAML with inferred values.
- If the user wants a template before answering all questions, write a non-runnable draft with `parameters_confirmed: false` and `TODO_USER_APPROVAL` placeholders.
- If the user gives a broad request such as "postprocess this batch" without confirmed TI/TST choices, default to a staged diagnostic workflow: propose or run only `stop_after: convergence` or `stop_after: extraction` when the required parser, column, unit, and screening choices are confirmed. Stop before integration unless the user explicitly confirms integration direction, zero reference, unit conversion, and mean-force sign convention.
- When asking the user for `sampling_output_root` or a sampling-output directory after a broad request, also state the intended first stop stage and downstream gates: first inspect/diagnose file shapes and convergence/extraction only; do not integrate until TI direction, zero reference, unit conversion, and mean-force sign are confirmed; do not run TST/rates until state selection, temperature, and prefactor are confirmed.
- If workspace inspection reveals likely directories such as `demo/`, `results/`, or reaction-coordinate window folders, describe them as candidate paths only. Do not silently adopt a discovered directory as `sampling_output_root`; ask the user to confirm the intended root before writing a runnable config or running commands.
- If the user only gives a sampling-output directory, inspect available file shapes if useful, then ask for the missing config parameters; do not run the runner directly and do not write a runnable config from directory names alone.
- Do not infer a whole-batch parser mode from one file. Use `format: phy_quant` only after confirming all included windows have reliable compatible headers with the named columns. If headers are absent, inconsistent, or only partially checked, ask whether to use `format: table` with explicit zero-based `rc_col_index` and `force_col_index` instead.
- Treat `skiprows` as a data-row discard applied after header/comment handling. Never set `skiprows: 1` merely to skip a header; headers are handled by the parser. Use `skiprows: 0` unless the user confirms an equilibration/data discard length.
- If the user gives a config with `parameters_confirmed: false` or no `parameters_confirmed` field, review the missing choices and stop before execution.
- If the user gives a config with `parameters_confirmed: true`, still run `--dry-run` first and check that the generated child commands match the intended inputs, outputs, units, integration direction, state selection, temperature, and prefactor.
- If the user gives a config with `run_convergence_diagnostics: true`, check that the generated child commands inspect the intended convergence columns, honor the confirmed plot or summary-only choice, and do not silently turn suggested equilibration cutoffs into TI-ready discard lengths.
- If the user wants per-window extraction discard, require a user-reviewed `per_window_skiprows_file`; do not auto-convert convergence `SUGGESTED` cutoffs into production `skiprows`. For production use, explicitly remind the user to inspect the convergence plots/CSVs themselves and approve whether the proposed discard is scientifically reasonable.
- If the user wants convergence or extraction only, use a confirmed `stop_after` value rather than filling fake TI/TST fields.
- If the user later confirms TI choices, create a separate `stop_after: integration` config or clearly update the existing config, then dry-run again before execution. Do not proceed from a generic postprocessing request directly to integration or TST.
- If the user only wants plots from existing `mean_force_table.csv` or `free_energy_profile.csv`, use `stop_after: plot`. Require explicit existing CSV paths, dataset label, `plot_rc_order`, y-column choices, and unit labels. Do not rerun extraction/integration or fill fake TST fields just to reach plotting.
- If the dry-run output is surprising, stop and ask the user whether to edit the config.
- After a real run, summarize `summary.json` when present. For `stop_after: plot`, summarize `plot_summary.json` instead. List generated CSV/plot files, and report selected reactant and transition-state coordinates from the TST output when `compute_tst: true`.
- Do not proceed from dry-run to real execution silently in the same response unless the user explicitly requested that behavior and the config is complete.

## Script

`scripts/nqe_postprocess_runner.py` performs only orchestration:

- optionally call `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py` per window for screening plots and CSV summaries
- discover window directories containing the configured input file
- call `ti-tst-rate/scripts/extract_mean_force.py`
- call `ti-tst-rate/scripts/integrate_free_energy.py`
- optionally call `plot_mean_force.py` and `plot_free_energy.py`
- optionally call `compute_tst_rates.py`
- write `summary.json`, or `plot_summary.json` for `stop_after: plot`

The `stop_after` config field can intentionally stop at `convergence`, `extraction`, or `integration` so the runner does not require or generate later-stage commands before those physical choices are confirmed. `stop_after: plot` is a separate plot-only mode for already generated CSV files.

The script supports a small YAML subset and JSON using only the Python standard library.

Before generating child commands, the script rejects runnable configs that still rely on implicit column choices or physical defaults.

The optional convergence step is still a pre-TI screening layer, not automatic convergence proof and not automatic equilibration trimming.

## References

- Read `references/postprocess-runner-failure-cases.md` when config parsing, dry-run, child-command generation, child-script execution, partial outputs, or runner-to-TI/TST/KMC handoff review fails.
