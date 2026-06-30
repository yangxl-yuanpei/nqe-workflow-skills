# DP-GEN Official Notes

Use this reference as a source-of-truth roadmap for DP-GEN run configuration. Do not invent workflow parameters or machine settings.

## Source Of Truth

- Official documentation: https://docs.deepmodeling.com/projects/dpgen/en/latest/
- Run documentation: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/index.html
- `param.json` parameters: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/param.html
- `machine.json` parameters: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/machine.html
- Supported software: https://docs.deepmodeling.com/projects/dpgen/en/latest/overview/software.html

Use official docs for JSON schema details, command-line interface, supported software, and dispatcher/machine semantics.

## Files To Recognize

- `param.json`: workflow/scientific configuration for DP-GEN run stages.
- `machine.json`: execution resources, machine, scheduler, and task-dispatch settings.
- `iter.000000`, `iter.000001`, etc.: iteration directories produced by DP-GEN run workflows.
- DeePMD training input templates referenced by DP-GEN are owned by the `deepmd-training` skill.
- ABACUS labeling templates referenced by DP-GEN are owned by the `abacus-dft-labeling` skill.

## Concepts To Inspect

- `type_map`: element/type mapping; must match DeePMD data and exploration structures.
- `init_data_sys`: initial training data systems.
- `sys_configs`: structures used for exploration.
- `numb_models`: model ensemble count.
- model-deviation thresholds and candidate-selection rules.
- machine, queue, resource, and dispatcher settings.

## Settings Requiring User Approval

- `tol_lo`, `tol_hi`, and any model-deviation thresholds
- exploration engine and all sampling settings
- DeePMD training hyperparameters
- ABACUS labeling settings
- HPC queue, resources, wall time, group/account, and dispatcher behavior
- candidate selection frequency and strategy for intermediate-deviation regions

## Workflow Handoff

- DP-GEN starts from a validated initial DFT-labeled dataset.
- Each iteration is `training -> exploration -> labeling`.
- Model-deviation selection is an exploration filter, not a fourth main stage.
- Accepted final models and datasets may be handed to optional final DeePMD training or downstream CHMC/CPIHMC after user validation.

## When To Stop And Ask User

- `param.json` or `machine.json` is missing required documented fields.
- Trust levels, exploration settings, machine settings, or labeling settings are absent.
- The user asks the agent to choose thresholds or claim convergence from iteration count alone.
- DeePMD training or ABACUS labeling outputs show failures or missing metadata.
