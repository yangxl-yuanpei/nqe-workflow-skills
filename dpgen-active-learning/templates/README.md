# DP-GEN Active-Learning Templates

These files are teaching templates for planning a DP-GEN train -> exploration -> labeling loop. They are not production-ready. Replace every `TODO_USER_APPROVAL` token with a documented value before running DP-GEN.

## Files

| File | Purpose |
|---|---|
| `param.json.template` | DP-GEN workflow configuration skeleton. |
| `machine.json.template` | Machine, scheduler, and command skeleton. |

## Use With Other Skills

- Use `deepmd-training/templates/input.json.template` for the DeePMD training section referenced by DP-GEN.
- Use `abacus-dft-labeling/templates/` for ABACUS labeling inputs.
- Confirm all field names and nesting against the official DP-GEN documentation for the installed version.
