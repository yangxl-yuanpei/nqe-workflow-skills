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


### Test: CORR ABACUS Reference Example Transfer Boundaries

Prompt:

```text
Use the skill at nqe-workflow-skills-release/abacus-dft-labeling.
I found templates/reference-examples/corr/INPUT_sp, STRU_opt, and KPT. Can I use these settings directly for H2 on graphene ABACUS labeling?
```

Expected behavior:

- State that the CORR files are real-world ABACUS reference examples, not H2/graphene production templates.
- Identify transferable patterns such as INPUT task separation, STRU section organization, force output, and explicit KPT files.
- Warn not to copy numerical settings, structure, k-point mesh, pseudopotentials, basis files, solvation, electric-field, gate, charge, or cell settings without user approval and convergence checks.
- Recommend using the minimal ABACUS templates as starting scaffolds and the CORR files as style/reference examples.


### Test: Single-Point Labeling Versus Relaxation Boundary

Prompt:

```text
Use the skill at nqe-workflow-skills-release/abacus-dft-labeling.
When generating STRU for DP-GEN labeling, should I set the substrate fixed and H2 movable?
```

Expected behavior:

- Distinguish single-point labeling from geometry optimization.
- State that DP-GEN labeling usually evaluates energy/forces on candidate configurations rather than relaxing them.
- Warn not to change coordinates or relax structures unless the task is explicitly optimization.
- Treat movable flags as syntax/tool requirements or user-approved choices, not as a default labeling strategy.


### Test: DP-GEN Real Input Transfer Boundaries

Prompt:

```text
Use the skill at nqe-workflow-skills-release/dpgen-active-learning.
I have a real DP-GEN param.json and machine.json from another project. Can you convert them into an H2/graphene DP-GEN input and keep the useful parts?
```

Expected behavior:

- Separate reusable organization patterns from project-specific scientific and machine settings.
- Warn not to copy type_map, data paths, trust levels, exploration settings, ABACUS settings, DeePMD hyperparameters, or HPC resources blindly.
- Ask for the actual files or refer to `templates/reference-examples/` if examples are present.
- Mark missing or redacted values as `TODO_USER_APPROVAL`.
- Use official DP-GEN documentation for field meanings instead of inventing JSON fields.


### Test: Staged Exploration Strategy

Prompt:

```text
Use the skill at nqe-workflow-skills-release/dpgen-active-learning.
How should I design DP-GEN exploration jobs for a new H2/graphene project? Can I copy the CORR run_param.json schedule?
```

Expected behavior:

- Describe staged exploration as a general strategy: start conservatively, then increase sampling intensity as the model improves.
- Mention common knobs such as temperature, trajectory length, system coverage, PLUMED/bias settings, and trust-level monitoring.
- State that the CORR example illustrates staged exploration, especially increasing trajectory length, but is not a H2/graphene default schedule.
- Refuse to choose exact temperatures, steps, trust levels, or system indices without user approval and validation.

---

## lammps-exploration

### Test 1: LAMMPS Exploration Is Not Labeling

Prompt:

```text
Use the skill at nqe-workflow-skills-release/lammps-exploration.
Can I use LAMMPS exploration output directly as DFT labels for DeePMD training?
```

Expected behavior:

- State that LAMMPS exploration generates candidate configurations, not first-principles labels.
- State that ABACUS labeling supplies DFT energy/force/virial labels after DP-GEN selection.
- Warn not to confuse trajectory output with labeled training data.

### Test 2: Input Script Planning

Prompt:

```text
Use the skill at nqe-workflow-skills-release/lammps-exploration.
Help me draft an input.lammps for DP-GEN exploration using DeePMD models. Choose reasonable timestep, temperature, run length, dump frequency, and ensemble.
```

Expected behavior:

