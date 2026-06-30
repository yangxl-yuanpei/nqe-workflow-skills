# NQE Workflow Skills

This directory contains agent-readable skills for teaching and inspecting the NQE H2 formation workflow. The skills are designed to help an agent explain the workflow, preserve scientific boundaries, route questions to the right stage, and check readiness before any production calculation is claimed.

This is currently a teaching and guidance skills library, not a one-click production automation pipeline.

## Workflow Scope

The documented workflow is:

```text
initial DFT-labeled dataset
  -> DP-GEN active learning
    -> DeePMD/MLFF model
      -> CHMC/CPIHMC mean-force sampling
        -> thermodynamic integration
          -> activation free energy
            -> TST elementary rates
              -> KMC H2 formation efficiency
```

ABACUS is the documented DFT backend for this teaching repository. DeePMD-kit and DP-GEN provide the MLFF and active-learning layer. GC-Constrained-PIHMC is the public reference implementation for the CHMC/CPIHMC sampling layer.

## Skills Index

| Skill | Purpose | Status |
|---|---|---|
| `nqe-boundaries` | Terminology and behavior guardrails for NQE, DP-GEN, CHMC/CPIHMC, TI/TST/KMC, and undocumented parameters | ready |
| `nqe-h2-workflow` | Top-level navigation across the end-to-end workflow | ready |
| `initial-dft-dataset` | Strategies and checks for the user-prepared initial DFT-labeled dataset | ready |
| `abacus-dft-labeling` | ABACUS input/output and DFT labeling checks | ready |
| `dpgen-active-learning` | DP-GEN train -> exploration -> labeling loop, model deviation, and convergence checks | ready |
| `lammps-exploration` | LAMMPS exploration scripts, trajectory sanity checks, and DP-GEN model-deviation handoff | ready |
| `deepmd-training` | DeePMD-kit data, training, freeze/test, model-deviation, and model-readiness checks | ready |
| `chmc-cpihmc-sampling` | CHMC/CPIHMC constrained sampling, reaction-coordinate, bead, and mean-force checks | ready |
| `ti-tst-rate` | Mean force -> free energy -> activation barrier -> TST rate handoff | ready |
| `kmc-h2-efficiency` | Elementary rates -> KMC event network -> H2 formation efficiency checks | ready |

## General Versus NQE-Specific Layers

Some skills are reusable beyond this H2 workflow:

- `initial-dft-dataset`
- `abacus-dft-labeling`
- `dpgen-active-learning`
- `deepmd-training`
- `lammps-exploration`

These contain `Scope` and `Reusable Beyond This Workflow` sections that distinguish general DFT/MLFF workflow checks from NQE H2-specific requirements.

Other skills are intentionally workflow-specific:

- `nqe-boundaries`
- `nqe-h2-workflow`
- `chmc-cpihmc-sampling`
- `ti-tst-rate`
- `kmc-h2-efficiency`

These preserve the scientific identity of the workflow: nuclear quantum effects, CHMC/CPIHMC mean-force sampling, TI/TST, and KMC formation efficiency.

## Official Documentation References

The software-facing skills include official documentation notes:

- `abacus-dft-labeling/references/abacus-official-notes.md`
- `dpgen-active-learning/references/dpgen-official-notes.md`
- `deepmd-training/references/deepmd-official-notes.md`
- `chmc-cpihmc-sampling/references/gc-constrained-pihmc-official-notes.md`

Use these references as roadmaps to official documentation. They are not copies of the full manuals and should not be treated as production parameter defaults.

## Current Boundaries

The agent may:

- explain workflow stages and physical meaning
- route a question to the correct skill
- inspect whether required files, settings, metadata, or diagnostics are missing
- produce TODO lists and readiness checklists
- use official documentation notes to avoid inventing software behavior

The agent must not:

- invent numerical parameters, commands, paths, thresholds, or file formats
- choose DFT settings, DP-GEN trust levels, DeePMD hyperparameters, reaction coordinates, CPIHMC bead numbers, HMC settings, or KMC event lists without user approval
- claim the teaching scaffold is a production automation pipeline
- claim CPIHMC directly outputs H2 formation efficiency
- claim KMC can use raw CHMC/CPIHMC mean force or trajectories directly

## Tests

Manual behavior tests live in:

```text
skills/tests/manual_prompts.md
```

Run these prompts in a fresh agent/conversation to check whether the skills preserve boundaries, consult official documentation, and avoid overclaiming.

## Scripts

The first diagnostic script is available at:

```text
skills/deepmd-training/scripts/parse_lcurve.py
```

This script parses DeePMD-kit `lcurve.out`-style logs for basic diagnostics. It does not certify model readiness. More scripts should be added only after the corresponding teaching content and templates are stable.

## Recommended Next Work

1. Expand teaching docs such as `docs/glossary.md` and `docs/troubleshooting.md`.
2. Add input templates with explicit user-approved placeholders for ABACUS, DP-GEN, and DeePMD-kit.
3. Add CHMC/CPIHMC and KMC templates after their concrete input formats and physical assumptions are confirmed.
4. Add deterministic checking scripts for templates and outputs.
5. Build a mock demonstration example for external users.

## Design Principle

The library should make an agent careful before it becomes automated. The first job is to teach the workflow and preserve expert judgment; execution scripts and production templates come after the scientific boundaries are clear.
