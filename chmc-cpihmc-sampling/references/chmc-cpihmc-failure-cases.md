# CHMC/CPIHMC Failure Cases

Use this reference when CHMC/CPIHMC inputs, completed windows, or sampling outputs look inconsistent. These cases are diagnostic patterns, not proof that a run is physically valid after the immediate issue is fixed.

Keep the stage boundary clear:

- CHMC/CPIHMC produces constrained sampling diagnostics and mean-force data.
- It does not directly produce a free-energy barrier, TST rate, KMC rate table, or H2 formation efficiency.
- Any fix involving reaction coordinates, bead counts, HMC/MC settings, electron-number controls, sampling length, or convergence thresholds requires user approval.

## Missing Or Misnamed PHY_QUANT / energy.dat

Typical symptoms:

- A completed window directory contains `INPUT` but no `PHY_QUANT` or `energy.dat`.
- `check_chmc_window.py` reports that no physical-quantity output file was found.
- Downstream `extract_mean_force.py` cannot open the configured sampling output.
- `ALL_INPUT` lists a `Phy_Quant_File` name that differs from the file the agent tried to read.

Likely causes:

- The run failed before physical quantities were written.
- The code wrote to a non-default file name configured by `Phy_Quant_File`.
- The output file was not copied back from the compute directory.
- The agent assumed `PHY_QUANT` when this run used `energy.dat`, or the reverse.

Agent response:

1. Inspect `ALL_INPUT` first when it is available, because it records the effective output file name.
2. Check the run directory for `PHY_QUANT`, `energy.dat`, and any file named by `Phy_Quant_File`.
3. If no output exists, report the window as failed or incomplete; do not fabricate a mean force.
4. If the output name differs from the runner config, ask the user whether to update `input_file`.
5. Do not continue to TI until the target-system window output is present and its columns are confirmed.

## PHY_QUANT / energy.dat Ends With An Incomplete Row

Typical symptoms:

- The last line of `PHY_QUANT` or `energy.dat` stops in the middle of a row.
- One row has fewer columns than the header or neighboring rows.
- A physical-quantity row contains a nonnumeric token where a number is expected.
- `check_chmc_window.py` reports `PHY_QUANT Integrity` as `FAIL`.
- `extract_mean_force.py` or a plotting script fails while parsing the final row.

Likely causes:

- The job was killed while writing physical quantities.
- The scheduler stopped the run at a wall-time limit.
- The allocation, queue budget, or storage quota was exhausted.
- The compute node, filesystem, or job launcher failed during output.
- The user copied a still-running or partially synchronized output file.

Agent response:

1. Treat the window as failed or incomplete, not as a valid short trajectory.
2. Preserve the raw file for audit; do not delete the partial final row silently.
3. Check scheduler logs, stdout/stderr, allocation or quota messages, and file timestamps.
4. Ask the user whether the window should be rerun or whether a complete earlier checkpoint/output exists.
5. Do not trim the half row and continue to TI unless the user explicitly approves a documented recovery policy.

## Missing Or Unexpected Mean-Force Columns

Typical symptoms:

- `analyze_phy_quant_convergence.py` or `extract_mean_force.py` reports a missing `MeanForce`, `MeanForce_0`, or `RxnCoord` column.
- A single-RC file uses `RxnCoord` and `MeanForce`, but the command requested `RxnCoord_0` and `MeanForce_0`.
- A multi-RC file contains `RxnCoord_0`, `RxnCoord_1`, `MeanForce_0`, and `MeanForce_1`, but the command requested the single-RC defaults.
- Numeric column mode reads the wrong columns because the user did not confirm 0-based indices.

Likely causes:

- Single-coordinate and multi-coordinate output conventions were mixed.
- The selected mean-force column does not correspond to the intended reaction coordinate.
- The output came from another project or code version with different headers.
- A table-mode command was copied without confirming column indices.

Agent response:

1. Read the header and list available `RxnCoord*` and `MeanForce*` columns.
2. For single-RC output, map `MeanForce` to `RxnCoord`.
3. For multi-RC output, map `MeanForce_i` to `RxnCoord_i`.
4. Ask the user which reaction coordinate should be handed to TI.
5. Do not collapse multi-dimensional mean-force data into 1D TI unless the user provides a path, projection, or marginalization rule.

## Potential Energy Or Mean Force Does Not Look Equilibrated

Typical symptoms:

