# Upstream DeepModeling Community Skills

Last checked: 2026-07-17

This repository is a teaching, checking, and semi-automated post-processing
skills library for a cross-software computational materials workflow. It is not
intended to duplicate every official software-operation skill maintained by the
DeepModeling community.

Use upstream DeepModeling skills as software-interface references when the user
needs command syntax, Python API usage, or package-specific workflow examples.
Keep this repository's scientific boundary rules in force when a task crosses
workflow stages or requires physical choices.

## Confirmed Upstream Skills

The following DeepModeling repositories expose public skills that overlap with
software layers used in this repository.

### dpdata

- `dpdata-cli`: https://github.com/deepmodeling/dpdata/tree/master/skills/dpdata-cli
- `dpdata-driver`: https://github.com/deepmodeling/dpdata/tree/master/skills/dpdata-driver
- `dpdata-minimizer`: https://github.com/deepmodeling/dpdata/tree/master/skills/dpdata-minimizer
- `dpdata-plugin`: https://github.com/deepmodeling/dpdata/tree/master/skills/dpdata-plugin

Use these for dpdata command-line syntax, Python driver/minimizer APIs, and
plugin-extension patterns.

### DeePMD-kit

- `deepmd-finetune-dpa3`: https://github.com/deepmodeling/deepmd-kit/tree/master/skills/deepmd-finetune-dpa3
- `deepmd-python-inference`: https://github.com/deepmodeling/deepmd-kit/tree/master/skills/deepmd-python-inference
- `deepmd-train`: https://github.com/deepmodeling/deepmd-kit/tree/master/skills/deepmd-train
- `lammps-deepmd`: https://github.com/deepmodeling/deepmd-kit/tree/master/skills/lammps-deepmd

Use these for DeePMD-kit training, fine-tuning, inference, testing, and
LAMMPS/DeePMD command examples.

### DP-GEN

- `dpgen-simplify`: https://github.com/deepmodeling/dpgen/tree/master/skills/dpgen-simplify

Use this for DP-GEN simplify-specific `param.json`, `machine.json`, execution,
and environment-boundary guidance.

## Boundary For This Repository

DeepModeling upstream skills can be useful operational references, but they do
not override this repository's workflow guardrails.

In this repository:

- Do not guess dpdata format strings for unknown data. Inspect the source and
  confirm format names for the installed version.
- Do not treat `dpdata` conversion success as physical validation or DeePMD
  training readiness.
- Do not choose DeePMD descriptors, cutoffs, architectures, learning-rate
  schedules, training steps, loss weights, batch sizes, random seeds, or
  pretrained/fine-tuning choices without user approval.
- Do not choose DP-GEN trust levels, exploration conditions, candidate
  selection rules, machine resources, or first-principles labeling settings
  without user approval.
- Do not choose LAMMPS timesteps, ensembles, thermostat/barostat parameters,
  run lengths, temperatures, pressures, PLUMED CVs, restraints, bias settings,
  or dump frequencies without user approval.
- Do not promote examples from upstream skills into production defaults for a
  new target system.

## How To Use These References

Recommended workflow when a task overlaps with an upstream skill:

1. Use this repository's relevant `SKILL.md` to determine the workflow stage and
   scientific confirmation boundary.
2. Use upstream DeepModeling skills or official documentation for command/API
   syntax when software behavior is version-specific.
3. Ask the user to confirm any scientific or production parameter before
   writing a runnable command or config.
4. Treat script or command success as diagnostic evidence only, not as proof of
   convergence, physical correctness, or downstream readiness.

## Why Both Layers Are Useful

The upstream skills are closer to official software-operation guidance. This
repository adds workflow governance around cross-stage handoffs such as:

- ABACUS/DFT labels to dpdata conversion
- dpdata conversion to DeePMD training readiness
- DeePMD/DP-GEN models to LAMMPS exploration
- exploration and active learning to CHMC/CPIHMC sampling
- mean-force sampling to TI/TST
- TST rates to KMC event-network reasoning

Keep both layers distinct: upstream skills help an agent operate software,
while this repository helps an agent avoid unsafe scientific inference across
the full workflow.

