# KMC Failure Cases

Use this reference when KMC setup, event networks, rate tables, simulation
outputs, or H2 formation-efficiency interpretation fails. These cases are
diagnostic patterns. They are not production defaults and they do not define a
complete KMC model for a new target system.

KMC in this repository consumes user-confirmed elementary rates, state models,
event networks, environment assumptions, simulation controls, and observable
definitions. It must not infer any of these from file names, old code examples,
or a single TST rate.

## Single Rate Is Treated As A Full KMC Network

Typical symptoms:

- The user has one TST rate and asks for H2 formation efficiency.
- A rate for one association channel is treated as the full surface reaction
  model.
- Adsorption, desorption, hopping, or competing association channels are absent.

Likely causes:

- The TST-to-KMC handoff was mistaken for a one-rate calculation.
- An elementary step rate was confused with a network-level observable.
- The user has not defined the lattice, states, event preconditions, or output
  normalization.

Agent response:

1. Explain that one elementary rate is not a full KMC event network.
2. Ask for the state model, event list, full rate table, environment
   assumptions, stopping rule, and observable definition.
3. Preserve missing events as TODOs.
4. Do not fabricate adsorption, desorption, hopping, association, or reverse
   rates.

## Missing State Or Lattice Definition

Typical symptoms:

- Events are listed but sites, species, occupancy rules, or boundary conditions
  are undefined.
- A rate table exists but there is no lattice, graph, site list, or coverage
  representation.
- Initial coverage or reservoir conditions are missing.

Likely causes:

- KMC was treated as a postprocessing formula instead of a discrete state model.
- The state representation lives in undocumented code or an unshared input file.
- A reference example was copied without adapting its state definitions.

Agent response:

1. Ask the user to define states, allowed species, site types, occupancy rules,
   boundary conditions, and initial state.
2. If a code-specific state model exists, inspect it as a reference for file
   shape only.
3. Do not assume one-dimensional, two-dimensional, graph, periodic, or
   sublattice structure without confirmation.

## Event Network Is Incomplete Or Inconsistent

Typical symptoms:

- Some events have rates but no preconditions or postconditions.
- Event products are not valid states.
- Required channels such as adsorption, desorption, hopping, or association are
  missing without an explicit TODO.
- Forward and reverse events are inconsistently included for a model that needs
  them.

Likely causes:

- The event list was assembled from several sources.
- A new species or reaction channel was added to rates but not to event logic.
- H2 formation-specific assumptions were copied into a more general KMC task.

Agent response:

1. Ask for event labels, reactant-state preconditions, product-state
   postconditions, and associated rate labels.
2. Mark missing or intentionally excluded channels explicitly.
3. Check whether each event changes the state in a defined way.
4. Do not invent missing transitions or reverse events.
5. Do not declare an association-only network impossible without checking the
   user-defined initial coverage, reservoir, or source assumptions. Missing
   adsorption, desorption, or hopping channels should remain explicit TODOs or
   documented exclusions.

## Rate Table Labels, Units, Or Conditions Do Not Match Events

Typical symptoms:

- Event labels do not match rate-table labels.
- Rates lack temperature, unit, classical/quantum, isotope, or environment
  metadata.
- A rate from one temperature or surface model is used in another KMC run.
- TST rates are present but the elementary-step labels are ambiguous.

Likely causes:

- Rates were copied from TI/TST output without a KMC mapping table.
- Multiple datasets or code versions were mixed.
- Unit conversion or prefactor choices were not preserved.

Agent response:

1. Ask for a rate table with explicit event labels, units, temperature,
   environment, and classical/quantum treatment.
2. Route unclear TST-derived rates back to `ti-tst-rate`.
3. Refuse to map rates by row order or file names alone.
4. Do not change units or choose prefactors without user confirmation.

## Invalid Or Degenerate Rates

Typical symptoms:

- A rate is negative, NaN, infinite, or missing.
- All enabled event rates are zero, so the total rate is zero.
- A simulation stalls immediately or reports no selectable events.
- Very rare events are misread as bugs without checking expected statistics.

Likely causes:

- Rate calculation failed upstream.
- A unit conversion or prefactor was omitted.
- Preconditions disable all events in the current state.
- The model legitimately has rare channels under the confirmed environment.

Agent response:

1. Separate numeric validity from physical interpretation.
2. Fail or warn on negative, NaN, infinite, or missing rates.
3. If total rate is zero, ask whether the current state has no allowed events or
   whether the event network is incomplete.
4. Do not declare rare-event absence a bug without trajectory statistics and
   model context.

## Event Selection Or Random-Time Logic Is Suspicious

Typical symptoms:

- Event counts are inconsistent with relative rates.
- Selection boundaries appear off by one or omit the last event.
- The stochastic clock is not advanced from the total rate.
- Random seeds or generators are reset in a way that destroys independence.

Likely causes:

- Cumulative probability logic was implemented incorrectly.
- Total-rate bookkeeping is inconsistent with the enabled event list.
- Random-number generation was placed inside a tight loop or reinitialized too
  often.
- A code-specific KMC implementation changed event ordering without tests.

Agent response:

