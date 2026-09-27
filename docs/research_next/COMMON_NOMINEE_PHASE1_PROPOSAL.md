# One phase-I certificate attempt for the closed common nominee

27 September 2026. **Design only.** No new model, scientific coefficient calculation, cut evaluation or optimizer call has been performed for this proposal. The closed master and its feasibility LP remain unchanged. Recommend one classical phase-I / Benders–Farkas certificate attempt for the already nominated schedule, with no next master iteration or alternative nominee proposed here.

## Existing evidence and missing certificate

Source inspection of `src/researchnext_common_master_bounded.py` and its pinned HiGHS transport helper confirms that the closed conditional LP called `h.run()` once and inspected `getSolution()`, but did not call `getDualRay` or save a row-dual vector. The25-file producer inventory contains the full backend readback and fixed schedule, but no LP raw point or multiplier certificate. `lp/solver_returned.json` records `kInfeasible`, `kOk`, and `valid_solution=false`. The saved backend matrix is not a certificate. No private log is treated as proof, and no recovery/re-solve of that closed LP is proposed.

The single fixed input is the exact12,096-bit schedule in `run01/lp/fixed_schedule.json`, SHA256 `26362ddab6b43aaa3ce2b605997a0c3460d9615492c13e177f7822c508ebf14a`, and the corresponding producer exact necessary-master admission `983c62c4aaec8969ecc02ee774a55aa1fe2b95edf74d884dbae6f69e28b5a87a`. Its pending independent post-run gate is a prerequisite to future preparation. Bind the original common models and239-binding master freeze `75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5`, plus the original masks/maps and accepted cut provenance. Do not derive a different schedule from the solver vector or modify any bit.

## One prospective phase-I model

Let the original common matrix be A with row endpoints l,u, continuous coordinates C, and shared state coordinates B. Keep all33,936 original columns and69,362 original rows as the source instance; add one continuous artificial variable s with0<=s and no upper bound. All12,096 original B coordinates are fixed exactly to the archived nominee, with the original mask retained in provenance. They are continuous to the LP solver solely because every integer coordinate is fixed. Every original continuous box is expanded by the exact `tau=Fraction.from_float(1e-5)`; no binary-box tau is added to the fixed state values.

For every finite original lower endpoint create `A_r x+s >= l_r-tau`. For every finite upper endpoint create `A_r x-s <= u_r+tau`. An equality has two separate endpoint rows. Enumerate by original row, lower first then upper; no endpoint selection or removal. The new objective is exactly `min s`, all original objective coefficients zero. Keep both original23,195MWh fossil electrical caps as ordinary source rows with their one uniform expansion. No means, new service cap, chronology, physical input or network coefficient is introduced.

Before execution, admit every original continuous box as finite and nonempty, all fixed state values as exact0/1 in their original boxes, and the complete source mask/maps. Unsupported infinite continuous boxes stop this first design rather than changing the support formula. With finite boxes and finite original coefficients/endpoints, the exact phase-I model is feasible: choose any point in those boxes with the fixed bits, then sufficiently large finite s covers every endpoint. Therefore a numerical phase-I infeasibility is itself a null/diagnostic, not evidence of original infeasibility.

Archive every intended rational widened endpoint/box and the actual binary64 encoding/rounding error supplied to HiGHS. The original A coefficients and artificial coefficients±1 are unchanged exact binary64 values. The numerical phase-I model only proposes multipliers; exact final verification concerns the original rational interpretation of archived A,l,u and tau. Full cached-array backend readback must verify every actual numerical coefficient, endpoint, fixed/continuous box, column coordinate, objective and declaration before the sole call. Do not confuse readback equality with exact equality between the intended rational and rounded numerical models.

## Exactly one multiplier recipe

Use one60s HiGHS1.12.0 simplex LP, one thread, seed0, presolve on, no warm start, retry, secondary objective, ray/IIS retrieval, alternative orientation or fallback. Save all returned raw primal, row-dual and column-dual fields with their validity flags, even if unusable. No `getDualRay` call is needed or allowed. Require one finite returned row-dual vector with the expected complete endpoint denominator and `dual_valid`; otherwise retain a null.

For a lower endpoint row use `lambda_r=max(raw_row_dual,0)`. For an upper endpoint row use `mu_r=max(-raw_row_dual,0)`. Interpret each raw binary64 entry exactly as a rational before this sign projection. Missing endpoints have zero multipliers. Preserve raw and projected values, including rejected signs and zero entries. This is the only candidate, not an attempt followed by alternative repairs. Combine duplicates as `d_r=lambda_r-mu_r` on the original row coordinates. Recompute every coordinate of `q=A^T d` from original coefficients without dropping any residual or consulting solver stationarity.

