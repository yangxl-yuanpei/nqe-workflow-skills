# 2026-07-11 Reviewed TI-Only Execution Record

Runner config: `tests/runner_configs/demo_multi_window_reviewed_ti_only.yaml`

Raw dataset: `../demo`, a 13-window CHMC/CPIHMC-style `energy.dat` dataset outside the repository

Generated outputs:

- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/mean_force_table.csv`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_profile.csv`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_profile.png`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/output/summary.json`
- `tests/real_case_records/2026-07-11_reviewed_ti_only/convergence/*.csv`

Boundary: this record verifies a guarded TI-only postprocessing run with user-confirmed integration choices. It does not certify production convergence, does not propagate uncertainty, does not select a TST reactant/transition state, and does not compute rates.

## Confirmed TI Choices

The user confirmed:

- Integration direction: small RC to large RC.
- Zero reference: most-negative reaction-coordinate endpoint.
- Free-energy reporting: convert `free_energy_converted` to eV.
- Mean-force sign: keep the extracted mean force as the free-energy derivative `dF/dRC`.

Runner/script mapping:

- `integration_direction: ascending`
- `zero: first`
- `free_energy_scale: 27.211386245988`
- `free_energy_unit_label: eV`

Important note: `zero: first` means the first point after ascending RC sorting is set to zero. In this dataset that is the most-negative RC endpoint, `RC = -1.6`. This is different from `zero: min`, which would shift by the minimum free-energy value.

## Output Summary

The TI-only run wrote 13 free-energy rows.

Selected rows from `free_energy_profile.csv`:

```text
RC              free_energy_au      free_energy_eV
-1.6            0                  0
-0.8            0.004065181726     0.110619230110
 0.0            0.009222009701     0.250943667946
 0.8            0.005357974424     0.145797911543
 1.80061778464 -0.007356575968    -0.200182630103
 2.99996399964 -0.013395311784    -0.364505002834
```

The profile reaches a positive relative value around `RC = 0.0` under this sign and zero convention, then decreases toward the large-RC end. This shape is an output of the confirmed convention, not an automatic physical interpretation.

## Plotting

The free-energy profile was plotted from the converted eV column:

```text
python ti-tst-rate/scripts/plot_free_energy.py \
  --curve file=tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_profile.csv,dataset=demo_multi_window_reviewed_ti_only,label=reviewed_TI_eV,marker=o \
  --output tests/real_case_records/2026-07-11_reviewed_ti_only/output/free_energy_profile.png \
  --rc-order ascending \
  --y-column free_energy_converted \
  --free-energy-unit-label eV \
  --xlabel "Reaction coordinate (au)" \
  --title "Reviewed TI-only free energy profile" \
  --grid \
  --confirm-parameters
```

This plotting step is allowed after the integration convention, selected dataset, RC order, y-column, and unit label are confirmed. It is a visualization artifact only and does not approve TST state selection or rate calculation.

## Review Before TST

Before any TST or rate calculation, the user must still confirm:

- whether this free-energy zero convention is the one desired for barrier extraction,
- which state is the reactant/reference state,
- which point or rule defines the transition state,
- which free-energy column and unit to use,
- temperature,
- prefactor model and prefactor units,
- whether the convergence evidence and uncertainty treatment are sufficient for the intended claim.
