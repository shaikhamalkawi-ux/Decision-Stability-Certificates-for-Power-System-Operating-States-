# Fresh January uncapped energy qualification

This separate follow-up is specified after the capped fresh-week experiment.
It is not a blind test of the already known capped labels. Its question is
whether finite uncapped fossil-electricity costs can be bounded for all four
prescribed targets, including the unresolved capped target. No result-dependent
target eligibility, replacement, cap choice, unit choice or permutation is
allowed. Earlier arm sources, results, labels and gates remain unchanged.

## Fixed cases and model

Use both accepted references from `fresh_january_weeks/references`: week 2
(January 8--14, native rows 168--335) and week 3 (January 15--21, rows 336--503).
The target denominator is exactly four: week 2 seeds 26093210 and 26093211,
followed by week 3 seeds 26093220 and 26093221. Every target enters regardless
of its capped verdict. Their complete hourly packages and permutations are
copied, with no new draws or source-hour choices.

For each target delete exactly its sole fossil-energy cap row. Use its actual
week's archived cap, checked against the exact reference formula ceil(101E/100),
not a hardcoded first-week cap. Every other row, coefficient, row bound, column
bound, native array, original binary mask and permutation remains unchanged.
No individual generator mean, shedding, storage or other variable is added.

Both reference matrices are already uncapped and are reused without a physical
model change. Independently compare each to its capped identity after deleting
only that identity's cap. The objective on every model is one on each of
168*23 dispatch coordinates belonging to native Coal/Oil/NG units and zero
elsewhere; exclude nuclear. Energy is fossil electrical MWh, not fuel, carbon
or monetary cost. Audit actual generator roster, objective and deleted row.

Keep the existing Area 1 isolated DC network, 24 buses, 38 internal branches,
41 generators, 24 thermal units and 168 hourly intervals. Retain native output,
hydro/renewable availability, nodal/aggregate balance, line/angle and dwell
constraints, free mature initial U, initial Y/Z zero, and terminal dwell
clipping. Native on/on ramps are unchanged, analytically redundant under the
selected nominal bounds and separately checked on accepted points. Do not
import another week's dispatch, reconstruct targets, or change boundary rules.

## Gates and provenance

Initially only this protocol and its new runner may be written. No preparation
or optimizer is permitted until the capped parent's final accounting and
independent review close and the root explicitly authorizes preparation.
Preparation requires the independent two-reference PASS records and complete
four-target final-ledger PASS, checks their bound artifact hashes, rechecks both
parent manifests, and binds completed parent outcomes without selecting cases
by those outcomes.

Preparation archives all six matrices/objectives/bounds/masks and provenance
before any new solve. It replays the two original reference binary witnesses
against the uncapped model and native inputs, preserves their exact energies,
and checks pinned native calendars/arrays and all four target package permutations (two per week).
The original full U/Y/Z mask remains the acceptance mask; an audited U-only
mask is used solely for the four optimization attempts. Transitive local source,
protocol, raw source and native-model files are hash-bound. The original
source/protocol become immutable at preparation. Independent prepared review,
root source review and separate explicit execution GO are required afterward.

## Fixed solve allocation

The execution/check allocation is 3600 seconds from entry into run-prepared,
including validation and native loading. Calls are sequential in this order:

1. Exactly one continuous LP60 on each reference, week 2 then week 3.
2. Exactly one U-only MIP600 attempt on each of the four targets in seed order.
3. Exactly one continuous LP60 on each target in the same order.

These are maximum scheduled calls: two identity LPs, four target MIPs and four
target LPs. There are no new identity MIPs. Every LP uses simplex, presolve off,
thread 1, random seed 0. Every MIP uses presolve on, thread 1, seed 0 and relative
gap 1e-8. There are no warm starts, retries, ray-recovery solves, adaptive
objectives, target skips due to a capped label, or follow-up calls.

After model loading and solver construction, immediately before each actual
solver.run, require at least 605 seconds for a MIP or 65 seconds for an LP both
within the remaining phase allocation and before 2026-09-27 04:00 UTC. A skipped
call records its guard reason, zero calls and zero solver elapsed time. Earlier
case failure does not authorize reallocation or extra cases. Preserve missing
duals, no incumbent, nonpositive lower bounds and UNKNOWN results. Record actual
starts, ends, solver times, all soft-limit overruns, phase overrun and cutoff
overrun. These are start guards and soft allocations, not hard process limits.
Root coordinates the at-most-two-long-MIP shared-host limit.

## Exact qualification and reporting

The mathematical model is the archived binary64 matrix with every finite row
and column endpoint widened by exact Fraction.from_float(1e-5); original U/Y/Z
remain exactly binary. Strict nominal membership is recorded separately. This
mixed-unit numerical convention is not measurement uncertainty.

An existing reference remains the unchanged binary upper witness for its
week. For a target, save every returned MIP point; eligible near-binary U may
be rounded and canonical Y/Z reconstructed, with P/theta bytes unchanged.
Acceptance requires raw/recovered numerical matrix checks, exact widened
membership using the original full binary mask, and the native no-cap check.
A continuous LP point, numerical infeasibility or solver bound is never a
binary upper witness. No accepted target point yields the explicit NO_UPPER
status; finite uncapped feasibility and finite cost must not be asserted for it.

For each LP retain its primal, row/column duals, options, statuses and gap/bound
diagnostics. To obtain an exact lower bound, reject nonfinite row multipliers
and explicitly project only signs selecting an infinite row endpoint to zero.
For the projected signed vector d, let beta be its selected row-endpoint sum
and q = c - A-transpose d. Compute all products/sums and q signs as exact
Fractions of the archived binary64 numbers. The nominal bound is
beta + sum_j min(q_j*a_j, q_j*b_j). Its uniformly expanded counterpart subtracts
tau*(||d||1+||q||1). This holds without exact dual stationarity or numerical
optimal status. Preserve raw/projected multipliers and the exact residual.
Do not clip the expanded bound to zero. A separately saved zero-row-dual bound
provides a valid finite fallback; use the maximum of that and any new valid
bound. No existing numerical MIP lower bound is treated as exact evidence.

For each week let [L_I,U_I] be the exact reference optimum enclosure, where U_I
is the unchanged reference witness energy. A target with accepted upper U_T
and exact lower L_T has an optimum-difference enclosure
[L_T-U_I, U_T-L_I]. Report separately the target optimum excess over that chosen
incumbent [L_T-U_I,U_T-U_I]. Only when L_I>0 and L_T>0 report the relative optimum
interval [L_T/U_I-1,U_T/L_I-1]. Keep nonpositive differences and intervals
containing zero unchanged. If a target has no upper, preserve its lower bound
without claiming a finite optimum or a finite difference enclosure. Reject any
exact lower/accepted-upper contradiction. Rational endpoints are authoritative;
all displayed interval endpoints must round outward.

Preserve the complete four-case denominator, actual labels, all failed/skipped
attempts and raw output. A positive lower penalty on new weeks is within-system
January evidence, not independent-network replication or real-weather/field
validation. This is energy qualification of fixed instances, not a new method.
Independent post-run replay is required before publication or manuscript use.
