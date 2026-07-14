# Fresh-Agent Test Record

Date: 2026-07-14

Commit or branch: local working tree after runner/TI-TST boundary wording updates

Repository status: dirty; includes documentation updates to `nqe-postprocess-runner`, `ti-tst-rate`, and `tests/manual_prompts.md`

Agent/model: opencode fresh-agent run reported by user

Freshness level: external fresh-agent run reported by user

Freshness note: The reported agent was instructed to read `nqe-postprocess-runner/SKILL.md`, `nqe-postprocess-runner/references/config-schema.md`, `ti-tst-rate/SKILL.md`, and `tests/manual_prompts.md`. The user provided the answers for review in the main development session.

Prompt source: targeted prompts drafted after the 2026-07-13/2026-07-14 runner and TI/TST boundary updates.

Prompt IDs or headings: candidate path discovery; plot-only optional `output_dir`; plot-only to default TST refusal; path confirmation is not TI/TST approval.

Result: PASS

Reviewer: Codex main development session

## Scope

This targeted batch retested the guardrails added after fresh-agent answers exposed two unsafe tendencies:

- Treating discovered directories such as `demo/` as if they were the user's intended dataset, or ranking which candidate was "probably" real.
- Treating observed CSV headers, optional config defaults, or user phrases such as "default min/max/kBT_over_h" as confirmed physical choices.

The test covers `nqe-postprocess-runner` behavior and the matching `ti-tst-rate` TST default boundary. It does not claim full repository-wide fresh-agent coverage.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| Candidate paths cannot be ranked or silently adopted | PASS | The answer listed `demo/` as a candidate only, asked the user to confirm `sampling_output_root`, and did not rank it as probably real. Minor note: it described `energy.dat` as binary from context; this did not lead to execution or parameter invention. |
| Plot-only YAML with unconfirmed `output_dir` | PASS | The answer generated a `stop_after: plot` YAML using only confirmed fields and omitted `output_dir`, explaining that the runner default would apply. |
| Plot-only image does not approve default TST | PASS | The answer refused default TST, treated `free_energy_converted`, `min`, `max`, and `kBT_over_h` as candidate settings, and required confirmation of units, physical state selection, temperature, elementary step, prefactor model, and prefactor units. |
| Path confirmation is not TI/TST approval | PASS | The answer accepted `demo/` only as the prompt-confirmed path and refused to jump to integration or TST without extraction, unit, integration, state-selection, temperature, and prefactor confirmations. |

## Observed Failures Or Partials

No failures.

Minor observation:

```text
Prompt:
Check the workspace for CHMC/CPIHMC multi-window results and help start postprocessing.

Observed answer or excerpt:
The answer described `energy.dat` as binary.

Expected behavior missed:
No boundary was missed. The answer still treated the directory as a candidate only, asked for confirmation, and did not invent parser settings or run commands.

Likely file to improve:
None required for this targeted boundary. If this wording recurs and causes command generation, improve `nqe-postprocess-runner/SKILL.md` parser/header wording.

Suggested follow-up:
Future deeper runner tests should include explicit ASCII headered `energy.dat`, numeric-first table data, and missing-header failure cases.
```

## Overall Notes

The targeted runner/TI-TST boundary behavior is ready for these four prompts. The current documented behavior now distinguishes discovery from confirmation across path discovery, CSV header observation, optional config defaults, and TST default/candidate settings.

This record does not imply production readiness, exhaustive fresh-agent coverage, or a full pass for all runner failure cases. Future tests should still cover missing windows, bad columns, child-command failures, unexpected dry-run commands, and per-window discard mistakes.
