# Initial DFT Dataset Checklist

The initial DFT-labeled dataset is the first source of ground-truth labels for DP-GEN and DeePMD-kit. It is prepared or curated by the user, not by the agent.

## Strategy 1: User-Provided Or Downloaded Data

Use when prior group data, public datasets, literature supplementary files, or previous calculations are available.

Check:

- energy, force, and virial labels exist if required
- atom types and element ordering match the target setup
- units and periodic boundary conditions are compatible
- DFT metadata are compatible with the current project
- the data cover the target reaction and configuration space
- broken, duplicated, or unconverged structures are removed or flagged

## Strategy 2: CINEB / Transition-State / Reaction-Path Data

Use when the elementary step and approximate reaction pathway are chemically understood.

Check:

- initial, final, and transition-state structures are physically reasonable
- enough structures sample the transition-state region
- sampled path covers key regions of the reaction coordinate
- all DFT calculations are converged
- high-force or distorted geometries are inspected rather than blindly included

## Strategy 3: AIMD With Enhanced Sampling

Use when the reaction pathway is unclear or the configuration space is complex.

Check:

- AIMD temperature, timescale, and sampling interval are documented
- enhanced-sampling bias covers the target region
- highly correlated consecutive frames are thinned or documented
- unphysical high-energy structures are removed or flagged
- DFT labeling settings are consistent with the intended MLFF target

## Required Metadata Before DP-GEN

- system identity and target elementary step
- structure source and generation strategy
- DFT backend, currently ABACUS for this teaching workflow
- functional, pseudopotential/basis, dispersion correction, k-points, spin, charge, and SCF criteria
- unit conventions for energy, force, virial, cell, and coordinates
- atom type map and element ordering
- dataset split or validation strategy, if known
- known limitations and TODOs

## Handoff Criteria

Before sending data to DP-GEN, confirm:

- labels are complete and internally consistent
- metadata are sufficient to reproduce the labels
- structures are relevant to downstream CHMC/CPIHMC free-energy sampling
- no undocumented DFT setting mismatch exists between initial data and future DP-GEN labeling
- unresolved decisions are explicitly listed for human approval

## Reusable Beyond This Workflow

General reusable parts:

- comparing initial dataset strategies
- checking energy, force, virial, units, atom ordering, PBC, metadata, and duplicate/broken structures
- requiring DFT setting consistency before MLFF training
- refusing to declare dataset sufficiency without documented validation

NQE H2-specific parts:

- requiring coverage of H2 formation reaction-coordinate regions
- handing off specifically to the ABACUS -> DP-GEN -> DeePMD pipeline in this repository
- preserving downstream CHMC/CPIHMC sampling needs
