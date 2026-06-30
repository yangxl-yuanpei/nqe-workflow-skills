# GC-Constrained-PIHMC Official Notes

Use this reference as the source-of-truth roadmap for the in-house/public CPIHMC implementation documented at `sxu39/GC-Constrained-PIHMC`. Do not invent input fields, commands, simulation defaults, or file formats beyond the repository documentation.

## Source Of Truth

- GitHub repository: https://github.com/sxu39/GC-Constrained-PIHMC
- README documentation: https://github.com/sxu39/GC-Constrained-PIHMC#readme
- Repository description: constrained GC-PIHMC sampling workflow for electrochemical PCET simulations with NQEs explicitly treated by PIMC.

Treat this repository README as the current public documentation for the code. It describes CPIHMC code version `0.1.0alpha` and states that optimizations will be updated in later versions.

## Capabilities Documented In The README

- MD, HMC, and CHMC simulations under canonical or grand-canonical ensemble conditions.
- Nuclear quantum effects through path-integral formalism.
- Grand-canonical ensemble support for CHMC and CPIHMC.
- Potential energy and forces are conceptually described for DP, VASP, and ABACUS, but the README states that only DP is supported for the moment.
- Model deviation is available for potential energy and force calculations by DP and can be used in model-deviation mode.

## Units Documented In The README

- mass: u
- length: Bohr
- time: fs
- energy: u * Bohr^2 * fs^-2
- force: u * Bohr * fs^-2
- temperature: K for `Temp`
- electrochemical potential: eV for `Mu`

Always check unit conversions before handing mean-force output to thermodynamic integration.

## Input Files To Recognize

- `INPUT`: simulation parameters; unspecified parameters use defaults documented by the README.
- `STRU`: initial structure in ABACUS-like format. The README notes that electron number may be placed at the beginning of `STRU` using `ELECTRON_NUMBER` followed by the value.
- `BEADS`: optional initial bead coordinates for path-integral simulations. If used, set `Beads_File` in `INPUT`. The README warns that `BEADS` coordinates are in Bohr.
- DP model file(s): when using DP potential, reference the model using `Deep_Pot_Model` in `INPUT`.

## Output Files To Recognize

- `ALL_INPUT`: values of all parameters used in the simulation.
- `PHY_QUANT`: selected physical quantities output at intervals controlled by `Phy_Quant_Intvl`.
- `ALL_STRU`: dumped structures along the simulation.
- `MODEL_DEVI`: model deviation of virials and forces in model-deviation mode.

## Key Parameters To Recognize

- `Stru_File`: structure file name.
- `Pot_Type`: potential style. README choices currently list DP.
- `Deep_Pot_Model`: DP potential model file.
- `Simu_Type`: simulation type. README choices list MD, HMC, CHMC.
- `Steps`: required number of sampling steps.
- `Temp`: simulation temperature.
- `N_Type`, `Element_Type`, `Element_Index`: element/type mapping for DP.
- `Wall`: hard walls to limit atom coordinates; not available for MD simulations according to the README.
- `Group`: atom groups by index ranges.
- `Time_Step`, `N_Evol_Step`, `Mass_Scal`: MD/HMC stepping controls.
- `Hybrid_Monte_Carlo_Ratio`: HMC ratio in centroid moves. See the tuning notes below before explaining or setting this parameter.
- `Virt_Atom`: virtual atoms for reaction-coordinate definitions.
- `Rxn_Coord`: constrained reaction coordinate. README choices include `DIST` and `DIFF`.
- `Elec_Num_Ratio`, `Mu`, `Elec_Num_Range`, `Elec_Num_Width`: grand-canonical electron-number controls.
- `Beads_File`, `N_Bead`, `N_Change_Bead`, `Bead_Index`: path-integral bead controls.
- `Model_Devi_Deep_Pot_Models`, `Model_Devi_Intvl`, `Model_Devi_File`: model-deviation controls.
- `Phy_Quant_File`, `Out_Phy_Quant`, `Phy_Quant_Intvl`: physical-quantity output controls.

## Reaction Coordinate Notes

- `DIST` represents the distance between two particles or virtual atoms.
- `DIFF` represents a signed difference of distances involving three particles or virtual atoms.
- The README examples show virtual atoms can be used in reaction-coordinate definitions.
- Reaction-coordinate choice remains a physical decision and must be user-approved for the NQE H2 workflow.

## Hybrid Monte Carlo Ratio Interpretation

Use this interpretation when users ask what `Hybrid_Monte_Carlo_Ratio` means or how to tune it:

- `Hybrid_Monte_Carlo_Ratio` controls the fraction of centroid moves attempted with the HMC component rather than pure MC components.
- In this workflow, the MC part can include electron-number sampling, path-integral bead sampling, and reaction-coordinate-related angular/free-degree sampling.
- The HMC part mainly samples the three-dimensional degrees of freedom of atoms not directly tied to the reaction coordinate.
- Do not describe MC as only a simple random displacement or as merely "no MD evolution"; list the relevant MC move classes when known from the input/workflow.
- Treat the CORR value in `ALL_INPUT` (0.8) as a real reference value, not a general default. The raw `INPUT` also preserves a spelling/value mismatch, so audit `ALL_INPUT` before reproducing.
- A typical useful acceptance-rate range is about 30-50%, not 60-80%. Tune `Time_Step`, `N_Evol_Step`, mass scaling, and move ratios against acceptance and mixing.
- Higher temperature can increase acceptance, so compare acceptance rates only together with temperature, step size, and the move schedule.
- Do not choose a final ratio for the user without their approval and system-specific testing.

## Constant-Potential-Like / Electrochemical Context

The public README documents grand-canonical ensemble support for CHMC/CPIHMC and parameters controlling electron-number variation and electrochemical potential. This is an important capability for electrochemical or constant-potential-like simulations. It should be described as package capability, not as a default assumption for an arbitrary target workflow.

## Settings Requiring User Approval

- `Simu_Type` and whether a run is CHMC-like classical sampling or CPIHMC/path-integral sampling.
- DP model path and model provenance.
- `Steps`, `Temp`, `Time_Step`, `N_Evol_Step`, and `Mass_Scal`.
- Reaction-coordinate definitions through `Virt_Atom` and `Rxn_Coord`.
- Grand-canonical electron-number controls.
- Path-integral bead settings such as `N_Bead`, `N_Change_Bead`, and `Beads_File`.
- Wall/group definitions and any restrictions used to stabilize sampling.
- Output intervals and requested physical quantities.

## Workflow Handoff

- The public README states current force/potential support is DP-only. For this NQE workflow, require an accepted DeePMD/DP frozen model before CHMC/CPIHMC sampling.
- Sampling output should be checked for `PHY_QUANT` mean-force quantities before handoff to `ti-tst-rate`.
- Preserve units and sign conventions when moving from `PHY_QUANT` to thermodynamic integration.
- Model-deviation outputs, if used, are diagnostics and do not by themselves certify production readiness.

## When To Stop And Ask User

- The user asks the agent to choose reaction coordinates, bead number, steps, timestep, temperature, walls, or electron-number controls.
- The requested potential backend is not supported by the documented public version.
- `INPUT`, `STRU`, `BEADS`, `PHY_QUANT`, or `MODEL_DEVI` contents are missing or ambiguous.
- Units or sign conventions for mean force are unclear before TI.
