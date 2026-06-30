# DeePMD Freeze, Test, Final Model, And Model-Deviation Notes

Use these notes when the user asks how to go from trained DeePMD checkpoints to a frozen model, how to compare multiple final models, or how model deviation is used in DP-GEN.

## Freeze

- Freeze/export is required before many downstream consumers use a DeePMD model as a portable frozen graph/model file.
- Do not invent the exact freeze command. Ask for the installed DeePMD-kit version and use official DeePMD-kit documentation for the command syntax.
- Record the checkpoint or training directory used for freeze and the frozen model output path.
- The reference `train.log` shows training finished and a freeze step restored parameters from a final checkpoint, then reported frozen graph nodes. Treat that as evidence of a freeze attempt, not automatic production certification.

## Test

- Use `dp test` or the version-appropriate DeePMD-kit test command to evaluate a frozen model on documented test data.
- Ask the user for the test dataset path, type map, number of frames if applicable, and output paths.
- Compare models using the same test data and metrics. Do not compare runs tested on different datasets or units.
- Record energy, force, and virial errors when available. Force errors are often critical for dynamics quality.

## Choosing A Final Model

If multiple final models are available, use `dp test` results to help select the best-performing model, subject to user-approved criteria. The lowest test error alone is not always sufficient: also check model-deviation behavior, reaction-coordinate coverage, stability in LAMMPS exploration, and downstream CHMC/CPIHMC needs.

Do not auto-select a production model without user approval.

## Model Deviation In DP-GEN

In DP-GEN, multiple DeePMD models are used during LAMMPS exploration to compute model deviation automatically. DP-GEN then classifies explored configurations using user-provided trust thresholds such as `trust_lo` and `trust_hi` or their DP-GEN parameter equivalents.

Typical categories are:

- accurate: model deviation below the lower trust threshold
- candidate: model deviation between lower and upper trust thresholds; these may be sent to ABACUS labeling
- failed: model deviation above the upper trust threshold or otherwise invalid for labeling policy

The exact threshold names, units, and classification output files depend on the DP-GEN version and parameter file. Verify against official DP-GEN documentation and the user-provided `param.json`/`run_param.json`.

## Required User Inputs For Complete Commands

Ask the user to provide or confirm:

- DeePMD-kit version
- checkpoint or training directory to freeze
- desired frozen model output filename
- test dataset path and type map
- `dp test` options used by the project
- acceptance criteria for final model selection
- whether the final model is chosen from DP-GEN ensemble models or from optional specialized final training
