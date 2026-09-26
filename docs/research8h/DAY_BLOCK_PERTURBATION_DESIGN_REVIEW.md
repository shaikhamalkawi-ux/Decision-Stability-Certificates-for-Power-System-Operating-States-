# Prospective review of the January whole-day order test

Review date: 2026-09-26 UTC. Recommendation: proceed as a bounded robustness
experiment after a separate executable protocol and all inputs are frozen.
This file is a design review, not an executed protocol or result. No solver
was called and no existing runner or evidence was edited.

Read sources: SEASONAL_TRANSFER_PROTOCOL.md, SEASONAL_REFERENCE_PROTOCOL.md,
SERVICE_CAP_NOVELTY_ASSESSMENT.md, and the native RTS-GMLC generator table
bound by the January manifest. Preserve the established 23,195 MWh cap, zero
named-generator means, full native DC model, and exact-arithmetic conventions.

## The question this experiment answers

The previous hourly permutations preserve every hourly package but disrupt
within-day profiles and hour-of-day alignment. This test preserves every
complete day and asks whether changing only the order of the three interior
days can change capped service feasibility. It is a stronger control on the
plausibility of the perturbation, not a new aggregation or certificate method.

Let A, B, C be source hours 48..71, 72..95, and 96..119 respectively, with
zero-based inclusive endpoints. Keep source hours 0..47 and 120..167 fixed.
Enumerate all five nonidentity permutations in the following fixed order:

| Case identifier | Interior order | Source positions moved |
|---|---|---:|
| day_ACB | A,C,B | 48 |
| day_BAC | B,A,C | 48 |
| day_BCA | B,C,A | 72 |
| day_CAB | C,A,B | 72 |
| day_CBA | C,B,A | 48 |

Identity day_ABC is the positive reference, outside the five-case denominator.
No random seed, replacement, or outcome-based permutation selection is needed.
The moved-position counts refer to source indices; do not confuse them with
the count of numerically distinct hourly packages.

For a block permutation pi of (0,1,2), define the source mapping for interior
position t = 48 + 24q + j by

    source(t) = 48 + 24*pi[q] + j,  q in {0,1,2}, j in {0,...,23}.

Outside the interior, source(t) = t. Move all availability, fixed hydro,
nodal loads, rooftop PV, native row identifiers, and corresponding static
witness P/U/theta through this single mapping. Validate a bijection and its
inverse, both fixed edge blocks, source(t) modulo 24 = t modulo 24, and exact
equality of each source and destination 24-hour package. Check the regular
hourly native timestamp mapping already established for the reference.

All seven complete day profiles, their intraday chronology, and the complete
hourly multiset are retained. All 161 within-day adjacent pairs are retained;
only the four interday joins at destination hours 48, 72, 96, and 120 can
change. The joins at hours 24 and 144 remain fixed. The test does not preserve
cross-day transition counts, day-of-week alignment, multi-day weather
evolution, or all windows crossing midnight. It remains a synthetic
perturbation, though substantially less disruptive than arbitrary hour swaps.

## Residence constraints cannot reset at day boundaries

The actual Area 1 thermal roster has maximum native minimum-up time 24 hours
and minimum-down time 48 hours. Both 123_STEAM_3 and 121_NUCLEAR_1 have up=24,
down=48. Other native fractional values include 2.2 hours and 4.5 hours; the
existing hourly formulation uses their ceilings, 3 and 5 hours respectively.
Do not replace these native values with a generic one-day assumption.

Consequently, a whole 24-hour block is not an independently interchangeable
operating period. An off-run can owe residence time across two days, and
shorter runs can cross any new join. Violations may appear inside a later
day as the consequence of an earlier join, not only at its first hour.
Keeping 48 hours of input at each edge does not fix the commitment history
there, nor establish invariance to different initial or terminal conventions.

Copy the verified reference U by whole days only as a candidate witness.
Recompute Y=max(delta U,0), Z=max(-delta U,0) across the entire new 168-hour
sequence, with the existing zero initial transitions. Never independently
permute the old Y/Z arrays, reset commitment at midnight, solve days in
isolation, or impose cyclic closure. A failed copied witness is not proof
that another dispatch/commitment is impossible.

Native hourly on/on ramps remain analytically redundant at the retained
operating ranges, as already audited. Verify that source fact and check all
candidate ramps directly, including new joins. Do not add unmodelled startup
ramps, storage, shedding, line slack, mean targets, or a substitute cap.

## Controls and pre-solve gates

Use the authoritative previously verified January binary positive point;
retain its raw incumbent provenance. Its exact fossil-energy sum is unchanged
by any permutation. The cap remains 23,195 MWh for every case, irrespective
of the new outcomes. There is no reference reoptimization or cap recalculation.

Before any target solve:

1. Rebuild and verify identity with the same native rules, full matrix, cap,
   and exact expanded-bound check used for the targets. Retain its strict
   exact check separately rather than asserting strict feasibility.
2. For all five cases, verify the permuted reference P/U/theta against the
   static model obtained by removing only minimum-up/down rows and replacing
   Y/Z canonically. Check every other row, exact binary coordinates, native
   DC physics, and the exact preserved fossil sum. This rules out an isolated
   hourly capacity/network explanation.
3. Also test each copied candidate against the full chronological model and
   native residence runs. A passing candidate is a constructive positive;
   retain it and spare that case an unnecessary MIP. A dwell failure is a
   descriptive result and does not stop the arm or become a negative label.
