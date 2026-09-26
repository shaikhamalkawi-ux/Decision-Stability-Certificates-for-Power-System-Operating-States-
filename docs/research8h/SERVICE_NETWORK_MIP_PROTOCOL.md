# Prospective full-network binary service experiment

This is a separately frozen post-pilot extension after the all-on restriction
failed. Preserve that unsuccessful run. Test exactly the four ordinary twins
`seed_26092600` through `seed_26092603`, in that order, with one 120-second MIP
call each. Use HiGHS, one thread, random seed zero, presolve on, relative MIP gap
1e-8 and a zero feasibility objective. No retry, adaptive target, warm start,
commitment fixing, or additional case belongs to this experiment.

Reconstruct every hourly input jointly from the archived source-hour permutation
and original native row. Reproduce the existing continuous unit service model
from these inputs, assert exact matrix/bound equality with the archived service
LP, then mark every U/Y/Z coordinate binary. Retain every unit output bound,
fixed hydro, renewable availability, transition exclusivity, and minimum up/down
constraint. Initial status is free and mature, initial startup/shutdown are zero,
and observed transitions enforce their residence only within the horizon. The
24 native thermal ramp limits satisfy R_hour >= Pmax-Pmin; establish this from
native data before any solve, so on/on ramp rows are redundant. Independently
check the actual on/on ramps in every proposed positive witness.

Append full nodal DC balance and branch-flow rows using all 24 buses and 38
internal branches, source susceptances/transformer ratios, continuous branch
ratings, nodal load proportions, and fixed RTPV negative load. Append bus angles
bounded in [-pi,pi], with the native slack bus fixed to zero. Preserve the shared
fossil-energy cap at the exact binary64 value from the previous service-cap
freeze, 180555.9189139999 MWh. Its unit coefficients apply to the 23 fossil
thermal units and exclude `121_NUCLEAR_1`. No generator mean is constrained.
No load shedding, storage, network slack or target slack is introduced.

Before the four calls, check the existing original reference binary network
witness against an identity version of this unfixed model and independently
against native physical constraints and the service cap. This is a read-only
preflight, not another optimization. Freeze source/protocol hashes, all native
inputs, original reference files, archived unit models, permutations, and the
four assembled models before the first MIP call.

Archive each matrix, bounds, integrality, objective, row metadata, native input
arrays, solver log, status and any returned vector. A positive verdict requires
both direct matrix/bound verification and independent physical checks at 1e-5:
finite dispatch; native capacity and thermal coupling to raw/rounded binary
status; binary startup/shutdown and transition consistency; directly observed
run lengths; native on/on ramps; fixed hydro and renewable availability;
aggregate balance; nodal injections, reconstructed DC branch flows, provided
angle/line constraints; and an exact binary64 fossil-energy sum compared with
the frozen budget. Describe per-unit mean changes only after verification;
never compare a schedule's means with themselves as evidence of target service.

A passing witness establishes binary DC-network feasibility for this aggregate
service specification only, without economic optimality, AC or field claims.
A time limit without a passing witness is UNKNOWN. An explicit Infeasible MIP
status is a numerical solver negative, not an exact Farkas proof. A failed
returned vector is retained without a positive verdict. Preserve all outcomes,
including unfavorable and inconclusive ones; do not edit the original twins or
their different individual-generator-mean conclusions.
