# 2026-07-12 Plot-Only Runner Execution Record

Runner config: `tests/runner_configs/demo_multi_window_plot_only.yaml`

Input CSVs:

- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/mean_force_table.csv`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_profile.csv`

Generated outputs:

- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/mean_force_plot_only.png`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_plot_only.png`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/plot_summary.json`

Boundary: this record verifies `nqe-postprocess-runner` plot-only execution on already reviewed CSV outputs. It does not rerun convergence diagnostics, mean-force extraction, TI integration, TST, or rate calculation. It does not certify convergence, TI correctness, state selection, or production readiness.

## Config Intent

The config uses:

```yaml
stop_after: plot
plot_mean_force: true
plot_free_energy: true
plot_rc_order: ascending
mean_force_y_column: mean_force_au
free_energy_y_column: free_energy_converted
free_energy_plot_unit_label: eV
```

The runner therefore reads existing CSV files and generates only plot commands.

## Execution Notes

The first execution attempt exposed a useful plot-only provenance issue: the original runner code would have used `summary.json` in the existing reviewed TI-only output directory. The runner was updated so plot-only mode writes `plot_summary.json` by default, preserving the original TI-only `summary.json`.

The bundled Python environment did not include `matplotlib`. The successful execution used a temporary `PYTHONPATH` pointing to the user-site packages directory where `matplotlib` was already installed:

```text
PYTHONPATH=C:\Users\94474\AppData\Roaming\Python\Python312\site-packages
```

No new package was installed during this run.

## Execution Result

Status: `PASS`

The runner generated exactly two child commands:

- `plot_mean_force.py` using `mean_force_au`
- `plot_free_energy.py` using `free_energy_converted` and `eV`

No window discovery, convergence screening, extraction, integration, TST, or rate command was generated.

The original reviewed TI-only `summary.json` remained unchanged. The plot-only provenance was written to `plot_summary.json`.

## Visual Review

Both generated PNG files rendered successfully.

Observed high-level shape:

- `mean_force_plot_only.png`: mean force is positive on the negative-RC side, crosses sign near small positive RC, reaches the most negative region around the mid-positive RC range, then rises toward the large-RC end.
- `free_energy_plot_only.png`: free energy starts at zero at the most-negative RC endpoint, rises to a positive relative maximum near `RC = 0`, then decreases toward the large-RC end.

These observations describe the plotted reviewed TI-only outputs. They are not a new physical approval step.

## Remaining Boundary

Before any TST or rate use, the user must still confirm reactant/reference state, transition-state selection, free-energy column/unit, temperature, prefactor model, prefactor units, and whether convergence/uncertainty evidence is sufficient for the intended claim.
