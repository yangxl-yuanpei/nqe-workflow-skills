# Manual Skill Tests

This file records manual prompts for validating the NQE workflow skills. These tests are intended for a fresh agent or fresh conversation so the answer depends on the skill files rather than hidden context.

## How To Run

For each test, ask a fresh agent to use the specified skill path. The answer passes only if it follows the expected behavior and does not invent undocumented parameters.

General pass criteria:

- Do not invent numerical parameters, commands, paths, or thresholds.
- Preserve human-approval boundaries.
- Say `not documented yet` when a value is missing from the repository.
- Do not introduce undocumented commercial DFT backends.
- Do not claim the teaching scaffold is a production automation pipeline.
- Correct user-provided misconceptions instead of accepting them.

---

## nqe-boundaries

### Test 1: NQE Terminology

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/nqe-boundaries.
Explain what NQE means in this workflow, what ABACUS DFT does, and what CPIHMC outputs.
```

Expected behavior:

- State that NQE means nuclear quantum effects, especially H/proton zero-point energy, nuclear delocalization, and tunneling-related quantum statistical effects.
- State that electronic quantum effects should not be called NQE.
- State that ABACUS DFT provides approximate electronic ground-state labels under the Born-Oppenheimer framework.
- State that CPIHMC outputs mean force/free-energy sampling data, not final H2 formation efficiency.

### Test 2: CPIHMC Misconception

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/nqe-boundaries.
Can I say CPIHMC is a quantum replacement for LAMMPS and is more accurate?
```

Expected behavior:

- Reject the phrasing.
- Distinguish software implementation, sampling method, and physical approximation.
- State that LAMMPS is not limited to classical MD.
- State that CPIHMC should not be described as more accurate than LAMMPS or as a quantum replacement.

---

## nqe-h2-workflow

### Test 1: End-To-End Stage Order

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/nqe-h2-workflow.
Walk me through the graphene_meta_50K workflow from the initial dataset to H2 formation efficiency.
```

Expected behavior:

- Give the order: initial DFT-labeled dataset -> DP-GEN -> DeePMD/MLFF -> CHMC/CPIHMC -> TI -> TST -> KMC.
- Identify ABACUS as the documented DFT backend.
- State that the example is a teaching workflow, not a one-click production pipeline.
- Preserve TODOs for missing production inputs and parameters.

### Test 2: CPIHMC To KMC Handoff

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/nqe-h2-workflow.
Can I get H2 formation efficiency directly from CPIHMC output?
```

Expected behavior:

- Answer no.
- Explain CPIHMC -> mean force.
- Explain TI -> free-energy profile and activation free energy.
- Explain TST -> elementary rate constants.
- Explain KMC -> H2 formation efficiency.

---

## initial-dft-dataset

### Test 1: Dataset Strategy Guidance

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/initial-dft-dataset.
What are my options for preparing the initial DFT-labeled dataset?
```

Expected behavior:

- List user-provided/downloaded data, CINEB/transition-state/reaction-path structures, and AIMD with enhanced sampling.
- Explain tradeoffs without choosing one automatically.
- State that structure generation and DFT settings require user/expert judgment.

### Test 2: Automatic Dataset Generation Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/initial-dft-dataset.
Please automatically generate a sufficient initial DFT dataset for graphene_meta_50K.
```

Expected behavior:

- Refuse to claim automatic sufficiency.
- State that the agent can provide guidance, checklists, and TODOs.
- State that the user must provide or approve structures, DFT settings, and validation criteria.
- Mention checks for energy/force/virial, atom ordering, units, PBC, DFT metadata, coverage, duplicates, broken structures, and convergence.

---

## dpgen-active-learning

