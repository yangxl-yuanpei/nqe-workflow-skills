---
name: nqe-boundaries
description: Boundary and terminology guardrails for the NQE H2 formation workflow. Use when explaining nuclear quantum effects, Born-Oppenheimer DFT labels, DP-GEN active learning, DeePMD MLFFs, CHMC/CPIHMC sampling, TI/TST/KMC handoff, ABACUS labeling, or when checking that an agent response does not invent undocumented parameters or overclaim automation.
---

# NQE Boundaries

Use this skill as the guardrail layer for the NQE H2 formation workflow. Apply it before giving explanations, generating workflow guidance, reviewing text, or deciding whether another workflow skill may act.

## Core Rules

- Treat the agent as a tutor and inspector, not as the researcher making physical decisions.
- Say `not documented yet` or mark TODO when a numerical parameter, command, threshold, file path, convergence criterion, or implementation detail is not documented in the repository.
- Do not claim a step is automated unless an actual script, tool, or workflow specification exists.
- Do not choose DFT settings, reaction coordinates, DP-GEN trust levels, DeePMD architecture, CPIHMC bead number, HMC sampling parameters, or KMC event lists without explicit user-provided values.
- Prefer ABACUS as the documented DFT backend for this teaching workflow.

## Terminology

- Use NQE only for nuclear quantum effects, especially H/proton zero-point energy, nuclear delocalization, and tunneling-related quantum statistical effects.
- Do not call electronic quantum effects NQE.
- Describe ABACUS DFT as an approximate quantum-mechanical treatment of the electronic ground state under the Born-Oppenheimer framework.
- Describe DeePMD-kit / MLFF as learning an approximate Born-Oppenheimer potential energy surface from DFT labels.
- Describe CPIHMC / path-integral sampling as introducing nuclear quantum statistical effects in nuclear degrees of freedom.

## Workflow Boundaries

- Keep the overall workflow separate from the DP-GEN internal loop.
- Overall workflow: initial DFT-labeled dataset -> DP-GEN -> MLFF -> CHMC/CPIHMC -> thermodynamic integration -> TST -> KMC.
- DP-GEN loop: training -> exploration -> labeling.
- Treat model-deviation-based selection as an internal filtering mechanism during or immediately after exploration, not as a fourth main DP-GEN step.
- State that CPIHMC outputs mean force along a reaction coordinate, not final H2 formation efficiency.
- State that TI converts mean force to a free-energy profile and activation free energy, TST converts activation free energy to elementary rate constants, and KMC uses those rate constants for grain-scale efficiency.

## Software Boundaries

- Do not equate LAMMPS with classical MD only; LAMMPS can support path-integral-related methods when configured.
- Do not describe CPIHMC as a quantum replacement for LAMMPS or as more accurate than LAMMPS.
- Distinguish software implementation, sampling method, and physical approximation:
  - software: LAMMPS versus in-house CHMC/CPIHMC code
  - sampling: MD-based versus MC/HMC-based
  - physical approximation: classical nuclei versus path-integral nuclei
- In production free-energy stages, state that this workflow uses CHMC for classical constrained sampling and CPIHMC for path-integral constrained sampling.

## References

- Read `references/boundary-rules.md` for the canonical statements that should be preserved when writing or reviewing NQE workflow text.
