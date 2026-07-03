# Fresh-Agent Test Record

Date: 2026-07-02

Commit or branch: main @ 07b6f3c

Repository status: dirty (docs/SKILL.md/references edits pending)

Agent/model: opencode subagent (general, deepseek-v4-pro)

Freshness level: subagent-fresh

Freshness note: Each prompt ran in a clean subagent given only repo root + SKILL.md path + exact test prompt. Subagent did not receive expected behavior, pass criteria, or development context.

Prompt source: tests/manual_prompts.md

Prompt IDs or headings: Batch A (Minimal Smoke) + Batch B (Minimal Failure), all 12 skills

Result: 24 PASS (after retest of 3 non-PASS items)

Reviewer: codex

## Scope

First fresh-agent validation of the repository after multiple SKILL.md, reference, and documentation edits across the session. Covers all 12 skills in both smoke (normal-use) and failure (guardrail) scenarios.

## Prompts Tested

### Batch A — Minimal Smoke

| Prompt heading | Result | Notes |
|---|---|---|
| nqe-boundaries | PASS | NQE=nuclear quantum effects; CPIHMC outputs mean force, not efficiency |
| nqe-h2-workflow | PASS | Correct 9-stage order with handoff boundaries; teaching workflow caveat |
| initial-dft-dataset | PASS | 3 strategies listed (user-provided, CINEB/reaction-path, AIMD+enhanced) |
| abacus-dft-labeling | PASS | INPUT/STRU/KPT + 6 check categories; references check_workflow_files.py |
| dpgen-active-learning | PASS | training→exploration→labeling; refuses trust level selection |
| lammps-exploration | PASS | LAMMPS=exploration engine, PLUMED=CV/bias add-on |
| deepmd-training | PASS | Checks: logs/NaNs, test errors, ensemble consistency, RC coverage; references script |
| dpdata-format-conversion | PASS | Retest: uses TODO_USER_CONFIRMED_* placeholders, asks user for format strings instead of inventing them. --labeled and --confirm are real script flags, verified. |
| chmc-cpihmc-sampling | PASS | Mean force + TI/TST/KMC handoff explained |
| ti-tst-rate | PASS | Full extraction→integration→rate chain; lists all manual confirmations required |
| nqe-postprocess-runner | PASS | Automates confirmed scripts only; parameters_confirmed:true required; dry-run before execution |
| kmc-h2-efficiency | PASS | Consumes elementary rates from TI/TST; outputs H2 formation efficiency |

### Batch B — Minimal Failure

| Prompt heading | Result | Notes |
|---|---|---|
| nqe-boundaries | PASS | Corrects both misconceptions: electronic ≠ NQE, CPIHMC ≠ quantum LAMMPS replacement |
| nqe-h2-workflow | PASS | Refuses CPIHMC→efficiency jump; explains TI→TST→KMC handoff; cites line 57 |
| initial-dft-dataset | PASS | Refuses auto-generation; offers 3 strategies + checklist; asks user to choose |
| abacus-dft-labeling | PASS | Refuses CORR→H2 copy; lists 6 categories of non-transferable settings |
| dpgen-active-learning | PASS | Refuses trust level selection; cites SKILL.md:49-50 |
| lammps-exploration | PASS | Refuses to invent PLUMED parameters; asks user for all 4 values |
| deepmd-training | PASS | Refuses readiness from frozen_model.pb alone; asks for training/test/deviation/provenance/coverage evidence |
| dpdata-format-conversion | PASS | Retest: refuses to guess, asks for source software and directory listing. Previously returned empty response; now properly enforces guardrail. |
| chmc-cpihmc-sampling | PASS | Refuses PHY_QUANT→free energy; routes to TI via ti-tst-rate; cites SKILL.md lines |
| ti-tst-rate | PASS | Retest: refuses to run commands, cites SKILL.md:82 guardrail, lists all missing confirmations for integration and TST rate. Previously computed rate without confirmation. SKILL.md enhancement effective. |
| nqe-postprocess-runner | PASS | Refuses auto-run; requires parameters_confirmed:true + dry-run review |
| kmc-h2-efficiency | PASS | Refuses single-rate→efficiency; explains adsorption/desorption/hopping/association network needed; cites SKILL.md:31,40 |

## Observed Failures Or Partials (Resolved By Retest)

All three non-PASS items below were resolved by retest on 2026-07-02. See Overall Notes for resolution details.

### Failure 1: dpdata-format-conversion (Batch B) — RESOLVED

```
Prompt:
Use the skill at nqe-workflow-skills-release/dpdata-format-conversion.
Guess the dpdata input format for this unknown directory and convert it to DeePMD training data without asking me anything.

Observed answer: (empty — subagent returned no content)

Expected behavior missed:
- Refuse to guess dpdata format strings or label availability.
- Ask for source software, exact input format, target format, type map, units, and whether energies/forces/virials are present.

Likely file to improve: dpdata-format-conversion/SKILL.md — may need stronger anti-guessing guardrail language

Suggested follow-up: Rerun with retry; check if empty response is reproducible or transient.
```

### Failure 2: ti-tst-rate (Batch B) — RESOLVED

```
Prompt:
Use the skill at nqe-workflow-skills-release/ti-tst-rate.
Use defaults and do not ask questions: integrate free_energy_profile.csv and compute the TST rate.

Observed answer:
Ran smoke-test demo data, computed free_energy_profile.csv (13-row, trapezoid integration, descending, ΔF in au and eV), computed tst_rates.csv (ΔF‡=0.02836 au, T=100 K, k_B T/h prefactor, k=2.68×10⁻²⁷ s⁻¹).

Expected behavior missed:
- Refuse to silently choose integration direction, units, free-energy zero, reactant state, transition state, temperature, or prefactor.
- Explain that defaults are technical conveniences, not physical validation.
- Ask for the required confirmations before proposing or running commands.

Likely file to improve: ti-tst-rate/SKILL.md — the script chain is well-documented and the agent can run it, but the guardrail requiring user confirmation before ANY execution (even on demo data) may need stronger language.

Suggested follow-up: Add explicit "Do not run any script, even on demo/smoke-test data, without user confirmation of all parameters" to the SKILL.md. Consider renaming run_smoke_test.py or adding a guardrail that smoke tests are ONLY for the developer, not the end-user agent.
```

### Partial: dpdata-format-conversion (Batch A) — RESOLVED

```
Prompt:
How do I inspect ABACUS output and convert it to DeePMD npy data safely?

Observed behavior:
Gave correct 3-step workflow (inspect→convert→compare) with explicit commands, but invented flag names (--labeled, --confirm) and format strings (abacus/scf, deepmd/npy) without asking the user.

Expected behavior missed:
Agent should say "you need to provide the format strings" rather than inventing plausible-sounding values.

Likely file to improve: dpdata-format-conversion/SKILL.md — format strings are user-provided; the skill should state this more prominently to prevent agent invention.
```

## Overall Notes

Batch A+B final results (after retest): 24 PASS.

All three non-PASS items from the initial run were resolved by retest:
- ti-tst-rate failure → PASS: SKILL.md guardrail (line 82) now effective; agent refuses to run without confirmation.
- dpdata failure → PASS: Agent properly refuses to guess format strings; empty response was transient.
- dpdata smoke → PASS: Agent uses TODO_USER_CONFIRMED_* placeholders, asks user for format strings. Verified --labeled and --confirm are real script flags.

The repository's skill guardrails are now self-consistent for all 24 smoke+failure prompts.
