# NQE Postprocess Runner Failure Cases

Use this reference when `nqe_postprocess_runner.py` config parsing, dry-run command generation, child-script execution, or output review fails. These cases are diagnostic patterns, not proof that the underlying CHMC/CPIHMC, TI, TST, or KMC assumptions are physically valid after the immediate issue is fixed.

Keep the stage boundary clear:

- The runner orchestrates already confirmed postprocessing steps.
- It does not choose reaction coordinates, columns, units, integration direction, state selection, temperature, prefactor, convergence thresholds, or KMC event networks.
- It calls CHMC/CPIHMC convergence diagnostics and TI/TST scripts as helper commands.
- Any fix involving scientific interpretation or physical parameters requires user confirmation.

## Config Is Not Confirmed

Typical symptoms:

- The runner raises `Refusing to run until config contains parameters_confirmed: true`.
- A config has `parameters_confirmed: false`, omits the field, or contains `TODO_USER_APPROVAL`.
- The user asks the agent to flip the flag to `true` so the command can run.

Likely causes:

- The config is a draft or example file.
- Some scientific choices have not been approved.
- The user copied `assets/config.example.yaml` or `assets/config.convergence-screening.example.yaml` without reviewing every field.

Agent response:

1. Do not change `parameters_confirmed` to `true` automatically.
2. List the unconfirmed fields and ask for user approval.
3. Keep draft configs non-runnable with `parameters_confirmed: false`.
4. Treat bundled assets as layout examples, not target-system defaults.
5. Run only `--dry-run` after the config is fully confirmed.

## Config Parser Rejects YAML Or JSON

Typical symptoms:

- The runner reports `Unsupported config line`.
- A nested YAML list, mapping, quoted value, or inline comment is parsed unexpectedly.
- A JSON config fails to load because of trailing commas or invalid syntax.
- A boolean value such as `maybe`, `Truee`, or `TODO` fails an `as_bool` check.

Likely causes:

- The runner intentionally supports only flat YAML or JSON using the Python standard library.
- A config contains nested structures not supported by the simple YAML parser.
- A boolean, number, path, or list-like value was written in a form the runner does not parse.

Agent response:

1. Explain that the runner expects flat key-value YAML or valid JSON.
2. Convert nested YAML to flat keys only after preserving user-approved values.
3. For comma-separated list fields such as `convergence_columns`, confirm the intended list before rewriting.
4. Do not use parser success as evidence that the scientific choices are valid.
5. Keep unsupported config features out of runnable examples.

## Required Fields Are Missing

Typical symptoms:

- The runner raises `Missing required config field: sampling_output_root`, `dataset_label`, `integration_direction`, `elementary_step`, `temperature_K`, `reactant_mode`, or `ts_mode`.
- `compute_tst: true` is enabled but TST-specific fields are absent.
- A child script fails because a required flag was not generated.

Likely causes:

- A config was shortened for testing but then run as if complete.
- `compute_tst`, `plots`, or convergence screening was enabled without required companion fields.
- The user assumed the runner would infer physical choices from directory names or examples.

Agent response:

1. Identify which stage needs the missing field.
2. Ask the user to confirm the value rather than filling it from examples.
3. If TST is not intended, ask whether `compute_tst: false` should be set.
4. If plotting is not intended or dependencies are unavailable, ask whether `plots: false` should be set.
5. Do not infer integration direction, state selection, temperature, or prefactor model.

## Path Resolution Points To The Wrong Place

Typical symptoms:

- The runner cannot find `sampling_output_root`.
- `ti-tst-rate scripts not found` appears after setting `ti_tst_scripts_dir`.
- Relative paths work from one current working directory but not another.
- Output appears under an unexpected directory.

Likely causes:

- Paths are resolved relative to the config file, not the shell's current working directory.
- The config file was moved without updating relative paths.
- An override path was copied from another machine or repository checkout.

Agent response:

1. Resolve paths relative to the config file and show the resolved path to the user.
2. Check whether the target exists before running.
3. Prefer repository-relative config examples only for bundled demos.
4. Ask before rewriting project paths in a config.
5. Do not silently redirect outputs to a new location.

## Window Discovery Finds Too Few Or Wrong Windows

