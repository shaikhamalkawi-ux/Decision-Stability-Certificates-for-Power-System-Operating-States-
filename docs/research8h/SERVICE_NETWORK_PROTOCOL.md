# Prospective all-thermal-on network service test

Freeze this single restriction before its outcome. Use the original 168-hour
July identity inputs and the exact binary64 fossil-energy budget recorded by
the service-cap experiment, 180555.9189139999 MWh. Do not recompute, round down,
tighten or optimize the budget. No individual generator mean is constrained.

Fix every one of the 24 thermal commitment states to one at every hour. Under
the established free mature initial history, startup and shutdown are zero and
minimum up/down constraints are satisfied. Preserve every native thermal
minimum/maximum output, renewable availability and fixed hourly hydro output.
Verify the source inequality R_hourly >= Pmax-Pmin for every thermal unit;
these native on/on ramp limits are then redundant for arbitrary permutations of
thermal output within those bounds. Nevertheless check the actual ramps of any
returned schedule and each replay directly.

Assemble one full DC network LP with dispatch and bus-angle variables. Use the
native 24 buses, 38 internal branches, source susceptances/transformer ratios,
nodal load proportions, fixed RTPV negative load, continuous branch ratings,
the source slack bus at zero angle, and angle bounds [-pi,pi], as in the existing
network-repair formulation. No load shedding, demand change, storage, angle
slack, line slack or target slack is available. Retain exact nodal balance and
the same shared sum of generation over the 23 fossil thermal units, excluding
121_NUCLEAR_1. Use a zero feasibility objective; there is no hidden nuclear
penalty or emissions-factor interpretation.

Run exactly one LP: HiGHS simplex, one thread, random seed zero, presolve off,
60-second time limit. Archive its matrix, bounds, objective, physical metadata,
input hashes, source budget and log. Before solving, ground the network assembly
against the existing verified network witness using that witness's own fixed
commitment bounds; this is a read-only check, not another optimization.

If the LP supplies a valid solution, save its dispatch, angles and constant
binary commitment. Independently verify availability, fixed hydro, aggregate
and nodal balance, branch limits, angles, full unit dwell/ramp behavior and the
fossil cap at the established 1e-5 tolerance. Reconstruct DC flows directly from
dispatch via the existing `temporal_information_pilot.nodal_check` as a separate
check. Then replay that same solution under the four already archived ordinary
permutations, jointly reordering native inputs, dispatch and angles. Check all
four schedules again, including actual on/on ramps and the unchanged cap.
Constant commitment and proven ramp redundancy make this replay permissible;
the direct checks remain mandatory.

A passing identity and four replays provide five binary DC-network witnesses
for this aggregate service specification, without any claim of economic
optimality, AC feasibility or field validation. If the single all-on restriction
is infeasible, times out without a verified vector, or fails verification, report
only that this restricted attempt failed. It is never a rejection of unrestricted
unit commitment or of the aggregate service specification. No adaptive choice of
another commitment pattern belongs to this experiment.
