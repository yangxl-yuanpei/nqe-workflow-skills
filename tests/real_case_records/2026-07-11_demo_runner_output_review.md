# 2026-07-11 Demo Runner Output Review

Reviewed outputs:

- `tests/real_case_records/2026-07-10_demo_runner_dry_run/output/summary.json`
- `tests/real_case_records/2026-07-10_demo_runner_dry_run/output/mean_force_table.csv`
- `tests/real_case_records/2026-07-10_demo_runner_dry_run/convergence/*.csv`
- `tests/real_case_records/2026-07-10_demo_runner_dry_run/convergence/*.png`

Raw dataset:

- `../demo`, a 13-window CHMC/CPIHMC-style `energy.dat` dataset outside the repository

## Boundary

This review checks runner behavior, output completeness, convergence-screening summaries, and obvious handoff risks before TI. It does not certify physical convergence, free-energy integration readiness, TST readiness, or production correctness.

## Runner Scope Check

Status: `PASS`

- `summary.json` reports `stop_after: extraction`.
- `window_count` is `13`.
- `outputs.mean_force_table` points to `mean_force_table.csv`.
- `outputs.free_energy_profile`, `outputs.tst_rates`, `outputs.mean_force_plot`, and `outputs.free_energy_plot` are all `null`.
- The recorded commands contain 13 convergence-screening calls and 13 mean-force extraction calls.
- Convergence-screening commands include `--no-plot`, so the run produced CSV summaries only.
- Extraction commands use explicit table columns: `--rc-col-index 6` and `--force-col-index 7`.

Interpretation: the runner did not cross into TI, plotting, or TST.

## Output Completeness

Status: `PASS`

- `mean_force_table.csv` contains 13 data rows.
- The convergence directory contains 13 CSV summaries.
- Sample counts in `mean_force_table.csv` are:
  - `99999` rows for 9 windows
  - `100000` rows for 4 windows
- No missing window was observed.

## Mean-Force Table Review

Status: `REVIEW BEFORE TI`

Extracted rows:

```text
sample  rc_raw          rc_minus_label  mean_force_raw    sem          n_samples
_1.6    -1.6            0               0.003604263753    3.4538e-05   99999
_1.2    -1.2            0               0.004188422900    3.1885e-05   100000
_0.8    -0.8            0               0.008344799078    3.3107e-05   99999
_0.4    -0.4            0               0.006723670077    3.0243e-05   99999
0.0      0.0            0               0.003559083231    2.8555e-05   99999
0.4      0.4            0              -0.006406707217    2.5947e-05   99999
0.8      0.8            0              -0.010498762598    2.3906e-05   99999
1.2      1.2            0              -0.015490678840    2.3483e-05   100000
1.4      1.4            0              -0.014251508055    2.5074e-05   99999
1.8      1.83857238572  +0.038572386   -0.009006869119    2.8127e-05   99999
2.2      2.2            0              -0.007989551670    3.2085e-05   100000
2.6      2.6            0              -0.003526976070    3.4378e-05   100000
3.0      2.99996399964  -0.000036000   0.001239502785    3.3106e-05   99999
```

Observed mean-force shape:

- The mean force is positive on the negative-RC side, crosses sign between `0.0` and `0.4`, remains negative through `2.6`, and becomes weakly positive near `3.0`.
- The largest adjacent mean-force change in the extracted table is from `0.0` to `0.4`, about `-0.00997`.
- The `1.8` window has a large extracted RC offset relative to its label: `+0.03857`.

Interpretation: the table is complete and numerically parseable, but it should not be used directly for TI with `skiprows=0` without reviewing equilibration and RC adjustment.

## Convergence-Screening Review

Status: `REVIEW BEFORE TI`

PNG plots were generated after installing `matplotlib` in the local Python environment. Because the bundled Python did not automatically include the user site-packages directory, plotting was run with a temporary `PYTHONPATH` pointing to `C:\Users\94474\AppData\Roaming\Python\Python312\site-packages`.

Plot-display correction: the first generated PNGs used Matplotlib's default y-axis offset notation. For near-constant reaction-coordinate panels, for example `_0.4`, this made a numerically flat `RxnCoord = -0.4` series look like a large trend. `analyze_phy_quant_convergence.py` was updated to disable misleading y-axis offset notation and to give near-constant series a centered y-axis range. The PNGs were regenerated after this correction.

All convergence summaries report `auto_status: SUGGESTED`. This is a screening hint only.

Most windows suggested `equilibration_index_zero_based = 0` for all inspected columns. The following windows require attention:

- `0.0`: `MeanForce` suggested `eq_index = 10000`, using `89999/99999` samples.
- `1.8`: `RxnCoord` suggested `eq_index = 10000`, using `89999/99999` samples.
- `1.8`: `MeanForce` suggested `eq_index = 5000`, using `94999/99999` samples.

