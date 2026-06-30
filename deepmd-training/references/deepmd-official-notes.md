# DeePMD-kit Official Notes

Use this reference as a source-of-truth roadmap for DeePMD-kit data, training, freeze, test, and model-deviation workflows. Do not invent input fields or hyperparameters.

## Source Of Truth

- Official documentation: https://docs.deepmodeling.com/projects/deepmd/en/latest/
- Training section: https://docs.deepmodeling.com/projects/deepmd/en/latest/train/index.html
- Data section: https://docs.deepmodeling.com/projects/deepmd/en/latest/data/index.html
- Freeze/compress section: https://docs.deepmodeling.com/projects/deepmd/en/latest/freeze/index.html
- Test section: https://docs.deepmodeling.com/projects/deepmd/en/latest/test/index.html
- Model deviation section: https://docs.deepmodeling.com/projects/deepmd/en/latest/model-deviation/index.html

Use official docs for input schema, command syntax, data format, model export/freeze behavior, testing, and model-deviation calculations.

## Files And Outputs To Recognize

- `input.json`: DeePMD-kit training input configuration.
- DeePMD dataset directories and data files such as type maps, coordinates, cells, energies, forces, and virials as defined by the official data documentation.
- training logs such as `lcurve.out` when produced by the training workflow.
- frozen/exported model files produced by the documented freeze/export step.
- test outputs and model-deviation outputs when produced by official commands.

## Concepts To Inspect

- descriptor and fitting-network configuration
- cutoff and type map
- energy/force/virial loss weights
- learning-rate schedule
- batch size, training steps, seeds, and validation split
- train/freeze/test command provenance
- model-deviation ensemble provenance

## Settings Requiring User Approval

- descriptor type and cutoff
- embedding and fitting network architecture
- loss weights
- learning-rate schedule
- batch size and training steps
- validation split or explicit validation systems
- random seeds and ensemble size
- final model selection for CHMC/CPIHMC sampling

## Workflow Handoff

- DeePMD-kit trains models inside DP-GEN iterations.
- After DP-GEN user acceptance, the user may select a final DP-GEN model or run optional specialized final training.
- Before CHMC/CPIHMC handoff, record model path, dataset provenance, training input, software version, validation/test errors, reaction-coordinate coverage, and known failure modes.

## When To Stop And Ask User

- Training hyperparameters are missing.
- Dataset provenance or units are unclear.
- Training logs show NaNs, divergence, or missing metrics.
- Test/model-deviation evidence is absent but the user asks to proceed to production sampling.
