# Prospective continuation of three unresolved seasonal references

This new, separately archived arm continues only the original April, July and
October 2020 reference cases, in that fixed order (months 4, 7, 10). Their
original 120-second full-U/Y/Z runs timed out without verified incumbents.
Retain those results and all previous UNKNOWN/NO_REFERENCE designations.
January, its reference schedule and its existing caps are unchanged. This arm
generates possible references for a separately predeclared later experiment;
it does not itself test temporal order or retroactively satisfy an earlier
replication gate.

For each month, use its unchanged original 168-hour uncapped full-DC-network
matrix, bounds, native inputs and fossil-energy objective from
results/research8h/seasonal_reference. Byte-copy these model artifacts into the
new output directory. There are zero individual-unit mean constraints and
zero fossil-energy-cap constraints. Preserve all 41 decision generators, 24
thermal units, 24 buses and 38 branches, hydro equality, renewable availability,
native nodal demand/rooftop PV, network equations and line/angle bounds. Preserve
free mature initial statuses, initial Y/Z zero, observed native minimum dwell
through hour 167, and no cyclic or post-horizon requirements. Native hourly
on/on ramp limits are analytically redundant here and still checked directly.

Preparation must first validate the original reference input manifest against
its recorded pre-solve hash and require each selected source result to be the
saved timeout with no returned incumbent. Reconstruct all three original
models from the pinned native source without optimization and compare every
matrix coefficient, row/column bound, original integer mask, objective,
row-family label, generator/bus roster, native hourly array and source-hour
mapping with its archive. Check all 24 native ramp inequalities. This is a
source/model audit, not a new model or data revision.

Keep exactly the original equal-weight objective: coefficient one on the
23 Coal/Oil/NG units' 168 hourly dispatch values and zero on every other
coordinate. The sole excluded thermal unit is 121_NUCLEAR_1. This is fossil
MWh, not operating cost or emissions. In particular, do not introduce an energy
cap, mean targets, load shedding, storage, reserves or relaxation slack.

Apply the existing research8h_u_only_continuation.audit_projection to the
actual archived matrix: only U remains declared binary (4,032 coordinates);
Y/Z retain their original continuous bounds and all physical rows remain
unchanged. Their original full integer mask (12,096 U/Y/Z coordinates) is
retained for witness verification. Audit all auxiliary appearances and senses
and the zero auxiliary objective. For exact binary U, replacing Y/Z by its
observed positive/negative changes weakens their nonnegative dwell sums while
preserving transitions and exclusivity, so this standard reduction preserves
the projected P/U/theta feasible set and objective. Make no method-novelty or
speedup claim; both representation and configured time differ from the old run.

Use separate prepare-only and run-prepared modes. Preparation freezes all
three cases, all source/model hashes and this protocol before any solver call.
Execution revalidates the complete manifest and uses an exclusive execution
marker to prevent accidental repeats. Do not run until the root has reviewed
the prepared arm and explicitly given GO. Run exactly one HiGHS MIP per case,
600 seconds each, one thread, random seed zero, presolve on and relative gap
target 1e-8. No warm starts, retries, tuning, replacement cases or adaptive
targets. Run sequentially, with at most one optimizer from this arm. The root
coordinates a maximum of two simultaneous long MIPs across arms. The total
configured allocation is 1,800 seconds. Record actual runtime/soft-limit
overshoot and complete solver logs; timings are not a benchmark.

Archive every returned raw vector and its matrix check. A finite candidate is
eligible for recovery only when every U is within 1e-5 of exact zero or one.
Round U, recompute Y/Z from adjacent changes with initial values zero, and leave
P/theta unchanged. Preserve raw and recovered vectors separately. Require
the recovered point to pass the original full-binary matrix/bounds and the
independent native no-cap physical_check in research8h_seasonal_reference:
output bounds, fixed hydro, transitions, direct residence runs, on/on ramps,
aggregate/nodal balance, provided and independently reconstructed DC flows,
line ratings, angles and reference angle. Record all residuals.

Also use the already tested exact_point_check from research8h_seasonal_uncapped.
Interpret all archived binary64 coefficients and recovered point coordinates
as exact rational numbers. Require all original U/Y/Z coordinates to be exact
zero or one. Report both strict membership and membership after every finite
row/column bound is expanded uniformly outward by
tau = Fraction.from_float(1e-5). Preserve exact maximum violations and compute
fossil MWh as an exact sum of the stored dispatch values. An expanded-model
positive is a rigorous witness only for that explicitly expanded model unless
strict membership also passes. A float tolerance check alone gives a numerical
candidate, not an exact strict feasible witness.

Accepted finite incumbents may supply additional tolerance-qualified seasonal
references regardless of optimality. Keep solver objective, numerical lower
bound and gap separate from exact point verification. No exact optimality
claim follows from a time-limited incumbent or an uncertified solver bound.
Timeouts without accepted witnesses remain UNKNOWN. A numerical MIP infeasible
status is recorded as numerical evidence, not an exact certificate. Preserve
all failed candidates and the unchanged original records. Any later cap or
permutation experiment requires its own prospective freeze and must not be
reported as part of the already completed January-only arm.