Typical symptoms:

- The runner raises `Need at least two windows containing 'energy.dat'`.
- A root directory has many subdirectories, but only some contain the configured `input_file`.
- A window directory name suggests one RC value, but the file inside belongs to another window.
- The root itself is included as a window because it contains the configured input file.

Likely causes:

- `sampling_output_root`, `input_file`, or `window_glob` is wrong.
- Failed CHMC/CPIHMC windows did not produce output files.
- Output files use `PHY_QUANT` while the config expects `energy.dat`, or the reverse.
- Directory names were used as proxy metadata without checking `INPUT`, `ALL_INPUT`, or the output columns.

Agent response:

1. List discovered windows and their input files during dry-run review.
2. Compare the configured `input_file` with `ALL_INPUT` or run-directory contents when available.
3. Treat missing or partial windows as upstream CHMC/CPIHMC failures, not as empty TI points.
4. Ask whether failed windows should be rerun, excluded with a documented reason, or left TODO.
5. Do not fabricate missing windows or infer RC values from directory names alone.

## Bad Or Truncated Window Output Enters TI

Typical symptoms:

- `extract_mean_force.py` fails on one window but earlier windows already wrote rows.
- `PHY_QUANT` or `energy.dat` ends mid-row.
- A row has fewer columns than the header.
- The runner discovers the file because it exists, but the file is not a complete sampling output.

Likely causes:

- The CHMC/CPIHMC job was killed while writing.
- A scheduler wall-time, allocation, storage quota, or copy/sync failure produced partial output.
- The runner currently discovers files by presence, not by full window health.

Agent response:

1. Route the window to `chmc-cpihmc-sampling` failure cases.
2. Run or suggest `check_chmc_window.py` before TI when output completeness is uncertain.
3. Preserve raw partial files for audit.
4. Do not trim partial final rows unless the user approves a documented recovery policy.
5. Do not continue to free-energy integration from a partially generated mean-force table.

## Convergence Screening Is Misread As Approval

Typical symptoms:

- `run_convergence_diagnostics: true` generates plots and CSV summaries, and the user wants to proceed to TI automatically.
- `--auto-equilibration` suggests a cutoff, and the user asks the runner to apply it silently to `skiprows`.
- Convergence columns are missing or point to the wrong mean-force component.

Likely causes:

- Screening diagnostics were mistaken for a convergence proof.
- The config's `convergence_columns` were copied from a single-RC demo to a multi-RC output.
- The user has not reviewed `PotEng`, `MeanForce`, or `MeanForce_i` traces.

Agent response:

1. State that convergence outputs are screening aids only.
2. Ask the user to review potential-energy and mean-force behavior before TI.
3. Keep `convergence_skiprows` and extraction `skiprows` separate unless the user explicitly approves a policy.
4. For multi-RC outputs, confirm which `MeanForce_i` corresponds to the intended `RxnCoord_i`.
5. Do not claim the runner proves equilibration or sampling sufficiency.

## Child Script Fails After Partial Outputs Are Written

Typical symptoms:

- The runner stops with a nonzero child-script exit.
- `mean_force_table.csv` exists but `free_energy_profile.csv` does not.
- `free_energy_profile.csv` exists but `tst_rates.csv` does not.
- A rerun appends duplicate rows or mixes outputs from a previous attempt.

Likely causes:

- Extraction succeeded for some windows before one failed.
- Integration failed because the collected table had too few rows, bad schema, or wrong labels.
- TST failed because state selection, temperature, prefactor, or free-energy units were inconsistent.
- Existing output files were not inspected before rerun.

Agent response:

1. Identify which child command failed from the printed command list.
2. Inspect the failing stage's output and route to the corresponding failure reference: CHMC/CPIHMC, TI/TST, or dpdata if relevant.
3. Treat partial outputs as diagnostic artifacts, not production results.
4. Before rerun, decide whether to write to a new output directory or user-approve cleanup.
5. Do not append to or reuse partial CSVs without checking schema and provenance.

## Dry-Run Commands Are Surprising

Typical symptoms:

- Dry-run shows unexpected paths, columns, units, integration direction, state-selection modes, temperature, or prefactor.
- The generated command contains `--format auto` when the user expected numeric table mode.
- `--rc-col-index` or `--force-col-index` appears without an intended `--format table`.
- Plot commands use a direction inconsistent with integration.

