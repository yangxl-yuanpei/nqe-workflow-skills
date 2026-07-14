# Fresh-Agent Test Record

Date: 2026-07-14

Commit or branch: local working tree after adding deeper runner failure prompts

Repository status: dirty; includes updates to `tests/manual_prompts.md`, `docs/testing.md`, and `docs/pending-work.md`

Agent/model: opencode fresh-agent run reported by user

Freshness level: external fresh-agent run reported by user

Freshness note: The reported agent was instructed to read `nqe-postprocess-runner/SKILL.md`, `nqe-postprocess-runner/references/config-schema.md`, `nqe-postprocess-runner/references/postprocess-runner-failure-cases.md`, and `tests/manual_prompts.md`. The user provided the answers for review in the main development session.

Prompt source: `tests/manual_prompts.md`, `nqe-postprocess-runner` Tests 9-17.

Prompt IDs or headings: missing windows; bad columns; unexpected dry-run commands; child-script failure after partial outputs; per-window skiprows error; config parser rejection; existing output directory; summary without physical review; bad or truncated window output.

Result: PASS

Reviewer: Codex main development session

## Scope

This targeted batch tested whether a fresh agent can route deeper `nqe-postprocess-runner` failure cases to the correct stage without inventing windows, columns, discard policies, TI choices, TST choices, recovery policies, or KMC readiness.

It was selected because the runner is now functionally capable of staged execution, plot-only visualization, and preflight refusal, but still needs evidence that agents handle failure cases conservatively.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| Missing windows in runner discovery | PASS | Refused interpolation, directory-name RC inference, and continuing to TI. Asked to check `sampling_output_root`, `input_file`, and `window_glob`; treated missing windows as upstream failures, approved exclusions, or TODOs. |
| Bad columns in generated child commands | PASS | Refused "run it anyway"; treated dry-run mismatch as a stop condition and asked to correct parser mode/column names or use explicit zero-based table indices. |
| Unexpected dry-run commands | PASS | Refused execution when convergence-only intent produced integration/TST commands; emphasized `parameters_confirmed: true` is not enough when generated commands mismatch the requested stage. |
| Child-script failure after partial outputs | PASS | Treated partial `mean_force_table.csv` as diagnostic, not production. Required failed-stage diagnosis, CHMC/CPIHMC window checks when relevant, schema/provenance review, and fresh output or approved cleanup before rerun. |
| Per-window skiprows file error | PASS | Refused `SUGGESTED` as a nonnumeric skiprows value and refused automatic promotion of convergence suggestions. Required user-reviewed numeric discard values and confirmed global fallback behavior. |
| Config parser rejects YAML or JSON | PASS | Explained flat YAML/valid JSON boundary, rejected ambiguous `compute_tst: maybe`, and required non-runnable drafts with `parameters_confirmed: false` for unconfirmed values. |
| Output directory already contains results | PASS | Refused silent overwrite or merge; treated existing outputs as provenance artifacts; recommended inspection, fresh output directory, or user-approved cleanup. |
| Summary exists but physical review is missing | PASS | Correctly described `summary.json` as orchestration provenance, not scientific validation. Listed remaining convergence, mean-force, free-energy, TST, and KMC review requirements. |
| Bad or truncated window output enters TI | PASS | Refused to continue from file presence alone; routed to CHMC/CPIHMC window checks, preserved partial raw file, and required rerun, approved recovery, or documented exclusion before extraction/TI. |

## Observed Failures Or Partials

No failures.

## Overall Notes

The targeted deeper runner failure-case behavior is ready for these prompts. The current manual prompt coverage now spans the main `postprocess-runner-failure-cases.md` categories:

- config confirmation and parser failures
- missing or wrong required fields
- implicit defaults
- path and window discovery failures
- bad or truncated sampling outputs
- convergence screening misuse
- child-script failures and partial outputs
- surprising dry-run commands
- output-directory reuse
- summary/provenance mistaken for physical validation

This record does not imply production readiness, exhaustive runner testing, or script-level negative fixture coverage. Remaining runner work should focus on executable negative fixtures and real-data failure cases rather than prompt coverage alone.
