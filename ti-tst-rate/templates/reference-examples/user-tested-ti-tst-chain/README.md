# User-Tested TI/TST Chain

This reference example captures a small manually tested TI/TST postprocessing chain provided by the user. It is intended as a smoke-test and file-shape example, not a production default.

## Contents

- `demo/`: small CHMC/CPIHMC-style window outputs. Each window contains `energy.dat` with columns including `RxnCoord` and `MeanForce`.
- `observed-output-2026-06-30/`: outputs observed during the user's manual test.

Window directory names encode reaction coordinates. Names beginning with `_` represent negative reaction coordinates, e.g. `_0.4` means `-0.4`.

## User-Tested Commands

These commands were reported as working in the user's environment:

```bash
python /personal/extract_mean_force.py --input energy.dat --output ../result.dat --dataset-label test --skiprows 1 --confirm-parameters --force-col-index 7 --rc-col-index 6
python /personal/integrate_free_energy.py --input result.dat --output free_energy.dat --dataset-label test --confirm-parameters --free-energy-scale 27.2 --free-energy-unit-label eV --integration-direction descending
python /personal/plot_mean_force.py --curve file=result.dat,dataset=test --output meanforce.png --confirm-parameters
python /personal/plot_free_energy.py --curve file=free_energy.dat,dataset=test --output free_energy.png --confirm-parameters
python /personal/compute_tst_rates.py --input free_energy.dat --output rate.csv --confirm-parameters --elementary-step CHO --dataset-label test --temperature 100
```

## Reuse Notes

- Treat the commands as smoke-test syntax, not production defaults.
- If relying on numeric columns in `extract_mean_force.py`, add `--format table`. Without it, header-name parsing may ignore `--rc-col-index` and `--force-col-index`.
- The current CHMC single-RC default header path can read `RxnCoord` and `MeanForce` without numeric column indices.
- `--skiprows 1` discards the first numeric data row after header handling.
- `27.2` is the user's approximate Hartree-to-eV smoke-test scale. For production-like conversion, prefer `27.211386245988` after confirming the input units.
- The observed `meanforce.csv` was produced before raw/au split columns were added to `extract_mean_force.py`; current reruns will produce a wider table.
- TST defaults select `reactant-mode first` and `ts-mode max`; confirm those physical states before treating rates as final.
