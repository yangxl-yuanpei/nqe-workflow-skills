# Release Readiness Checklist

Last updated: 2026-07-17

This checklist separates what is suitable for a public repository release from
what remains local validation evidence or future production-workflow work.

The repository is release-facing as a teaching, checking, and semi-automated
post-processing skills library. It is not release-ready as a one-click
computational production pipeline.

## Recommended Release Profile

Recommended public framing:

```text
An agent-readable skills library for teaching, checking, and guarded
post-processing across an atomistic NQE workflow.
```

This is a good release profile because it matches the repository's strongest
evidence: broad workflow coverage, populated guardrails, conservative scripts,
manual prompts, fresh-agent records, and selected real-case diagnostic records.

Avoid framing the release as:

```text
A complete automated NQE production workflow.
A validated H2 formation-efficiency pipeline.
A benchmark dataset or reproducibility package for a specific physical system.
```

Those stronger profiles would require bundled target-system inputs, confirmed
physical parameters, reproducible raw data, end-to-end provenance, convergence
evidence, uncertainty propagation, and complete KMC event-network validation.

## Public Repository Contents

The following content is suitable for a public skills-library release:

- The 12 `SKILL.md` directories and their stage-specific references.
- Template files with explicit `TODO_USER_APPROVAL` placeholders.
- Failure-case references that describe common unsafe agent behaviors.
- Conservative Python helper scripts for static checks, diagnostics, format
  inspection/conversion, CHMC/CPIHMC screening, TI/TST post-processing, plotting,
  and guarded runner orchestration.
- `tests/manual_prompts.md` as behavior-test prompts for fresh agents.
- Small runner fixtures under `tests/runner_configs/`, including negative
  fixtures that are expected to fail.
- Dated fresh-agent records under `tests/fresh_agent_records/`, as prompt-level
  behavior evidence rather than benchmark claims.
- Compact real-case records under `tests/real_case_records/`, as diagnostic and
  regression evidence rather than raw production data.

## Public Release Boundaries

A public release should state these boundaries clearly:

- This repository teaches and checks cross-stage workflow reasoning; it does not
  choose target-system physics.
- Reference examples are file-shape and transfer-boundary examples, not default
  parameters for a new calculation.
- Helper-script success is diagnostic evidence only. It is not proof of
  convergence, physical correctness, TST readiness, KMC readiness, or production
  validity.
- ABACUS is the documented open DFT backend in this repository.
- Upstream DeepModeling skills are useful software-operation references, but
  they do not override this repository's scientific guardrails.

## Local Or Maintainer-Only Evidence

The following evidence is useful for project development but should not be
presented as bundled public data:

- `../00`: a maintainer-local mini example for confirmed
  `abacus/scf -> deepmd/npy` dpdata inspection and comparison. It may not exist
  in a fresh clone.
- `../demo`: a maintainer-local 13-window CHMC/CPIHMC-style dataset used for
  runner and TI-only validation. The raw data are intentionally outside the
  repository.
- Large raw `PHY_QUANT` files. Only compact metadata, excerpts, checksums, and
  derived diagnostic records should be retained in the repository.
- Local absolute paths. Retained records should use sanitized placeholders such
  as `<REPO>`, `<USER_SITE_PACKAGES>`, and `../demo`.

The public repository may mention `../00` and `../demo` as sanitized external
path labels. Those labels should be read as maintainer-local evidence pointers,
not as files guaranteed to exist in a fresh clone. Do not move large raw data
into the repository just to make those paths resolvable.

## Evidence That Can Be Claimed

The current repository can reasonably claim:

- Broad skill coverage from DFT dataset preparation through KMC reasoning.
- Populated failure-case references for all major stages.
- Manual prompt coverage for normal-use and guardrail behavior.
- Recorded fresh-agent passes for selected targeted behavior, including runner
  preflight, plot-only boundaries, deeper runner failure cases, output-directory
  reuse boundaries, and upstream DeepModeling boundary behavior.
- Script-level syntax and interface checks for the current helper scripts.
- Real or representative diagnostic records for selected CHMC/CPIHMC, runner,
  TI-only, and plot-only paths.
- A clear separation between public teaching/checking artifacts and
  maintainer-local raw validation data.

Use careful wording:

```text
Recorded targeted fresh-agent and script-level checks pass for the tested
sections.
```

Avoid stronger wording:

```text
All possible agent behavior is validated.
The workflow is production-ready.
The real-data examples prove convergence or physical correctness.
```

## Claims To Avoid

Do not claim:

- The repository is a fully automated production workflow.
- Bundled or local examples are reusable physical defaults.
- The runner can safely infer parser mode, columns, unit conversions,
  equilibration discard, integration direction, state selection, TST prefactor,
  or KMC event networks.
- A single TST rate is enough for H2 formation efficiency.
- KMC can consume raw CHMC/CPIHMC trajectories or mean-force files directly.
- Fresh-agent records are equivalent to exhaustive formal verification.

## Release-Blocking Issues

The following issues should be checked before tagging or announcing a public
release:

- `git status --short` is clean.
- `git diff --check` passes before commit.
- A local-path scan finds no maintainer absolute paths in public docs or
  retained records.
- The README, quickstart, testing guide, current-status report, and pending-work
  document agree on the same maturity level.
- Any local-only example path is labeled as maintainer-local and not guaranteed
  to exist in a fresh clone.
- New script changes have at least syntax/interface checks and relevant
  failure-boundary notes.
- The release announcement or repository description uses the recommended
  teaching/checking/post-processing profile rather than production-pipeline
  wording.

Useful checks:

```bash
git status --short
git diff --check
rg -n "C:\\\\Users|C:/Users|/mnt/c/Users|Documents\\\\Codex" README.md docs tests
python -m py_compile common/scripts/check_workflow_files.py
```

For the Python syntax check, include all helper scripts or use an equivalent
read-only compile check when local `__pycache__` permissions prevent `.pyc`
writing.

## Future Release Improvements

These are useful but not required for a teaching/checking release:

- Replace maintainer-local `../00` with a tiny in-repository dpdata fixture if
  public reproducibility becomes a priority.
- Add a minimal KMC event/rate schema checker when KMC work resumes.
- Extend executable runner negative fixtures toward stale partial-output and
  real-data recovery families.
- Add optional static checkers for DP-GEN, DeePMD, LAMMPS/PLUMED, ABACUS, or
  dpdata conversion plans only if they remain conservative and do not invent
  physical parameters.
- Prepare separate manuscript or project-description materials outside the
  repository if targeting a journal submission.

## Manuscript Readiness Boundary

The repository is mature enough to support an initial methods/software-style
manuscript draft if the paper describes:

- the skill-library design,
- cross-stage scientific guardrails,
- failure-mode references,
- staged post-processing scripts,
- fresh-agent behavior tests, and
- selected diagnostic records as case studies.

The repository alone is not enough for a results paper that claims new
production-quality NQE rates, validated H2 formation efficiencies, or a
complete target-system simulation campaign. Those claims need separate
scientific datasets, parameter justifications, convergence analysis,
uncertainty estimates, and system-specific validation.
