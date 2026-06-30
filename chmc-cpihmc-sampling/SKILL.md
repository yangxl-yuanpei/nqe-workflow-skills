---
name: chmc-cpihmc-sampling
description: Guidance and checks for CHMC and CPIHMC constrained sampling in the NQE H2 formation workflow. Use when a user asks about classical versus path-integral free-energy sampling, reaction-coordinate definitions, path-integral beads, HMC/MC sampling windows, mean-force outputs, CHMC/CPIHMC use as DP-GEN exploration engines or production samplers, or whether sampling output is ready for thermodynamic integration.
---

# CHMC/CPIHMC Sampling

Use this skill for the in-house constrained HMC/MC sampling stage. CHMC and CPIHMC are two modes of the same in-house code, not separate physical workflows.

## Required Boundary Skills

- Apply `nqe-boundaries` before explaining classical versus quantum sampling or comparing CHMC/CPIHMC with LAMMPS.
- Use `deepmd-training` when the question concerns whether a DeePMD frozen model is ready for sampling.
- Use `dpgen-active-learning` only if CHMC/CPIHMC is being discussed as a possible exploration engine.
- Use `ti-tst-rate` when the question concerns converting mean force to free energy or rate constants.
- Use `nqe-h2-workflow` when the user asks how this stage connects to the full workflow.

## Roles In This Workflow

- Production classical role: CHMC performs constrained HMC/MC sampling without path-integral beads and outputs classical mean force along the reaction coordinate.
- Production quantum role: CPIHMC performs constrained path-integral HMC/MC sampling with beads and outputs NQE-inclusive mean force along the reaction coordinate.
- Optional exploration role: CHMC or CPIHMC may be used as an exploration engine inside DP-GEN only when documented for the specific example.

## What This Skill May Do

- Explain the difference between CHMC and CPIHMC.
- Explain that the classical versus quantum distinction depends on whether path-integral beads are used.
- Help inspect planned sampling inputs for MLFF path, reaction coordinate, temperature, windows, bead number, HMC/MC parameters, equilibration, sampling length, and output format.
- Help inspect mean-force output readiness for thermodynamic integration.
- Produce TODO lists for missing sampling parameters and convergence evidence.

## What This Skill Must Not Do

- Do not choose reaction coordinates, bead number, window positions, HMC step size, HMC step count, equilibration length, production length, or convergence criteria without user approval.
- Do not claim CHMC/CPIHMC results are converged without documented acceptance rates, autocorrelation/mixing checks, and mean-force convergence evidence.
- Do not claim CPIHMC directly outputs H2 formation efficiency.
- Do not claim CPIHMC is a replacement for LAMMPS or more accurate than LAMMPS.
- Do not invent in-house code input fields, commands, paths, or file formats.

## Input Checks

- Confirm the DeePMD frozen model has been accepted for downstream sampling.
- Confirm the reaction coordinate definition is documented and approved.
- Confirm temperature, sampling windows, and output format are documented.
- For CPIHMC, confirm bead number and bead convergence plan are documented.
- Confirm HMC/MC step settings, equilibration, production length, and random seeds are documented or marked TODO.
- Confirm constraints and walls/restrictions are documented if used to stabilize sampling.

## Output Checks

- Check that mean force is reported for each reaction-coordinate window.
- Check uncertainty estimates, autocorrelation, and mixing diagnostics if available.
- Check HMC acceptance rate and abnormal rejection behavior if available.
- Check CPIHMC bead convergence evidence when NQE results are reported.
- Check output format is compatible with thermodynamic integration.
- Report missing diagnostics as TODO rather than declaring convergence.

## References

- Read `references/gc-constrained-pihmc-official-notes.md` for the public GC-Constrained-PIHMC repository documentation, input/output files, units, and recognized parameters.
- Read `references/sampling-checklist.md` for local workflow-specific checks.
- Read repository file `templates/chmc_cpihmc/README.md` for the current placeholder template plan and software-boundary statements.
- Read repository file `docs/overview.md` for the full CHMC/CPIHMC role in the workflow.
