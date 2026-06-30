# DP-GEN Exploration Strategy Notes

Use these notes when planning the exploration/model-deviation stage of DP-GEN.

## General Strategy

A practical active-learning strategy is to start exploration conservatively and then expand sampling as the model becomes more stable. Common ways to do this include:

- start with lower temperatures and shorter trajectories
- gradually increase trajectory length
- gradually increase temperature or diversify thermodynamic conditions
- add more system configurations or reaction-coordinate regions after early iterations are stable
- monitor model deviation and failed first-principles labels before increasing exploration aggressiveness

This is a strategy pattern, not a default schedule. The actual temperature, pressure, timestep, trajectory length, PLUMED bias, trust levels, and system index coverage are project-specific.

## Lesson From The CORR Reference Example

The CORR reference example under `templates/reference-examples/corr-dpgen/` contains many `model_devi_jobs` entries. It keeps the observed temperature fixed while increasing LAMMPS step counts from short to longer trajectories. That illustrates the broader idea of staged exploration: begin with cheaper/safer exploration and gradually increase sampling intensity.

## Checks Before Increasing Exploration Intensity

Before moving to longer trajectories, higher temperatures, stronger biasing, or broader configuration coverage, check:

- whether model-deviation distributions are stable or dominated by pathological structures
- whether ABACUS labeling succeeds for selected candidates
- whether selected candidates are chemically meaningful and relevant downstream
- whether DeePMD training logs remain stable across iterations
- whether the trust levels and candidate counts are still appropriate

Do not treat decreasing candidate counts alone as proof of convergence.
