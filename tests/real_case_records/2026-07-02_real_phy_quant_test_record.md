# Real PHY_QUANT Script Test Record

Date: 2026-07-02

Commit: 07b6f3c

Repository status: dirty working tree; this record was created during CHMC/CPIHMC acceptance-fallback development.

Input files:

- `../PHY_QUANT`
- `../INPUT_real`
- `../ALL_INPUT_real`

Stored lightweight input attachments:

- `tests/real_case_records/inputs/INPUT_real`
- `tests/real_case_records/inputs/ALL_INPUT_real`
- `tests/real_case_records/inputs/PHY_QUANT.fileinfo.txt`
- `tests/real_case_records/inputs/PHY_QUANT.sha256.txt`
- `tests/real_case_records/inputs/PHY_QUANT.head_tail.txt`

Input file notes:

- `../PHY_QUANT` size was 44,800,224 bytes.
- Header was `Steps KinEng PotEng TotEng dE_dN ElecNum RxnCoord MeanForce`.
- The first numeric row had `RxnCoord = 0.80`.
- The `INPUT_real` reaction-coordinate target parsed by the window checker was `DIFF_64_141_91 = 0.4000`.
- The final reaction coordinate reported by the window checker was `0.4000`.

## Window Check

Command:

```bash
python chmc-cpihmc-sampling/scripts/check_chmc_window.py \
  --window-dir .. \
  --input-file INPUT_real \
  --all-input-file ALL_INPUT_real \
  --phy-quant-file ../PHY_QUANT \
  --confirm-parameters \
  --summary tests/real_case_records/2026-07-02_chmc_window_summary.txt
```

Result: exit code `1`

Output file:

- `tests/real_case_records/2026-07-02_chmc_window_summary.txt`

Summary:

- `Acceptance Rate`: `FAIL` under the default threshold `0.500`.
- Inferred acceptance source: `energy-delta-inferred`.
- Total inferred acceptance: `0.489`.
- HMC inferred acceptance: `97905/192305 = 0.509`.
- MC inferred acceptance: `97846/207695 = 0.471`.
- `PHY_QUANT Integrity`: `PASS`, with `400001` complete numeric rows and `8` columns.
- `Initial RC Adjustment`: `WARN`, target `0.4000`, first `0.8000`, final `0.4000`, first deviation `0.4000`, final deviation `0.0000`.
- `RC Consistency`: `PASS`, target `0.4000`, final `0.4000`, deviation `0.0000`.
- `Convergence`: `PASS` under the script's simple heuristic.
- `INPUT/ALL_INPUT Agreement`: `PASS`, all `21` explicit `INPUT` parameters matched `ALL_INPUT`.

Interpretation:

- The default acceptance threshold is a screening threshold, not a universal production target.
- The inferred total acceptance `0.489` is slightly below `0.500`, so the default check failed.
- The value should be reviewed together with the user-approved acceptance policy before deciding whether the window is acceptable.
- The fallback acceptance estimate is not an internal program counter; it was inferred from neighboring-row `KinEng` and `PotEng` changes.
- The initial RC adjustment warning is expected for this real case: the initial structure started away from the target, then the final sampled RC matched the target. This is a startup diagnostic, not an automatic window failure.

## Convergence Summary

Command:

```bash
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py \
  --input ../PHY_QUANT \
  --column PotEng \
  --column MeanForce \
  --column RxnCoord \
  --summary tests/real_case_records/2026-07-02_phy_quant_convergence_summary.csv \
  --auto-equilibration \
  --running-window 1000 \
  --no-plot \
  --confirm-parameters
```

Result: exit code `0`

Output file:

- `tests/real_case_records/2026-07-02_phy_quant_convergence_summary.csv`

Summary:

- `PotEng`: `SUGGESTED`, `eq_index = 0`, mean `-11412.955210070504`, SEM `2.8104399069134316e-05`.
- `MeanForce`: `SUGGESTED`, `eq_index = 0`, mean `-0.005712218444453889`, SEM `1.2327067784127206e-05`.
- `RxnCoord`: `SUGGESTED`, `eq_index = 0`, mean `0.4003599991000023`, SEM `1.8965102204371162e-05`.

Interpretation:

- The automatic cutoff is a diagnostic suggestion only.
- The initial `RxnCoord = 0.80` was rapidly adjusted toward the target `0.40`, so an overall `eq_index = 0` suggestion should not be treated as proof that no startup adjustment occurred.
- Plot review and user approval are still required before a production TI handoff.

## Plot Attempt

Command:

```bash
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py \
  --input ../PHY_QUANT \
  --column PotEng \
  --column MeanForce \
  --column RxnCoord \
  --summary tests/real_case_records/2026-07-02_phy_quant_convergence_plot_summary.csv \
  --output tests/real_case_records/2026-07-02_phy_quant_convergence.png \
  --auto-equilibration \
  --running-window 1000 \
  --confirm-parameters
```

Result: exit code `1`

Output files:

- `tests/real_case_records/2026-07-02_phy_quant_convergence_plot_summary.csv`
- No PNG was produced.

Failure reason:

- The local Python environment did not have `matplotlib`.
- The script reported: `matplotlib is required for plotting; use --no-plot for summary-only mode`.

Interpretation:

- Summary-only convergence diagnostics work in the current environment.
- Plot generation needs a Python environment with `matplotlib`.

## Mean-Force Extraction

Command:

```bash
python ti-tst-rate/scripts/extract_mean_force.py \
  --input ../PHY_QUANT \
  --output tests/real_case_records/2026-07-02_real_case_mean_force_table.csv \
  --format phy_quant \
  --dataset-label real_case \
  --sample-label window_target_0p4_all_rows \
  --rc-column RxnCoord \
  --force-column MeanForce \
  --uncertainty sem \
  --notes "diagnostic extraction from real PHY_QUANT; no production equilibration discard approved" \
  --confirm-parameters
```

Result: exit code `0`

Output file:

- `tests/real_case_records/2026-07-02_real_case_mean_force_table.csv`

Summary:

- `reaction_coordinate_raw = 0.4003599991`
- `mean_force_raw = -0.00571221844445`
- `uncertainty_raw = 1.23270677841e-05`
- `n_samples = 400001`
- `equilibration_discard = 0 rows`

Interpretation:

- The extraction path works for this real single-RC `PHY_QUANT` shape.
- This row is diagnostic because no production equilibration discard, unit scaling, sign convention, or TI handoff policy was approved for this test.

## Follow-Up

- `Initial RC Adjustment` was added to `check_chmc_window.py` after this real-case behavior was observed.
- Keep the existing final-RC consistency check as the main window-target consistency check.
- Add future tests for multi-RC startup adjustment and for cases where final RC does not reach the target.
