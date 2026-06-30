---
name: nqe-postprocess-runner
description: Configuration-driven runner for guarded NQE postprocessing. Use when a user wants to automate confirmed CHMC/CPIHMC sampling-output postprocessing into mean-force tables, free-energy profiles, TST rate CSVs, plots, and run summaries without inventing reaction coordinates, units, state selections, prefactors, or production scientific parameters.
---

# NQE Postprocess Runner

## Overview

Use this skill as the thin automation layer above `ti-tst-rate`. It discovers sampling windows from a confirmed config file, calls the existing TI/TST scripts, and writes reproducible CSV/plot/summary outputs.

## Boundaries

- Require `parameters_confirmed: true` in the config before running scripts.
- Do not choose reaction coordinates, units, integration direction, reactant/transition-state selection, temperature, prefactor model, or KMC event definitions.
- Do not describe the result as production-ready unless the user provides convergence, uncertainty, and physical validation evidence.
- Treat TST rates as elementary rates for later KMC use, not final H2 formation efficiency.

## Workflow

1. Read `references/config-schema.md` when creating or reviewing a runner config.
2. Copy or adapt `assets/config.example.yaml`.
3. Confirm the config values with the user, especially units, columns, integration direction, zero reference, temperature, elementary-step label, and state selection.
4. Run:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py path/to/config.yaml
```

5. Report generated files and repeat the reactant/transition-state selection from `tst_rates.csv` for user confirmation.

## Script

`scripts/nqe_postprocess_runner.py` performs only orchestration:

- discover window directories containing the configured input file
- call `ti-tst-rate/scripts/extract_mean_force.py`
- call `ti-tst-rate/scripts/integrate_free_energy.py`
- optionally call `plot_mean_force.py` and `plot_free_energy.py`
- optionally call `compute_tst_rates.py`
- write `summary.json`

The script supports a small YAML subset and JSON using only the Python standard library.
