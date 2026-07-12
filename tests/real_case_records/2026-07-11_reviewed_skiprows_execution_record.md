# 2026-07-11 Reviewed Per-Window Skiprows Execution Record

Runner config: `tests/runner_configs/demo_multi_window_candidate_skiprows.yaml`

Override CSV: `tests/runner_configs/demo_multi_window_candidate_skiprows.csv`

Generated outputs:

- `tests/real_case_records/2026-07-11_candidate_skiprows/output/mean_force_table.csv`
- `tests/real_case_records/2026-07-11_candidate_skiprows/output/summary.json`

Note: duplicate convergence CSV attachments from this execution were pruned during repository cleanup. Use the canonical baseline convergence summaries in `tests/real_case_records/2026-07-10_demo_runner_dry_run/convergence/` plus the reviewed output table above.

Boundary: this record accepts `10000` discarded rows for windows `0.0` and `1.8` in this demo review only. It does not approve a reusable production discard policy, does not certify convergence, and does not approve TI/TST. In production-facing use, the user must inspect the convergence plots/CSVs directly and personally decide whether the discard length is scientifically reasonable.

## Accepted Demo Policy

The user accepted a `10000`-row discard for this reviewed demo extraction:

```csv
sample_label,skiprows
0.0,10000
1.8,10000
```

All other windows use the global `skiprows: 0`.

Rationale:

- `0.0`: MeanForce convergence screening suggested `eq_index = 10000`, and sensitivity screening showed a noticeable mean-force shift with discard.
- `1.8`: RxnCoord shows clear initial adjustment toward the target coordinate, and sensitivity screening showed both RC and mean-force shifts with discard.

## Baseline Versus Reviewed Extraction

Only the two accepted per-window discard overrides changed the extracted values:

```text
sample  baseline_skip  reviewed_skip  baseline_rc     reviewed_rc     delta_rc       baseline_force      reviewed_force      delta_force
0.0     0              10000          0               0               0              0.003559083231      0.003992000644      +0.000432917414
1.8     0              10000          1.83857238572   1.80061778464   -0.03795460108 -0.009006869119     -0.008425684963     +0.000581184156
```

The reviewed `1.8` extraction is much closer to the intended window coordinate after the startup adjustment, but this is still diagnostic evidence rather than automatic convergence proof.

## Production Reminder

For any real production handoff to TI:

- Do not reuse this `10000` value as a default for a new system.
- Plot or otherwise inspect the relevant PotEng/RxnCoord/MeanForce convergence diagnostics.
- Ask the user to personally approve the discard policy after looking at the plots/CSVs.
- Regenerate the mean-force table from the approved policy.
- Only then discuss TI direction, zero reference, units, and sign convention.
