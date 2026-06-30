# DP-GEN Real Input Reference Examples

This directory is reserved for real DP-GEN input examples such as `param.json` and `machine.json`.

Do not treat any example here as a universal default. DP-GEN settings encode the system, dataset layout, exploration engine, trust levels, labeling backend, HPC scheduler, queue names, paths, commands, and resource policy.

## Suggested Layout For A Real Example

```text
reference-examples/
  <example-name>/
    param.json
    machine.json
    README.md
```

Each example README should state:

- original system or project context
- DP-GEN / DeePMD-kit / ABACUS versions if known
- which fields were redacted
- which settings are system-specific
- which patterns are safe to borrow
- which fields must be re-approved before reuse

## Redaction Checklist

Before publishing a real example, remove or replace:

- personal usernames, home directories, scratch paths, cluster names, and account IDs
- private server addresses and SSH settings
- queue names if they reveal site-specific information
- proprietary project names or unpublished dataset paths
- credentials, tokens, environment activation commands containing secrets

Use `REDACTED_*` or `TODO_USER_APPROVAL` placeholders for removed values.

## Available Examples

- `corr-dpgen/`: redacted real CORR-related DP-GEN inputs. Includes a detailed `run_param.json` with staged `model_devi_jobs` and a redacted `machine.json`.
