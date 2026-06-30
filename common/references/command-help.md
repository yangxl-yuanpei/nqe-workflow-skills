# Command Help And Version Checks

Use this reference whenever a command, option, executable name, or version-specific behavior is not documented in the skill repository.

## Rule

Do not invent command-line syntax. Prefer, in order:

1. official documentation for the installed software version
2. project-provided scripts or command logs
3. local executable help output such as `-h`, `--help`, `help`, or subcommand help
4. a TODO asking the user to provide the command they use

## Typical Help Patterns

These are common patterns, not guaranteed commands:

- ABACUS: check the installed executable help or official ABACUS documentation; executable names vary by environment.
- DP-GEN: try command help for `dpgen`, `dpgen run`, and related subcommands if available.
- DeePMD-kit: try command help for `dp`, `dp train`, `dp freeze`, `dp test`, and version-specific subcommands.
- LAMMPS: try `lmp -h`, `lmp --help`, or the local executable name used by the user, then verify input-script commands in the LAMMPS manual.
- PLUMED: try `plumed --help`, `plumed help`, or action-specific help if available, then verify actions in the PLUMED manual.
- GC-Constrained-PIHMC / CPIHMC: check the repository README, bundled examples, and executable help if the compiled binary supports it.

## What To Record

When a command is confirmed, record:

- software name and version
- executable name and path if relevant
- exact command used
- working directory assumptions
- required input files
- expected output files
- whether the command was tested or only documented

## Boundary

If neither official docs nor local help are available, say `not documented yet` and ask the user for their actual command rather than guessing.
