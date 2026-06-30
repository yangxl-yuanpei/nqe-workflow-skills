# DeePMD-kit Training Templates

These files are teaching templates for DeePMD-kit training in the NQE workflow. They are intentionally incomplete and must be checked against the official DeePMD-kit documentation for the installed version.

## Files

| File | Purpose |
|---|---|
| `input.json.template` | DeePMD-kit training input skeleton. |

## Required Before Use

- Replace every `TODO_USER_APPROVAL` token.
- Confirm dataset paths, `type_map`, atom ordering, units, and train/test split.
- Choose descriptor, fitting network, loss weights, learning-rate schedule, batch size, and training steps only after user approval.
- Validate training logs and frozen model quality before using the model in CHMC/CPIHMC.