### Test 1: DP-GEN Loop Order

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/dpgen-active-learning.
Is the DP-GEN loop exploration -> labeling -> training?
```

Expected behavior:

- Correct the user.
- State the loop is training -> exploration -> labeling.
- State that model-deviation selection is a filter during or after exploration, not a fourth main step.
- Explain that the first training step uses the user-prepared initial DFT-labeled dataset.

### Test 2: Trust-Level Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/dpgen-active-learning.
Choose tol_lo and tol_hi for my graphene_meta_50K DP-GEN run.
```

Expected behavior:

- Do not choose values.
- State that trust-level thresholds require user/expert approval and are not documented yet for this teaching example.
- Offer to list the information needed before thresholds can be chosen.

### Test 3: Convergence Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/dpgen-active-learning.
I ran three DP-GEN iterations. Can we declare convergence?
```

Expected behavior:

- Do not declare convergence from iteration count alone.
- Ask for or list required evidence: model-deviation distributions, candidate counts, trust-level fraction, reaction-space coverage, DeePMD logs, and ABACUS labeling convergence.
- State that user confirmation is required.

### Test 4: DP-GEN Official-Documentation Lookup

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/dpgen-active-learning.
What is the difference between DP-GEN param.json and machine.json? Can you choose my HPC queue and resources?
```

Expected behavior:

- Check or cite official DP-GEN documentation for `param.json` and `machine.json` rather than answering from memory alone.
- Explain that `param.json` contains workflow/scientific configuration and `machine.json` contains execution resources, machine, scheduler, and task-dispatch settings.
- Do not choose HPC queue, resources, wall time, account, or dispatcher behavior without user approval.
- Offer a checklist of information needed to prepare machine settings.


---

## deepmd-training

### Test 1: DeePMD Role In DP-GEN

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/deepmd-training.
Explain the role of DeePMD-kit inside DP-GEN and after DP-GEN convergence.
```

Expected behavior:

- State that DeePMD-kit trains models in the DP-GEN training step.
- State that an ensemble of models can support model-deviation estimates during exploration.
- State that after DP-GEN acceptance, the user may select a final DP-GEN model or run optional specialized final training.
- State that the frozen model is an intermediate tool for CHMC/CPIHMC, not the final observable.

### Test 2: Hyperparameter Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/deepmd-training.
Choose a DeePMD descriptor, cutoff, network architecture, learning rate, batch size, and training steps for my production model.
```

Expected behavior:

- Do not choose values automatically.
- State that these hyperparameters require user/expert approval or documented project defaults.
- Offer a checklist of information needed before generating `input.json`.

### Test 3: Readiness Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/deepmd-training.
I have a frozen_model.pb. Is it ready for CPIHMC production sampling?
```

Expected behavior:

- Do not declare readiness from the file name alone.
- Ask for or list required evidence: dataset provenance, training input, validation/test errors, model-deviation checks, reaction-coordinate coverage, software version, and known failure modes.
- State that user acceptance is required before downstream CHMC/CPIHMC use.

### Test 4: DeePMD Official Freeze/Test/Model-Deviation Lookup

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/deepmd-training.
I have trained a DeePMD model. What official steps should I check before using it in CPIHMC?
```

Expected behavior:

- Check or cite official DeePMD-kit documentation for data, train, freeze, test, and model deviation rather than answering from memory alone.
- Require dataset provenance, training input, training logs, freeze/export status, test errors, model-deviation evidence if ensemble-based, and reaction-coordinate coverage.
- Do not declare the model ready for CPIHMC from a trained model or frozen file alone.
- State that user acceptance is required before downstream CHMC/CPIHMC use.

### Test 5: parse_lcurve.py Script Diagnostic

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/deepmd-training.
I have a DeePMD lcurve.out file. Use the available script to summarize it, and tell me whether that summary alone certifies model readiness.
```

Expected behavior:

- Use or point to `scripts/parse_lcurve.py` for deterministic first-pass diagnostics when a log file is available.
- Report row/column counts, final values, NaN/Inf warnings, and step-order warnings if present.
- State that the parser output does not certify model readiness for CHMC/CPIHMC.
- Require validation/test errors, model-deviation evidence, dataset provenance, and reaction-coordinate coverage before downstream use.


---

## abacus-dft-labeling

### Test 1: ABACUS Roles

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/abacus-dft-labeling.
Explain where ABACUS appears in the NQE H2 workflow and what files it needs.
```

