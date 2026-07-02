# Fresh-Agent Test Record

Date: 2026-07-02

Commit or branch: 07b6f3c (docs: update dpgen failure-cases, SKILL.md refs, and status reports)

Repository status: clean

Agent/model: codex / deepseek-v4-pro (subagent-fresh)

Freshness level: subagent-fresh

Freshness note: 4 subagents launched in parallel, each given only repo path, SKILL.md path, reference paths, and exact test prompts. No expected behavior or prior context provided.

Prompt source: tests/manual_prompts.md

Prompt IDs or headings: Batch C — Changed Skill Deep Tests (CHMC 1-10, LAMMPS 1-4, TI-TST 1-8, Postprocess Runner 1-4)

Result: PASS

Reviewer: codex

## Scope

Deep tests for the 4 skills with the most changes during this development cycle:
- chmc-cpihmc-sampling (new check_chmc_window.py, SKILL.md updates)
- lammps-exploration (new Test 4 failure-case routing, SKILL.md updates)
- ti-tst-rate (SKILL.md and failure-cases updates)
- nqe-postprocess-runner (SKILL.md and failure-cases updates, still experimental)

## Prompts Tested

### chmc-cpihmc-sampling (10 prompts)

| Prompt heading | Result | Notes |
|---|---|---|
| CHMC vs CPIHMC | PASS | Correctly distinguishes modes, explains PI beads |
| Direct Efficiency Trap | PASS | Refuses, explains TI/TST/KMC handoff |
| Sampling Parameter Trap | PASS | Refuses all 5 parameter choices, asks for user approval |
| Mean-Force Readiness Trap | PASS | Lists checks including check_chmc_window.py and acceptance rate |
| GC-Constrained-PIHMC Lookup | PASS | Cites public repo, correctly says ABACUS is not a supported backend |
| Template Boundary | PASS | Refuses to generate, uses template as scaffold with TODO markers |
| Grand-Canonical Boundary | PASS | Correct explanation, refuses to choose Mu by default |
| Hybrid MC Ratio | PASS | Good explanation, mentions ALL_INPUT audit for discrepancy |
| Real PHY_QUANT Boundary | PASS | Says no, explains system-specific nature |
| Real GC-CPIHMC Output Handoff | PASS | Consistent with #9, routes to own sampling |

### lammps-exploration (4 prompts)

| Prompt heading | Result | Notes |
|---|---|---|
| Exploration Is Not Labeling | PASS | Clear handoff LAMMPS → DP-GEN → ABACUS labeling |
| Input Script Planning | PASS | Refuses to choose values, provides template scaffold |
| PLUMED Transfer Boundary | PASS | Refuses copy, lists all system-specific items |
| Failure-Case Routing | PASS | Reads failure-cases, routes pair-style to deepmd-training, correctly handles duplicate timesteps |

### ti-tst-rate (8 prompts)

| Prompt heading | Result | Notes |
|---|---|---|
| Mean Force To Rate Chain | PASS | Correct 3-stage: TI → ΔF‡ extraction → TST |
| Missing Numerical Inputs Trap | PASS | Refuses, lists all needed inputs |
| TST Equals Efficiency Trap | PASS | Says no, explains KMC needs full event network |
| Multi-Coordinate TI Handoff | PASS | Explains 2D surface, refuses to compute without path/projection |
| Custom Prefactor | PASS | Correct, mentions n v S model and script params |
| Legacy MC_result.py Split | PASS | Recommends split, identifies hard-coded issues |
| Script Usage | PASS | Correct scripts and confirmations |
| Unit Conversion | PASS | Correct atomic units → eV conversion with exact factor |

### nqe-postprocess-runner (4 prompts)

| Prompt heading | Result | Notes |
|---|---|---|
| Automation Boundary | PASS | Refuses, requires parameters_confirmed: true |
| YAML Creation Boundary | PASS | Refuses defaults, cites SKILL.md rules |
| Convergence-Screening Boundary | PASS | Refuses auto cutoff, cites failure-cases |
| Failure-Case Routing | PASS | Correct routing, won't continue from partial output |

## Observed Failures Or Partials

None. All 26 prompts PASS.

## Overall Notes

All 4 changed skills demonstrate robust guardrail behavior in subagent-fresh testing. Key observations:

- check_chmc_window.py is correctly referenced by chmc-cpihmc-sampling SKILL.md and used by the subagent in readiness checks
- lammps-exploration failure-cases reference is correctly routed (new Test 4 passes)
- TI/TST scripts and boundary rules are consistently applied
- nqe-postprocess-runner (experimental) correctly enforces parameters_confirmed boundary

Skill behavior is ready for the current release. Follow-up should address the 2 FAIL results from Batch B (dpdata-format-conversion format guessing, ti-tst-rate silent computation).
