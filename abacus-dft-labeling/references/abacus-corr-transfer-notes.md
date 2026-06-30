# ABACUS CORR Reference Transfer Notes

These notes summarize what can and cannot be transferred from the CORR ABACUS reference files into the NQE H2 workflow skills.

## Source Files

The reference example is stored under `templates/reference-examples/corr/` and contains:

- `INPUT_aimd`: molecular dynamics task (`calculation md`)
- `INPUT_opt`: cell relaxation task (`calculation cell-relax`)
- `INPUT_sp`: single-point SCF task (`calculation scf`)
- `STRU_opt`: structure file
- `KPT`: k-point file

## Transferable Patterns

- Separate ABACUS tasks by purpose: MD, relaxation, and single-point labeling can use different INPUT files while sharing structure and KPT conventions.
- Start ABACUS INPUT files with `INPUT_PARAMETERS` and keep calculation-type settings near the top.
- Keep force-label generation explicit with `cal_force 1` when forces are needed downstream.
- Treat dispersion, smearing, mixing, SCF limits, and force thresholds as documented calculation settings that must remain consistent across labels when they define the training data.
- In STRU files, keep `ATOMIC_SPECIES`, `NUMERICAL_ORBITAL`, `LATTICE_CONSTANT`, `LATTICE_VECTORS`, and `ATOMIC_POSITIONS` clearly separated.
- Preserve movable flags and magnetic tags when converting, copying, or generating structures.
- Use KPT files as explicit inputs, even when the mesh is simple.

## System-Specific Content That Must Not Be Copied Blindly

- Element list, pseudopotential filenames, numerical orbital filenames, masses, cell vectors, atom coordinates, movable flags, and magnetic tags.
- K-point mesh. The CORR example uses a slab-like mesh (`3 3 1`), which is not a general default.
- `ecutwfc`-like numerical cutoffs, SCF thresholds, smearing values, mixing parameters, relaxation thresholds, and MD parameters.
- Dispersion method, implicit solvation, dipole correction, electric field, gate compensation, and `nelec` settings. These can change the physical problem.
- Any charged-slab, electrochemical, or field-related settings unless the user explicitly confirms they are part of the target H2/graphene model.

## How Agents Should Use This Example

- Cite the CORR files as a real-world ABACUS style reference, not as H2/graphene input recommendations.
- Compare new user-provided ABACUS files against the CORR example for missing structural sections or task separation.
- Keep minimal templates generic; borrow organization patterns, not numerical values.
- Ask the user to confirm any physical setting that changes the Hamiltonian, boundary conditions, charge state, or sampling target.
