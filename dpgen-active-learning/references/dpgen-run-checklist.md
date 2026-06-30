# DP-GEN Run Checklist

This reference summarizes how DP-GEN should be treated in the NQE H2 formation workflow. It is not a production `param.json` or `machine.json` template.

## Official Documentation Anchors

- DP-GEN run overview: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/index.html
- DP-GEN `param.json` parameters: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/param.html
- DP-GEN `machine.json` parameters: https://docs.deepmodeling.com/projects/dpgen/en/latest/run/machine.html

Use official documentation for parameter meanings and schema details. Use this repository for NQE workflow boundaries and scientific handoff rules.

## Required Inputs

- user-prepared initial DFT-labeled dataset
- initial and exploration structure sets
- `param.json` or an explicit TODO placeholder
- `machine.json` or an explicit TODO placeholder
- DeePMD-kit training template from the `deepmd-training` skill
- ABACUS labeling template from the `abacus-dft-labeling` skill
- user-approved exploration engine and sampling settings
- user-approved trust-level thresholds and candidate selection rules

## Key `param.json` Concepts To Inspect

- `type_map`: atom types; must match data and exploration structures.
- `init_data_sys`: initial data systems; should point to validated initial DFT labels.
- `sys_configs`: structures/configurations used during exploration.
- `numb_models`: number of models trained per iteration; four is commonly used in the project teaching text, but user approval is still required for production.
- `mlp_engine`: DP-GEN ML potential engine; DeePMD-kit is the intended engine for this workflow.
- training parameters: owned by `deepmd-training`.
- exploration settings: require user approval.
- FP/labeling task controls: require consistency with ABACUS labeling policy.

## Iteration Outputs To Inspect

- iteration directories such as `iter.000000`, `iter.000001`, etc.
- trained/frozen model ensemble from each iteration
- exploration trajectories and model-deviation data
- candidate structures selected for labeling
- ABACUS labeling outputs and convergence status
- updated training dataset after newly labeled data are added

## Model-Deviation Interpretation

- Low model deviation means the model ensemble agrees and the configuration is likely within the learned domain.
- High model deviation means the model ensemble disagrees and the configuration may need ABACUS labeling.
- Intermediate regions require a user-defined DP-GEN strategy.
- Thresholds such as `tol_lo` and `tol_hi` are not chosen by the agent.

## Convergence Review

Do not claim convergence from a fixed iteration number. Review:

- trust-level distribution in exploration trajectories
- fraction of structures below the user-approved low-deviation threshold
- trend in selected candidate counts across iterations
- coverage of reaction-relevant configuration space
- absence of DeePMD training divergence or NaNs
- completeness and convergence of ABACUS labels

## NQE Workflow Handoff

After DP-GEN is accepted by the user:

- the final dataset and model ensemble feed the optional final DeePMD training stage or direct model selection
- one selected frozen model may be used for CHMC/CPIHMC free-energy sampling only after validation
- downstream CHMC/CPIHMC reliability depends on reaction-coordinate coverage in the DP-GEN exploration and labeling data

## Reusable Beyond This Workflow

General reusable parts:

- enforcing the DP-GEN loop as training -> exploration -> labeling
- treating model-deviation selection as an exploration filter
- checking `param.json`, `machine.json`, `type_map`, `init_data_sys`, `sys_configs`, and model ensemble settings
- refusing to choose trust-level thresholds or declare convergence without evidence

NQE H2-specific parts:

- requiring exploration coverage relevant to H2 formation reaction coordinates
- keeping ABACUS labeling and DeePMD training aligned with this repository's workflow
- handing accepted models toward CHMC/CPIHMC rather than generic production MD only
