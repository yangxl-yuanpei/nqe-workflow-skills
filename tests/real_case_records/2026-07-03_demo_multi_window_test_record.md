# Real Multi-Window CHMC/CPIHMC Demo Test Record

Date: 2026-07-03

Dataset location: `../demo` relative to the repository root

Repository output directory: `tests/real_case_records/2026-07-03_demo_multi_window/`

Scope: real multi-window CHMC/CPIHMC-style `energy.dat` diagnostics and mean-force extraction.

Boundary: this record verifies script behavior and records diagnostics. It does not certify sampling convergence, physical correctness, TI readiness, TST readiness, or production validity.

## Input Shape

- Window count: 13
- Windows: `_1.6`, `_1.2`, `_0.8`, `_0.4`, `0.0`, `0.4`, `0.8`, `1.2`, `1.4`, `1.8`, `2.2`, `2.6`, `3.0`
- Files per window: `INPUT`, `STRU`, `energy.dat`
- Missing by design in this dataset: `ALL_INPUT`, `PHY_QUANT`, log/stdout acceptance files
- Total input size outside the repository: about 139 MB
- Per-window `energy.dat` size: about 11.2 MB
- Detected columns for headered files: `Steps KinEng PotEng TotEng dE_dN ElecNum RxnCoord MeanForce`

Some windows begin with a numeric data row rather than a header: `_1.2`, `1.2`, `2.2`, and `2.6`. These windows are useful for testing numeric-column fallback behavior.

## Commands Exercised

`check_chmc_window.py` was initially run for each window with:

```text
--window-dir <window>
--phy-quant-file <absolute path to energy.dat>
--confirm-parameters
--summary tests/real_case_records/2026-07-03_demo_multi_window/check_chmc_window/<window>.txt
```

An initial probe with `--phy-quant-file energy.dat` failed because the script interpreted that path relative to the current working directory rather than relative to `--window-dir`. This was an interface observation, not a data failure. The script was later updated so relative input, log, and physical-output paths resolve under `--window-dir`.

`analyze_phy_quant_convergence.py` was run for each window with numeric columns:

```text
--step-col-index 0
--col-index 2
--col-index 6
--col-index 7
--auto-equilibration
--running-window 1000
--no-plot
--confirm-parameters
```

`extract_mean_force.py` was run for each window with table-format numeric columns:

```text
--format table
--rc-col-index 6
--force-col-index 7
--rc-raw-unit-label au
--force-raw-unit-label au
--uncertainty sem
--confirm-parameters
```

The extracted table is `tests/real_case_records/2026-07-03_demo_multi_window/mean_force_table.csv`.

## check_chmc_window Findings

Acceptance-rate fallback used neighboring-row `KinEng`/`PotEng` changes because no log acceptance file was present. This is a fallback diagnostic, not an internal log counter.

Acceptance rate:

- PASS: `_1.6`, `_1.2`, `_0.8`, `_0.4`, `0.0`
- FAIL below default threshold 0.500: `0.4`, `0.8`, `1.2`, `1.4`, `1.8`, `2.2`, `2.6`, `3.0`

RC consistency:

- PASS: `_1.6`, `_0.8`, `_0.4`, `0.0`, `0.4`, `0.8`, `1.4`, `1.8`, `3.0`
- FAIL: `_1.2`, `1.2`, `2.2`, `2.6`

The RC-consistency failures occurred on the windows where `energy.dat` starts with numeric data rather than a header. `check_chmc_window.py` initially reported that it could not find `RxnCoord` columns, while numeric-column convergence analysis succeeded. The script was later updated to infer a missing header from same-named sibling-window files with matching column counts and to report the inferred source/mapping explicitly.

Initial RC adjustment:

- WARN: `1.8`, `3.0`
- Both reached the target final RC but started 0.4 away from target, consistent with the CHMC/CPIHMC startup-adjustment behavior this repository now records as warning rather than automatic failure.

INPUT/ALL_INPUT:

- SKIP for all windows because `ALL_INPUT` is absent.

## Convergence Diagnostics

All convergence summaries reported `SUGGESTED` auto-equilibration status for the selected columns. This is diagnostic only.

Notable suggested equilibration cutoffs:

- `0.0`: `MeanForce` suggested `eq_index=10000`.
- `1.8`: `RxnCoord` suggested `eq_index=10000`; `MeanForce` suggested `eq_index=5000`.

For no-header windows, summary column names are numeric fallback names such as `col_2`, `col_6`, and `col_7`.

## Mean-Force Extraction

`mean_force_table.csv` contains 13 rows. It was generated to verify multi-window extraction and table shape. Units, sign convention, reaction-coordinate ordering, integration direction, and physical TI readiness still require user confirmation.

Selected extracted rows:

```text
sample_label  reaction_coordinate_raw  mean_force_raw
_1.6          -1.6                     0.00360426375264
_1.2          -1.2                     0.0041884229
_0.8          -0.8                     0.00834479907799
_0.4          -0.4                     0.0067236700767
0.0            0                       0.00355908323083
0.4            0.4                    -0.00640670721707
0.8            0.8                    -0.0104987625976
1.2            1.2                    -0.01549067884
1.4            1.4                    -0.0142515080551
1.8            1.83857238572          -0.00900686911869
2.2            2.2                    -0.00798955167
2.6            2.6                    -0.00352697607
3.0            2.99996399964           0.00123950278503
```

The `1.8` row averages over startup-adjustment samples and therefore reports `reaction_coordinate_raw=1.83857238572` rather than exactly `1.8`. Before TI, the user should decide whether to discard startup/equilibration rows or use a window target via `--window-rc`.

## Not Run

TI integration and TST-rate computation were not run. They require explicit user confirmation of integration direction, zero reference, units, sign convention, state selection, temperature, and prefactor model.

## Follow-Up

- Retest `check_chmc_window.py` on the headerless windows after the relative-path and sibling-header-inference update.
- Consider whether explicit numeric-column options are still needed for cases where no reliable sibling header exists.
- For startup-adjustment windows such as `1.8` and `3.0`, test extraction with equilibration discard or explicit `--window-rc`.
- If the user confirms TI assumptions, integrate `mean_force_table.csv` as a separate postprocessing test.
- Keep the 139 MB raw `../demo` dataset outside the repository; only small summaries and records are stored here.

## Follow-Up Retest After Script Update

Date: 2026-07-08

Script update tested:

- Relative `--input-file`, `--all-input-file`, `--phy-quant-file`, and `--log-file` paths are resolved under `--window-dir`.
- Numeric-first physical-output files can infer a missing header from same-named sibling-window files with matching column counts.
- Header inference is reported explicitly as a `Header Inference` warning.

Retest commands:

```text
check_chmc_window.py --window-dir ../demo/0.4 --phy-quant-file energy.dat --confirm-parameters
check_chmc_window.py --window-dir ../demo/1.2 --phy-quant-file energy.dat --confirm-parameters
```

Observed outcome:

- `0.4`: relative `energy.dat` resolved correctly under the window directory. RC consistency passed. Acceptance remained below the default threshold, which is a diagnostic result unrelated to path resolution.
- `1.2`: headerless `energy.dat` was parsed by inferring the header from sibling file `../demo/0.0/energy.dat`, with mapping `Steps KinEng PotEng TotEng dE_dN ElecNum RxnCoord MeanForce`. The script reported this as `Header Inference` and RC consistency passed.

Additional note:

The updated convergence check now recognizes single-column `MeanForce` as well as `MeanForce_0`, so it may emit mean-force drift warnings that older runs missed. These warnings remain diagnostic and require user review before TI.
