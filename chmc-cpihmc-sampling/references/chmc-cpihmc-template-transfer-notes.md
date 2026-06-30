# CHMC/CPIHMC Template Transfer Notes

Use these notes when converting a real CHMC/CPIHMC input or output into a reusable reference example.

## Transferable Patterns

- separate simulation parameters (`INPUT`) from structure (`STRU`) and optional bead coordinates (`BEADS`)
- record the DeePMD/DP model path and provenance before sampling
- document reaction coordinate, window/grid point, temperature, HMC settings, and output intervals
- preserve output files needed by TI, especially mean force and uncertainty/block statistics when available
- keep model-deviation diagnostics separate from convergence proof

## Do Not Transfer Blindly

- reaction coordinate definitions and virtual atom selections
- bead number, bead-change policy, and bead convergence assumptions
- HMC timestep, number of evolution steps, mass scaling, hybrid MC ratio, sampling length, and seeds
- walls, group definitions, grand-canonical controls, and electron-number settings
- mean-force sign convention and units
- model path or frozen model choice without downstream validation evidence

## Grand-Canonical / Constant-Potential Transfer Boundary

Grand-canonical CHMC/CPIHMC is a transferable software capability of the package, not a default assumption for every workflow. When adapting examples:

- Transfer the idea that electron-number controls can represent electrochemical/constant-potential-like sampling when documented.
- Do not transfer `Mu`, electron-number ranges, widths, or initial electron numbers between systems without user approval.
- Keep constant-potential interpretation tied to the physical model, units, and electrochemical reference used by the project.

## Agent Behavior

- Use official notes and local command help rather than inventing fields.
- Ask the user to approve reaction coordinates, bead settings, and sampling controls.
- Treat `PHY_QUANT` as input to TI only after units, sign convention, grid, and uncertainty information are documented.
- Report missing diagnostics as TODO instead of declaring convergence.
