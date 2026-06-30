# DP-GEN Real Input Transfer Notes

Use these notes when converting a real DP-GEN `param.json`/`machine.json` into a reusable teaching reference.

## What Can Usually Transfer

- The overall separation between `param.json` for scientific workflow settings and `machine.json` for execution resources.
- The mapping between DP-GEN stages: training, exploration/model-deviation, and first-principles labeling.
- The idea that DeePMD training settings belong to the DeePMD template or embedded training section, while ABACUS labeling settings belong to the ABACUS labeling skill.
- Directory organization patterns for initial data, system configs, iteration outputs, and labeling tasks.
- The habit of documenting `type_map`, data paths, model count, trust levels, exploration settings, and labeling backend metadata.

## What Must Not Transfer Blindly

- `type_map`, masses, atom ordering, dataset paths, system config paths, and selected structures.
- Trust levels such as lower/upper model-deviation thresholds. These are system-, model-, and unit-dependent.
- Exploration engine, temperature, pressure, ensemble, trajectory length, timestep, and sampling frequency.
- ABACUS labeling settings, pseudopotential/basis paths, k-points, and convergence thresholds.
- DeePMD network architecture, descriptor, cutoff, loss weights, learning rate, random seeds, and training steps.
- Machine settings: scheduler type, queue, account, node/GPU counts, local/remote roots, and commands.

## Agent Behavior

When a user provides real DP-GEN files:

- Inspect structure and missing fields, but do not silently repair scientific parameters.
- Separate scientific settings from machine/HPC settings.
- Mark redacted or missing values as `TODO_USER_APPROVAL`.
- Compare the files with `templates/param.json.template` and `templates/machine.json.template`.
- Use official DP-GEN documentation to verify field meanings for the installed version.
- Explain which parts are reusable patterns and which parts are example-specific.
