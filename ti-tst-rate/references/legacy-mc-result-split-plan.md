# Legacy MC_result.py Split Plan

Use this reference when migrating the user's rough `MC_result.py` postprocessing script into maintainable tools. Treat the legacy script as provenance for workflow logic, not as a production-ready implementation.

## What The Legacy Script Does

The script currently mixes several responsibilities:

1. Parse plotting and output options from the command line.
2. Discover temperature directories in the current working directory.
3. Inside each temperature directory, discover classical `mc*` and path-integral `pimc*` runs.
4. Inside each run directory, read numeric `.dat` window files; filenames encode signed reaction-coordinate windows.
5. Average a fixed data column after skipping an optional number of rows.
6. Convert reaction coordinates from Bohr-like units to Angstrom with a hard-coded factor `0.529`.
7. Convert mean force with a hard-coded divisor `0.01824`.
8. Integrate mean force with a trapezoidal rule and shift the final free energy to zero.
9. Optionally average replicate curves and estimate standard deviations.
10. Write a combined `data` file and plot classical versus path-integral free-energy curves.

## Hidden Assumptions To Make Explicit

Before turning the logic into scripts, require the user to confirm:

- Which column in the input files contains mean force. The legacy script uses zero-based column 7.
- Whether the hard-coded `0.01824` force conversion is still valid and what units it converts.
- Whether the hard-coded `0.529` coordinate conversion should be used, and whether output coordinates should be Angstrom or atomic units.
- Whether negative windows encoded as filenames like `_0.4.dat` should become negative reaction coordinates.
- Whether free energy should be shifted so the last grid point is zero, or whether another reference state should define zero.
- The integration direction: default from small reaction coordinate to large reaction coordinate, or descending when the larger reaction coordinate is the initial/reference side.
- Whether `mc*` means classical CHMC and `pimc*` means CPIHMC/NQE for all future datasets.
- How equilibration discard, block averaging, uncertainty, and failed windows should be handled.

## Recommended Script Split

Do not keep all behavior in one monolithic script. Split into small tools with clear input/output contracts:

1. `extract_mean_force.py`
   - Input: raw window output files or `PHY_QUANT` files.
   - Output: `mean_force_table.csv`.
   - Responsibilities: column selection, skip/equilibration discard, mean/statistics, unit metadata.

2. `integrate_free_energy.py`
   - Input: `mean_force_table.csv`.
   - Output: `free_energy_profile.csv`.
   - Responsibilities: window ordering, sign convention, trapezoidal or user-selected integration, reference-zero shift, uncertainty propagation placeholder.

3. `compute_tst_rates.py`
   - Input: `free_energy_profile.csv` or explicit activation barriers plus prefactor table.
   - Output: `tst_rates.csv`.
   - Responsibilities: barrier extraction only when reactant/TS states are documented, prefactor model handling such as `kBT_over_h`, `custom_numeric`, or `adsorption_flux_n_v_S`.

4. `plot_free_energy.py`
   - Input: `free_energy_profile.csv` and optional comparison labels.
   - Output: plot image.
   - Responsibilities: plotting only; no hidden averaging or physics.

5. Optional `legacy_mc_result_adapter.py`
   - Input: legacy directory layout used by `MC_result.py`.
   - Output: normalized `mean_force_table.csv`.
   - Responsibilities: preserve backwards compatibility while moving new workflows to explicit tables.

## What Not To Script Yet

Do not write production scripts until the user confirms unit conversions, file columns, reference-zero convention, and example inputs. In particular, do not hard-code `0.01824`, `0.529`, column 7, or final-point zeroing as universal defaults.

## Migration Target

The final postprocessing chain should be:

```text
raw CHMC/CPIHMC outputs or PHY_QUANT
  -> mean_force_table.csv
  -> free_energy_profile.csv
  -> tst_rates.csv
  -> KMC event-rate table or custom postprocessing
```

Each file should preserve dataset label, classical/NQE label, units, uncertainty/TODO markers, and source paths.

## Current Implemented Scripts

- `scripts/extract_mean_force.py`: implemented first. It handles one sampling/window output and appends one standardized row to `mean_force_table.csv`. It requires `--confirm-parameters` before writing because units and columns may differ between CHMC/CPIHMC settings.
- `scripts/integrate_free_energy.py`: implemented first. It integrates an already collected `mean_force_table.csv` for one reaction-coordinate index and writes `free_energy_profile.csv`. It requires `--confirm-parameters` before writing.

Temperature-directory scanning, plotting, TST-rate computation, and KMC handoff should remain separate.
