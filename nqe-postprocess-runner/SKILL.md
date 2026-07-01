---
name: nqe-postprocess-runner
description: Configuration-driven runner for guarded NQE postprocessing. Use when a user wants to automate confirmed CHMC/CPIHMC sampling-output postprocessing into mean-force tables, free-energy profiles, TST rate CSVs, plots, and run summaries without inventing reaction coordinates, units, state selections, prefactors, or production scientific parameters.
---

# NQE Postprocess Runner

## Overview

Use this skill as the thin automation layer above `ti-tst-rate`. It discovers sampling windows from a confirmed config file, calls the existing TI/TST scripts, and writes reproducible CSV/plot/summary outputs.

## Boundaries

- Require `parameters_confirmed: true` in the config before running scripts.
- Ask the user to confirm every config parameter before writing it into a runnable YAML file.
- Treat `assets/config.example.yaml` as a format example only, not as approved defaults for a new project.
- Do not choose reaction coordinates, units, integration direction, reactant/transition-state selection, temperature, prefactor model, or KMC event definitions.
- Do not describe the result as production-ready unless the user provides convergence, uncertainty, and physical validation evidence.
- Treat TST rates as elementary rates for later KMC use, not final H2 formation efficiency.

## Workflow

1. Read `references/config-schema.md` when creating or reviewing a runner config.
2. When the user needs a new config, use `assets/config.example.yaml` only as a field/layout example. Do not copy its values into the user's YAML unless the user explicitly approves each value.
3. Before writing a runnable YAML file, ask the user to confirm every parameter listed in `references/config-schema.md`. If values are unknown, produce a question checklist or non-runnable draft with TODOs instead of setting `parameters_confirmed: true`.
4. Inspect the config before running anything. Confirm that paths exist, `parameters_confirmed: true` is present, and all required scientific choices are explicit.
5. If any required value is missing or ambiguous, ask the user before editing or running the config. Do not infer it from file order, directory names, or examples.
6. If the config enables convergence screening, confirm the selected `PHY_QUANT`/`energy.dat` diagnostic columns, skip policy, and whether `--auto-equilibration` is only being used as a screening aid.
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

## Agent Invocation Protocol

When the user asks an agent to run this postprocessing workflow:

- If the user asks to create a YAML file, ask for each parameter first. Do not output a runnable YAML with inferred values.
- If the user wants a template before answering all questions, write a non-runnable draft with `parameters_confirmed: false` and `TODO_USER_APPROVAL` placeholders.
- If the user only gives a sampling-output directory, inspect available file shapes if useful, then ask for the missing config parameters; do not run the runner directly and do not write a runnable config from directory names alone.
- If the user gives a config with `parameters_confirmed: false` or no `parameters_confirmed` field, review the missing choices and stop before execution.
- If the user gives a config with `parameters_confirmed: true`, still run `--dry-run` first and check that the generated child commands match the intended inputs, outputs, units, integration direction, state selection, temperature, and prefactor.
- If the user gives a config with `run_convergence_diagnostics: true`, check that the generated child commands inspect the intended convergence columns and that the workflow does not silently turn suggested equilibration cutoffs into TI-ready discard lengths.
- If the dry-run output is surprising, stop and ask the user whether to edit the config.
- After a real run, summarize `summary.json` when present, list generated CSV/plot files, and report selected reactant and transition-state coordinates from the TST output when `compute_tst: true`.
- Do not proceed from dry-run to real execution silently in the same response unless the user explicitly requested that behavior and the config is complete.

## Script

`scripts/nqe_postprocess_runner.py` performs only orchestration:

- optionally call `chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py` per window for screening plots and CSV summaries
- discover window directories containing the configured input file
- call `ti-tst-rate/scripts/extract_mean_force.py`
- call `ti-tst-rate/scripts/integrate_free_energy.py`
- optionally call `plot_mean_force.py` and `plot_free_energy.py`
- optionally call `compute_tst_rates.py`
- write `summary.json`

The script supports a small YAML subset and JSON using only the Python standard library.

The optional convergence step is still a pre-TI screening layer, not automatic convergence proof and not automatic equilibration trimming.

## References

- Read `references/postprocess-runner-failure-cases.md` when config parsing, dry-run, child-command generation, or runner execution fails. This placeholder should be expanded with real observed failures before relying on it for diagnosis.
