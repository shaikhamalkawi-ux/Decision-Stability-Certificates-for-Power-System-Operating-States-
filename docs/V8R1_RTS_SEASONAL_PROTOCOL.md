# Fixed RTS seasonal chronology extension

Protocol recorded before running the new seasonal solves, 2026-09-26.

Use every archived target week in the original mean/shape table: February,
March, April, May, June, July and October 2020, plus January as a source-week
control. Each window is the first 168 hours of its month. No new date selection
or dispatch optimization is used to choose targets. The target is the complete
41-coordinate mean of the archived static dispatch. Input dispatches must match
the published reproducibility CSVs, and their timestamp/row mapping must match
the native RTS hourly input tables.

For each window, first independently check that the archived static dispatch
satisfies generator bounds, binary minimum output and aggregate balance. Then
test exact-mean admission in the same no-network relaxation under two separate
families: native online-to-online ramping, and native minimum up/down times.
Both include binary commitment, unchanged hydro-as-fixed-output semantics,
hourly availability and aggregate balance, and no load shedding. Ramp changes
are enforced only when both consecutive statuses are on. Minimum residence
times use explicit startup/shutdown variables, a free initial status,
y[0]=z[0]=0, and only observed in-horizon transitions. No terminal extension is
imposed. Do not combine the families in this extension.

Each feasibility solve gets at most 60 seconds, one HiGHS thread and seed zero.
An independently checked feasible incumbent means admission **in this
relaxation only**. HiGHS' explicit Infeasible status means solver-certified
rejection within numerical tolerances; a time limit or other termination with
no verified incumbent is unresolved, never infeasible. Preserve solver logs,
inputs' SHA-256 values and complete feasible witnesses. No repair distance is
claimed by this experiment. The two previously tested months are internal
replication controls, and all eight outcomes must be reported.

This closes a within-system seasonal selection question. It is neither an
independent-system chronology replication, a field experiment, nor evidence
about all hours of the year. A rejected relaxation excludes any stricter model
with the same semantics; an admitted relaxation does not establish network or
AC feasibility.
