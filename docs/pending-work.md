# Pending Work

Last updated: 2026-07-01

This file tracks work that remains after the current repository consistency pass. It intentionally separates documented repository state from production readiness.

## Current Repository State

- 12 skills exist.
- 14 Python helper scripts exist.
- 19 `.template` files exist.
- 9 failure-case references exist; 3 are still placeholders.
- `nqe-postprocess-runner` has a basic config example and a convergence-screening config example.
- `check_chmc_window.py` exists; it is no longer a future script placeholder.
- `dpgen-active-learning/templates/reference-examples/placeholder-real-example/` contains placeholder-shaped files, but it is not a real DP-GEN example.
- Manual prompts exist, but complete fresh-agent pass records are still missing.

## 1. Failure-Case References

High priority. The following files still need real observed failures, causes, checks, and conservative responses:

- `dpgen-active-learning/references/dpgen-failure-cases.md`
- `kmc-h2-efficiency/references/kmc-failure-cases.md`
- `lammps-exploration/references/lammps-failure-cases.md`

`abacus-dft-labeling/references/abacus-failure-cases.md`, `chmc-cpihmc-sampling/references/chmc-cpihmc-failure-cases.md`, `ti-tst-rate/references/ti-tst-failure-cases.md`, `dpdata-format-conversion/references/dpdata-failure-cases.md`, `nqe-postprocess-runner/references/postprocess-runner-failure-cases.md`, and `deepmd-training/references/deepmd-failure-cases.md` already have populated cases and can be used as style references.

## 2. CHMC/CPIHMC Window Checking

`chmc-cpihmc-sampling/scripts/check_chmc_window.py` exists and should now be exercised on more real or representative windows.

Remaining work:

- Validate acceptance-rate parsing on real logs or outputs.
- Validate final-RC and target-RC checks against real `INPUT`/`ALL_INPUT` examples.
- Connect recurring diagnostic outcomes to `chmc-cpihmc-failure-cases.md`.
- Decide which checks should remain in `check_chmc_window.py` and which should remain in `analyze_phy_quant_convergence.py`.

Boundary: `check_chmc_window.py` can screen file and diagnostic consistency. It must not certify sampling convergence by itself.

## 3. nqe-postprocess-runner Experimental To Ready

Current state:

- Core runner exists.
- Config schema exists.
- Basic and convergence-screening example configs exist.
- Dry-run command generation has been exercised for the bundled demo.

Remaining work:

- Exercise the populated failure cases with fresh-agent behavior tests for config parsing, missing windows, bad columns, unexpected dry-run commands, and child-script failures.
- Add fresh-agent behavior tests for runnable versus non-runnable configs.
- Validate convergence-screening config on real multi-window `PHY_QUANT` data.
- Consider adding a `--generate-config` or draft-config mode only if it can preserve `parameters_confirmed: false` for unapproved values.

## 4. KMC Teaching-Ready To Ready

Current state:

- KMC concepts, state/event/rate-table boundaries, and generic examples exist.

Remaining work:

- Define a minimal KMC event-network schema.
- Add a checker such as `check_kmc_network.py` or `check_kmc_events.py`.
- Add failure cases for missing states, invalid transitions, negative rates, duplicate events, missing reverse events when required, and mismatched output metrics.
- Keep H2 formation efficiency as one possible observable, not a hard-coded output.

## 5. dpdata Conversion Examples

Current state:

- `inspect_dpdata_system.py`, `convert_with_dpdata.py`, and `compare_converted_system.py` exist.

Remaining work:

- Add small real or toy conversion examples with explicit format strings.
- Use the populated dpdata failure cases to design small example checks for wrong format strings, missing labels, element-order mismatch, cell-shape mismatch, and frame-count mismatch.
- Add a short recipe reference for ABACUS -> DeePMD raw/npy and LAMMPS dump inspection when format names are confirmed.

## 6. Fresh-Agent Test Records

Manual prompts are available, but pass/fail records should be dated and scoped.

Recommended record fields:

```text
Date:
Commit or branch:
Agent/model:
Prompt section:
Pass/fail:
Notes:
```

Highest-priority fresh-agent sections:

- `nqe-postprocess-runner`
- `chmc-cpihmc-sampling`
- `ti-tst-rate`
- `dpdata-format-conversion`
- `kmc-h2-efficiency`

## 7. Documentation Synchronization

After future changes, keep these files aligned:

- `README.md`
- `docs/quickstart.md`
- `docs/testing.md`
- `docs/current-status-report.md`
- `docs/pending-work.md`
- affected `SKILL.md` files
- affected `references/*.md` files

Do not state that all manual tests have passed unless there is a dated test record. Do not state that a placeholder example is a real production example.

## Suggested Priority Order

1. Populate DP-GEN and LAMMPS/PLUMED failure references.
2. Run and record fresh-agent tests for changed skills.
3. Validate convergence screening on real multi-window `PHY_QUANT` data.
4. Add a minimal KMC event-network checker.
5. Add real small dpdata conversion examples and failure-case-driven checks.
6. Polish release-facing README and tutorial material after the evidence above is in place.
