# CORR PHY_QUANT Handoff Example

This semi-real example maps the real `corr-gc-cpihmc/PHY_QUANT` columns into TI/TST handoff tables. It demonstrates column semantics only. The CSV files follow the current TI/TST table schemas, including raw/au mean-force columns and separate `free_energy_converted` values.

Important boundaries:

- `MeanForce_0` maps to `RxnCoord_0`; `MeanForce_1` maps to `RxnCoord_1`.
- Reaction coordinates and mean forces are treated as atomic units.
- This single-window excerpt is not enough to integrate a free-energy profile.
- No equilibration discard or uncertainty estimate is documented here.
- TST rates are not computed until an activation free energy, temperature, prefactor model, and unit convention are provided. The example `tst_rates.csv` includes both `kBT_over_h` and a hydrogen adsorption `n v S` prefactor row as schemas, not computed rates.
