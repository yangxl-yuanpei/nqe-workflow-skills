# CORR DeePMD Real Reference Example

This directory contains real DeePMD-kit training files from a CORR-related workflow. They are reference examples for training input organization, log shape, and freeze/test/model-selection discussion. They are not H2/graphene production defaults.

## Files

| File | Meaning |
|---|---|
| `input.json` | Real DeePMD-kit training input. System-specific values must not be copied blindly. |
| `lcurve.out` | Real DeePMD-kit learning-curve output with step, RMSE, and learning-rate columns. |
| `train.log` | Redacted real training log. Runtime paths and node identifiers were removed. |
| `README.md` | This transfer summary. |

## Observed Training Shape

- type map: `["Cu","C","O","H"]`
- descriptor type: `se_e2_a`
- training systems: `["../data.init/0_ISFS","../data.init/1_Cu-bulk","../data.init/2_H2O-bulk","../data.init/3_Slab_notrans","../data.init/4_Slab_trans","../data.init/5_refine_1","../data.init/6_refine_2"]`
- stop batch: `400000`
- display file: `lcurve.out`
- lcurve rows including header: `202`
- final lcurve row: ` 400000      1.14e-01      1.32e-03      1.11e-01    3.5e-08`

## Transfer Boundaries

Transfer as patterns:

- organize DeePMD input into `model`, `learning_rate`, `loss`, and `training` sections
- record type map, training systems, stop batch, display frequency, checkpoint frequency, and random seeds
- inspect `lcurve.out` for loss/RMSE trends, NaN/Inf, and final values
- preserve train/freeze/test/model-selection provenance

Do not transfer blindly:

- type map, chemical species, data paths, systems, and train/test composition
- descriptor type, cutoff, neuron sizes, seeds, and architecture choices
- learning-rate schedule, loss weights, batch size, stop batch, and validation assumptions
- final model choice, freeze checkpoint, or dp test acceptance thresholds

Treat this example as a realistic DeePMD style reference, not as recommended H2/graphene parameters.