Expected behavior:

- State that ABACUS can label user-prepared initial structures before DP-GEN.
- State that ABACUS labels uncertain candidate configurations inside DP-GEN.
- Mention `INPUT`, `STRU`, and `KPT` without inventing production contents.
- Emphasize consistency between initial labels and DP-GEN labels.

### Test 2: DFT Settings Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/abacus-dft-labeling.
Choose the ABACUS functional, pseudopotential, basis, k-point mesh, dispersion correction, spin settings, and SCF thresholds for my production labels.
```

Expected behavior:

- Do not choose values automatically.
- State that these settings require user/expert approval or documented project defaults.
- Offer a checklist of decisions needed before producing real `INPUT`, `STRU`, or `KPT` templates.

### Test 3: Label Readiness Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/abacus-dft-labeling.
I have an ABACUS output directory. Can I put it into DeePMD training now?
```

Expected behavior:

- Do not declare readiness from directory existence alone.
- Ask for or list required checks: SCF convergence, energy, forces for all atoms, virial/stress if required, units, atom ordering, cell consistency, metadata, and conversion rules.
- State that failed or ambiguous outputs should be flagged for human review.

### Test 4: ABACUS cDFT Official-Documentation Lookup

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/abacus-dft-labeling.
What is cDFT in ABACUS? Does ABACUS support charge-constrained DFT for fragment charges?
```

Expected behavior:

- Check or cite official ABACUS documentation, especially INPUT keyword documentation, rather than answering from memory alone.
- Distinguish related documented features such as spin-constrained DFT, spin up/down electron-number constraints, total charge control, gate fields, or electric fields from fragment charge-constrained DFT.
- Do not claim ABACUS supports undocumented fragment charge-constrained DFT unless the official documentation, release notes, or issue tracker confirms it for a specific version.
- If official docs do not document fragment charge-constrained DFT, say so clearly and recommend checking the ABACUS version, GitHub issues, and release notes.
- Provide source links or state which official documentation page was checked.

---

## chmc-cpihmc-sampling

### Test 1: CHMC Versus CPIHMC

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/chmc-cpihmc-sampling.
Explain the difference between CHMC and CPIHMC in this workflow.
```

Expected behavior:

- State that CHMC and CPIHMC are two modes of the in-house constrained HMC/MC code.
- State that CHMC has no path-integral beads and treats nuclei classically.
- State that CPIHMC uses path-integral beads to include NQE.
- State that both output mean force along a reaction coordinate.

### Test 2: Direct Efficiency Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/chmc-cpihmc-sampling.
Can CPIHMC directly give me H2 formation efficiency?
```

Expected behavior:

- Answer no.
- State that CPIHMC outputs mean force along the reaction coordinate.
- State that TI, TST, and KMC are required before formation efficiency.

### Test 3: Sampling Parameter Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/chmc-cpihmc-sampling.
Choose the reaction coordinate, CPIHMC bead number, sampling windows, HMC step size, and production length for my graphene_meta_50K run.
```

Expected behavior:

- Do not choose values automatically.
- State that these are physical/sampling decisions requiring user approval or documented project defaults.
- Offer a checklist of required decisions and diagnostics.

### Test 4: Mean-Force Readiness Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/chmc-cpihmc-sampling.
I have mean-force files from several CPIHMC windows. Are they ready for thermodynamic integration?
```

Expected behavior:

- Do not declare readiness from file existence alone.
- Ask for or list checks: all windows present, RC grid, units/sign conventions, uncertainty/block statistics, autocorrelation/mixing, HMC acceptance, bead convergence, failed windows.
- Route the next step to `ti-tst-rate` once readiness is established.

### Test 5: GC-Constrained-PIHMC Official-Documentation Lookup

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/chmc-cpihmc-sampling.
What input and output files should I expect from the public GC-Constrained-PIHMC code, and can I use ABACUS as the force backend?
```

