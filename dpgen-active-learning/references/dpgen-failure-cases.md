# DP-GEN Failure Cases

Use this reference when `dpgen run`, `param.json`, `machine.json`, training, exploration/model-deviation, first-principles labeling, restart, or task-dispatch behavior fails or looks ambiguous. These cases are diagnostic patterns, not proof that a DP-GEN campaign is scientifically ready after the immediate issue is fixed.

Some patterns below are informed by public upstream DP-GEN issues. Treat those issues as examples of error shapes, workflow boundaries, and version-specific behavior. Do not copy their systems, trust levels, machine settings, DFT settings, or backend choices as defaults for this repository.

## Upstream Issue References

These public GitHub issues are useful as searchable examples of real DP-GEN failures:

- Search all upstream DP-GEN issues: [deepmodeling/dpgen issues](https://github.com/deepmodeling/dpgen/issues).
- Search open and closed issues by symptom, stage, backend, or error text: [deepmodeling/dpgen issue search](https://github.com/deepmodeling/dpgen/issues?q=is%3Aissue).
- Missing executable or command-path problems: [deepmodeling/dpgen#1858](https://github.com/deepmodeling/dpgen/issues/1858), [deepmodeling/dpgen#1832](https://github.com/deepmodeling/dpgen/issues/1832), [deepmodeling/dpgen#1733](https://github.com/deepmodeling/dpgen/issues/1733).
- `machine.json`, dispatcher, or API-version behavior: [deepmodeling/dpgen#1844](https://github.com/deepmodeling/dpgen/issues/1844), [deepmodeling/dpgen#1847](https://github.com/deepmodeling/dpgen/issues/1847), [deepmodeling/dpgen#1913](https://github.com/deepmodeling/dpgen/issues/1913).
- Restart and partial-task continuation: [deepmodeling/dpgen#1678](https://github.com/deepmodeling/dpgen/issues/1678), [deepmodeling/dpgen#1557](https://github.com/deepmodeling/dpgen/issues/1557).
- Model-deviation NaN or missing/malformed output: [deepmodeling/dpgen#1460](https://github.com/deepmodeling/dpgen/issues/1460), [deepmodeling/dpgen#1543](https://github.com/deepmodeling/dpgen/issues/1543), [deepmodeling/dpgen#1699](https://github.com/deepmodeling/dpgen/issues/1699), [deepmodeling/dpgen#1756](https://github.com/deepmodeling/dpgen/issues/1756).
- Exploration LAMMPS/PLUMED template issues: [deepmodeling/dpgen#1870](https://github.com/deepmodeling/dpgen/issues/1870), [deepmodeling/dpgen#1757](https://github.com/deepmodeling/dpgen/issues/1757).
- Data-format/backend mismatch across iterations: [deepmodeling/dpgen#1687](https://github.com/deepmodeling/dpgen/issues/1687), [deepmodeling/dpgen#1753](https://github.com/deepmodeling/dpgen/issues/1753).
- First-principles labeling and ABACUS handoff examples: [deepmodeling/dpgen#1456](https://github.com/deepmodeling/dpgen/issues/1456), [deepmodeling/dpgen#1487](https://github.com/deepmodeling/dpgen/issues/1487).

Keep the stage boundary clear:

- DP-GEN's main loop is `training -> exploration -> labeling`.
- Model-deviation selection is an exploration filter, not a fourth main stage.
- DP-GEN does not certify final MLFF reliability without user-approved convergence evidence.
- This repository documents ABACUS as the open first-principles labeling backend; other upstream issue backends are useful for error patterns only.
- Any fix involving trust levels, exploration conditions, LAMMPS/PLUMED settings, DeePMD training hyperparameters, ABACUS settings, machine resources, or restart policy requires user confirmation.

## `param.json` Or `machine.json` Does Not Match The Installed DP-GEN Version

Typical symptoms:

- `dpgen run param.json machine.json` fails before or during early iteration setup.
- A field from a tutorial, older example, or another site is ignored or rejected.
- Dispatcher API-version, machine schema, or runtime section behavior differs from the example.
- The user asks the agent to repair JSON fields by guessing names.

Likely causes:

- DP-GEN schema and dispatcher conventions are version-specific.
- A tutorial example targets another DP-GEN or dpdispatcher version.
- `param.json` and `machine.json` were copied from a reference project without confirming fields.
- Redacted machine settings were not replaced with site-specific values.

Observed upstream examples:

- Missing or incompatible dispatcher/API behavior has been reported in machine/init paths: [deepmodeling/dpgen#1913](https://github.com/deepmodeling/dpgen/issues/1913).
- General `param.json`/`machine.json` failures often require reading `dpgen.log`, `dpdispatcher.log`, and stage logs together: [deepmodeling/dpgen#1844](https://github.com/deepmodeling/dpgen/issues/1844), [deepmodeling/dpgen#1847](https://github.com/deepmodeling/dpgen/issues/1847).

Agent response:

1. Ask for DP-GEN version, dpdispatcher version, command, `param.json`, `machine.json`, and logs.
2. Use official DP-GEN documentation for the installed version before editing schema fields.
3. Separate scientific workflow fields from machine/resource fields.
4. Mark unknown values as `TODO_USER_APPROVAL`.
5. Do not guess queue, account, resource, dispatcher, or JSON field names.

## Required Executables Or Environment Commands Are Missing

Typical symptoms:

- Logs report missing `dp`, LAMMPS, DeePMD, VASP, ABACUS, MPI, or wrapper commands.
- `execvp` or scheduler logs say an executable cannot be found.
- Training, exploration, or labeling tasks fail repeatedly with the same missing-command error.
- A command works interactively but fails in the dispatched job environment.

Likely causes:

- `machine.json` does not load the same environment as the user's shell.
- Executable names differ between tutorial examples and the local HPC/software stack.
- Modules, conda environments, containers, or remote paths are not configured in dispatcher commands.
- A production backend command was copied from another project.

Observed upstream examples:

- Missing tutorial executables such as `dp`, `lmpdplws`, and `vasplws` were reported: [deepmodeling/dpgen#1858](https://github.com/deepmodeling/dpgen/issues/1858).
- `execvp` failure for a first-principles executable is a common command-path symptom: [deepmodeling/dpgen#1832](https://github.com/deepmodeling/dpgen/issues/1832).
- `mpirun` can fail to locate the requested executable in model-deviation jobs: [deepmodeling/dpgen#1733](https://github.com/deepmodeling/dpgen/issues/1733).

Agent response:

1. Ask for scheduler stdout/stderr, `dpdispatcher.log`, and the exact remote command.
2. Verify executable names with local `-h`/`--help` or official docs when available.
3. Ask the user to confirm environment setup, modules, conda activation, container image, and remote paths.
4. Do not substitute a different executable name or backend without approval.
5. Keep VASP/SIESTA/PWmat issue examples as upstream patterns; do not reintroduce them as this repository's default DFT backend.

## Training Stage Fails Inside DP-GEN

Typical symptoms:

- DP-GEN reports a training job failed multiple times.
- `iter.*/00.train` contains DeePMD logs with NaN, tensor shape mismatch, backend import errors, or runtime failures.
- Training succeeds in one iteration but fails after newly labeled data are added.
- A PyTorch-style setup triggers TensorFlow import errors or vice versa.

Likely causes:

- DeePMD backend and DP-GEN integration settings are inconsistent.
- New labeled data have a different format, type map, optional arrays, or mixed-type layout.
- Training hyperparameters are unstable for the expanded dataset.
- Remote training environment differs from the tested local environment.

Observed upstream examples:

- A PyTorch backend workflow raised a TensorFlow import error in model-deviation context: [deepmodeling/dpgen#1753](https://github.com/deepmodeling/dpgen/issues/1753).
- Mixed-type format inconsistency appeared after iter0 data entered iter1 training: [deepmodeling/dpgen#1687](https://github.com/deepmodeling/dpgen/issues/1687).

Agent response:

1. Route DeePMD-specific log diagnosis to `deepmd-training`.
2. Check type map, data format, new FP data, and converted dataset consistency.
3. Ask whether backend selection, model type, and training template are user-approved for this DP-GEN version.
4. Do not change DeePMD descriptor, learning rate, batch size, or backend automatically.
5. Do not proceed to exploration from failed or partially trained models.

## Exploration LAMMPS Or PLUMED Template Fails

Typical symptoms:

- `01.model_devi` tasks fail with LAMMPS input errors.
- LAMMPS reports an illegal `fix`, missing input file, missing model, or unsupported package.
- PLUMED-enhanced sampling commands fail because the local LAMMPS build lacks the expected interface.
- `model_devi.out` is not produced.

Likely causes:

- The LAMMPS executable lacks required DeePMD or PLUMED support.
- `model_devi_jobs` references a template path that was not uploaded or generated.
- Template syntax depends on a DP-GEN/LAMMPS/PLUMED version not installed locally.
- Exploration settings were copied from another project.

Observed upstream examples:

- A `fix dpgen_plm` command was not recognized in one enhanced-sampling example environment: [deepmodeling/dpgen#1870](https://github.com/deepmodeling/dpgen/issues/1870).
- An upload/path issue reported missing `in.lammps`: [deepmodeling/dpgen#1757](https://github.com/deepmodeling/dpgen/issues/1757).
- Missing `model_devi.out` has been reported after model-deviation tasks: [deepmodeling/dpgen#1699](https://github.com/deepmodeling/dpgen/issues/1699).

Agent response:

1. Route LAMMPS/PLUMED input details to `lammps-exploration`.
2. Confirm the LAMMPS binary supports DeePMD and any required PLUMED/fix features.
3. Check `model_devi_jobs` template paths and uploaded files.
4. Ask the user to confirm atom indices, CVs, timestep, temperature, trajectory length, and plugin requirements.
5. Do not replace a failing enhanced-sampling template with a simpler one unless the user approves the scientific change.

## Model-Deviation Output Is NaN, Missing, Or Malformed

Typical symptoms:

- DP-GEN raises an error that a frame with `f devi nan` belongs to neither accurate, candidate, nor failed categories.
- `model_devi.out` is absent, empty, has duplicated timesteps, or has multiple rows per timestep.
- Candidate counts are surprising or cannot be classified by the configured thresholds.
- The user asks whether to ignore NaN model-deviation frames.

Likely causes:

- Exploration produced invalid geometries or unstable MLFF predictions.
- LAMMPS template settings create repeated output rows or unexpected trajectory frequencies.
- Model ensemble inference failed for some frames.
- Trust thresholds or output parsing assumptions do not match the data.

Observed upstream examples:

- `f devi nan` classification failure has been reported: [deepmodeling/dpgen#1460](https://github.com/deepmodeling/dpgen/issues/1460).
- Multiple outputs per timestep were reported when using `fix atom/swap`: [deepmodeling/dpgen#1756](https://github.com/deepmodeling/dpgen/issues/1756).
- Missing `model_devi.out` appears as a model-deviation stage failure: [deepmodeling/dpgen#1699](https://github.com/deepmodeling/dpgen/issues/1699).

Agent response:

1. Treat NaN or malformed model deviation as a failure signal, not a valid low-deviation sample.
2. Inspect LAMMPS logs, trajectory files, model ensemble paths, and `model_devi.out`.
3. Check whether invalid structures, bad boxes, atom overlap, or unsupported fix behavior occurred.
4. Ask the user to confirm how to handle bad frames and whether exploration settings should be reduced.
5. Do not claim convergence from candidate counts when model-deviation output is malformed.

## Candidate Extraction Or FP Handoff Fails

Typical symptoms:

- `02.fp` cannot find `conf.dump` or another selected configuration file.
- The trajectory dump frequency and FP candidate extraction frequency are inconsistent.
- Candidate directories are created but required structure files are absent.
- Labeling tasks start from the wrong or missing frame.

Likely causes:

- `traj_freq`, dump settings, and DP-GEN candidate extraction settings are inconsistent.
- LAMMPS or PLUMED template writes different file names than DP-GEN expects.
- Model-deviation output references frames not present in the trajectory dump.

Observed upstream example:

- A `02.fp` failure reported missing `conf.dump` due to trajectory-frequency mismatch: [deepmodeling/dpgen#1143](https://github.com/deepmodeling/dpgen/issues/1143).

Agent response:

1. Compare LAMMPS dump frequency, `model_devi.out` timestep spacing, and FP candidate extraction settings.
2. Inspect the selected candidate directories before launching labeling.
3. Ask whether the user wants to rerun exploration or adjust output frequencies.
4. Do not fabricate missing candidate structures.
5. Do not continue to ABACUS labeling from incomplete FP handoff directories.

## First-Principles Labeling Fails Or Produces Incompatible Labels

Typical symptoms:

- `02.fp` tasks fail or label outputs are missing.
- ABACUS output files are absent after a dispatched job.
- Generated ABACUS `STRU` or input misses spin/magnetic, cell, pseudopotential, basis, or element metadata.
- Newly labeled data cannot be converted back into DeePMD training data.

Likely causes:

- ABACUS input generation lost system-specific metadata.
- Remote work directories were cleaned before outputs were copied back.
- DFT settings are inconsistent with the initial dataset.
- Labeling backend settings were copied from another project.

Observed upstream examples:

- Missing copied ABACUS output after remote cleanup has been reported: [deepmodeling/dpgen#1456](https://github.com/deepmodeling/dpgen/issues/1456).
- ABACUS `STRU` generation missing magnetic moment handling was reported: [deepmodeling/dpgen#1487](https://github.com/deepmodeling/dpgen/issues/1487).

Agent response:

1. Route ABACUS settings and output checks to `abacus-dft-labeling`.
2. Preserve scheduler logs, remote paths, and copied output directories for audit.
3. Check consistency between initial DFT labels and DP-GEN FP labels.
4. Ask the user to confirm spin, magnetic moments, pseudopotentials, basis files, k-points, convergence thresholds, and output-copy policy.
5. Do not treat a selected candidate as labeled until complete energy, force, and required virial data are present.

## Restart Or Resume Does Not Continue The Intended Tasks

Typical symptoms:

- Restart creates a new scratch/remote directory instead of continuing unfinished tasks.
- Completed FP or model-deviation tasks are repeated unexpectedly.
- The user wants to rerun `dpgen run` and assume it will pick up exactly where it stopped.
- Logs mention recovered submissions but job state remains inconsistent.

Likely causes:

- DP-GEN/dpdispatcher restart semantics are version- and stage-specific.
- Local iteration state and remote work directories disagree.
- Partial outputs were removed, moved, or not copied back.
- The previous failure left incomplete bookkeeping JSON.

Observed upstream examples:

- FP restart creating a new scratch directory instead of continuing was reported: [deepmodeling/dpgen#1678](https://github.com/deepmodeling/dpgen/issues/1678).
- Users have asked how to restart from model-deviation jobs after unexpected termination: [deepmodeling/dpgen#1557](https://github.com/deepmodeling/dpgen/issues/1557).

Agent response:

1. Do not recommend blind rerun until local and remote state are inspected.
2. Check iteration directories, task status files, remote roots, scheduler status, and copied outputs.
3. Ask the user whether to resume, rerun a stage, or archive and start a clean iteration.
4. Preserve partial outputs and logs before cleanup.
5. Use official DP-GEN/dpdispatcher restart documentation for the installed version.

## Trust Levels Or Convergence Are Overclaimed

Typical symptoms:

- The user asks the agent to choose `tol_lo`, `tol_hi`, or equivalent trust thresholds.
- Candidate counts decrease, and the user wants to declare convergence immediately.
- Model-deviation distributions look good for generic exploration but not for reaction-coordinate regions.
- DP-GEN has completed a fixed number of iterations, and the user asks whether that is enough.

Likely causes:

- Trust thresholds were treated as universal defaults.
- Candidate counts were used without checking label success, training stability, and downstream coverage.
- Reaction-relevant configurations were not included in exploration or labeling.

Agent response:

1. Refuse to choose trust thresholds without user-approved evidence.
2. Review model-deviation distributions, candidate/failed fractions, trends across iterations, label convergence, and DeePMD training stability.
3. Ask whether exploration covered the intended CHMC/CPIHMC reaction-coordinate regions.
4. Preserve missing convergence evidence as TODO.
5. Do not claim DP-GEN convergence from iteration count or decreasing candidates alone.

## Placeholder Or Reference Example Is Treated As Production Input

Typical symptoms:

- The user wants to run `templates/reference-examples/placeholder-real-example/` as a real DP-GEN example.
- CORR `run_param.json` or `machine.json` values are copied into a new H2/graphene or other target system.
- Redacted paths, queues, accounts, or system-specific settings appear in a runnable config.

Likely causes:

- Reference examples were mistaken for reusable defaults.
- Transfer boundaries were not reviewed.
- The agent filled missing values from nearby examples.

Agent response:

1. State that CORR examples show file organization and staged-exploration patterns only.
2. State that `placeholder-real-example` is not a real DP-GEN production example.
3. Ask the user to confirm type map, systems, trust levels, exploration settings, DeePMD training, ABACUS labeling, and machine settings.
4. Keep redacted or unknown values as `TODO_USER_APPROVAL`.
5. Do not generate a production `param.json` or `machine.json` from examples alone.

## How These Cases Connect To Checks

Use the shared static checker for minimal file-shape checks:

```bash
python common/scripts/check_workflow_files.py \
  --software dpgen \
  --path PATH_TO_DPGEN_RUN_OR_INPUTS
```

Use stage-specific skills after locating the failing stage:

- DeePMD training logs or frozen models: `deepmd-training/references/deepmd-failure-cases.md`.
- LAMMPS/PLUMED exploration templates or trajectories: `lammps-exploration`.
- ABACUS first-principles labeling: `abacus-dft-labeling/references/abacus-failure-cases.md`.
- Data conversion back into DeePMD format: `dpdata-format-conversion/references/dpdata-failure-cases.md`.

The checker and references are diagnostic aids. DP-GEN readiness still requires user-approved initial data, trust levels, exploration coverage, successful labels, stable training, model-deviation evidence, and downstream reaction-coordinate coverage.
