# LAMMPS Real Reference Examples

Place redacted real LAMMPS exploration scripts here when available.

Suggested layout:

```text
reference-examples/
  <example-name>/
    input.lammps
    input.plumed        # optional, if used
    README.md
```

Each README should state the original project context, what was redacted, which settings are system-specific, and which organization patterns are reusable.

Do not publish credentials, private paths, unpublished dataset names, or cluster/account details.

## Available Examples

- `corr-lammps-plumed/`: real CORR-related LAMMPS `input.lammps` and PLUMED `input.plumed_1`, with transfer-boundary notes.
