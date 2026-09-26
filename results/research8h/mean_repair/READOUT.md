# Continuous named-unit mean-repair sensitivity

All five predeclared LPs returned numerical Optimal status and passed primal checks at tolerance 1e-5. Identity returned epsilon zero. The four ordinary twins returned radii near 1.52%–2.00% of nameplate. Exact rational lower bounds independently show a positive relaxation requirement of comparable size, including after the declared outward numerical-tolerance expansion. This quantifies the sensitivity of the earlier exact named-unit-mean rejection; it does not establish binary or DC-network repair.

| Case | Numerical candidate epsilon | Exact-arithmetic nominal lower bound, % of nameplate, rounded down | Outward-tolerance lower bound, %, rounded down | Solve seconds |
|---|---:|---:|---:|---:|
| identity | 0 | 0 | -0.001001 | 37.941 |
| seed 26092600 | 0.015220960506995387 | 1.522096 | 1.521551 | 31.581 |
| seed 26092601 | 0.020048032574594280 | 2.004803 | 2.004253 | 26.218 |
| seed 26092602 | 0.015227588586094961 | 1.522758 | 1.522195 | 12.017 |
| seed 26092603 | 0.018081508385971966 | 1.808150 | 1.807536 | 13.250 |

The percentage columns equal 100 times epsilon and are conservatively rounded down to six decimal places; identity's actual widened bound is approximately -0.001%. A positive lower bound means that at least one named-unit average must change by that fraction of its own nameplate in any feasible repair in this model. It does not mean every generator changes by that amount, that the change is a percentage of its original target, or that aggregate demand/fossil energy changes by that percentage. Individual deviations for the returned fractional schedules are in each case's `mean_shifts.csv`.

## What was held fixed

Each archived service-cap LP was retained exactly: aggregate hourly balance, dispatch availability, fixed hydro, continuous thermal states/transitions and minimum up/down rows, plus the same 23-fossil-unit energy cap of 180555.9189139999 MWh. No network constraints, integrality, new permutation, target selection or cap adjustment were introduced. All 41 native PMax scales are positive (12–713.5 MW), with every source hourly upper availability at most its nameplate.

For every original archived mean equality a_i x = mu_i, the model adds a_i x - S_i epsilon <= mu_i and -a_i x - S_i epsilon <= -mu_i. Original binary64 coefficients, including stored 1/168, and target bounds were copied exactly. Epsilon is the sole objective variable and lies in [0,1]. Each model has 24,347 rows and 18,985 continuous columns. All five models, protocol, source files and inputs were frozen and hashed before the first solve.

Exactly five solves were run: HiGHS 1.12.0, simplex, presolve off, one thread, seed zero, 60 seconds maximum per case, no warm start or retry. All finished within that limit. Shared-host timings are not a benchmark.

## Exact lower bound versus numerical primal candidate

Given saved row multipliers d, inadmissible signs selecting infinite row endpoints are explicitly projected to zero. With q = c - A^T d, the checker computes the signed-row lower contribution plus the minimum of q^T x over the finite variable box. Every multiplication, sum and sign decision uses exact fractions of archived binary64 data. It preserves raw/projected multipliers, exact stationarity residuals and rational numerator/denominator strings. No extra solve or exact dual-stationarity assumption is needed. The zero-multiplier sanity check produces nominal lower bound zero.

The displayed nominal bounds are rounded downward from the exact rational results. They are objective lower bounds, not assertions of the exact minimum. The corresponding numerical primal epsilons are tolerance-qualified upper estimates only. Nominal lower-bound decimals exceed those numerical epsilons by about 2e-16–5e-16 because the saved primal is not an exact feasible vector. This is retained, not rounded away or called a certified enclosing interval.

The append-only `post_run_audit.json` recomputes fossil energy and cap excess as exact rational sums of saved binary64 dispatch. Identity satisfies the cap exactly. The four twins exceed it by approximately 2.8941e-11, 1.9104e-11, 1.2858e-11 and 3.3454e-11 MWh, respectively, far below the declared 1e-5 numerical tolerance but strictly positive. Thus no exact primal upper bound is claimed. Increasing epsilon alone cannot repair residuals in the retained balance, chronology or cap rows.

The outward-tolerance lower bound is obtained by subtracting tau times the sum of absolute projected row multipliers and exact stationarity residuals, where tau is the exact binary64 value of 1e-5. Every finite row and box bound is expanded, including epsilon's box to [-tau,1+tau]. This mixed-units numerical expansion is not a model of physical measurement error. The widened lower bound is not clamped at zero; identity's -1e-5 is expected. All four twin widened bounds remain positive.

Identity's numerical zero control passed without retuning any means. Its returned primal has an exact maximum mean-deviation ratio of approximately 1.65e-14, illustrating why numerical zero is not asserted as an exact rational feasibility result. Its epsilon-zero preflight and the exact widened bound are consistent. Returned fractional-state counts are 528, 535, 569, 502 and 495 in case order; none of these LP outputs is presented as a binary witness.

## Review, scope and artifacts

Separate reviewers checked the complete implementation, all five archived model constructions and all 100 manifest entries. Synthetic multiplier tests covered both signs, imperfect stationarity, outward-bound expansion and forbidden-sign projection. A separate reviewer also independently replayed all five actual saved primal/dual bounds without optimization and matched the nominal/widened exact results and tolerance checks. Review ordering was post-launch; model/protocol freezing preceded every solve. See `docs/research8h/MEAN_REPAIR_REVIEW.md` for the detailed independent mathematical and result review.

The continuous aggregate-balance repair requirement is about 1.52%–2.00% on the chosen nameplate-normalized metric for these four already declared July permutations. No threshold for practical materiality was selected, no new-season generalization is claimed, and this result does not show that binary/network repair is possible at these radii. It shows that exact-mean rejection persists over a quantified nonzero band in the stated continuous model, including the explicit numerical expansion tested here.

Per-case artifacts include the full matrix/bounds/objective, original mean rows, scales/targets, source order, raw primal and row/column dual vectors, projected dual, exact lower-bound certificate, exact mean diagnostics, mean shifts, continuous dispatch, primal check, metadata, solver log and complete result. `summary.json` and `summary.csv` retain all outcomes. `post_run_audit.py` contains the separate no-solver fossil-cap/hash audit; its output confirms all 100 frozen source/model hashes still match.

Frozen runner SHA256: `1d3ab964494177c09110ae348e01ed10d69def9ea890555665548851b46c9328`. Frozen protocol SHA256: `46a5de8ce4654442230010ace68c204c03904e30709b2ee97be1b2ac670a4755`. The main run made exactly five optimization calls. Existing artifacts and earlier checkpoints were not changed.
