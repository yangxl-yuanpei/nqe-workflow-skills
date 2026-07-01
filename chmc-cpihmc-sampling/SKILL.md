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
- Help plot and summarize `PHY_QUANT` convergence diagnostics for potential energy and mean-force columns after each sampling window.
- Produce TODO lists for missing sampling parameters and convergence evidence.

## What This Skill Must Not Do

- Do not choose reaction coordinates, bead number, window positions, HMC step size, HMC step count, equilibration length, production length, or convergence criteria without user approval.
- Do not claim CHMC/CPIHMC results are converged without documented acceptance rates, autocorrelation/mixing checks, and mean-force convergence evidence.
- Do not treat the automatic cutoff from `scripts/analyze_phy_quant_convergence.py` as proof of equilibration; it is a screening suggestion that requires user review.
- Do not claim CPIHMC directly outputs H2 formation efficiency.
- Do not claim CPIHMC is a replacement for LAMMPS or more accurate than LAMMPS.
- Do not invent in-house code input fields, commands, paths, or file formats.
- Do not treat `PHY_QUANT` or `MODEL_DEVI` as input files; they are output/diagnostic files for TI handoff and model-deviation review.
- Do not enable grand-canonical or constant-potential assumptions for a target system unless the user explicitly documents that physics.

## Grand-Canonical / Constant-Potential Capability

- Recognize grand-canonical CHMC/CPIHMC as an important capability of the GC-Constrained-PIHMC package.
- Explain that grand-canonical electron-number sampling can be used to model electrochemical/constant-potential-like conditions when the method, parameters, and system context are documented.
- Keep this capability separate from the current workflow unless the user explicitly adds electrochemical or constant-potential assumptions. This is a package capability, not a default assumption for an arbitrary target system.
- Require user approval for `Elec_Num_Ratio`, `Mu`, `Elec_Num_Range`, `Elec_Num_Width`, initial electron number in `STRU`, and any interpretation as constant-potential sampling.

- Use `../common/scripts/check_workflow_files.py --software chmc --path PATH_TO_RUN` for a minimal static check of CHMC/CPIHMC `INPUT`, `STRU`, optional `BEADS`, and `PHY_QUANT`/`energy.dat` file shapes. Treat warnings as prompts for human review, not as sampling-convergence proof.

## Input Checks

- Confirm the DeePMD frozen model has been accepted for downstream sampling.
- Confirm the reaction coordinate definition is documented and approved.
- Confirm temperature, sampling windows, and output format are documented.
- For CPIHMC, confirm bead number and bead convergence plan are documented.
- Confirm HMC/MC step settings, equilibration, production length, and random seeds are documented or marked TODO.
- Confirm constraints and walls/restrictions are documented if used to stabilize sampling.

## Output Checks

- Use `scripts/check_chmc_window.py` for a five-part window health check: acceptance rate, `PHY_QUANT`/`energy.dat` row integrity, final RC vs INPUT constraint consistency, potential energy and mean force convergence, and ALL_INPUT vs INPUT parameter agreement. Require `--confirm-parameters` before running.
- For deeper convergence analysis, use `scripts/analyze_phy_quant_convergence.py` when the user asks to inspect `PHY_QUANT` potential-energy or mean-force convergence with plots; ask the user to confirm columns, unit scaling, and equilibration policy before running it.
- Check that mean force is reported for each reaction-coordinate window.
- Check uncertainty estimates, autocorrelation, and mixing diagnostics if available.
- Check HMC acceptance rate and abnormal rejection behavior if available.
- Check CPIHMC bead convergence evidence when NQE results are reported.
- Check output format is compatible with thermodynamic integration.
- Report missing diagnostics as TODO rather than declaring convergence.

## Templates

- Use `templates/INPUT.template`, `templates/STRU.template`, and `templates/BEADS.template` as teaching scaffolds for CHMC/CPIHMC inputs.
- Use `templates/PHY_QUANT.template` and `templates/MODEL_DEVI.template` only as output-shape scaffolds for diagnostics and downstream TI handoff.
- Treat every `TODO_USER_APPROVAL` token as a required user-approved value.
- Read `templates/README.md` and `references/chmc-cpihmc-template-transfer-notes.md` before adapting real or template inputs.
- Read `templates/reference-examples/README.md` when the user provides real CHMC/CPIHMC inputs or outputs from another project.
- Read `references/chmc-cpihmc-real-output-notes.md` when interpreting `ALL_INPUT`, `BEADS`, `PHY_QUANT`, or real CHMC/CPIHMC output files.

## References

- Read `references/chmc-cpihmc-failure-cases.md` when CHMC/CPIHMC runs fail, outputs are missing, or `PHY_QUANT`/`energy.dat` appears truncated.
- Read `references/phy-quant-convergence-diagnostics.md` before plotting or automatically screening `PHY_QUANT` convergence.

- Read `../common/references/command-help.md` when an executable name, command option, subcommand, or version-specific syntax is missing; use official docs and local `-h`/`--help`/`help` output instead of guessing.

- Read `references/gc-constrained-pihmc-official-notes.md` for the public GC-Constrained-PIHMC repository documentation, input/output files, units, and recognized parameters.
- Read `references/sampling-checklist.md` for local workflow-specific checks.
