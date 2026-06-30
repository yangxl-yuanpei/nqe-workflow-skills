# CHMC/CPIHMC Real Reference Examples

Place redacted real inputs and outputs here when available.

Suggested layout:

```text
reference-examples/
  <example-name>/
    INPUT
    STRU
    BEADS              # optional
    PHY_QUANT          # output sample if available
    MODEL_DEVI         # output sample if available
    README.md
```

Each README should state the original project context, what was redacted, units, reaction coordinate, bead settings if used, and which settings are system-specific.

## Available Examples

- `corr-gc-cpihmc/`: real CORR-related GC-CPIHMC-style `INPUT`, `BEADS`, `ALL_INPUT`, and `PHY_QUANT` files with transfer-boundary notes.
