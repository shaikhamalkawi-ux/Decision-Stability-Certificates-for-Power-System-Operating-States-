# Prospective uncapped January witness arm

This separate arm follows the two exact capped January negatives. Test both
ordinary seeds 26093100 and 26093101, in that order, without selecting between
them. Preserve every previous source, protocol, model, result and control.
Remove exactly the single fossil_energy_cap row from each frozen seasonal
transfer matrix and its row bounds. All remaining rows, column bounds, native
inputs, generator identities and boundary semantics remain unchanged. There
are no individual generator-mean constraints and no replacement cap.

The objective is the sum of hourly dispatch over exactly the 23 native
Coal/Oil/NG units, with coefficient one per one-hour interval. Exclude
121_NUCLEAR_1. All angle and U/Y/Z objective coefficients are zero. This is
fossil MWh, not emissions, operating cost or a proxy cap.

Use the U-only integrality projection audited by
research8h_u_only_continuation.audit_projection. Preserve U as binary and Y/Z
as continuous in their original [0,1] bounds, with initial Y/Z fixed zero.
Audit the actual row coefficients and senses, allowed auxiliary appearances,
integer intervals and auxiliary-free objective before solving. For integer U,
replacing Y/Z by max(delta U,0) and max(-delta U,0) decreases nonnegative
auxiliaries, preserves transitions/exclusivity and weakens minimum-dwell rows.
The physical P/U/theta feasible set and this auxiliary-free objective are
therefore unchanged over exact real arithmetic. This is not a novel method.

The script has separate prepare-only and run-prepared modes. Preparation
archives both uncapped matrices, bounds, original and projected integrality,
objective, row metadata, native arrays, structural audits and source bindings.
It writes a manifest and source/protocol hashes before either optimization.
Run-prepared first validates every frozen hash. An execution marker prevents
an accidental rerun. Do not execute either MIP until the parent has reviewed
the source/protocol and explicitly authorized the prepared run.

Run one HiGHS MIP per case with 600 seconds, one thread, seed zero, presolve on,
relative gap 1e-8 and no warm start. No retries, parameter tuning, replacement
cases or adaptive targets. Record actual elapsed time, including soft-limit
overshoot, and preserve complete logs. The total configured allocation is
1,200 seconds. At most one solver from this arm is active; the parent may run
one separate solver concurrently. Timings are not a performance benchmark.

Keep every returned raw vector and its matrix check. Recovery is eligible only
for finite vectors whose U values are within 1e-5 of exact zero or one. Round U,
derive exact binary Y/Z from adjacent rounded U, set their initial values zero,
and leave dispatch and angles unchanged. Save the recovered vector separately.
It must pass the complete original full-binary uncapped matrix/bounds and the
native no-cap checker research8h_seasonal_reference.physical_check, including
direct dwell/transitions, on/on ramps, availability/fixed hydro, aggregate and
nodal DC balance, branch ratings and angles. Never imitate removal of the cap
by supplying an outcome-dependent large cap to a capped checker.

Also check the recovered point using exact Fraction arithmetic against the
archived binary64 coefficients: every original binary coordinate must be an
exact integer, and every finite row/column bound is compared both strictly and
after uniform outward expansion by tau = Fraction.from_float(1e-5), matching
the robust capped-certificate convention. Record both outcomes and the exact
maximum row/column violations. The native and matrix tolerance checks remain
separate requirements; their float calculations alone do not establish exact
unwidened feasibility.

A passing recovered point supplies an exact rational fossil-energy objective
value. It is a rigorous feasible energy upper bound for the expanded model
only when the exact expanded-bound check passes, and for the strict model only
when the exact strict check also passes. A merely tolerance-verified point is
a tolerance-qualified numerical upper estimate, not an exact unwidened-model
upper bound. Canonical NPZ vectors are authoritative; CSV exports are readable
copies. Report the solver's objective, numerical lower bound and gap separately;
a time-limited incumbent need not be optimal, and a numerical solver bound is
not an independently certified exact lower bound.

Any accepted finite uncapped witness can be paired, at the explicitly matching
tolerance convention, with its existing robust capped negative to delimit a
finite fossil-energy penalty of order. It does not establish the optimum from
an incumbent or fix the missing April/October replication. Numerical MIP
infeasibility remains numerical evidence only; a timeout without an accepted
witness is UNKNOWN. Preserve failed raw/recovered candidates and all settings.