- Instantaneous `PotEng` or `MeanForce*` traces drift over the sampled region.
- Cumulative averages continue moving near the end of the trajectory.
- Early and late block means disagree.
- `analyze_phy_quant_convergence.py --auto-equilibration` returns `WARN` or chooses a large suggested cutoff.
- Neighboring reaction-coordinate windows produce visibly jagged or discontinuous mean forces.

Likely causes:

- Equilibration was too short.
- Production sampling was too short.
- The window is poorly mixed or trapped in one region.
- The HMC/MC move settings are not appropriate for this system.
- The reaction-coordinate restraint or wall settings are causing poor sampling.

Agent response:

1. Run or suggest `analyze_phy_quant_convergence.py` on at least `PotEng` and the mean-force column intended for TI.
2. Report the plotted behavior, production mean, SEM, and any automatic cutoff as diagnostics only.
3. Ask the user to review the plot and approve any equilibration discard.
4. Preserve the window as TODO or failed if convergence evidence is insufficient.
5. Do not state that a CSV summary or automatic cutoff proves convergence.

Useful command shape:

```bash
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py \
  --input PHY_QUANT \
  --column PotEng \
  --column MeanForce_0 \
  --summary convergence_summary.csv \
  --output convergence.png \
  --auto-equilibration \
  --confirm-parameters
```

## Acceptance Rate Missing Or Outside The User-Approved Range

Typical symptoms:

- `check_chmc_window.py` reports `SKIP` because no acceptance rate was found.
- The parsed or user-provided acceptance rate is much lower than expected.
- The output shows repeated rejection or almost no accepted HMC/MC moves.
- The user asks the agent to tune HMC/MC parameters automatically.

Likely causes:

- The log file was not provided or uses an unrecognized acceptance-rate format.
- HMC step size, move ratio, wall settings, or temperature may be unsuitable.
- The run is not sampling the intended degrees of freedom efficiently.
- The target acceptance range for this workflow has not been approved for the specific system.

Agent response:

1. Ask for the log file or an explicitly user-provided acceptance rate.
2. Treat the acceptance rate as a diagnostic, not a pass/fail proof by itself.
3. Report whether it is missing, unusually low, or outside the user-approved project range.
4. Ask the user to approve any change to HMC step size, HMC/MC ratio, sampling length, or temperature.
5. Do not choose new HMC/MC settings automatically.

Notes:

- The local checklist notes that about 30-50% acceptance is often useful for this workflow, but this is not a universal production threshold.
- `check_chmc_window.py` has command-line thresholds for screening; those thresholds require user review before production-like use.

## Final Reaction Coordinate Does Not Match The Window Definition

Typical symptoms:

- `check_chmc_window.py` reports an RC consistency failure.
- Final `RxnCoord*` values differ from the window target in `INPUT`.
- The output contains no `RxnCoord*` columns even though the user expected constrained sampling.
- A window directory name suggests one RC value, while `INPUT`, `ALL_INPUT`, or `PHY_QUANT` suggests another.

Likely causes:

- The wrong `INPUT` or output file was paired with the window directory.
- The reaction-coordinate definition was changed but old outputs remain.
- The run did not enforce the expected constraint.
- The agent inferred the window target from directory names rather than from user-approved input metadata.

Agent response:

1. Compare `INPUT`, `ALL_INPUT`, directory naming, and final `RxnCoord*` values.
2. Prefer `ALL_INPUT` for auditing what the code actually used after defaults or normalization.
3. Ask the user which source should define the intended window target.
4. Mark the window as suspect before TI if the intended target and sampled coordinate cannot be reconciled.
5. Do not infer the reaction-coordinate grid from directory names alone.

## INPUT And ALL_INPUT Disagree

Typical symptoms:

- `check_chmc_window.py` reports one or more `INPUT` / `ALL_INPUT` discrepancies.
- `INPUT` contains a value that differs from the effective value in `ALL_INPUT`.
- A parameter spelling differs between the user file and the code-generated audit file.
- The CORR reference example shows `Hybrid_Monte_Cralo_Ratio` in `INPUT` while `ALL_INPUT` records `Hybrid_Monte_Carlo_Ratio`.

Likely causes:

- The code normalized, defaulted, or corrected an input field.
- The run used built-in defaults not visible in the submitted `INPUT`.
- The user edited `INPUT` after the run completed.
- A spelling mismatch or deprecated field name was accepted differently by the code.

Agent response:

1. Preserve raw `INPUT` and `ALL_INPUT`; do not silently normalize the files.
2. Use `ALL_INPUT` when auditing what was actually run.
3. Ask the user whether the difference is expected, a default, or a setup error.
4. Record unresolved differences before downstream TI or model comparison.
5. Do not reuse the effective value for a new system without user approval.

## BEADS File Missing Or Inconsistent For CPIHMC

Typical symptoms:

- A CPIHMC-style run has `N_Bead` or `Bead_Index` settings but no `BEADS` file.
- The `BEADS` line count or coordinate structure does not match the documented bead setup.
- BEADS coordinates appear inconsistent with `STRU` because units were compared directly.
- The user wants to copy a reference `BEADS` file into a new target system.

Likely causes:

- CPIHMC initialization files were not copied.
- Bead count, bead index, or quantized atom list changed without regenerating `BEADS`.
- BEADS coordinates are in Bohr, while another structure file may be interpreted differently.
- The reference example belongs to a different system.

Agent response:

1. Check whether the run is intended to be CHMC or CPIHMC.
2. For CPIHMC, compare `N_Bead`, `Bead_Index`, and `BEADS` shape.
3. Confirm coordinate units before comparing `BEADS` to `STRU`.
4. Treat `BEADS` as initialization data, not a physical observable.
5. Do not copy a reference `BEADS` file into a new target system without user approval and regeneration logic.

## Grand-Canonical Diagnostics Present But Not Intended

Typical symptoms:

- `PHY_QUANT` contains `dE_dN` and `ElecNum`.
- `INPUT` or `ALL_INPUT` contains `Mu`, `Elec_Num_Range`, `Elec_Num_Width`, or `Elec_Num_Ratio`.
- The user did not intend a grand-canonical or constant-potential-like calculation.
- The agent starts interpreting electron-number fluctuations as part of an ordinary fixed-electron workflow.

Likely causes:

- A GC-CPIHMC reference example was copied too directly.
- Grand-canonical fields were left enabled from another project.
- The target workflow actually is electrochemical, but the assumptions were not documented.

Agent response:

1. Identify `dE_dN`, `ElecNum`, and electron-number control fields as grand-canonical/electrochemical diagnostics.
2. Ask whether variable electron number or electrochemical-potential control is intended.
3. If not intended, flag the run configuration for review before TI.
4. If intended, ask the user to confirm `Mu`, electron-number range, width, initial electron number, units, and downstream interpretation.
5. Do not assume grand-canonical physics for a target workflow just because the reference example contains these columns.

## MODEL_DEVI Or MLFF Diagnostics Are Abnormal

Typical symptoms:

- `MODEL_DEVI` is present and suggests high model disagreement.
- The user asks to ignore model-deviation diagnostics because `PHY_QUANT` exists.
- Sampling explores regions outside the DeePMD model's accepted domain.
- CHMC/CPIHMC windows produce plausible-looking mean forces but lack model-validity evidence.

Likely causes:

- The DeePMD model was used outside its training or DP-GEN coverage.
- The reaction-coordinate window enters configurations not covered by active learning.
- Model selection or freeze/test evidence was incomplete before sampling.

Agent response:

1. Treat `MODEL_DEVI` as MLFF uncertainty evidence, not as sampling convergence proof.
2. Ask for DeePMD training, validation/test, model-deviation, and reaction-coordinate coverage evidence.
3. Mark the window as not ready for production TI if model validity evidence is missing or concerning.
4. Route model-readiness questions to `deepmd-training` and active-learning coverage questions to `dpgen-active-learning`.
5. Do not declare the sampling window valid from `PHY_QUANT` shape alone.

## How These Cases Connect To Scripts

Use `check_chmc_window.py` for a conservative window-level screen:

```bash
python chmc-cpihmc-sampling/scripts/check_chmc_window.py \
  --window-dir PATH_TO_WINDOW \
  --confirm-parameters
```

Use `analyze_phy_quant_convergence.py` for detailed `PHY_QUANT` / `energy.dat` convergence plots and CSV summaries:

```bash
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py \
  --input PATH_TO_PHY_QUANT_OR_ENERGY_DAT \
  --column PotEng \
  --column MeanForce \
  --confirm-parameters \
  --output convergence.png \
  --summary convergence.csv
```

Both scripts produce diagnostics. They do not replace user-approved physical interpretation, convergence decisions, or downstream TI/TST/KMC checks.
