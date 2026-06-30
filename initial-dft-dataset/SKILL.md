---
name: initial-dft-dataset
description: Guidance and quality checks for preparing the initial DFT-labeled dataset that bootstraps DP-GEN in the NQE H2 formation workflow. Use when a user asks how to obtain starting DFT data, compare user-provided data, CINEB/transition-state, or AIMD/enhanced-sampling strategies, inspect dataset readiness, or connect initial labels to DP-GEN without inventing DFT settings.
---

# Initial DFT Dataset

Use this skill to guide and inspect the initial DFT-labeled dataset stage. This stage is user-controlled and is not automated by the agent.

## Scope

- General: Use the dataset strategy and readiness checks for other DFT-labeled MLFF workflows that need consistent energy, force, virial, structure, metadata, and coverage validation.
- NQE H2-specific: Keep the handoff tied to the documented ABACUS -> DP-GEN -> DeePMD -> CHMC/CPIHMC workflow and preserve reaction-coordinate relevance for H2 formation studies.

## Required Boundary Skills

- Apply `nqe-boundaries` before judging dataset sufficiency or DFT settings.
- Use `nqe-h2-workflow` when the user asks how this stage connects to the full workflow.
- Use `abacus-dft-labeling` only after the user asks for ABACUS-specific labeling templates or output checks.

## Purpose

- Treat the initial DFT-labeled dataset as the starting point for the first DP-GEN training iteration.
- Explain that it should contain consistent energy, force, and virial labels for structures relevant to the target reaction and configuration space.
- Emphasize that dataset quality directly controls the reliability of the downstream MLFF and free-energy calculations.

## Allowed Strategies

Explain these strategies without choosing one automatically:

1. User-provided or downloaded DFT-labeled data.
2. Chemically guided CINEB, transition-state, or reaction-path DFT structure generation.
3. AIMD combined with enhanced sampling.

## What This Skill May Do

- Explain the tradeoffs of the three dataset strategies.
- Inspect a described or provided dataset for expected files, metadata, units, atom ordering, and label completeness.
- Produce a checklist of missing information before DP-GEN can start.
- Suggest chemical regions that may need more user-provided data, while labeling them as suggestions rather than decisions.
- Document assumptions and TODOs for the user to confirm.

## What This Skill Must Not Do

- Do not automatically decide the initial dataset strategy.
- Do not choose reaction paths, transition states, adsorption sites, or initial structures automatically.
- Do not choose ABACUS functional, pseudopotential, basis, k-points, dispersion correction, spin, charge, or SCF criteria.
- Do not claim a dataset is sufficient unless validation criteria and checks are documented and satisfied.
- Do not generate production DFT parameters without user approval.

## Dataset Readiness Checks

- Check energy, force, and virial labels are present when required by the downstream DeePMD/DP-GEN setup.
- Check atom types, element order, type map, units, and periodic boundary conditions are consistent.
- Check DFT metadata are documented: functional, pseudopotential/basis, dispersion correction, spin, charge, k-points, SCF criteria, and backend version.
- Check structures cover the target reaction coordinate and chemically relevant high-energy regions.
- Check duplicated, broken, unconverged, or physically unreasonable structures are identified before training.

## Handoff to DP-GEN

- State that the first DP-GEN training step uses this initial DFT-labeled dataset.
- State that later DP-GEN iterations augment the dataset with ABACUS-labeled uncertain configurations selected by model deviation.
- Require consistency between initial DFT labels and DP-GEN labeling settings.

## References

- Read `references/initial-dataset-checklist.md` for strategy details and inspection checklist.
- Read repository file `docs/initial_dataset.md` for the full teaching explanation when needed.
