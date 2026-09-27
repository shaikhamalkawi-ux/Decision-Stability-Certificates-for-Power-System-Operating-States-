# Selected-proof affine commitment cut — proposal only

The independently accepted union energy-floor rejection can be lifted to a globally valid affine necessary condition by undoing the state substitution in its **already selected** row/box implications. This is a standard linear implication / dual-aggregation construction, not a new algorithm, an optimal cut, a minimum-information result or a feasibility characterization. No arithmetic, model assembly, optimization or cut generation has been executed for this proposal.

The scope is the two original expanded world models, the already frozen union schedule and the archived exact energy-floor proof. The complete common binary question remains UNKNOWN. A cut rejecting the union must not be described as rejecting every common schedule.

## Exact construction

Let the original model use generation variables `P`, shared commitment variables `U`, transition variables `Y,Z`, and angles. All coefficients and finite endpoints are interpreted as their exact binary64 rationals. Keep the established expansion `tau = Fraction.from_float(1e-5)`.

For each archived selected generation bound, recover its original row or variable-box source. A row source has exactly one generation coefficient `a != 0` and state part `b·s`, with no other continuous coordinate. Its finite lower or upper endpoint yields the same affine lower or upper function as before substitution:

`L_j(s) = (endpoint ± tau - b·s) / a`, or `H_j(s)` with that expression,

where the endpoint side and sign of `a` determine the direction exactly. The lower form is `L_j(s) - P_j <= 0`; the upper form is `P_j - H_j(s) <= 0`. A variable-box source is simply its expanded constant bound. The archived bound choice may cease to be the strongest at another state vector, but its underlying inequality stays valid. **Do not reselect a row, bound or hourly branch at a different state.**

For hour `t`, preserve the archived `active` branch, including its original tie choice:

- Direct branch: `A_t(s) = sum_{j in fossil} L_j(s)`.
- Balance branch: `A_t(s) = original aggregate lower endpoint - tau - sum_{j not in fossil} H_j(s)`.

Each satisfies `A_t(s) <= sum_{j in fossil} P_tj`. Sum over the fixed 168 hours and combine with the original fossil-cap row. This gives

`alpha + c·s <= original cap upper endpoint + tau`.

The singleton source in `temporal_lp_certificate.py` is the commitment output envelope: `P - Pmax*U <= 0` or `Pmin*U - P <= 0`; variable boxes are constant. That source evidence supports an **expected U-only cut**, but the implementation must validate the actual archived selected rows. Every state coefficient must lie in the original 4,032-coordinate U block. If a selected row has a nonzero Y or Z coefficient, stop the U-only claim and report the mismatch; do not silently discard it or adapt to a different cut family. The generation, theta, Y and Z coefficients must cancel or be exactly zero in the final actual-row combination.

For a direct original-inequality proof, express every used finite row endpoint and box endpoint as an upper halfspace. Divide a singleton halfspace by the positive magnitude of its generation coefficient; never by an unchecked signed quantity. Combine the resulting nonnegative multipliers with the aggregate lower endpoints where selected, then add the original cap upper endpoint. This must reconstruct the complete coefficient vector and constant of `alpha + c·U - B <= 0` exactly. Store endpoint-specific nonnegative multipliers, coalescing only equal `(row, side)` or `(column-box, side)` keys. Do not merge opposite endpoint multipliers and then lose their separate tau contributions.

The derived inequality is already an implication of the expanded original model. It receives **no additional tau expansion** as a newly invented row. It remains valid for every continuous or binary assignment satisfying those original expanded rows and boxes; no binary rounding or [0,1] assumption is used to derive it.

## Fixed inputs and decisive controls

Bind the reviewed floor source/protocol, its four producer records and the independent review; the frozen original matrices, boxes, full masks, column maps, candidate schedule and original cap rosters remain unchanged. Use the exact archived lower/upper source keys and hourly active labels. The existing `common_union` freeze is `8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2`.

