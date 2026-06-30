# ABACUS Labeling Checklist

This reference summarizes ABACUS labeling checks for the NQE H2 formation workflow. It is not a production ABACUS input template.

## Official Documentation Anchors

- ABACUS documentation: https://abacus.deepmodeling.com/en/latest/
- Use official documentation for `INPUT`, `STRU`, `KPT`, output file syntax, supported calculation modes, and keyword meanings.

## Required Inputs

- `INPUT`: calculation control and physical settings.
- `STRU`: atomic structure, lattice/cell, atom types, pseudopotential/basis references, and coordinates.
- `KPT`: k-point sampling when required by the chosen calculation mode.

## Settings Requiring User Approval

- exchange-correlation functional
- pseudopotential type, source, and version
- numerical atomic orbital basis or plane-wave-related basis settings
- cutoff / basis accuracy settings
- k-point mesh
- smearing and occupation settings
- dispersion correction method
- spin polarization, magnetic moments, and charge state
- slab, vacuum, and periodic boundary condition treatment
- SCF convergence threshold and structure/force convergence criteria
- output label format and unit conversion rules

## Initial Dataset Labeling

When ABACUS labels user-prepared initial structures:

- do not generate initial structures automatically
- document the source of each structure
- confirm the ABACUS settings match the intended DP-GEN labeling settings
- check energy, force, and virial labels before training
- flag unconverged or physically unreasonable structures

## DP-GEN Labeling

When ABACUS labels DP-GEN candidate configurations:

- candidates should come from model-deviation filtering in DP-GEN exploration
- ABACUS settings should be consistent with the initial dataset labels
- all completed labels should be checked before appending to the training dataset
- failures should be logged rather than silently included


## Single-Point Labeling Versus Geometry Optimization

For DP-GEN/DeePMD labeling, treat candidate structures as fixed input configurations unless the user explicitly requests a relaxation workflow. The usual labeling goal is to evaluate energy, forces, and optionally virial/stress on the candidate configuration, not to optimize it into a different structure.

When reviewing or generating ABACUS `STRU` files for single-point labeling:

- Preserve atom order, atom count, element mapping, cell vectors, coordinates, and PBC exactly as required by the dataset conversion path.
- Do not change coordinates, relax the slab, or move adsorbates unless the task is explicitly geometry optimization rather than labeling.
- Do not describe movable flags as a default labeling strategy. If ABACUS syntax or a conversion tool requires movable flags, preserve or set them according to the documented tool requirement and user approval.
- Discuss fixed/free atoms only for relaxation, cell-relaxation, or other geometry-optimization tasks.
- For single-point labels, prioritize SCF convergence, complete force output, virial/stress availability when required, unit conversion, and metadata consistency.

## Label Readiness For DeePMD/DP-GEN

Before labels are accepted:

- SCF convergence is documented
- total energy is present
- forces are present for all atoms
- virial/stress is present if required by the training setup
- units and conversion rules are documented
- atom ordering and cell are consistent
- metadata record backend version, functional, pseudopotential, basis, k-points, dispersion, spin/charge, and convergence settings

## Failure Modes To Flag

- non-converged SCF
- missing or incomplete forces
- missing virial when required
- atom count or ordering mismatch
- abnormal high forces or distorted structures
- inconsistent metadata between initial labels and DP-GEN labels
- output parsing ambiguity or unit uncertainty

## Reusable Beyond This Workflow

General reusable parts:

- checking ABACUS `INPUT`, `STRU`, and `KPT` presence
- requiring user-approved functional, pseudopotential, basis, k-points, dispersion, spin, charge, and convergence settings
- checking SCF convergence, energy, forces, virial/stress, units, atom ordering, and metadata
- refusing to declare labels ready from output-directory existence alone

NQE H2-specific parts:

- preserving consistency between initial labels and DP-GEN labels for the NQE H2 workflow
- checking readiness for downstream DeePMD models used by CHMC/CPIHMC
- keeping ABACUS as the documented backend for this teaching repository
