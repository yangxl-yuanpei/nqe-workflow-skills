# Conversion Checklist

Use this checklist before and after every dpdata conversion.

## Before Conversion

- Confirm source software and exact dpdata input format.
- Confirm target software and exact dpdata output format.
- Confirm whether the data are labeled or unlabeled.
- Confirm expected elements and type map.
- Confirm frame count and atom count if known.
- Confirm whether energies, forces, virials, cells, and PBC are required downstream.
- Confirm units and whether dpdata handles the required unit conversion for the selected format.
- Confirm whether atom ordering must be preserved.

## During Conversion

- Use explicit `--input-format` and `--output-format`.
- Use `--labeled` only when labels are required and present.
- Do not pass a type map to `convert_with_dpdata.py`. Inspect the source first and let dpdata preserve the reported atom names/order. If the source format lacks reliable element names, stop and ask the user how to prepare that source before conversion.
- Do not pass external type maps to `compare_converted_system.py`; compare the source and converted data as reported by dpdata.
- Refuse to overwrite existing output unless the user explicitly approves.
- Record the exact command, dpdata version if available, and source/target paths.

## After Conversion

- Inspect the converted data.
- Compare source and converted frame count and atom count.
- Compare atom names/type map.
- Check whether energies, forces, virials, cells, and coordinates survived as expected.
- Route DeePMD data to `deepmd-training` checks.
- Route DP-GEN initial/iteration data to `dpgen-active-learning` checks.
- Route LAMMPS structures or trajectories to `lammps-exploration` checks.

## Stop Conditions

Stop and ask the user before continuing if:

- format names are unknown
- labels disappear during conversion
- atom count changes unexpectedly
- type map or element order changes unexpectedly
- cells or PBC are missing when downstream needs them
- virials are required but absent
- units are unclear
