# LAMMPS/PLUMED Failure Cases

Use this reference when LAMMPS exploration, PLUMED coupling, DeePMD pair-style usage, DP-GEN `model_devi_jobs`, trajectories, dumps, restarts, or model-deviation outputs fail or look suspicious. These cases are diagnostic patterns, not proof that exploration is scientifically useful after the immediate issue is fixed.

Some patterns below are informed by public upstream LAMMPS, PLUMED, DeePMD-kit, and DP-GEN issues. Treat those issues as examples of error shapes, interface boundaries, and version sensitivity. Do not copy their systems, atom indices, CVs, timestep, temperature, restraint parameters, model paths, or scheduler settings as defaults for this repository.

## Upstream Issue References

These public GitHub issues are useful as searchable examples of real LAMMPS/PLUMED/DeePMD coupling failures:

- Search LAMMPS issues: [lammps/lammps issues](https://github.com/lammps/lammps/issues).
- Search PLUMED issues: [plumed/plumed2 issues](https://github.com/plumed/plumed2/issues).
- Search DeePMD-kit issues: [deepmodeling/deepmd-kit issues](https://github.com/deepmodeling/deepmd-kit/issues).
- Search DP-GEN issues: [deepmodeling/dpgen issues](https://github.com/deepmodeling/dpgen/issues).
- PLUMED/LAMMPS interface or restart behavior: [plumed/plumed2#555](https://github.com/plumed/plumed2/issues/555), [plumed/plumed2#705](https://github.com/plumed/plumed2/issues/705), [plumed/plumed2#924](https://github.com/plumed/plumed2/issues/924).
- DeePMD LAMMPS pair-style or pair-coeff behavior: [deepmodeling/deepmd-kit#1201](https://github.com/deepmodeling/deepmd-kit/issues/1201), [deepmodeling/deepmd-kit#1809](https://github.com/deepmodeling/deepmd-kit/issues/1809), [deepmodeling/deepmd-kit#4749](https://github.com/deepmodeling/deepmd-kit/issues/4749), [deepmodeling/deepmd-kit#5087](https://github.com/deepmodeling/deepmd-kit/issues/5087).
- Model quality or unstable MLFF behavior in downstream LAMMPS: [deepmodeling/deepmd-kit#5159](https://github.com/deepmodeling/deepmd-kit/issues/5159).
- DP-GEN LAMMPS/PLUMED handoff and `model_devi.out` issues: [deepmodeling/dpgen#1870](https://github.com/deepmodeling/dpgen/issues/1870), [deepmodeling/dpgen#1756](https://github.com/deepmodeling/dpgen/issues/1756), [deepmodeling/dpgen#1757](https://github.com/deepmodeling/dpgen/issues/1757), [deepmodeling/dpgen#1699](https://github.com/deepmodeling/dpgen/issues/1699).

Keep the stage boundary clear:

- LAMMPS exploration generates configurations and trajectories.
- PLUMED may define or bias collective variables during exploration.
- DP-GEN model-deviation filtering may select candidate configurations.
- ABACUS labeling, not LAMMPS, produces first-principles labels.
- Any fix involving timestep, ensemble, thermostat/barostat, temperature/pressure, run length, dump frequency, atom indices, CVs, bias settings, model paths, or trust thresholds requires user confirmation.

## DeePMD Pair Style Or Pair Coefficients Fail

Typical symptoms:

- LAMMPS reports `Unrecognized pair style`, `Incorrect args for pair coefficients`, or a DeePMD C API error.
- `pair_style deepmd` works in one environment but not in a DP-GEN dispatched task.
- A PyTorch model, TensorFlow frozen graph, compressed model, spin model, DPLR model, or hybrid pair style is used with syntax from another version.
- The LAMMPS log fails before producing a valid trajectory or `model_devi.out`.

Likely causes:

- LAMMPS was built without the required DeePMD plugin or uses an incompatible plugin version.
- `pair_coeff` syntax changed between DeePMD-kit versions or model formats.
- Model files in the input script do not match the intended backend or atom types.
- DP-GEN `machine.json` launches a different `lmp` binary than the one tested interactively.

Observed upstream examples:

- DeePMD-kit/LAMMPS pair coefficient errors have been reported across versions: [deepmodeling/deepmd-kit#1201](https://github.com/deepmodeling/deepmd-kit/issues/1201).
- A LAMMPS run reported an unrecognized DeePMD pair style after version/environment changes: [deepmodeling/deepmd-kit#1809](https://github.com/deepmodeling/deepmd-kit/issues/1809).
- Backend/runtime C API errors can surface inside LAMMPS when evaluating DeePMD models: [deepmodeling/deepmd-kit#5087](https://github.com/deepmodeling/deepmd-kit/issues/5087).

Agent response:

1. Ask for LAMMPS version/build, DeePMD-kit version, model format, full LAMMPS log, and the exact `pair_style`/`pair_coeff` lines.
2. Verify syntax against official DeePMD-kit LAMMPS command documentation and the installed `lmp -h` output.
3. Confirm that DP-GEN dispatch uses the same LAMMPS binary and environment as the tested command.
4. Route model-format and frozen-model questions to `deepmd-training`.
5. Do not rewrite pair-style syntax or swap model formats without user approval.

## Type Map Or Atom-Type Mapping Is Wrong

Typical symptoms:

- LAMMPS runs but energies, forces, or model deviations are nonsensical.
- DeePMD reports atom-type or NULL-type related errors.
- `pair_coeff` atom-type mapping does not match the DeePMD training `type_map`.
- LAMMPS data, dump, or restart files have a different atom-type order from the model.

Likely causes:

- LAMMPS numeric atom types were mapped to elements differently from DeePMD training.
- A hybrid pair style uses `NULL` or type placeholders unsupported by the selected model path.
- Data conversion or DP-GEN system generation changed type order.

Observed upstream example:

- A DeePMD LAMMPS issue reported `NULL` atom-type behavior with a PyTorch model path: [deepmodeling/deepmd-kit#4749](https://github.com/deepmodeling/deepmd-kit/issues/4749).

Agent response:

1. Compare LAMMPS atom types, DeePMD `type_map`, DP-GEN `type_map`, and any dpdata conversion summary.
2. Route converted-data checks to `dpdata-format-conversion`.
3. Ask the user to confirm the intended atom-type mapping before editing `pair_coeff`.
4. Do not silently reorder atom types or assume type numbers from another example.
5. Treat suspicious energies/forces as model/domain evidence to review, not just syntax issues.

## PLUMED Coupling Or `fix plumed` Fails

Typical symptoms:

- LAMMPS reports an illegal or unrecognized PLUMED-related fix.
- Build or runtime logs mention PLUMED API/interface incompatibility.
- A DP-GEN enhanced-sampling template uses a project-specific fix name that the installed LAMMPS does not have.
- PLUMED output files are missing even though the run completes.

Likely causes:

- LAMMPS was not compiled with the PLUMED interface expected by the input script.
- PLUMED and LAMMPS interface versions are incompatible.
- The template uses `fix plumed`, `fix dpgen_plm`, or another coupling syntax specific to a patched build.
- Required PLUMED input files were not uploaded by DP-GEN.

Observed upstream examples:

- PLUMED API version incompatibility with the LAMMPS interface has been reported: [plumed/plumed2#555](https://github.com/plumed/plumed2/issues/555).
- A PLUMED/LAMMPS interface compile issue was reported around the typesafe interface: [plumed/plumed2#705](https://github.com/plumed/plumed2/issues/705).
- A DP-GEN enhanced-sampling example reported an illegal `fix dpgen_plm` command in an environment without that fix: [deepmodeling/dpgen#1870](https://github.com/deepmodeling/dpgen/issues/1870).

Agent response:

1. Ask for LAMMPS version/build packages, PLUMED version, coupling method, LAMMPS log, and PLUMED input.
2. Verify the coupling syntax against the installed LAMMPS/PLUMED documentation.
3. Check whether DP-GEN uploaded the PLUMED input file to the task directory.
4. Do not replace a biased template with an unbiased run unless the user approves the scientific change.
5. Do not assume `fix dpgen_plm` and `fix plumed` are interchangeable.

## PLUMED Atom Indices, Units, Or CV Definitions Are Wrong

Typical symptoms:

- PLUMED distance/CV output is impossible, discontinuous, or inconsistent with the trajectory.
- Restraints pull the wrong atoms or bias the wrong coordinate.
- PLUMED uses one unit system while LAMMPS uses another.
- Atom indices in a reference PLUMED file do not match the current LAMMPS data file.

Likely causes:

- PLUMED atom indices are 1-based and were copied from another system.
- LAMMPS atom ordering changed after conversion, replication, sorting, or DP-GEN system generation.
- `UNITS`, PBC handling, `NOPBC`, molecule reconstruction, or component settings were not confirmed.
- CV definitions were copied from the CORR reference example.

Agent response:

1. Ask the user to confirm atom IDs from the current LAMMPS data/dump file.
2. Confirm PLUMED `UNITS`, CV definitions, PBC behavior, output stride, and file names.
3. Route reaction-coordinate design questions back to the relevant scientific workflow discussion.
4. Do not choose CV atom indices, restraint centers, force constants, metadynamics widths/heights, or pace automatically.
5. Treat real PLUMED examples as syntax/style references only.

## LAMMPS Trajectory Is Unstable Or Contains NaN/Inf

Typical symptoms:

- LAMMPS reports `Non-numeric box dimensions`, NaN coordinates, lost atoms, exploding temperature/pressure, or huge energy drift.
- DeePMD runtime errors appear after several MD steps.
- Trajectory frames show atom overlap, broken cell, or chemically unreasonable configurations.
- DP-GEN reports high, NaN, or malformed model deviation for exploration frames.

Likely causes:

- The DeePMD model is outside its training domain.
- Timestep, temperature, pressure, thermostat/barostat, walls, restraints, or bias settings are unsuitable.
- Initial structures or type maps are wrong.
- Restart/coupled PLUMED state is inconsistent.

Observed upstream examples:

- A PLUMED/LAMMPS restart case reported `Non-numeric box dimensions - simulation unstable`: [plumed/plumed2#924](https://github.com/plumed/plumed2/issues/924).
- Large errors after DeePMD training can lead to downstream LAMMPS instability rather than useful exploration: [deepmodeling/deepmd-kit#5159](https://github.com/deepmodeling/deepmd-kit/issues/5159).

Agent response:

1. Stop treating the trajectory as a candidate source until logs and frames are reviewed.
2. Inspect LAMMPS thermo, dump, restart, PLUMED COLVAR, and model-deviation outputs.
3. Ask the user to approve any change to timestep, thermostat/barostat, temperature, pressure, run length, wall/restraint, or bias settings.
4. Route model-domain concerns to `deepmd-training` and DP-GEN trust-level interpretation to `dpgen-active-learning`.
5. Do not send chemically broken structures to ABACUS labeling unless the user has an explicit filtering/debug policy.

## Dump, Restart, Or Trajectory Files Are Missing Or Inconsistent

Typical symptoms:

- LAMMPS completes but expected dump, restart, or trajectory files are absent.
- DP-GEN cannot find `model_devi.out`, `conf.dump`, or uploaded input files.
- Dump frequency does not match DP-GEN candidate extraction settings.
- Atom count, box, or type map changes unexpectedly across frames.

Likely causes:

- `dump`, `thermo`, `restart`, or `write_data` commands are missing or use unexpected file names.
- DP-GEN `model_devi_jobs` template paths do not match uploaded files.
- A restart run writes output to a new path or restarts from a different state.
- LAMMPS task failed before output generation but DP-GEN proceeded to parse expected files.

Observed upstream examples:

- DP-GEN has reported missing uploaded LAMMPS input files: [deepmodeling/dpgen#1757](https://github.com/deepmodeling/dpgen/issues/1757).
- Missing `model_devi.out` has been reported in DP-GEN model-deviation tasks: [deepmodeling/dpgen#1699](https://github.com/deepmodeling/dpgen/issues/1699).

Agent response:

1. Compare LAMMPS input output-file names with DP-GEN expected paths.
2. Check task directories for logs before assuming output files should exist.
3. Use `dpdata-format-conversion` only for shape/readability inspection, not physical validation.
4. Ask before changing dump frequency, file names, restart behavior, or DP-GEN template paths.
5. Do not fabricate missing trajectory/candidate files.

## `model_devi.out` Has Duplicate Timesteps Or Malformed Rows

Typical symptoms:

- `model_devi.out` contains multiple rows for the same timestep.
- DP-GEN candidate selection behaves unexpectedly or fails to classify frames.
- Model-deviation rows do not line up with dump frames.
- NaN values appear in force or virial deviation columns.

Likely causes:

- Custom LAMMPS fixes or swaps output multiple states per nominal timestep.
- Dump/model-deviation output frequencies are inconsistent.
- The model ensemble failed for some frames.
- The trajectory contains invalid geometries.

Observed upstream example:

- Multiple `model_devi.out` rows per timestep were reported when using `fix atom/swap`: [deepmodeling/dpgen#1756](https://github.com/deepmodeling/dpgen/issues/1756).

Agent response:

1. Treat malformed model-deviation output as a DP-GEN exploration failure.
2. Compare `model_devi.out`, LAMMPS dump timesteps, and LAMMPS fixes.
3. Ask whether custom fixes or swaps are intended and how candidate extraction should interpret them.
4. Do not ignore duplicate or NaN rows when declaring convergence.
5. Route candidate-selection policy back to `dpgen-active-learning`.

## DP-GEN Template Substitution Produces Wrong Commands

Typical symptoms:

- Variables such as `V_TEMP`, `V_NSTEPS`, `V_PRES`, or `V_STRIDE` remain unsubstituted.
- LAMMPS exits because a variable is undefined.
- DP-GEN uses a LAMMPS or PLUMED template from a different directory than expected.
- Exploration jobs use a CORR schedule or template unintentionally.

Likely causes:

- `model_devi_jobs` template paths or revision matrices do not match the script variables.
- A reference script's variable names differ from the target DP-GEN config.
- Paths are relative to a different working directory.
- The agent copied the CORR example without reviewing transfer boundaries.

Agent response:

1. Compare `model_devi_jobs` entries with actual variables used in `input.lammps` and PLUMED files.
2. Ask the user to confirm every substituted physical parameter and file path.
3. Keep CORR templates as organization examples, not production defaults.
4. Do not choose an exploration schedule from the reference example.
5. Run static checks before launching expensive exploration when possible.

## Exploration Output Is Mistaken For DFT Labels

Typical symptoms:

- The user wants to add LAMMPS trajectory frames directly to DeePMD training data as labels.
- Candidate structures are treated as ABACUS-labeled data before first-principles labeling.
- `model_devi.out` or PLUMED COLVAR values are mistaken for energy/force labels.

Likely causes:

- The DP-GEN handoff boundary was skipped.
- Exploration and labeling stages were conflated.
- The user focused on trajectory generation and forgot ABACUS labeling.

Agent response:

1. State that LAMMPS exploration generates configurations, not DFT labels.
2. Route selected candidates to `abacus-dft-labeling` for first-principles labeling.
3. Route converted trajectory-shape checks to `dpdata-format-conversion`.
4. Preserve unlabeled configurations separately from labeled DeePMD training data.
5. Do not claim exploration output is ready for DeePMD training without labels.

## How These Cases Connect To Checks

Use the shared static checker for minimal file-shape checks:

```bash
python common/scripts/check_workflow_files.py \
  --software lammps \
  --path PATH_TO_LAMMPS_RUN
```

Use the PLUMED static check for PLUMED inputs:

```bash
python common/scripts/check_workflow_files.py \
  --software plumed \
  --path PATH_TO_PLUMED_INPUT_OR_RUN
```

Route deeper diagnosis by stage:

- DP-GEN `model_devi_jobs`, candidate selection, and trust thresholds: `dpgen-active-learning/references/dpgen-failure-cases.md`.
- DeePMD model files, `pair_style deepmd`, type maps, and model readiness: `deepmd-training/references/deepmd-failure-cases.md`.
- Converted LAMMPS dumps/data/restarts: `dpdata-format-conversion/references/dpdata-failure-cases.md`.
- ABACUS labeling handoff: `abacus-dft-labeling/references/abacus-failure-cases.md`.

LAMMPS/PLUMED scripts are exploration tools. They should produce reviewable trajectories and diagnostics, not replace user-approved physical settings or first-principles labels.
