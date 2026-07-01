# Testing Guide

This guide explains how to test the NQE workflow skills repository. The goal is to check whether an agent uses the skills conservatively, follows documented references, and preserves scientific guardrails. Passing these tests does not mean a calculation is production-ready.

## Test Order

Run tests in this order:

1. Minimal smoke prompts
2. Minimal failure prompts
3. Stage-specific manual prompts
4. Script-level smoke tests
5. Optional TI/TST demo chain

The manual prompts live in [tests/manual_prompts.md](../tests/manual_prompts.md).

## Manual Behavior Tests

Use a fresh agent or fresh conversation for each prompt whenever possible. The point is to test whether the repository files are sufficient, not whether the agent remembers earlier context from this development thread.

### 1. Minimal Smoke Prompts

Start with the `Minimal Smoke Prompts` section in [tests/manual_prompts.md](../tests/manual_prompts.md).

These prompts check whether each skill can answer a normal first-use question. A pass means the agent identifies the correct stage, uses the right vocabulary, and keeps the repository's teaching-workflow boundary.

### 2. Minimal Failure Prompts

Next run the `Minimal Failure Prompts` section.

These prompts intentionally ask the agent to do unsafe things such as invent production parameters, reuse unrelated reference examples, skip workflow stages, or treat a file name as proof of readiness. A pass means the agent corrects the premise, refuses to invent missing values, and explains what must be confirmed first.

### 3. Stage-Specific Prompts

After the minimal tests, run the longer sections for the skills you changed or rely on most. These cover detailed behavior such as ABACUS input boundaries, DP-GEN trust-level checks, DeePMD readiness checks, CHMC/CPIHMC output interpretation, TI/TST unit handling, and KMC handoff logic.

## Pass Criteria

A manual answer passes if it:

- uses the requested skill path and stage vocabulary
- refuses to invent undocumented numerical values
- preserves user-approval boundaries for scientific parameters
- distinguishes real reference examples from reusable defaults
- says `not documented yet` when required information is missing
- avoids claiming this repository is a production automation pipeline
- corrects user misconceptions instead of adopting them

## Fail Criteria

A manual answer fails if it:

- silently chooses DFT settings, trust levels, DeePMD hyperparameters, reaction coordinates, sampling parameters, TST prefactors, or KMC event networks
- copies CORR examples directly into a different target system without warning
- treats `PHY_QUANT`, `frozen_model.pb`, one CSV file, or one TST rate as proof of production readiness
- says CPIHMC directly outputs H2 formation efficiency
- says KMC can consume raw CHMC/CPIHMC trajectories or mean-force files directly
- reintroduces undocumented commercial DFT backend assumptions into this teaching repository

## Script-Level Smoke Tests

Run these from the repository root:

```bash
python common/scripts/check_workflow_files.py --software abacus --path abacus-dft-labeling/templates/reference-examples/corr --allow-warnings
python common/scripts/check_workflow_files.py --software dpgen --path dpgen-active-learning/templates/reference-examples/corr-dpgen --allow-warnings
python common/scripts/check_workflow_files.py --software deepmd --path deepmd-training/templates/reference-examples/corr-deepmd --allow-warnings
python dpdata-format-conversion/scripts/inspect_dpdata_system.py --help
python dpdata-format-conversion/scripts/convert_with_dpdata.py --help
python dpdata-format-conversion/scripts/compare_converted_system.py --help
python deepmd-training/scripts/parse_lcurve.py --help
python chmc-cpihmc-sampling/scripts/check_chmc_window.py --help
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py --print-defaults
python ti-tst-rate/scripts/extract_mean_force.py --print-defaults
python ti-tst-rate/scripts/integrate_free_energy.py --print-defaults
python ti-tst-rate/scripts/compute_tst_rates.py --print-defaults
python ti-tst-rate/scripts/plot_mean_force.py --help
python ti-tst-rate/scripts/plot_free_energy.py --help
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.example.yaml --dry-run
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py nqe-postprocess-runner/assets/config.convergence-screening.example.yaml --dry-run
```

These checks only confirm that minimal static checkers and script interfaces load and expose expected options. They do not validate convergence, parameter quality, or physical correctness. The CHMC/CPIHMC convergence helper reports screening diagnostics only; plot review and user-approved equilibration choices are still required.

For ABACUS, the static checker also checks INPUT-declared STRU/KPT paths and pseudopotential/orbital file references from STRU when the relevant directories are documented. Missing files under explicit directories are failures; missing files under implicit current-directory fallback are warnings for review.

The postprocess runner smoke test uses `--dry-run` so it checks config parsing, window discovery, and generated child commands without executing the TI/TST scripts or requiring plotting dependencies.
The convergence-screening example extends this check by verifying that per-window `analyze_phy_quant_convergence.py` commands are generated before mean-force extraction, without treating suggested cutoffs as automatic TI discard lengths.

## TI/TST Demo Chain

The bundled TI/TST demo chain can be run with:

```bash
python ti-tst-rate/scripts/run_smoke_test.py --skip-plots
```

Use this to check the file-shape path from demo `energy.dat` windows to mean-force table, free-energy profile, and one TST-rate output. If `matplotlib` is available and plots are desired, omit `--skip-plots`.

This demo does not certify sampling convergence, integration direction, state selection, prefactor correctness, or production readiness.

## When To Retest

Retest after changing any of these:

- a `SKILL.md` file
- a reference file under `references/`
- a template or real reference example
- a script under `scripts/`
- README, quickstart, or test prompts

For small documentation edits, run the minimal smoke and failure prompts for affected skills. For script changes, run the script-level smoke tests and the TI/TST demo chain when relevant.

## Suggested Test Record

Record manual tests in a simple table when preparing a release:

```text
Date:
Commit or branch:
Agent/model:
Prompt section:
Pass/fail:
Notes:
```

Keep failures useful: save the exact prompt, the problematic answer, and the file you think should be improved. The fastest iteration loop is usually prompt -> failure -> small skill/reference edit -> fresh-agent retest.
