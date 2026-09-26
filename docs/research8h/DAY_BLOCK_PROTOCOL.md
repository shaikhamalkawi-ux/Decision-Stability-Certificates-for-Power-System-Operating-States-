# January whole-day order test

This follow-up was chosen after observing two negative unrestricted hourly
permutations. It is a prespecified sensitivity test of that artificial
perturbation family, not a blind replication or a new chronology method.

Use the same January 168-hour RTS-GMLC Area 1 model, 23 fossil generators,
24 buses, 38 branches, native bounds, initial/final treatment and fixed
23195 MWh fossil-electricity cap as the archived January service-cap arm.
There are no individual generator mean constraints. Keep hours 0..47 and
120..167 fixed. Enumerate, lexicographically, all five nonidentity orders of
the three whole 24-hour blocks covering 48..119. Apply each order jointly
to every hourly exogenous input. No replacement order, new cap or new week.

This preserves the exact hourly multiset, each within-day sequence and
hour-of-day alignment. It does not establish realistic weather continuity,
preserve every inter-day transition or represent a field intervention.
Count and archive all changed adjacent source-hour pairs and residence
violations in the permuted reference schedule. A failing reference schedule
does not establish infeasibility of its model.

Before any optimization, archive all five full models and permutations,
prove the joint permutation and nodal reconstruction, and verify the
permuted reference against every row except minimum-up/down rows. Check
exact binary64 point membership with every finite bound expanded outward
by Fraction.from_float(1e-5); also report strict membership. Verify the
archived January identity and U-class positive-control constructive points
against their full models with the same exact check. Archive source,
protocol, dependencies, models, controls and input hashes before solving.

Routing is fixed. If the permuted reference itself passes the exact expanded
full model, classify it as a constructive positive without optimization.
Constructive admission also requires the full native binary/network check.
For each remaining order, run one 30-second continuous LP, simplex,
presolve off, one thread, seed 0. A verified rational Farkas ray must remain
strictly contradictory after the same finite-bound expansion to establish
the negative label. A numerical LP point establishes only relaxation
admission. Every order without an exact robust negative then receives one
300-second zero-objective MIP, presolve on, one thread, seed 0,
relative MIP gap 1e-8, no warm
start, no retries. Only U is declared integer, after the existing actual
matrix projection audit; recover canonical binary Y/Z and verify both the
original matrix and native physical checks. An accepted positive requires
exact membership of the recovered binary point in the expanded full model.
Keep numerical-only candidates and unverified solver statuses separate.

All LPs precede all conditional MIPs. At most five LPs and five MIPs: 1650
configured solver seconds. Stop initiating MIPs when fewer than 305 seconds
remain in the 2100-second solve/check phase, preserving UNKNOWN outcomes.
Actual solver overrun and all route exclusions are recorded. Preparation
and execution are separate; independent review precedes execution.

Report the full five-order denominator, exact positives, exact robust
negatives and unknowns separately. A null result weakens generalization
from arbitrary hourly shuffles; it is not suppressed. No general method
novelty, statistical population inference, optimality, speedup or station
operating recommendation follows from this test.