1. Ask for the event-selection algorithm, total-rate calculation, random-number
   handling, and seed policy.
2. Suggest code-level review or minimal reproducibility tests when the user is
   working on an implementation.
3. Do not infer physical conclusions from suspicious event-count statistics.
4. Keep implementation checks separate from rate-network validation.

## New Species Or New Event Type Is Added Incompletely

Typical symptoms:

- A new species appears in rate calculation but not in state storage.
- Events exist for one isotope or species but counters, outputs, or reverse
  channels are missing.
- New event labels are absent from dispatch logic or output summaries.
- Old single-species assumptions remain in a multi-species run.

Likely causes:

- Code was extended in rate tables only.
- Event construction, event selection, state updates, and output counters were
  not updated together.
- A historical code note was treated as a complete migration procedure.

Agent response:

1. Ask for the synchronized changes across state representation, event
   generation, rate mapping, state update, counters, and outputs.
2. Require regression tests against a documented old behavior when code is
   modified.
3. Do not copy species ratios, temperatures, or barriers from old examples as
   defaults.
4. Do not copy historical regression tolerances, isotope ratios, temperature
   grids, or rare-event explanations into a new system. Ask the user to define
   acceptance criteria and isotope/environment assumptions for the target run.

## Output Counts Are Misinterpreted As Formation Efficiency

Typical symptoms:

- Raw product event counts are reported as formation rate or efficiency.
- The output lacks simulated physical time, surface size, flux, density, or
  normalization information.
- Coverage histories or event counts are present but no observable definition is
  documented.

Likely causes:

- KMC output files were treated as final physical observables.
- Formation efficiency was not defined for the specific model.
- Normalization depends on environmental assumptions not yet confirmed.

Agent response:

1. Ask for the observable definition and normalization method.
2. Require simulated time, surface/site count, event counts, and environmental
   assumptions before interpreting rates or efficiency.
3. Preserve custom observables as user-defined postprocessing.
4. Do not hard-code H2 formation efficiency as the only KMC output.

## Statistical Convergence Is Missing

Typical symptoms:

- A single trajectory is treated as converged.
- Event counts are too small for the reported observable.
- No uncertainty, independent seeds, or steady-state check is recorded.
- Transient and steady-state results are mixed.

Likely causes:

- KMC stochastic uncertainty was ignored.
- Simulation length, number of trajectories, or stopping criteria were copied
  from an example.
- Rare events need longer trajectories or targeted uncertainty analysis.

Agent response:

1. Ask for independent trajectories, seeds, simulation lengths, event counts,
   uncertainty estimates, and steady-state or transient interpretation.
2. Report missing convergence evidence as TODO.
3. Do not claim statistical convergence from script completion alone.
4. Do not provide fixed default convergence thresholds such as a required
   trajectory count, event-count cutoff, or percent uncertainty target unless
   the user or project protocol has supplied them. Ask the user to define the
   statistical precision and review criteria for the target observable.

## Stale Or Mixed Outputs Are Used

Typical symptoms:

- Output files from different code versions, temperatures, rate tables, or
  random seeds are combined.
- A previous failed run left partial results.
- Parameter summaries do not match event-count files.
- Backup or reference-code output is mixed with current output.

Likely causes:

- The same output directory was reused.
- Code-specific examples were treated as current production runs.
- Provenance was not recorded for rate table, state model, random seeds, or code
  version.

Agent response:

1. Ask for provenance: code version, input files, rate table, parameters, output
   directory, and run timestamp.
2. Prefer a fresh output directory for materially different runs.
3. Do not merge outputs without confirming common schema and provenance.
4. Treat stale outputs as diagnostic artifacts until reviewed.

## Code-Specific KMC Notes Are Treated As General Defaults

Typical symptoms:

- A user-provided KMC code note contains compile commands, hard-coded
  temperatures, species ratios, barriers, or old bug lists.
- The agent tries to promote those values into a general workflow template.
- A material-specific implementation is reused for a different surface or event
  network.

Likely causes:

- Historical code documentation was mistaken for a reusable physical model.
- Debugging notes were mixed with scientific parameter choices.
- A reference implementation was not separated from a target-system setup.

Agent response:

1. Treat code-specific notes as reference examples for file shape,
   implementation structure, and known failure patterns only.
2. Ask the user to confirm any compile command, input format, parameter value,
   event list, or observable before using it.
3. Do not migrate material-specific rates, temperatures, isotope ratios,
   lattice models, or output definitions into a new target system.
4. Do not promote historical testing thresholds, trajectory counts, event-count
   expectations, or tolerance percentages into general recommendations. If they
   appear in an old code note, label them as code-specific historical values
   that require separate user approval before reuse.

## How To Recover

For a KMC handoff, collect these before execution or interpretation:

- state model and allowed species
- event list with preconditions and postconditions
- rate table with event labels, units, temperature, environment, and
  classical/quantum treatment
- simulation controls: stopping rule, trajectory count, random seeds, output
  interval
- observable definitions and normalization
- provenance for input files, code version, and output directory

If any item is missing, keep it as TODO and stop before claiming KMC readiness,
formation efficiency, or production correctness.
