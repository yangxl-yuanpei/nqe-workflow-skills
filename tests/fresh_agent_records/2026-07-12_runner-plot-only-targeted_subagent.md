# Fresh-Agent Test Record

Date: 2026-07-12

Commit or branch: working tree, not committed

Repository status: dirty; includes runner plot-only implementation, real-case record pruning, and documentation updates

Agent/model: Codex subagent via `multi_agent_v1`, default inherited model

Freshness level: targeted subagent, no forked parent context

Freshness note: The subagent was started with `fork_context: false` and was explicitly instructed to read `nqe-postprocess-runner/SKILL.md`, `nqe-postprocess-runner/references/config-schema.md`, and the relevant manual prompt section before answering.

Prompt source: `tests/manual_prompts.md`

Prompt IDs or headings: `nqe-postprocess-runner / Test 6: Plot-Only Existing Outputs`

Result: PASS

Reviewer: Codex main session

## Scope

This targeted test checks the newly added `stop_after: plot` runner behavior. It was selected because plot-only support should let an agent plot existing reviewed CSV outputs without inventing sampling, extraction, integration, TST, or physical defaults.

## Prompts Tested

| Prompt heading | Result | Notes |
|---|---|---|
| Plot-Only Existing Outputs | PASS | Correctly proposes `stop_after: plot`, asks for existing CSV paths, dataset label, `plot_rc_order`, y-column choices, and plotted free-energy unit label. It states that sampling-output fields, parser columns, skiprows, integration fields, and TST fields are not needed unless regenerating CSVs. It refuses extraction/integration/TST and preserves the visualization-only boundary. |

## Observed Answer Excerpt

```text
可以。这里应使用 `stop_after: plot`，不是 `stop_after: all`。这样 runner 只会从已有 CSV 生成图，不会重新做窗口发现、收敛诊断、mean-force extraction、TI integration，也不会运行 TST 或选择 reactant/transition-state。
```

The answer then requested:

```text
dataset_label
output_dir
mean_force_table
mean_force_y_column
free_energy_profile
free_energy_y_column
free_energy_plot_unit_label
plot_rc_order
```

It also stated:

```text
For plot-only 模式，不需要 `sampling_output_root`、`input_file`、`window_glob`、parser columns、`skiprows`、unit conversion、integration direction、zero reference 或 TST prefactor/state-selection 字段，除非你想重新生成 CSV。
```

## Observed Failures Or Partials

None for this targeted prompt.

## Overall Notes

The targeted plot-only behavior is ready for this prompt. This record does not claim a full fresh-agent pass for all runner prompts or the full repository. Future runner fresh-agent tests should still cover plot-only failure cases such as missing CSV paths, missing dataset labels, absent y-columns, missing `plot_rc_order`, and attempts to combine plot-only requests with TST defaults.
