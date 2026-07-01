---
name: lammps-exploration
description: Guidance and checks for LAMMPS and PLUMED exploration runs in the NQE H2 formation workflow and DP-GEN active learning. Use when a user asks about LAMMPS input scripts, input.lammps templates, PLUMED input files, collective variables, restraints, metadynamics/biasing, DeePMD pair_style deepmd usage, DP-GEN model_devi_jobs, LAMMPS variables such as V_TEMP/V_NSTEPS/V_PRES/V_STRIDE, trajectory/dump/thermo/PLUMED output checks, exploration scheduling, or whether exploration output is ready for model-deviation selection and ABACUS labeling.
---

# LAMMPS Exploration

Use this skill for LAMMPS-based exploration in DP-GEN and related MLFF sampling workflows. In this repository, LAMMPS is treated as an exploration engine that runs trajectories with DeePMD/Deep Potential models and produces configurations for model-deviation screening.

## Scope

- General: Use LAMMPS input-script, trajectory, thermo, dump, restart, variable, and MLFF pair-style checks for other DP-GEN/MLFF exploration workflows.
- NQE H2-specific: Keep exploration coverage connected to the reaction-coordinate regions and surface configurations needed before CHMC/CPIHMC free-energy sampling.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining exploration settings, timesteps, temperature schedules, biasing, or readiness.
- Use `dpgen-active-learning` when the LAMMPS run is part of DP-GEN `model_devi_jobs`.
- Use `deepmd-training` when the question concerns frozen DeePMD model paths, model ensemble consistency, or `pair_style deepmd` model files.
- Use `abacus-dft-labeling` when selected exploration configurations are handed off for first-principles labeling.
- Use `dpdata-format-conversion` when LAMMPS dumps/data/restarts need to be inspected or converted through dpdata for downstream checking or dataset preparation.

## Roles In This Workflow

- Exploration engine role: LAMMPS generates MD trajectories using DeePMD models during DP-GEN exploration.
- Model-deviation role: DP-GEN compares predictions from multiple DeePMD models on LAMMPS-generated configurations.
- Candidate-generation role: Configurations with model deviation in the user-approved selection window may be sent to ABACUS labeling.
- PLUMED role: Optional PLUMED inputs may define collective variables, restraints, walls, metadynamics, or diagnostic CV output during LAMMPS exploration.

## What This Skill May Do

- Explain the structure of a LAMMPS input script used for DP-GEN exploration.
- Inspect or draft teaching templates for `input.lammps` with variables for temperature, pressure, timestep, run length, restart flag, and model paths.
- Check whether a LAMMPS script records enough thermo and dump information for DP-GEN model-deviation analysis.
- Explain how DP-GEN substitutes values such as `V_TEMP`, `V_NSTEPS`, `V_PRES`, or template paths through `model_devi_jobs`.
- Help separate reusable LAMMPS organization patterns from system-specific physical settings.
- Explain staged exploration strategy together with `dpgen-active-learning`.
- Inspect PLUMED inputs for collective-variable definitions, restraints, output files, units, atom-index assumptions, and user-approved bias settings.

## What This Skill Must Not Do

- Do not choose timestep, ensemble, thermostat/barostat parameters, temperature, pressure, trajectory length, dump frequency, collective variables, PLUMED restraints/biases, metadynamics parameters, or trust-level thresholds without user approval.
- Do not claim LAMMPS exploration is stable without logs, thermo output, trajectory sanity checks, and model-deviation evidence.
- Do not invent LAMMPS commands, variable syntax, pair styles, fix styles, or output filenames; use official LAMMPS or DeePMD-kit documentation.
- Do not treat a LAMMPS trajectory as a DFT label. LAMMPS exploration proposes configurations; ABACUS labeling supplies first-principles labels.
- Do not treat the CORR DP-GEN exploration schedule as an H2/graphene default.

- Use `../common/scripts/check_workflow_files.py --software lammps --path PATH_TO_RUN` for a minimal static check of LAMMPS input/log files. Use `--software plumed` for standalone PLUMED input checks. Treat warnings as prompts for human review, not as trajectory-stability proof.

## Input Checks

- Confirm the LAMMPS input script and data/restart source are documented.
- Confirm units, atom style, boundary conditions, type mapping, masses, and model files match the DeePMD/DP-GEN dataset.
- Confirm `pair_style` and `pair_coeff` syntax are compatible with the installed LAMMPS/DeePMD-kit build.
- Confirm variables substituted by DP-GEN are clearly named and documented.
- Confirm thermostat/barostat, timestep, run length, and output frequency are user-approved.
- Confirm optional PLUMED or bias templates are documented if used.
- Confirm PLUMED atom indices, units, collective-variable definitions, output stride, and bias parameters match the intended system.

## Output Checks

- Check LAMMPS completed without fatal errors.
- Check thermo output for NaNs, extreme temperatures, pressure blow-ups, or energy drift inconsistent with the intended ensemble.
- Check dump trajectories are present, readable, and have consistent atom count, type map, cell, and ordering assumptions.
- Use `dpdata-format-conversion` for dpdata-readable trajectory/data shape inspection; do not treat that as proof of physical stability.
- Check restart and model-deviation outputs are present if required by DP-GEN.
- Check PLUMED output files such as CV traces or restraint diagnostics are present and synchronized with LAMMPS output when PLUMED is used.
- Flag broken trajectories or chemically unreasonable structures for human review before ABACUS labeling.

## Templates

- Use `templates/input.lammps.template` as a teaching scaffold for DP-GEN/LAMMPS exploration scripts.
- Use `templates/input.plumed.template` as a teaching scaffold when PLUMED collective variables, restraints, or biasing are part of exploration.
- Treat every `TODO_USER_APPROVAL` token as a required user-approved value.
- Read `templates/README.md` before adapting the template.
- Read `templates/reference-examples/README.md` when the user provides real LAMMPS scripts from another project.

## References

- Read `references/lammps-failure-cases.md` when LAMMPS or PLUMED exploration fails. This placeholder should be expanded with real observed failures before relying on it for diagnosis.

- Read `../common/references/command-help.md` when an executable name, command option, subcommand, or version-specific syntax is missing; use official docs and local `-h`/`--help`/`help` output instead of guessing.

- Read `references/lammps-official-notes.md` for official LAMMPS and DeePMD-kit documentation entry points.
- Read `references/lammps-exploration-checklist.md` for workflow-specific checks.
- Read `references/lammps-dpgen-handoff.md` for how LAMMPS templates connect to DP-GEN `model_devi_jobs`.

- Read `references/plumed-usage-notes.md` when the user asks about PLUMED syntax, CVs, restraints, metadynamics, output files, or LAMMPS/PLUMED coupling.
