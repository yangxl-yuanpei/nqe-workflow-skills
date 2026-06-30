# LAMMPS DP-GEN Handoff

This reference explains how LAMMPS exploration connects to DP-GEN in this skills library.

## DP-GEN Stage

LAMMPS belongs to the DP-GEN exploration/model-deviation stage. The canonical DP-GEN loop remains:

training -> exploration -> labeling

LAMMPS is an exploration engine inside the exploration stage. It is not a fourth DP-GEN stage.

## Template Substitution

Real DP-GEN `model_devi_jobs` may point to LAMMPS and PLUMED templates, then substitute values through matrices such as:

- `V_TEMP`: exploration temperature
- `V_PRES`: exploration pressure
- `V_NSTEPS`: trajectory length
- `V_STRIDE`: PLUMED/output stride or a project-specific variable

These names come from project templates; verify the actual LAMMPS script before interpreting them.

## CORR DP-GEN Reference

The CORR DP-GEN reference example uses `lmp/input.lammps` and multiple PLUMED templates in `model_devi_jobs`. The observed pattern increases LAMMPS step count from short to longer trajectories while holding the observed temperature fixed. Treat this as a staged exploration example, not as H2/graphene defaults.

## Handoff To Labeling

LAMMPS exploration generates configurations. DP-GEN model-deviation filtering selects candidates. ABACUS then labels selected candidates with first-principles energy/force/virial data. Do not call LAMMPS output a DFT label.