4. Check inverse mappings recover the original packages exactly. The existing
   commitment-class control may be replayed as an additional implementation
   control, but label it separately: it is not a whole-day permutation and
   must not enter the five-case outcome count.
5. Freeze all five permutations, matrices, bounds, objective, native arrays,
   source/reference/protocol hashes, integrality masks, and control reports
   before the first LP. A failed identity, static witness, package mapping,
   or cap audit stops execution and is reported as a preparation failure.

No distinct nonidentity day permutation is assumed feasible in advance.
Requiring one, or selecting one after inspecting outcomes and calling it an
independent positive control, would bias the design. Identity plus the
mapping/static controls supplies the mandatory positive/control structure.

## One fixed solver routing proposal

The following is a concrete recommended budget, to be accepted and frozen
before implementation outcomes. It does not amend earlier experiments.

Stage A: run one continuous full-network LP for each of the five cases in
the table order, including any constructively positive case. Use the same
zero feasibility objective, simplex, presolve off, one thread, seed zero,
and 30 seconds per call. Mandatory LPs for all five give uniform stage-A
coverage and a check against the constructive positives. Preserve every
returned vector and the one returned raw ray, if available. Test both ray
orientations and explicitly sign-projected candidates by full exact rational
recomputation, with no ray-recovery optimization.

A negative requires strictly positive separation after expanding every
finite row and column bound outward by tau=Fraction.from_float(1e-5).
A simultaneously verified exact expanded positive and robust exact negative
for the same bound matrix is a contradiction: stop and audit, rather than
selecting a preferred outcome. Numerical LP infeasibility without a passing
certificate is unresolved, not certified negative.

Stage B: after all five LP calls, in the same fixed order, run one 300-second
MIP only for a case lacking both a robust exact LP negative and an accepted
binary witness. Use the already audited U-only projection, original bounds,
zero objective, presolve on, one thread, seed zero, relative gap 1e-8, and no
warm start, fixing, retry, or extension. This preserves physical projection
feasibility while avoiding unnecessary auxiliary integers. The structural
audit must pass on every actual generated matrix before any solve.

A candidate from stage A, stage B, or constructive replay can establish a
positive only after finite near-binary U is canonically recovered and the
recovered point passes all original full-binary matrix/native checks plus
exact expanded-bound membership. Save raw and recovered vectors separately;
keep P/theta unchanged during recovery. Report strict exact membership too.
Use the exact fossil sum and the stated expanded-cap convention B+tau.

Maximum allocation: five LP30 calls and five MIP300 calls, or 1,650 configured
solver seconds. Run this arm sequentially, under the root's overall
concurrency limit. A 35-minute phase limit starts immediately before the first
LP. Do not start a MIP with fewer than 305 seconds remaining. Record an
unstarted case as NOT_RUN_BUDGET. Record actual elapsed times and soft-limit
overshoot; report generation/checking separately. Host delay and concurrency
make this unsuitable as a speed comparison against previous arms.

The fixed route is conditional on evidence, not outcome tuning: a proof or
verified witness already answers a case, while continuous feasibility alone
does not. Do not change caps, orders, time limits, solver settings, or
integrality conventions to obtain a preferred result.

## Interpretation fixed before outcomes

| Outcome | Permitted interpretation |
|---|---|
| At least one robust exact negative, with the positive/static controls passing | The multiset of complete daily profiles, their intraday chronology, and these fixed boundary inputs do not determine feasibility under this shared cap. Interday order alone can distinguish this reference from that twin in the stated model. |
| All five have verified binary witnesses | All six orders of these three days are feasible under this cap. The earlier arbitrary-hour obstruction does not extend to this restricted family; retain this adverse result. It is not a general sufficiency theorem for typical days. |
| Positive and unknown cases, no certified negatives | The experiment has not established an interday counterexample. UNKNOWN is not feasible or infeasible. |
| Numerical LP/MIP infeasibility without an exact accepted proof | Numerical negative evidence only, excluded from the certified-negative count. |
| Cap-ray multiplier allows exact objective normalization | Report the resulting necessary fossil-energy lower bound in MWh, with residual/box and noncap expansion terms included. It is not an attained finite penalty. |

Enumerating five possibilities is complete for this specific three-day family;
it is not five independent draws, five weeks, or seasonal/network replication.
No uncapped run is silently added to this protocol. Any finite-price claim
would need a separately declared uncapped witness for the relevant case.

## Value relative to known prior art

This arm addresses a concrete weakness of the earlier stress test: loss of
intraday profiles and clock alignment. A certified failure here would be a
cleaner benchmark for representative-day models that omit interday state.
Conversely, universal admission among these five cases would delimit the
earlier result and reduce the basis for practical claims about day-level
aggregation on this week.

It would not refute methods that use the changed interday transitions. Auer
et al.'s representative-period study already varies the order of unchanged
periods and uses transition information; Bahl et al. already assess full-series
feasibility and objective error. See SERVICE_CAP_NOVELTY_ASSESSMENT.md for
the primary-source sections and limitations. An exact day-transition matrix
with unique day labels can itself reveal their order. This experiment does
not preserve that stronger observation and is not a Markov counterexample.

The appropriate contribution remains a controlled and reproducible evidence
set, possibly strengthened by a more realistic perturbation. The design
itself is not novel; a positive scientific result would be the actual
certified case, and a negative result would be a useful limit on the claimed
phenomenon. Both deserve the same frozen routing and reporting.