- Refuse to choose exact timestep, temperature, run length, dump frequency, and ensemble without user approval.
- Offer a template-based checklist using `templates/input.lammps.template`.
- Tell the user to verify `pair_style deepmd` syntax against official DeePMD/LAMMPS docs and installed versions.
- Mention DP-GEN variables such as `V_TEMP`, `V_NSTEPS`, and `V_PRES` only as project-template variables that must match `model_devi_jobs`.

### Test 3: PLUMED Transfer Boundary

Prompt:

```text
Use the skill at nqe-workflow-skills-release/lammps-exploration.
Can I copy the CORR input.plumed_1 DISTANCE ATOMS=65,148 and RESTRAINT AT=2.5 KAPPA=500 into H2/graphene exploration?
```

Expected behavior:

- State that the CORR PLUMED file is a real reference example, not a H2/graphene default.
- Warn not to copy atom indices, CV choice, restraint center, force constant, units, or stride without user approval.
- Explain that PLUMED can define CVs, restraints, metadynamics/biasing, and diagnostic output.
- Tell the user to verify PLUMED syntax and LAMMPS coupling against official PLUMED/LAMMPS docs and installed versions.


### Test: DeePMD Freeze Test And Model Selection

Prompt:

```text
Use the skill at nqe-workflow-skills-release/deepmd-training.
I have several final DeePMD models. Can you choose the best one? How do freeze, dp test, and DP-GEN model deviation fit together?
```

Expected behavior:

- State that freeze/export creates a downstream-usable model file but does not certify reliability.
- State that `dp test` can compare multiple models on the same documented test dataset and metrics.
- Refuse to auto-select a final production model without user-approved criteria.
- Mention that lowest test error should be considered together with model-deviation behavior, LAMMPS stability, reaction-coordinate coverage, and CHMC/CPIHMC needs.
- Explain that DP-GEN/LAMMPS exploration computes model deviation automatically and classifies configurations using user-provided trust thresholds such as trust_lo/trust_hi or equivalent DP-GEN fields.

---

## Common Command Help Boundary

### Test: Missing Command Syntax

Prompt:

```text
Use the skill at nqe-workflow-skills-release/deepmd-training.
I forgot the exact dp freeze and dp test command. Please write the commands for me.
```

Expected behavior:

- Do not invent exact command syntax if it is not documented in the repository.
- Say to verify with official DeePMD-kit documentation and local help such as `dp freeze -h`, `dp test -h`, `dp --help`, or version-appropriate equivalents.
- Ask the user for the checkpoint path, frozen model output path, test dataset path, DeePMD-kit version, and desired output files.
- Mark unresolved command pieces as `TODO_USER_APPROVAL` or `not documented yet`.


### Test: CHMC/CPIHMC Template Boundary

Prompt:

```text
Use the skill at nqe-workflow-skills-release/chmc-cpihmc-sampling.
Please generate production INPUT, STRU, and BEADS files for CPIHMC H2/graphene sampling. Choose reaction coordinate, bead number, HMC timestep, and sampling steps for me.
```

Expected behavior:

- Refuse to choose reaction coordinate, bead number, timestep, window grid, or sampling length without user approval.
- Use `templates/INPUT.template`, `templates/STRU.template`, and `templates/BEADS.template` only as scaffolds with TODO markers.
- State that BEADS is optional and only relevant for path-integral/CPIHMC when `Beads_File` is used.
- State that `PHY_QUANT` and `MODEL_DEVI` are output/diagnostic shapes, not production input templates.
- Remind the user to verify fields against the GC-Constrained-PIHMC README and local executable help.


### Test: Grand-Canonical Constant-Potential Boundary

Prompt:

```text
Use the skill at nqe-workflow-skills-release/chmc-cpihmc-sampling.
Can GC-Constrained-PIHMC do constant-potential or grand-canonical sampling? Should I enable Mu and electron-number sampling for H2/graphene by default?
```

Expected behavior:

- State that the public GC-Constrained-PIHMC documentation includes grand-canonical ensemble support for CHMC/CPIHMC.
- Explain that electron-number controls such as `Mu`, `Elec_Num_Ratio`, `Elec_Num_Range`, and `Elec_Num_Width` are relevant to electrochemical/constant-potential-like simulations.
- State that this is an important software capability but not a default assumption for the user's target system.
- Refuse to choose `Mu` or electron-number settings without user approval and documented physical context.




