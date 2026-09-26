# Prospective full-unit integer extension of the Markov twins

This extension is fixed after observing that all 16 commitment-transition-
preserving cases passed the continuous LP relaxation while their directly
permuted seed schedules violated dwell constraints. It does not overwrite those
original UNKNOWN operational verdicts and is not an unseen-sample experiment.

The four fixed cases are seeds 260926100, 260926101, 260926102 and 260926103,
selected by their first-four positions in the original fixed sequence. Use each
already archived permutation and the unchanged full 41-unit mean vector from
the verified July repaired network dispatch. Keep all individual physical units,
native availability, fixed hydro, hourly aggregate balance, thermal minimum and
maximum output, binary commitment/startup/shutdown, transition identities,
exclusive transitions and minimum up/down constraints. Preserve the mature
free initial history and clipped terminal dwell conventions. No pooling of
generator energies, load shedding or target slack is introduced.

Run the existing `v8r1_rts_seasonal.solve` minimum-up/down formulation once per
case, with 60 seconds, one thread, seed zero and its unchanged feasibility
objective. The model has no network constraints. Binary unit native on/on ramps
were separately proved redundant; nevertheless any positive witness receives
the existing direct ramp check in addition to all full-unit mean, output,
transition and dwell checks. No warm start, tuning or retry is part of this step.

Alternative schedules are allowed to change the commitment transition counts:
those counts describe the permuted seed packages, not additional constraints of
the target-mean admission problem. A verified integer schedule is labeled
ADMITTED_NO_NETWORK_CHRONOLOGY, which does not prove network feasibility.
Explicit solver Infeasible is labeled REJECTED_NO_NETWORK_MIP, with its numerical
solver evidence identified; it is not an exact Farkas proof. Any time limit or
other termination without a verified incumbent remains UNKNOWN. If a verified
incumbent exists at a limit, preserve that positive evidence and the literal
termination status. Never infer infeasibility from a bad seed replay or LP
fractionality.

Before solving, verify the original network seed in the same physical model,
and compare reconstructed continuous matrices and bounds against the archived
Markov LP models. Record source, code, protocol, permutation and preservation
artifact hashes. Save every solve log and every available verified P/U/Y/Z
witness. No result in the earlier Markov directory is changed.

Maximum optimization budget: four independent 60-second solves, at most 240
seconds of solver budgets. A later fixed-commitment network feasibility step
requires a separate prospective extension and is outside this task.
