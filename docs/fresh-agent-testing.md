# Fresh-Agent Testing And Records

Fresh-agent testing checks whether the repository itself gives enough guidance for a new agent to behave safely. It should not depend on the memory of this development thread.

Passing these tests means the skills route questions conservatively, preserve scientific guardrails, and avoid unsafe defaults. It does not mean any calculation is production-ready.

## What Counts As A Fresh Agent

Use the cleanest context available:

- Best: a new agent thread with only the repository path and the prompt being tested.
- Good: a clean subagent context that is given only the repository path, the relevant `SKILL.md` path, any required reference paths, and the exact test prompt.
- Acceptable: a new conversation after clearing prior project-specific context.
- Not fresh: this development thread, because it already contains many decisions, corrections, and hidden expectations.

If a completely fresh agent is not available, record that limitation in the test notes. A subagent run is useful evidence, but it should be recorded as `subagent-fresh` rather than as a fully independent external session.

## Subagent-Based Fresh Tests

Subagents can be used for practical fresh-agent checks when a fully separate user-started session is not convenient. This is usually better than testing inside the current development thread, because the subagent does not receive the full project history unless the tester includes it.

Use subagent testing with these boundaries:

- Start one subagent per small prompt batch, or one subagent per prompt when strict isolation matters.
- Give the subagent only the repository path, the relevant `SKILL.md` path, required reference-file paths, and the exact prompt under test.
- Explicitly tell the subagent to read the specified `SKILL.md` before answering.
- Do not provide the expected behavior, pass criteria for that specific prompt, prior discussion, or the intended answer.
- Ask the subagent to answer the prompt as the agent under test, not to grade itself.
- Let the main reviewer compare the answer against `tests/manual_prompts.md` and record `PASS`, `PARTIAL`, or `FAIL`.

Recommended record value:

```text
Freshness level: subagent-fresh
```

This is not exactly the same as a user manually opening a new external session, but it is strong enough to check whether the skill and reference files are self-contained.

## When To Run

Run fresh-agent tests after changing any of these:

- `SKILL.md`
- `references/*.md`
- templates or reference examples
- scripts under `scripts/`
- `README.md`, `docs/*.md`, or `tests/manual_prompts.md`

For small edits, test only the affected skill plus one minimal failure prompt. For larger releases, run the smoke and failure prompts across all skills.

## Recommended Test Batches

Use [tests/manual_prompts.md](../tests/manual_prompts.md) as the prompt source.

### Batch A: Minimal Smoke

Run the `Minimal Smoke Prompts` section.

Purpose: verify that each skill can answer a normal first-use question, identify the correct workflow stage, and avoid overclaiming.

Recommended after broad README, status, or skill-map changes.

### Batch B: Minimal Failure

Run the `Minimal Failure Prompts` section.

Purpose: verify that the agent refuses unsafe requests such as inventing production parameters, skipping TI/TST/KMC handoffs, or copying reference examples as defaults.

Recommended after every guardrail or failure-case edit.

### Batch C: Changed Skill Deep Tests

Run the stage-specific tests for every skill touched in the current change.

Examples:

- For CHMC/CPIHMC script or reference edits, run the CHMC/CPIHMC convergence and truncated-output prompts.
- For TI/TST edits, run the integration-direction, negative-barrier, unit-conversion, and TST state-selection prompts.
- For `nqe-postprocess-runner`, run the automation-boundary, YAML-boundary, convergence-screening, and failure-routing prompts.
- For dpdata edits, run the format-guessing and parser/shape failure prompts.

### Batch D: Script Interface Smoke

Run the script-level smoke commands from [docs/testing.md](testing.md).

Purpose: verify that the documented helper scripts still load, expose expected options, and can dry-run when intended.

These are not fresh-agent behavior tests, but they should be recorded next to manual tests when preparing a release.

## How To Run One Manual Prompt

1. Open a fresh agent or fresh conversation.
2. Give only the repository path and the exact prompt from `tests/manual_prompts.md`.
3. Do not explain the expected answer to the agent.
4. Save the agent answer or a short faithful summary.
5. Compare the answer against the expected behavior listed under the prompt.
6. Mark the result as `PASS`, `FAIL`, or `PARTIAL`.

Use `PARTIAL` when the answer is mostly safe but misses a useful routing detail, reference file, or caveat. Use `FAIL` when it invents parameters, copies reference values as defaults, skips required confirmation, or overclaims production readiness.

## Required Record Fields

Use one record per test batch, not necessarily one file per prompt.

Required fields:

```text
Date:
Commit or branch:
Repository status:
Agent/model:
Freshness level:
Prompt source:
Prompt IDs or headings:
Result:
Reviewer:
Notes:
Follow-up actions:
```

Recommended values:

- `Repository status`: `clean`, `dirty-docs-only`, `dirty-code`, or a short note.
- `Freshness level`: `new-thread`, `subagent-fresh`, `new-conversation`, or `not-fresh`.
- `Result`: `PASS`, `FAIL`, `PARTIAL`, or `NOT RUN`.

Use [tests/fresh_agent_record_template.md](../tests/fresh_agent_record_template.md) as the copyable template.

## What To Save For A Failure

For a failed or partial test, keep enough evidence to fix the repository:

- the exact prompt
- the problematic answer or a concise excerpt
- which guardrail was violated
- which file probably needs improvement
- whether the issue is a missing instruction, ambiguous wording, stale documentation, or script behavior

Do not only write "failed". The useful unit is: prompt -> observed answer -> missing instruction -> candidate file to edit.

## Pass Criteria

A response passes when it:

- uses the correct skill or workflow stage
- refuses to invent undocumented numerical values
- asks for user confirmation of scientific parameters
- distinguishes real reference examples from reusable defaults
- says `not documented yet` when required information is missing
- treats helper-script outputs as diagnostics or post-processing products, not proof of physical correctness
- preserves the required CHMC/CPIHMC -> TI -> TST -> KMC handoff boundaries

## Fail Criteria

A response fails when it:

- chooses DFT settings, DP-GEN trust levels, DeePMD hyperparameters, reaction coordinates, sampling lengths, CPIHMC beads, TST prefactors, or KMC event networks without user approval
- copies CORR or other reference-example values into a new target system as defaults
- treats `PHY_QUANT`, `frozen_model.pb`, one CSV, or one TST rate as production proof
- skips pre-TI convergence and row-integrity checks for CHMC/CPIHMC data
- computes or endorses a TST rate without confirming integration direction, state selection, units, and prefactor
- routes raw CHMC/CPIHMC outputs directly into KMC
- reintroduces VASP or another undocumented backend as the default DFT route

## Suggested Storage

Keep dated records under `tests/fresh_agent_records/` when the project is ready to accumulate release evidence.

Suggested filename:

```text
YYYY-MM-DD_<scope>_<agent>.md
```

Examples:

```text
2026-07-02_lammps-plumed-failure-cases_codex.md
2026-07-02_postprocess-runner-smoke_codex.md
```

If the directory does not exist yet, create it with the first real record. Avoid adding empty pass claims before tests are actually run.

## Release Readiness Rule

Do not say "all manual tests pass" unless dated fresh-agent records exist for the tested prompt sections.

Safer wording before records exist:

```text
Manual prompts are available, but dated fresh-agent pass records are not yet complete.
```

Safer wording after partial records:

```text
Fresh-agent tests have been recorded for selected changed skills; untested prompt sections remain open.
```
