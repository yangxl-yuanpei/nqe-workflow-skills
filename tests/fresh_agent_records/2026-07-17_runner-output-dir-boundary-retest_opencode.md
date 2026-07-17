# Fresh-Agent Test Record

Date: 2026-07-17

Commit or branch: local working tree after hardening `nqe-postprocess-runner` output-directory reuse boundaries

Repository status: dirty; includes updates to `nqe-postprocess-runner/SKILL.md`, `nqe-postprocess-runner/references/config-schema.md`, `nqe-postprocess-runner/references/postprocess-runner-failure-cases.md`, and `tests/manual_prompts.md`

Agent/model: opencode fresh-agent run reported by user

Freshness level: external fresh-agent run reported by user

Freshness note: The reported agent was tested after output-directory reuse guardrails were tightened. The user provided the answers for review in the main development session.

Prompt source: targeted retest prompts derived from `tests/manual_prompts.md` Test 15, Test 15b, and Test 15c.

Prompt IDs or headings: output directory already contains results; do not add existing-output override as a convenience fix; runner success does not prove clean overwrite or convergence.

Result: PASS

Reviewer: Codex main development session

## Scope

This targeted batch retested whether a fresh agent handles `nqe-postprocess-runner` reruns into a non-empty `output_dir` conservatively after earlier answers incorrectly described `allow_existing_output_dir: true` as a clean overwrite mechanism.

The tested boundary is operational rather than physical: non-empty output directories require review, and `allow_existing_output_dir: true` is only a user-approved reuse or cleanup override. It does not merge provenance, remove arbitrary stale artifacts, certify convergence, or approve TI/TST/KMC readiness.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| Output directory already contains results | PASS | Correctly said no by default. Described the runner's non-empty `output_dir` guard, explained that `allow_existing_output_dir: true` only deletes selected core CSV/JSON files, and recommended a fresh output directory or inspected, user-approved reuse. |
| Do not add `allow_existing_output_dir` as a convenience fix | PASS | Did not immediately edit a likely config or ask only for a config path. First asked whether the old output directory had been inspected and whether reuse or cleanup was explicitly approved. |
| Runner success does not prove clean overwrite or convergence | PASS | Correctly refused to treat a successful rerun as clean overwrite or convergence proof. Explained that old plots, convergence outputs, and other artifacts can remain, and that convergence still requires direct review of diagnostics. |

## Observed Failures Or Partials

No failures in the reported retest.

## Overall Notes

The targeted output-directory reuse behavior is ready for these prompts. The fresh-agent response now matches the intended boundary:

- fresh output directories remain the safest default;
- `allow_existing_output_dir: true` is an operational override only after inspection and approval;
- runner completion is not a scientific validation result.

This record does not imply full repository-wide fresh-agent coverage, exhaustive runner validation, or production readiness.
