---
name: nqe-h2-workflow
description: Navigation skill for the NQE H2 formation workflow on graphene/silicate surfaces. Use when a user asks for the end-to-end workflow, stage ordering, how ABACUS, DP-GEN, DeePMD-kit, CHMC/CPIHMC, thermodynamic integration, TST, and KMC connect, or which specialized skill should handle a specific stage.
---

# NQE H2 Workflow

Use this skill as the top-level navigator for the NQE H2 formation workflow. It coordinates the stage order and points to specialized skills. It should not replace the detailed skills for ABACUS, DP-GEN, DeePMD, CHMC/CPIHMC, TI/TST, or KMC.

## Always Apply Boundaries

Before answering, apply the `nqe-boundaries` skill. Do not invent undocumented numerical parameters, commands, thresholds, file names, convergence criteria, or production settings.

## Workflow Map

Use this stage order:

1. Prepare or curate the initial DFT-labeled dataset.
2. Run DP-GEN active learning: training -> exploration -> labeling.
3. Select DP-GEN final frozen models or optionally run specialized DeePMD-kit training.
4. Run CHMC for classical constrained free-energy sampling.
5. Run CPIHMC for path-integral constrained free-energy sampling with NQE.
6. Perform thermodynamic integration on mean-force data to obtain F(xi) and Delta F dagger.
7. Convert activation free energies to elementary TST rate constants.
8. Feed elementary rates into KMC to compute H2 formation efficiency.
9. Generate a report that preserves TODOs and uncertainty labels.

## Stage Routing

- Use `initial-dft-dataset` for questions about starting DFT labels, CINEB/TS/AIMD strategies, data compatibility, and dataset sufficiency checks.
- Use `abacus-dft-labeling` for ABACUS INPUT/STRU/KPT templates, DFT labeling checks, SCF convergence, and label extraction.
- Use `dpgen-active-learning` for train-explore-label loops, model deviation, trust levels, candidate selection, and convergence diagnostics.
- Use `deepmd-training` for DeePMD-kit input.json, training/freeze/test, data format, and model error checks.
- Use `chmc-cpihmc-sampling` for reaction coordinates, CHMC/CPIHMC modes, beads, sampling windows, and mean-force output.
- Use `ti-tst-rate` for mean-force integration, free-energy barriers, TST rate constants, and NQE enhancement factors.
- Use `kmc-h2-efficiency` for event lists, elementary-step rates, lattice assumptions, and formation efficiency.
- Use `nqe-boundaries` whenever reviewing terminology, automation claims, or scientific boundaries.

## What This Skill May Do

- Explain the end-to-end workflow and the physical purpose of each stage.
- Identify which stage a user is asking about and route to the relevant specialized skill.
- Summarize inputs, outputs, checks, and human-approval points for each stage.
- Compare the teaching workflow state with the user's requested action and list missing TODOs.
- Preserve the distinction between a teaching scaffold and a production automation pipeline.

## What This Skill Must Not Do

- Do not generate production input files by itself.
- Do not choose ABACUS settings, DP-GEN trust levels, DeePMD architecture, reaction coordinates, CPIHMC bead number, HMC parameters, TI method, or KMC event lists.
- Do not claim the workflow can run end-to-end unless all required input files, scripts, and execution environments exist.
- Do not claim final H2 formation efficiency from CHMC/CPIHMC output directly; require TI, TST, and KMC stages.

## References

- Read `references/workflow-map.md` for the condensed stage table and the graphene_meta_50K teaching example status.
- Read repository files `docs/overview.md`, `workflow.yaml`, and `examples/graphene_meta_50K/README.md` when more detail is needed.
