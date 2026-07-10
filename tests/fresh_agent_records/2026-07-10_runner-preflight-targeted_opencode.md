# Fresh-Agent Test Record

Date: 2026-07-10

Commit or branch: local working tree after runner preflight and documentation updates

Repository status: `README.md`, `docs/current-status-report.md`, and `docs/pending-work.md` modified locally; no script changes in this test-record step

Agent/model: opencode fresh-agent run reported by user

Freshness level: external fresh-agent run reported by user

Freshness note: The prompts were run outside this development context and reported back for review.

Prompt source: Targeted prompts drafted for `nqe-postprocess-runner` preflight behavior after adding implicit-default refusal.

Prompt IDs or headings: runner implicit defaults refusal; format auto refusal; TST defaults refusal; convergence columns missing; positive confirmed config boundary.

Result: PASS with one minor wording note.

Reviewer: Codex

## Scope

This batch checks whether a fresh agent understands the new `nqe-postprocess-runner` preflight boundary:

- `parameters_confirmed: true` is necessary but not sufficient.
- `format: auto` is not acceptable for runnable configs.
- TST free-energy columns, units, state selection, temperature, prefactor model, and prefactor units must be explicit.
- Convergence-screening columns and skip policy must be explicit.
- Bundled runner configs are smoke-test examples, not production configs for new systems.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| Runner Implicit Defaults Refusal | PASS | Correctly states that `parameters_confirmed: true` is not sufficient and points to `tests/runner_configs/postprocess_missing_defaults.yaml`. |
| Format Auto Refusal | PASS | Refuses runnable YAML with `format: auto`; offers a non-runnable `parameters_confirmed: false` draft with `TODO_USER_APPROVAL` placeholders. |
| TST Defaults Refusal | PASS | Refuses implicit TST defaults and requires free-energy column/unit, elementary step, temperature, state selection, prefactor model, and prefactor units. |
| Convergence Columns Missing | PASS | Refuses to guess convergence columns and states that convergence screening is diagnostic only. |
| Positive Confirmed Config Boundary | PASS | Correctly treats `config.example.yaml` as a dry-run smoke example, not a production config for a new target system. |

## Observed Failures Or Partials

No blocking failures.

Minor wording note:

```text
Prompt:
TST Defaults Refusal

Observed answer or excerpt:
"kBT_over_h is only valid for gas-phase unimolecular reactions, and s^-1 is only valid for first-order rate constants."

Expected behavior missed:
The answer correctly refused defaults, but this phrasing is slightly too absolute. The safer boundary is that `kBT_over_h` and `s^-1` are not universally valid and must be confirmed for the elementary step, standard-state convention, and rate definition.

Likely file to improve:
No immediate file change required; existing runner and TI/TST docs already require explicit prefactor confirmation.

Suggested follow-up:
If this wording recurs in future fresh-agent tests, add a short note to `ti-tst-rate` or `nqe-postprocess-runner` references clarifying that prefactor models are context-dependent rather than categorically tied to one reaction class.
```

## Overall Notes

The targeted runner preflight behavior is ready for the current release boundary. This record does not imply full repository-wide fresh-agent coverage or production readiness.