Prospective checks, with no search or optimizer:

1. Reconstruct each selected symbolic implication from its actual original coefficients and endpoint, validate U-only support and exact nonnegative multiplier signs, and verify complete cancellation of P and every other unwanted column.
2. Evaluate each cut at the already frozen union bits. It must reproduce the archived floor and exact excess `242967941527088396181895 / 590295810358705651712 MWh` in each world, with no approximation or changed branch selection.
3. Evaluate each cut on the saved **unrounded** original joint LP point at `results/research_next/common_commitment/run01/lp/raw_solution.npz`, SHA256 `90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a`. Its prior independent review established exact expanded continuous membership; that old full membership need not be replayed. Both cuts must have nonnegative exact slack at this point. Any violation is a hard audit failure, since a valid consequence cannot reject this accepted continuous point. Do not change, round or repair that control, reselect a source, or tune a cut after failure.
4. Retain both world cuts, even if their coefficient vectors are identical, redundant or weak for other schedules. Report their equality only after exact comparison, with no elimination or maximization.

The negative-control point is genuinely fractional and does not establish common binary feasibility. Conversely, the union violation only excludes that particular common U choice and schedules with the same U that necessarily violate a derived cut; it does not establish nonexistence of other common commitments. No cost optimum, regret or finite upper witness follows.

## Conditional monotonicity corollary

After the actual coefficient audit, a cut may also reject every **binary** commitment vector componentwise greater than or equal to the frozen union `U*`. A sufficient condition is that every negative surviving coefficient has `U*_j = 1`; all other coefficients are nonnegative. The narrower expected case is nonnegative fossil-U coefficients and either zero nonfossil-U coefficients or negative coefficients only on nonfossil units already on. This must be checked against the actual reconstructed coefficients and frozen bits, not inferred from a unit label or anticipated nuclear behavior.

For binary `V >= U*`, a negative-coefficient coordinate with `U*_j=1` is forced to remain exactly one. Every remaining coordinate change has a nonnegative coefficient. Therefore `alpha + c·V >= alpha + c·U* > B`. If this condition holds for either valid world cut, merely adding on-hours to the union cannot supply a common binary witness under the unchanged cap. Here the already reviewed schedule has zero gap-fill additions, so `U*` is exactly the pointwise maximum of the two input U schedules. Any feasible common binary commitment would then have to remove at least one on-bit from that union (possibly while adding other on-hours elsewhere).

The corollary is conditional until the one prospective cut run checks every sign and relevant union bit. It does not apply automatically to the tau-expanded **continuous** relaxation: a fractional coordinate already at one can exceed one within its expanded box, so a negative coefficient might decrease the expression. Failure of the sign condition must be retained as a null corollary while preserving any valid affine cut. No alternative cut, coefficient suppression, different proof selection or optimization is authorized to obtain monotonicity.

## Size and replay expectations

Each cut has at most 4,032 U coefficients before exact zero removal. There are at most 23 selected fossil lower-bound implications in a direct hour, or 18 nonfossil upper implications plus one aggregate lower endpoint in a balance hour. Thus at most 3,864 hourly endpoint implications plus the single cap endpoint are needed before coalescing. This is an upper bound, not a measured support count. The future record should distinguish unique original row endpoints, box endpoints, surviving U coefficients, chronological hours, and the shared global cap dependency; these counts are proof-support metrics, not raw-data requirements or minimal memory.

Lossless output would include sorted numerator/denominator coefficients, alpha and B, endpoint multipliers, selected-source provenance and both exact control evaluations. A small standard-library implementation using the pinned existing NPZ decoder should suffice. It should freeze the two cases, inherited selections, control-point hash and a bounded arithmetic budget before running. Source review and separate execution authorization are still required. This proposal is distinct from the peer's universal capacity-cover/dynamic-programming bound and does not compute or replace it.