Likely causes:

- The config field names do not match the schema.
- A value was inherited from a demo config.
- The user changed the config but did not rerun dry-run.
- Plotting, integration, and TST conventions were reviewed separately and drifted.

Agent response:

1. Stop before real execution.
2. Compare the dry-run commands against the user's intended paths, columns, units, direction, state selection, temperature, and prefactor.
3. Edit the config only after user approval.
4. Rerun dry-run after edits.
5. Do not proceed from dry-run to real execution silently.

## Free-Energy Or TST Defaults Are Treated As Physical Choices

Typical symptoms:

- A config uses `integration_direction: ascending`, `zero: first`, `reactant_mode: first`, or `ts_mode: max` because they were in an example.
- `free_energy_scale` and `free_energy_unit_label` are copied from a demo.
- `prefactor_model: kBT_over_h` is assumed for every elementary step.
- The user asks the runner to compute "the rate" without defining the elementary step.

Likely causes:

- Script conventions were mistaken for physical state definitions.
- Example values were copied into a new system.
- TST was enabled before confirming barrier extraction and prefactor model.

Agent response:

1. Route state-selection and unit questions to `ti-tst-rate`.
2. Ask the user to confirm integration direction, zero reference, reactant/reference state, transition-state selection, free-energy unit, temperature, elementary-step label, and prefactor model.
3. Use `compute_tst: false` until TST choices are confirmed.
4. Do not report TST rates as final KMC observables.
5. Preserve unconfirmed values as TODOs in non-runnable drafts.

## Output Directory Already Contains Results

Typical symptoms:

- A previous `mean_force_table.csv`, `free_energy_profile.csv`, `tst_rates.csv`, or `summary.json` exists in `output_dir`.
- The runner removes known output CSV/JSON files before a real run.
- Plot or convergence files from a previous run remain and may be confused with new outputs.

Likely causes:

- The same `output_dir` is reused across attempts.
- A failed run left partial outputs.
- The runner cleans only selected output files and does not fully validate old plots or convergence summaries.

Agent response:

1. Inspect `output_dir` before rerunning.
2. Prefer a fresh output directory for materially different configs.
3. Ask the user before deleting or overwriting outputs.
4. Record which run produced which outputs.
5. Do not merge outputs from different configs without provenance.

## Summary Exists But Physical Review Is Missing

Typical symptoms:

- `summary.json` exists and lists commands, windows, and outputs.
- The user asks whether this means the postprocessing is complete.
- TST output exists, but reactant/transition-state selections have not been reviewed.
- Convergence diagnostics exist, but no human review is recorded.

Likely causes:

- Successful script execution was mistaken for scientific validation.
- `summary.json` records orchestration provenance, not physical acceptance.
- Downstream KMC requirements were not checked.

Agent response:

1. Explain that `summary.json` is a provenance and output-index file.
2. Review generated mean-force, free-energy, convergence, and TST outputs with the appropriate stage skills.
3. Ask the user to confirm TST state selections and prefactor before KMC.
4. Preserve missing convergence, uncertainty, or KMC event-network evidence as TODOs.
5. Do not call the workflow production-ready from runner success alone.

## How These Cases Connect To Commands

Always start with dry-run:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  PATH_TO_CONFIRMED_CONFIG.yaml \
  --dry-run
```

Run for real only after the dry-run commands are accepted:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  PATH_TO_CONFIRMED_CONFIG.yaml
```

If a child command fails, route diagnosis by stage:

- CHMC/CPIHMC window or `PHY_QUANT`/`energy.dat` issue: `chmc-cpihmc-sampling/references/chmc-cpihmc-failure-cases.md`.
- Mean-force extraction, integration, plotting, or TST issue: `ti-tst-rate/references/ti-tst-failure-cases.md`.
- Format conversion or label-shape issue before postprocessing: `dpdata-format-conversion/references/dpdata-failure-cases.md`.
- KMC handoff issue after TST: `kmc-h2-efficiency` references and checks.

The runner is an orchestration helper. It should make postprocessing more reproducible, not less reviewable.
