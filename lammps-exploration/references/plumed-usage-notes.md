# PLUMED Usage Notes For LAMMPS Exploration

Use these notes when reviewing or drafting PLUMED inputs coupled to LAMMPS exploration runs.

## Official Documentation Anchors

- PLUMED user manual: https://www.plumed.org/doc-v2.9/user-doc/html/index.html
- PLUMED `UNITS`: https://www.plumed.org/doc-v2.9/user-doc/html/_u_n_i_t_s.html
- PLUMED `DISTANCE`: https://www.plumed.org/doc-v2.9/user-doc/html/_d_i_s_t_a_n_c_e.html
- PLUMED `RESTRAINT`: https://www.plumed.org/doc-v2.9/user-doc/html/_r_e_s_t_r_a_i_n_t.html
- PLUMED `PRINT`: https://www.plumed.org/doc-v2.9/user-doc/html/_p_r_i_n_t.html
- PLUMED `FLUSH`: https://www.plumed.org/doc-v2.9/user-doc/html/_f_l_u_s_h.html
- PLUMED `METAD`: https://www.plumed.org/doc-v2.9/user-doc/html/_m_e_t_a_d.html

## Common PLUMED Roles In Exploration

- define collective variables such as distances, angles, coordination numbers, or custom reaction coordinates
- apply restraints, walls, or metadynamics-like biasing when the user approves enhanced exploration
- print collective variables for diagnostics and later analysis
- flush output periodically to reduce data-loss risk in long runs

## Checks

- Confirm PLUMED is available in the LAMMPS build or coupling method used by the project.
- Confirm `fix plumed` or project-specific coupling syntax against the installed LAMMPS/PLUMED version.
- Confirm `UNITS` are consistent with the LAMMPS unit style and intended CV interpretation.
- Confirm atom indices in PLUMED match the LAMMPS data file and are not shifted by type/order conversion.
- Confirm PBC behavior for distance-like CVs, including whether `NOPBC`, components, or molecule reconstruction is needed.
- Confirm restraint centers, force constants, metadynamics widths/heights/pace, and print strides are user-approved.
- Confirm PLUMED output files exist and are consistent with LAMMPS trajectory/log output.

## Boundaries

Do not choose a collective variable, restraint center, force constant, metadynamics parameter, or biasing schedule without user approval. Treat real PLUMED files from other systems as style references unless the user explicitly documents transferability.
