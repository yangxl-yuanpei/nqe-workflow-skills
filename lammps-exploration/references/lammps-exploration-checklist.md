# LAMMPS Exploration Checklist

Use this checklist for LAMMPS exploration in DP-GEN active learning. It is not a production input template.

## Required Inputs

- LAMMPS input script, usually `input.lammps` or a project-specific template
- structure source such as LAMMPS data file, restart file, or DP-GEN-generated configuration
- DeePMD frozen model files or model ensemble paths
- element/type map consistent with DeePMD training data
- user-approved ensemble, timestep, temperature/pressure, run length, and output frequency
- optional PLUMED/bias template when biased exploration is used

## Staged Exploration

A common DP-GEN strategy is to start LAMMPS exploration conservatively and then expand sampling intensity as the model becomes stable. Common knobs include:

- lower to higher temperature
- shorter to longer trajectories
- narrower to broader system/configuration coverage
- weaker to stronger biasing or more PLUMED templates
- cheaper early trajectories before expensive long runs

This is only a strategy pattern. Do not choose the actual schedule without user approval.

## Input Script Checks

- confirm `units` match model training and downstream interpretation
- confirm atom types and type map match DeePMD model expectations
- confirm `pair_style` and `pair_coeff` refer to the correct model files
- confirm variables such as temperature, pressure, timestep, run length, and restart flag are documented
- confirm thermostat/barostat choices match the intended ensemble
- confirm dump and thermo settings are sufficient for model-deviation analysis
- confirm restart behavior is deliberate

## Output Checks

- LAMMPS exits normally
- log contains no fatal errors, NaNs, or obvious instabilities
- thermo columns needed for sanity checks are present
- dump or trajectory files exist at expected frequency
- atom count, type map, and cell information remain consistent
- generated configurations are chemically plausible before ABACUS labeling

## Failure Modes To Flag

- exploding temperature, pressure, or energy
- missing model files or pair-style plugin errors
- type-map mismatch between LAMMPS data and DeePMD model
- broken dump format or missing trajectory
- trajectories dominated by unphysical structures
- confusion between exploration configurations and DFT labels
