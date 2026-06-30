# ABACUS Official Notes

Use this reference as a source-of-truth roadmap for ABACUS file syntax and command meanings. Do not copy production settings from examples without user approval.

## Source Of Truth

- Official documentation: https://abacus.deepmodeling.com/en/latest/
- Input files overview: https://abacus.deepmodeling.com/en/latest/quick_start/input.html
- Output files overview: https://abacus.deepmodeling.com/en/latest/quick_start/output.html
- DP-GEN interface entry: https://abacus.deepmodeling.com/en/latest/advanced/interface/DP-GEN.html

Use official docs for keyword meanings, file syntax, output-file interpretation, and supported calculation modes.

## Files To Recognize

- `INPUT`: calculation type and settings. The official input overview states that this file contains parameters controlling the calculation type and settings.
- `STRU`: structural information such as lattice, atom types, pseudopotential/basis references, and coordinates.
- `KPT`: k-point grid information when required by the calculation setup.
- `OUT.{suffix}/`: output directory pattern controlled by `suffix` in `INPUT`.

## Commands To Recognize

- `abacus -h`: show general help and common parameters.
- `abacus -s <keyword>`: search for input parameters by keyword.
- `abacus -h <parameter>`: inspect help for a specific parameter.

Do not run these commands unless ABACUS is installed and the user has approved interacting with that environment.

## Settings Requiring User Approval

- exchange-correlation functional
- pseudopotential source/version and `pseudo_dir`
- numerical orbital basis and `orbital_dir` when LCAO is used
- `basis_type`, cutoff and basis accuracy settings such as `ecutwfc`
- `calculation` mode
- `KPT` grid
- smearing, dispersion, spin, charge, magnetization, and slab/PBC settings
- SCF and force convergence thresholds such as `scf_thr`
- output options required for energy/force/virial extraction

## Workflow Handoff

- For initial datasets, ABACUS labels user-prepared structures before DP-GEN starts.
- For DP-GEN, ABACUS labels uncertain candidate structures selected by model deviation.
- Before handoff to DeePMD/DP-GEN, confirm SCF convergence, total energy, forces, virial/stress if required, units, atom ordering, cell consistency, and metadata.

## When To Stop And Ask User

- Any required setting is missing or undocumented.
- The user asks the agent to choose production DFT settings.
- Output files are missing, incomplete, ambiguous, or unconverged.
- Initial-label settings and DP-GEN-labeling settings disagree.
