# PHY_QUANT Convergence Diagnostics

Use this reference after each CHMC/CPIHMC reaction-coordinate window finishes sampling and before mean force is handed to thermodynamic integration.

## What To Check

For each window, inspect at least the potential energy and the mean-force column that corresponds to the reaction coordinate used for TI.

Typical columns are:

- PotEng: potential energy diagnostic
- MeanForce: mean force when only one reaction coordinate is defined
- MeanForce_0, MeanForce_1, ...: mean force for multiple reaction coordinates
- RxnCoord, RxnCoord_0, ...: sampled reaction-coordinate values

Column indices in the scripts are zero-based. Prefer column names when the header is available.

## Diagnostic Script

Use scripts/analyze_phy_quant_convergence.py to plot one or more columns from a PHY_QUANT or energy.dat style file.

Example command:

    python chmc-cpihmc-sampling/scripts/analyze_phy_quant_convergence.py --input PHY_QUANT --column PotEng --column MeanForce_0 --output convergence.png --summary convergence_summary.csv --auto-equilibration --running-window 1000 --confirm-parameters

The plot contains:

- instantaneous values
- cumulative average from the beginning of the plotted data
- optional rolling average
- final production mean after the selected or suggested equilibration cutoff
- optional vertical equilibration cutoff line

The CSV summary contains the selected cutoff, production mean, standard deviation, standard error of the mean, and the reason for any automatic suggestion.

## Required Agent Behavior

Before running the script, ask the user to confirm:

- input file path
- columns to inspect
- whether any initial rows should be skipped
- whether --equilibration-index, --equilibration-step, or --auto-equilibration should be used
- whether any unit scaling is needed through --x-scale or --y-scale
- whether the selected reaction-coordinate/mean-force pair is the one intended for TI

After running the script, do not declare convergence from the CSV alone. Ask the user to inspect the plot. If the automatic cutoff is used, report that it is a suggested cutoff, not proof of equilibration.

## Automatic Convergence Heuristic

--auto-equilibration scans candidate burn-in fractions and chooses the first one whose remaining trajectory passes simple block-stability checks:

- enough production samples remain
- early and late block means agree within a combined-SEM or relative/absolute tolerance rule
- block-mean drift is small compared with block scatter

This is useful for screening many windows and finding likely pre-equilibration lengths. It is not rigorous proof of Markov-chain convergence.

For stronger evidence, consider:

- block averaging with increasing block size
- integrated autocorrelation time and effective sample size
- multiple independent replicas and cross-run agreement
- smoothness of mean force across neighboring reaction-coordinate windows
- bead-number convergence for CPIHMC

Keep the final decision human-approved unless the project has already validated an automated rule for this system.
