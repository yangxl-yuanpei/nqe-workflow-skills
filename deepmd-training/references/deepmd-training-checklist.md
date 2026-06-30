# DeePMD Training Checklist

This reference summarizes DeePMD-kit training checks for the NQE H2 formation workflow. It is not a production `input.json` template.

## Official Documentation Anchors

- DeePMD-kit documentation: https://docs.deepmodeling.com/projects/deepmd/en/latest/
- Use official documentation for data format, training, freeze, test, and model-deviation command meanings.

## DeePMD In DP-GEN

- DeePMD-kit is called in the training step of each DP-GEN iteration.
- The current DFT-labeled dataset is used for training.
- Multiple models are trained with different random seeds when an ensemble is needed for model deviation.
- The trained models are passed to exploration, where prediction disagreement helps identify uncertain configurations.

## Optional Final Training

After DP-GEN is accepted by the user, either:

- use one of the final DP-GEN frozen models, or
- run optional specialized DeePMD training on the accumulated dataset.

The choice requires user approval. Do not assume specialized final training is always required.

## Data Checks

- DFT labels originate from consistent ABACUS settings.
- Energy, force, and virial labels are complete if required.
- `type_map` and atom ordering match all dataset systems.
- Units for energy, force, virial, coordinates, and cell are documented.
- Structures relevant to reaction-coordinate sampling are represented.
- Broken, duplicated, unconverged, or physically unreasonable labels are removed or flagged.

## Training Input Checks

User approval is required for:

- descriptor type and cutoff
- embedding network architecture
- fitting network architecture
- loss weights for energy, force, and virial
- learning-rate schedule
- batch size
- number of training steps
- validation split or explicit validation set
- random seeds and ensemble settings
- model export/freeze settings

## Output Checks

- training log exists and has no NaNs or obvious divergence
- energy and force errors are reported on training and validation/test data when available
- frozen model file exists only if the freeze/export step has completed
- model-deviation analysis is available when DP-GEN exploration depends on an ensemble
- selected production model has documented provenance: dataset, training input, random seed, software version, and validation evidence

## Downstream Handoff

A DeePMD frozen model can be handed to CHMC/CPIHMC only after user acceptance. The handoff should record:

- model path and version
- training dataset provenance
- relevant validation errors
- known failure modes or uncovered configuration regions
- whether the model was selected from DP-GEN or produced by optional final training

## Reusable Beyond This Workflow

General reusable parts:

- checking DeePMD data format, type maps, units, labels, and train/test assumptions
- inspecting `input.json`, training logs, freeze/test outputs, and model provenance
- refusing to auto-select descriptor, cutoff, networks, loss weights, learning rate, batch size, training steps, or seeds
- requiring validation evidence before production use

NQE H2-specific parts:

- requiring reaction-coordinate coverage relevant to CHMC/CPIHMC sampling
- treating the selected frozen model as an intermediate for free-energy calculations, not a final observable
- preserving the DP-GEN ensemble and optional final-training distinction used in this repository

## Script: parse_lcurve.py

Use `../scripts/parse_lcurve.py` from this skill to summarize DeePMD-kit `lcurve.out`-style logs.

The script reports:

- row and column counts
- parsed column names when a header exists
- final, minimum, and maximum finite values
- NaN/Inf counts
- nonmonotonic or duplicate step warnings
- a reminder that log parsing does not certify model readiness

Use it for deterministic diagnostics only. Model acceptance still requires user-approved validation criteria and downstream reaction-coordinate coverage checks.
