# dpdata Official Notes

Use official dpdata documentation as the source of truth for format names, supported formats, and API behavior.

Official entry points:

- Documentation: https://docs.deepmodeling.com/projects/dpdata/en/master/
- GitHub repository: https://github.com/deepmodeling/dpdata

dpdata is documented as a Python package for manipulating atomistic data between computational-science software packages. It supports many formats, including DeepMD data formats, ABACUS, LAMMPS, VASP, Gaussian, CP2K, QE, xyz, ASE, and others, depending on installed version.

## Key Concepts

- `dpdata.System`: geometry/trajectory-style atomistic data without requiring labels.
- `dpdata.LabeledSystem`: atomistic data with labels such as energies, forces, and sometimes virials.
- DeepMD training data usually require labels; prefer `LabeledSystem` when preparing DeePMD raw/npy data from DFT outputs.
- Format strings are version-specific. Do not invent them; check official docs, examples, local help, or user-provided working commands.

## Boundary

dpdata can preserve and transform data arrays, but it does not prove:

- DFT convergence
- force/energy/virial correctness
- unit compatibility
- atom-ordering validity for a target workflow
- DP-GEN or DeePMD readiness
- physical reasonableness of structures

Always route converted data to the target-stage skill for readiness checks.
