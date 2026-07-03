# Repair Verification Record

Date: 2026-07-02

Commit or branch: working tree after `07b6f3c`

Repository status: dirty; repairs made after reviewing `2026-07-02_batch-ab_codex.md` and `2026-07-02_batch-d_codex.md`.

Agent/model: codex

Freshness level: N/A

Freshness note: This is a targeted repair verification record, not a fresh-agent behavior test.

Prompt source:

- `tests/fresh_agent_records/2026-07-02_batch-ab_codex.md`
- `tests/fresh_agent_records/2026-07-02_batch-d_codex.md`

Result: targeted script/interface checks PASS; fresh-agent retest still needed.

Reviewer: codex

## Scope

This record tracks fixes for issues observed in the fresh-agent and script smoke records:

- TI/TST guardrail failure: agent ran demo/smoke-test data and computed a TST rate when asked to use defaults without questions.
- dpdata partial/failure: agent invented dpdata format strings and command flags, and one subagent returned an empty answer.
- Script smoke warnings: four `--print-defaults` modes were blocked by argparse `required=True`.
- Runner dry-run warning: `nqe_postprocess_runner.py --dry-run` looked too much like execution and previously created output directories.

## Changes Verified

### `--print-defaults`

The following commands now exit `0` and print defaults without requiring other arguments:

```bash
python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py --print-defaults
python ti-tst-rate/scripts/extract_mean_force.py --print-defaults
python ti-tst-rate/scripts/integrate_free_energy.py --print-defaults
python ti-tst-rate/scripts/compute_tst_rates.py --print-defaults
```

Implementation note:

- Required argparse fields were converted to runtime validation so `--print-defaults` can short-circuit first.

### `nqe_postprocess_runner.py --dry-run`

The following commands now print generated child commands and end with an explicit dry-run message:

```bash
python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  nqe-postprocess-runner/assets/config.example.yaml \
  --dry-run

python nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  nqe-postprocess-runner/assets/config.convergence-screening.example.yaml \
  --dry-run
```

Observed message:

```text
DRY RUN: generated N command(s); no commands were executed and no output files were written.
```

Additional check:

- `tmp/nqe-postprocess-demo-output/summary.json` did not exist after dry-run verification.

Implementation note:

- Dry-run mode no longer creates the output directory or writes summary files.

### TI/TST Guardrail

`ti-tst-rate/SKILL.md` now explicitly says not to run TI/TST scripts, including demo or smoke-test scripts, when the user asks to use defaults or not ask questions.

It also states that `run_smoke_test.py` may be run only when the user explicitly asks for the bundled demo smoke test or when a developer is performing script-interface testing.

### dpdata Anti-Guessing

`dpdata-format-conversion/SKILL.md` and `dpdata-format-conversion/README.md` now use `TODO_USER_CONFIRMED_*` placeholders instead of concrete format strings in examples.

The skill now explicitly says not to provide runnable conversion commands with invented format strings, paths, labels, or flags.

## Commands Run

```bash
python -m py_compile \
  nqe-postprocess-runner/scripts/nqe_postprocess_runner.py \
  chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py \
  ti-tst-rate/scripts/extract_mean_force.py \
  ti-tst-rate/scripts/integrate_free_energy.py \
  ti-tst-rate/scripts/compute_tst_rates.py
```

Result: `PASS`

```bash
python dpdata-format-conversion/scripts/inspect_dpdata_system.py --help
```

Result: `PASS`

## Remaining Follow-Up

- Rerun the affected fresh-agent prompts for `ti-tst-rate` and `dpdata-format-conversion`.
- Rerun script-level smoke Batch D so the historical `12 PASS, 4 WARN` summary can be superseded by a new dated record.
- Check whether the `dpdata-format-conversion` empty answer was transient or reproducible.

