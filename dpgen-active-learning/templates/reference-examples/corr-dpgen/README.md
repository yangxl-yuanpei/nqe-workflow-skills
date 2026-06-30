# CORR DP-GEN Real Reference Example

This directory contains redacted real DP-GEN input files from a CORR-related project. It is a reference example for input organization and exploration strategy, not a production template for H2/graphene.

## Files

| File | Meaning |
|---|---|
| `run_param.json` | Real DP-GEN parameter file with training, exploration/model-deviation, and ABACUS labeling settings. |
| `machine.json` | Redacted execution configuration. Credentials and site-specific identifiers have been removed. |
| `README.md` | This summary. |

## Exploration Strategy Observed

This example defines 62 `model_devi_jobs` entries. The observed exploration pattern is:

- temperature values observed: [50]
- LAMMPS step counts observed: [300,500,1000,2000,3000,5000,10000]
- system indices explored: [0,1,2,3,4,5]
- LAMMPS template files: ["lmp/input.lammps"]
- PLUMED template count: 12

The concrete CORR example keeps the listed temperature fixed while increasing sampling length across jobs. The more general transferable strategy is to begin exploration conservatively, then increase exploration strength as model quality improves. In practice this often means starting from lower temperatures and shorter trajectories, then gradually increasing temperature and/or trajectory length. The exact schedule is system-specific and must be approved by the user.

## Transfer Boundaries

Transfer as patterns:

- separating `param/run_param` settings from `machine` settings
- using multiple `model_devi_jobs` to stage exploration
- grouping exploration by system index and template
- using LAMMPS and optional PLUMED templates for exploration
- using ABACUS as the first-principles labeling backend

Do not transfer blindly:

- type map, masses, data paths, system configs, and chemical species
- model-deviation trust levels
- temperature, pressure, timestep, trajectory length, PLUMED settings, or sampling schedule
- ABACUS pseudopotential, orbital, k-point, and input settings
- DeePMD architecture, learning rate, loss weights, training steps, or seeds
- machine commands, images, queues, accounts, or cloud resource settings

All redacted or system-specific values must be re-approved before reuse.
