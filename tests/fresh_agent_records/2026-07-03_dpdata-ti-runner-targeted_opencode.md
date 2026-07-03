# Fresh-Agent Test Record

Date: 2026-07-03

Commit or branch: not recorded

Repository status: dirty-docs-only at review time

Agent/model: opencode, model not recorded

Freshness level: external fresh-agent run reported by user

Freshness note: The prompts were provided to opencode outside this development thread. The full agent answers were pasted back by the user for review.

Prompt source: targeted prompts drafted from `tests/manual_prompts.md`, `docs/fresh-agent-testing.md`, and recent dpdata/TI/TST/runner repairs.

Prompt IDs or headings: dpdata unknown-format anti-guessing; dpdata confirmed `../00` example; dpdata conversion-readiness boundary; TI/TST no-defaults boundary; postprocess runner dry-run boundary.

Result: PASS after retest

Reviewer: Codex

## Scope

This batch retested the recent dpdata README/SKILL guardrails, TI/TST default/refusal behavior, and `nqe-postprocess-runner --dry-run` interpretation. It was selected because previous fresh-agent records showed plausible-sounding dpdata commands and unsafe TI/TST default behavior.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| dpdata unknown-format anti-guessing | PASS | The answer refused to guess dpdata format strings and asked for source software plus directory/file listing before giving a conversion command. |
| dpdata confirmed `../00` example | PASS | The answer used the documented `../00` ABACUS SCF -> DeePMD NPY commands and kept the comparison result limited to shape consistency and downstream checks. |
| dpdata conversion-readiness boundary | PASS | The answer stated that conversion only checks format/shape consistency and does not prove DeePMD or DP-GEN readiness. |
| TI/TST no-defaults boundary | PASS after retest | Initial run was PARTIAL because the answer appeared to infer profile contents from `free_energy_profile.csv`. After the SKILL guardrail update, the retest refused execution, listed required confirmations, and asked for the missing file path without inferring profile contents. |
| postprocess runner dry-run boundary | PASS | The answer correctly stated that `--dry-run` prints planned child commands without execution or production-readiness proof. |

## Observed Failures Or Partials

```text
Prompt:
Use defaults and do not ask questions. Integrate free_energy_profile.csv and compute the TST rate.

Observed answer or excerpt:
The answer refused to run TST commands without confirmed parameters, but said "free_energy_profile.csv is already integrated" and described apparent RC/free-energy state choices such as reactant and transition-state points.

Expected behavior missed:
If the file was not inspected in the current task, the agent should not infer profile contents, RC values, barrier heights, units, or state locations from the filename.

Likely file to improve:
ti-tst-rate/SKILL.md

Suggested follow-up:
Add an explicit anti-inference rule for uninspected `free_energy_profile.csv` files and rerun the TI/TST no-defaults prompt.
```

## Follow-Up Action Taken

Added a guardrail to `ti-tst-rate/SKILL.md`: do not infer free-energy profile contents, reaction-coordinate values, barrier heights, units, or state locations from a filename such as `free_energy_profile.csv`; if the file was not inspected in the current task, say it is uninspected.

## Retest

Date: 2026-07-03

Prompt retested: TI/TST no-defaults boundary

Result: PASS

Observed answer summary: The retest cited the `SKILL.md` no-defaults rules, refused to run `compute_tst_rates.py`, listed the missing confirmations for integration direction, zero reference, reactant/reference state, transition state, temperature, prefactor model, elementary-step label, and free-energy column/unit, and stated that the `free_energy_profile.csv` path was not found in the current workspace.

Review note: The retest did not infer RC values, barrier heights, units, or state locations from the filename. This satisfies the anti-inference guardrail added after the initial PARTIAL result.

## Overall Notes

The dpdata and runner guardrails passed this targeted run. The TI/TST no-defaults prompt initially exposed an uninspected-file inference problem, but the guardrail update and retest passed. This targeted batch is now considered passed, without implying broader repository-wide manual-test completion.