Important differences between extracted all-row means and suggested post-equilibration means:

- `0.0` MeanForce:
  - extracted all-row value in `mean_force_table.csv`: `0.003559083231`
  - convergence CSV post-10000 value: `0.003992000644`
  - difference: about `+0.000433`
- `1.8` RxnCoord:
  - extracted all-row value in `mean_force_table.csv`: `1.83857238572`
  - convergence CSV post-10000 value: `1.80061778464`
  - difference: about `-0.037955`
- `1.8` MeanForce:
  - extracted all-row value in `mean_force_table.csv`: `-0.009006869119`
  - convergence CSV post-5000 value: `-0.008729838514`
  - difference: about `+0.000277`

Interpretation: the `1.8` window strongly reflects initial reaction-coordinate adjustment. The current extraction used `skiprows: 0`, so its RC value in `mean_force_table.csv` reflects the full trajectory average rather than the post-adjustment production region suggested by the convergence screen.

Visual plot review:

- `0.0.png`: MeanForce shows a mild early transient and slow running-mean variation. The suggested `10000`-step discard is plausible as a conservative screening choice, but it should be checked by comparing means with several discard values.
- `1.8.png`: RxnCoord shows a clear step-like adjustment from about `2.18` to about `1.8` near the suggested cutoff. This visually confirms that the full-trajectory RC average is not appropriate as a production TI coordinate for this window.
- `_0.4.png`: RxnCoord is flat at about `-0.4`; after the y-axis formatting fix, the panel no longer suggests a false RC drift.

## TI-Handoff Assessment

Current assessment: `NOT READY FOR AUTOMATIC TI`

Reasons:

- The current mean-force extraction used `skiprows: 0` for every window.
- Convergence screening suggests nonzero discard for at least `0.0` MeanForce and `1.8` RxnCoord/MeanForce.
- The `1.8` all-row RC average is visibly offset from the window label and from the post-adjustment convergence mean.
- Integration direction, zero reference, unit conversion, and mean-force sign convention have not been confirmed in this review.

This does not mean the dataset is bad. It means the staged runner output is a useful diagnostic/extraction result, not yet a TI-ready input table.

## Discard Sensitivity Check

Sensitivity output:

- `tests/real_case_records/2026-07-11_discard_sensitivity.csv`

Rows were calculated for `0.0` and `1.8` with `skiprows = 0, 5000, 10000, 20000`. This comparison is diagnostic only and is not a production discard policy.

```text
sample  skiprows  n_samples  rc_raw          mean_force_raw    uncertainty_raw
0.0     0         99999      0               0.003559083231    2.8555e-05
0.0     5000      94999      0               0.003706604164    2.9277e-05
0.0     10000     89999      0               0.003992000644    2.9878e-05
0.0     20000     79999      0               0.004348517781    3.1313e-05
1.8     0         99999      1.83857238572  -0.009006869119    2.8127e-05
1.8     5000      94999      1.82062758555  -0.008729838514    2.9000e-05
1.8     10000     89999      1.80061778464  -0.008425684963    2.9922e-05
1.8     20000     79999      1.8            -0.007896096964    3.1661e-05
```

Interpretation:

- `0.0`: the reaction coordinate is fixed at `0`, but the mean force changes monotonically as more early rows are discarded. This supports treating the `10000`-row suggestion as a real sensitivity point rather than a harmless display artifact.
- `1.8`: the reaction coordinate moves from `1.83857` at `skiprows=0` to `1.80062` at `skiprows=10000` and `1.8` at `skiprows=20000`. This confirms the initial RC adjustment seen in the plot.
- `1.8`: the mean force also changes with discard, from `-0.00900687` at `skiprows=0` to `-0.00842568` at `skiprows=10000` and `-0.00789610` at `skiprows=20000`.
- A per-window discard capability is therefore useful. The user accepted `10000` discarded rows for `0.0` and `1.8` in this demo review only. This is not a reusable production cutoff; production use still requires direct user review of convergence plots/CSVs.

## Recommended Next Steps

1. Use the reviewed demo extraction record at `tests/real_case_records/2026-07-11_reviewed_skiprows_execution_record.md` as the current `../demo` comparison against the `skiprows=0` table.
2. Do not reuse the `10000`-row discard as a default for new production systems.
3. For production-facing runs, require the user to inspect convergence plots/CSVs personally before accepting any discard policy.
4. Only after reviewing the regenerated table should a `stop_after: integration` config be prepared, with explicit integration direction, zero reference, units, and sign convention.
5. Keep TST disabled until the free-energy profile, state selection, temperature, elementary step, and prefactor model are explicitly confirmed.