For signed d define the original endpoint sum

`beta(d)=sum_(d_r>0) d_r*l_r + sum_(d_r<0) d_r*u_r`.

The endpoint required by each nonzero d must be finite. Sign projection guarantees this for one-sided source rows; check it explicitly. Every original expanded feasible point satisfies `q*x >= beta(d)-tau*||d||_1`. This follows directly by multiplying the available lower/upper endpoint inequalities with nonnegative weights.

Combining a row's two projected endpoint multipliers is sound and can strengthen their raw sum. Writing `beta_raw=sum(lambda*l-mu*u)`, one has exactly

```text
beta(d)-beta_raw = sum_r min(lambda_r,mu_r)*(u_r-l_r)
sum_r(lambda_r+mu_r)-||d||_1 = 2*sum_r min(lambda_r,mu_r)
```

Only two-finite-endpoint rows can contribute to these sums. Thus the canonical combined expanded RHS exceeds the raw expanded RHS by `sum min(lambda,mu)*(u-l+2*tau)>=0`. This is justified by the original endpoint interval, not an unsupported cancellation of expansion. Archive and check this identity. The artificial s coefficient and the phase-I dual normalization are unnecessary for validity of the reconstructed original-row inequality: any admitted signed d suffices. A positive numerical phase-I objective, approximate dual feasibility, numerical optimality or solver infeasibility alone proves nothing.

## Exact separation and globally valid state cut

For continuous coordinates only, use the original unexpanded boxes to compute

`S_C(q)=sum_(j in C,q_j>=0) q_j*upper_j + sum_(j in C,q_j<0) q_j*lower_j`.

The support over uniformly expanded continuous boxes is exactly `S_C(q)+tau*||q_C||_1`. Hence every full original expanded common solution satisfies the state inequality

`q_B*z >= beta(d)-S_C(q)-tau*(||d||_1+||q_C||_1)`.

This inequality is globally valid for the original common model, not merely for the nominated fixed boxes. It may involve U,Y and Z, with arbitrary signs; no U-only or monotonicity claim is presumed. It also applies to a fractional state vector whenever that vector and a continuous dispatch satisfy the same expanded rows/continuous boxes. No additional binary tau or newly derived row tolerance is appended to this exact cut.

For the archived nominee z0, evaluate the exact gap

`M=beta(d)-S_C(q)-q_B*z0-tau*(||d||_1+||q_C||_1)`.

Only **M>0** yields a verified rejection of this fixed nominee and an exact necessary state cut. M=0 or M<0 is a null. Retain every coefficient of q, exact fractions, all endpoint provenance, both cancellation identities, support endpoints, norm terms and final margin. Check the complete original vector identity and nominated state mapping, not only selected support entries. A fixed8192-bit rational numerator/denominator guard and the overall phase guard may stop with an incomplete/null result; no partial certificate is accepted.

As a fixed non-optimization consistency control, a future protocol should evaluate any accepted cut on the already independently verified unrounded common continuous LP state's B block (raw point SHA `90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a`). It must satisfy the cut. This does not repeat the old full-point membership proof or relabel that point binary. A contradiction is a hard review stop. No new accepted positive witness or unrestricted common negative follows from a separating cut for z0.

## Boundaries, budget and attainable conclusion

Propose one180s whole phase, including frozen-input revalidation, numerical model/readback, the sole60s LP, exact reconstruction/checking and closing admission. Require65s remaining immediately before the call; retain actual soft solver overruns and gate final certificate admission on completion of all exact checks within the phase. Preserve nulls and every raw output. The run should use the direct existing scientific interpreter process and an externally monitored owned process chain if needed; do not rely on a Windows venv launcher PID as proof that an actual worker descendant was terminated. No second solver is needed for this arm.

All new source, invented signed-endpoint/cancellation/tau controls and solver-free preparation would require authorization and independent gates before any scientific call. A numerical phase-I solution only nominates the one d; exact M>0 is the decisive evidence. A successful result excludes this third tested schedule and supplies one classical Benders/Farkas necessary cut, leaving unrestricted common binary feasibility UNKNOWN. A null leaves the same question UNKNOWN. No next master iteration, new schedule, cost bound, method novelty or minimum-information claim is included. Prior classical decomposition attribution remains the existing inspected literature; this proposal adds no paper reading or literature-count claim.