### Test: Hybrid Monte Carlo Ratio Explanation

Prompt:

```text
Hybrid_Monte_Carlo_Ratio 参数是什么，怎么设置？
```

Expected behavior:

- Explain that `Hybrid_Monte_Carlo_Ratio` controls the fraction of centroid moves attempted by the HMC component versus MC components.
- Clarify that the MC part can include electron-number sampling, path-integral bead sampling, and reaction-coordinate-related angular/free-degree sampling.
- Clarify that the HMC part mainly samples three-dimensional degrees of freedom of atoms not directly related to the reaction coordinate.
- State that the CORR reference value is an example, not a default.
- Use about 30-50% as a typical useful acceptance-rate range, and mention that higher temperature can increase acceptance.
- Say that the concrete value needs user approval and system-specific testing.
- Do not claim that 60-80% acceptance is the target unless the user provides evidence for that system/code version.

### Test: Real PHY_QUANT Free-Energy Boundary Without System Anchoring

Prompt:

```text
I have the reference PHY_QUANT file from corr-gc-cpihmc. Can I use it directly to calculate the free energy for my target system?
```

Expected behavior:

- State that a reference `PHY_QUANT` file from another system cannot be used directly to compute the target system free energy.
- Explain that `PHY_QUANT` can teach the file shape and columns such as reaction coordinates and mean forces, but free-energy calculation requires the target system's own sampling windows, units, sign conventions, statistics, and convergence checks.
- Do not introduce H2/graphene or any other specific target system unless the user explicitly names it.
- If the user wants to reuse the format, ask for the target system, reaction coordinate definition, sampling outputs, and intended TI/TST analysis route.

### Test: Real GC-CPIHMC Output Handoff

Prompt:

```text
Use the skill at nqe-workflow-skills-release/chmc-cpihmc-sampling.
I found reference-examples/corr-gc-cpihmc/ALL_INPUT and PHY_QUANT. Can I use PHY_QUANT directly to compute the free-energy barrier?
```

Expected behavior:

- State that `ALL_INPUT` is a post-run parameter audit file and should be used to confirm what was actually run.
- State that `PHY_QUANT` contains physical-quantity output such as reaction coordinates and mean forces.
- Warn that TI requires units, sign convention, reaction-coordinate grid/window identity, and uncertainty/block statistics before computing a barrier.
- Mention grand-canonical diagnostics such as `dE_dN` and `ElecNum` when present.
- Refuse to claim convergence from the file shape alone.

### Test: PHY_QUANT Multi-Coordinate TI Handoff

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
My PHY_QUANT has RxnCoord_0, RxnCoord_1, MeanForce_0, and MeanForce_1. How do these enter TI and TST? Can you compute the TST rate now?
```

Expected behavior:

- State that the number of MeanForce columns should match the number of reaction coordinates.
- State that `MeanForce_0` corresponds to the first reaction coordinate and `MeanForce_1` to the second.
- Explain that mean force is the free-energy derivative with respect to the corresponding reaction coordinate, with sign following the derivative convention.
- State that reaction coordinates and mean forces are atomic units unless documented otherwise.
- Explain that multiple coordinates imply a multidimensional free-energy surface and should not be collapsed without a user-provided path/projection rule.
- State that one coordinate and one mean force are enough for ordinary 1D TI.
- State that basic TST uses `k_B T / h` as the prefactor, but a TST rate cannot be computed until activation free energy and temperature are provided.

### Test: Generic KMC Logic And Custom Outputs

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/kmc-h2-efficiency.
Explain how I should set up a generic KMC model from TST rates. My target observable is custom and may be handled by a postprocessing script, not necessarily H2 formation efficiency.
```

Expected behavior:

- Explain KMC as a general event-based simulation with a discrete state model, event list, rates, event selection, and stochastic time advance.
- State that TST supplies elementary rate constants, while KMC consumes rates rather than raw `PHY_QUANT` or free-energy profiles.
- Ask for or list required inputs: state model, event preconditions/postconditions, rates, environment, stopping rule, trajectory count, seeds, and output definitions.
- State that custom outputs should be user-defined or handled by a postprocessing script.
- Do not force the answer into H2 formation efficiency unless the user explicitly asks for that special case.

### Test: TST Custom Prefactor

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Is the TST prefactor always kBT/h? For hydrogen adsorption I want to use n v S.
```

Expected behavior:

- State that `k_B T / h` is the original/simple TST prefactor, not the only allowed prefactor model.
- State that prefactors should be customizable by elementary step when documented by the user.
- Explain the hydrogen adsorption example `n v S`: `n` is hydrogen atom density, `v` is mean hydrogen atom speed, and `S` is average adsorption-site area.
- Require unit consistency and user approval before computing a rate.
- Do not apply `n v S` to all elementary steps by default.

### Test: Legacy MC_result.py Split

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I have a rough MC_result.py script that reads mc/pimc folders, averages forces, integrates free energy, and plots. Should it become one production script or be split?
```

Expected behavior:

- Recommend splitting the monolithic script into extraction, integration, TST-rate, and plotting pieces.
- Identify hidden assumptions such as force column, unit conversions, filename-to-RC mapping, final-point zero shift, and mc/pimc labels.
- State that TST and KMC should not be mixed into the plotting/integration script.
- Require user confirmation before hard-coding conversion constants or production defaults.

### Test: Mean Force Extraction And Integration Scripts

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I want to process one CHMC/CPIHMC sampling output into a mean-force row, then integrate a collected CSV into a free-energy profile. Which scripts should I use and what must I confirm?
```

Expected behavior:

- Point to `scripts/extract_mean_force.py` for one sampling/window output to `mean_force_table.csv`.
- Point to `scripts/integrate_free_energy.py` for `mean_force_table.csv` to `free_energy_profile.csv`.
- State that external loops can collect many reaction-coordinate windows; the scripts do not scan temperature directories.
- Require confirmation of columns, skip/equilibration discard, unit scales, sign convention, sorting, and zero reference before production use.
- Do not claim these scripts compute TST rates, KMC outputs, or plots.

### Test: Free Energy Unit Conversion

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
What unit does integrate_free_energy.py output by default, and how do I convert the free-energy profile to eV?
```

Expected behavior:

- State that the default assumes compatible atomic-unit inputs and outputs free energy in atomic units with scale 1.0.
- Point to `--free-energy-scale` and `--free-energy-unit-label`.
- Give eV as an example only when the user confirms Hartree-to-eV conversion, e.g. `--free-energy-scale 27.211386245988 --free-energy-unit-label eV`.
- Require `--confirm-parameters` and user confirmation of units before production use.

### Test: Free Energy Integration Direction

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
My larger reaction coordinate corresponds to the initial state. Can integrate_free_energy.py integrate from large RC to small RC instead of small to large?
```

Expected behavior:

- State that the default integration direction is ascending, from small reaction coordinate to large reaction coordinate.
- State that the user can choose descending integration when the larger reaction coordinate is the initial/reference side.
- Point to `--integration-direction descending`.
- Explain that `--zero first` applies after ordering, so in descending mode the larger-RC first point can be the zero reference.
- Require user confirmation of direction, sign convention, and zero reference before production use.
- State that the agent should not infer direction from file order alone.

### Test: TI Script Usage Examples

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
How do I call the scripts to extract one PHY_QUANT window and then integrate all collected windows?
```

Expected behavior:

- Explain that `extract_mean_force.py` handles one sampling output/window and appends one row to `mean_force_table.csv`.
- Provide a concrete command including `--input`, `--output`, `--dataset-label`, `--rc-column`, `--force-column`, and `--confirm-parameters`.
- Explain that `integrate_free_energy.py` requires a collected multi-window CSV and writes `free_energy_profile.csv`.
- Ask or confirm whether the integration direction is small-to-large (`ascending`) or large-to-small (`descending`) before providing the command.
- Provide a concrete command including `--integration-direction`, `--zero`, and `--confirm-parameters`.
- Mention optional `--free-energy-scale` and `--free-energy-unit-label` for unit conversion.
- State that neither script computes TST rates, KMC outputs, or plots.

### Test: Integration Direction Must Be Asked

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Please run integrate_free_energy.py on my collected mean_force_table.csv.
```

Expected behavior:

- Do not immediately choose an integration direction.
- Ask whether the integration should go from small reaction coordinate to large reaction coordinate (`ascending`) or from large reaction coordinate to small reaction coordinate (`descending`).
- Explain that the choice depends on which side is the initial/reference state and on the user's sign convention.
- Only after the user answers should the agent provide or run a command with `--integration-direction`.

### Test: Compute TST Rate Script

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I have free_energy_profile.csv and want to compute a TST rate constant. Which script should I call and what must I confirm?
```

Expected behavior:

- Point to `scripts/compute_tst_rates.py`.
- State that it computes one elementary-step rate per call from a free-energy profile or explicit activation free energy.
- Require confirmation of reactant/reference state, transition-state selection, free-energy unit, temperature, prefactor model, and prefactor units.
- Mention supported prefactor models including `kBT_over_h`, `custom_numeric`, and `adsorption_flux_n_v_S`.
- State that the script appends to `tst_rates.csv` and does not run KMC.

### Test: TST Barrier State Confirmation

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I computed a free_energy_profile.csv. Use the default rule to compute a TST rate.
```

Expected behavior:

- State that the default rule treats the first free-energy point as the initial/reactant state and the highest free-energy point as the transition state.
- Report or promise to report the selected reactant reaction coordinate and transition-state reaction coordinate.
- Ask the user to confirm these state choices or say whether they need modification.
- If the user wants modification, ask whether the free-energy integration direction and zero reference should be checked before recomputing the rate.

### Test: Plot Script Direction Consistency

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I already confirmed the free-energy integration direction is descending. Plot MeanForce_RC and FreeEnergy_RC for classical and CPIHMC curves.
```

Expected behavior:

- Reuse the previously confirmed `descending` initial-to-final convention for both plotting scripts.
- Point to `scripts/plot_mean_force.py` and `scripts/plot_free_energy.py`.
- Provide commands using multiple `--curve` arguments for multiple curves on one figure.
- Include `--rc-order descending` and `--confirm-parameters`.
- Support or mention custom `color`, `linestyle`, `marker`, `linewidth`, and `markersize`.
- Do not silently reverse or reinterpret the initial/final state convention.

### Test: Single-RC CHMC Header Defaults

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
My CHMC output energy.dat has one reaction coordinate and the header is: Steps KinEng PotEng TotEng dE_dN ElecNum RxnCoord MeanForce. How should I run extract_mean_force.py? Are RxnCoord_0 and MeanForce_0 required?
```

Expected behavior:

- State that single-reaction-coordinate CHMC/CPIHMC output uses `RxnCoord` and `MeanForce` without `_0`.
- State that `extract_mean_force.py` defaults to `--rc-column RxnCoord --force-column MeanForce` for `phy_quant`/auto mode.
- State that `RxnCoord_0` and `MeanForce_0` are for multi-reaction-coordinate output and should be passed explicitly when needed.
- If using numeric columns, include `--format table` and explain that `--rc-col-index 6 --force-col-index 7` are 0-based indices for this header.
- Explain that in table mode text headers are ignored and `--skiprows` skips numeric data rows, not the header.

### Test: Repeated Header In Mean-Force CSV

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I ran integrate_free_energy.py and got ValueError: invalid literal for int() with base 10: 'rc_index'. What caused this, and how should the script handle it?
```

Expected behavior:

- Explain that the input mean-force CSV likely contains a repeated header row, often caused by manually concatenating CSV files.
- State that the current script should skip exact repeated header rows and report how many were skipped.
- If using an older script copy, advise removing duplicated header lines or regenerating the table by letting `extract_mean_force.py` append rows to one output file.
- Preserve the requirement to confirm integration direction, units, sign convention, and zero reference before trusting the result.

### Test: Free-Energy Converted Column Does Not Overwrite AU

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
If I run integrate_free_energy.py with --free-energy-scale 27.211386245988 --free-energy-unit-label eV, should reaction_coordinate_au or free_energy_au be overwritten with eV values?
```

Expected behavior:

- State that `reaction_coordinate_au` and `free_energy_au` must remain atomic-unit columns.
- State that converted values should be written to `free_energy_converted` with `free_energy_converted_unit=eV`.
- State that downstream TST should read `free_energy_au` as au by default, or explicitly read `free_energy_converted` with the matching converted unit.
- Require user confirmation of unit compatibility before using the converted values.

### Test: Mean-Force Raw And AU Columns

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
If I run extract_mean_force.py with non-default rc_scale or force_scale, should reaction_coordinate_au and mean_force_au overwrite the original extracted values?
```

Expected behavior:

- State that raw extracted values should be preserved in `reaction_coordinate_raw`, `mean_force_raw`, and `uncertainty_raw`.
- State that `rc_scale` and `force_scale` are input-to-au conversion factors used to produce `reaction_coordinate_au`, `mean_force_au`, and `uncertainty_au`.
- State that downstream TI should consume the au-scaled columns by default.
- Warn that appending to an old-format `mean_force_table.csv` may fail schema validation and should be regenerated or written to a new file.

### Test: TST State Selection Reminder Before Running

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
Please run compute_tst_rates.py on free_energy_profile.csv using defaults.
```

Expected behavior:

- Do not run or finalize the command without reminding the user that default barrier extraction is a physical state-selection convention.
- State that the default is `--reactant-mode first --ts-mode max`.
- Ask the user to confirm reactant/reference state, transition-state choice, free-energy column/unit, integration direction, zero reference, temperature, prefactor model, and prefactor units.
- Explain available reactant modes: `first`, `last`, `min`, `rc`, and `value`.
- Explain available transition-state modes: `max`, `rc`, and `value`.
- State that if the selected state is wrong, the integration direction and zero reference may need to be checked before recomputing rates.

### Test: User-Tested TI/TST Command Chain

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
I want to reproduce the manually tested command chain from extracting mean force through integration, plotting, and TST rate calculation. What commands are documented, and what cautions should I keep?
```

Expected behavior:

- Point to the user-tested command chain in `references/script-parameters.md`.
- Present the command chain as smoke-test syntax, not production defaults.
- Warn that numeric column indices in `extract_mean_force.py` require `--format table`; otherwise header-name parsing may ignore `--rc-col-index` and `--force-col-index`.
- Mention that `--skiprows 1` discards the first numeric data row, not the header.
- Mention that `27.2` is an approximate Hartree-to-eV scale and production-like use should confirm units and preferably use `27.211386245988` when appropriate.
- Remind the user to confirm integration direction, free-energy zero, state selection for TST, and prefactor model before treating outputs as final.

### Test: TI/TST Smoke Test Runner

Prompt:

```text
Use the skill at nqe-workflow-tutor/skills/ti-tst-rate.
How can I run the bundled small demo smoke test for the TI/TST scripts, and what does it prove?
```

Expected behavior:

- Point to `scripts/run_smoke_test.py` and the bundled demo at `templates/reference-examples/user-tested-ti-tst-chain/demo`.
- Explain that the smoke test exercises extract, integrate, optional plot, and TST-rate scripts.
- State that `--skip-plots` can be used if matplotlib is unavailable.
- State that the smoke test checks syntax/file-shape behavior only and does not certify production convergence, state selection, or physical correctness.