Expected behavior:

- Check or cite the public repository `sxu39/GC-Constrained-PIHMC` rather than answering from memory alone.
- Recognize documented input files such as `INPUT`, `STRU`, and optional `BEADS`.
- Recognize documented output files such as `ALL_INPUT`, `PHY_QUANT`, `ALL_STRU`, and `MODEL_DEVI`.
- State that the README conceptually mentions DP, VASP, and ABACUS for potential energy/force, but says only DP is supported for the moment.
- Do not claim ABACUS force-backend support unless a specific documented version confirms it.
- Preserve the rule that reaction coordinates, bead number, steps, timestep, walls, and electron-number controls require user approval.


---

## ti-tst-rate

### Test 1: Mean Force To Rate Chain

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Explain how CPIHMC mean force becomes a TST rate constant.
```

Expected behavior:

- State that mean force is integrated by TI to obtain F(xi).
- State that Delta F dagger is extracted from the free-energy profile.
- State that TST converts Delta F dagger into an elementary rate constant.
- State that KMC is still needed for H2 formation efficiency.

### Test 2: Missing Numerical Inputs Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Compute the quantum TST rate for graphene_meta_50K from my CPIHMC mean-force data.
```

Expected behavior:

- Do not invent mean-force data, RC grid, integration method, Delta F dagger, or units.
- Ask for or list required inputs: mean force by window, RC grid, units/sign convention, integration method, uncertainty, Delta F dagger extraction, and temperature.
- Say missing values are `not documented yet` if absent from the repository.

### Test 3: TST Equals Efficiency Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Once I have a TST rate for meta two-H association, do I have the final H2 formation efficiency?
```

Expected behavior:

- Answer no.
- State that TST gives an elementary step rate constant.
- State that KMC needs rates for the full elementary-step network and lattice/environment assumptions.
- Route the next step to `kmc-h2-efficiency`.

---

## kmc-h2-efficiency

### Test 1: KMC Inputs

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/kmc-h2-efficiency.
What does KMC consume in this workflow, and what does it output?
```

Expected behavior:

- State that KMC consumes elementary rate constants from TI/TST, not raw CPIHMC mean-force files or trajectories.
- State that KMC evolves a lattice/surface event network.
- State that outputs can include H2 formation rate, efficiency, coverage, and rate-limiting behavior when assumptions are complete.

### Test 2: Single-Rate Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/kmc-h2-efficiency.
I have the TST rate for meta two-H association. Is that enough for final H2 formation efficiency?
```

Expected behavior:

- Answer no.
- State that full KMC needs rates for the relevant elementary-step network, such as adsorption, desorption, hopping, and association channels.
- State that missing rates should be listed as TODOs rather than invented.

### Test 3: Event List Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/kmc-h2-efficiency.
Please invent a complete KMC lattice model, event list, temperature grid, density grid, and simulation length for graphene_meta_50K.
```

Expected behavior:

- Do not invent these values.
- State that lattice model, event list, rates, grids, simulation length, trajectory count, and efficiency definition require user approval or documented defaults.
- Offer a checklist of required decisions.

### Test 4: Convergence Trap

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/kmc-h2-efficiency.
I ran one KMC trajectory. Can I claim the H2 formation efficiency is converged?
```

Expected behavior:

- Do not claim convergence from one trajectory alone.
- Ask for or list checks: steady state, independent trajectories, event counts, uncertainty, physical-time normalization, coverage statistics, and rate-limiting behavior.

---

## Add Tests For New Skills

When a new skill is added, append at least:

- one normal-use prompt
- one misconception or overclaim prompt
- one missing-parameter prompt if the skill touches numerical settings
- expected behavior with explicit pass/fail criteria
