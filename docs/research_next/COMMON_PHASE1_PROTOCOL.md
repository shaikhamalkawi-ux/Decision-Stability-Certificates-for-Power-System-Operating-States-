# One frozen phase-I multiplier attempt for the common nominee

27 September 2026. Prospective source/preparation protocol; no scientific execution without independent source/prepared review and separate explicit root GO. The design is `COMMON_NOMINEE_PHASE1_PROPOSAL.md` SHA256 `7ee2190eb6fd240b9e07924899cea0e7d22f67afba8260f4cd38b84a44cc21db`; its independent theory review is `86f2774978fbe4d1b80670b5cc288fda03d7a2ac8f3d9cacc17c8f16d3c74806`. This is a classical phase-I / Benders–Farkas refinement, with no method-novelty or minimum-information claim.

The arm is `results/research_next/common_phase1`, runner `src/researchnext_common_phase1.py`. The sole nominee is the existing complete state block in `common_master_bounded/run01/lp/fixed_schedule.json`, hash `26362ddab6b43aaa3ce2b605997a0c3460d9615492c13e177f7822c508ebf14a`. The master independent post-run PASS `d5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2` is a pinned prerequisite. That review establishes the nominated bits and necessary-master membership, while the old conditional LP remains only numerically infeasible. No usable dual/ray was saved by that LP. The old master, feasibility LP and all existing25 producer artifacts remain untouched; this is a distinct prospective LP, not hidden ray recovery.

## Source model, exact intended phase I and numerical encoding

Freeze the original joint69,362-row /33,936-column /291,176-coefficient matrix, complete12,096 original U/Y/Z mask and maps. Verify the nominee has exactly those unique binary columns, exact0/1 values inside original boxes, and the same values as the independently accepted master admission. No rounding, permutation, altered candidate or second schedule is permitted.

Keep all original x columns, fix their12,096 state boxes exactly to the nominee and expand only original continuous boxes by `tau=Fraction.from_float(1e-5)`. Admit every original column interval as finite/nonempty. Add one new continuous s with lower0 and upper+infinity. For each finite original lower endpoint create `A_r*x+s >= l_r-tau`; for each finite upper endpoint create `A_r*x-s <= u_r+tau`. An equality produces two distinct rows. Enumerate original rows in order, lower before upper. All original coefficients are retained; only the new s coefficient±1 is appended. Every backend column is continuous because the original integer columns are fixed. The objective is exactly min s, with all original objective coefficients zero.

Preparation checks original row intervals `l<=u` before any canonical-gain argument. Both original fossil electrical-generation caps are identified through the original row-origin and column maps: exactly23 native fossil units,3864 mapped P coefficients1 per world, original upper23195 and expanded upper23195+tau. No mean target, changed cap, different native data, new chronology or omitted source endpoint is allowed.

Every intended finite expanded endpoint/box is archived as an exact numerator/positive denominator, actual binary64 hex encoding and exact `binary64-intended` rounding residual. Nonrepresentable endpoints are not described as exactly represented in the numerical solver. Original A entries and s coefficients are exact binary64 values. Infinite source sides generate no constraint; s has no upper bound. The intended exact phase-I problem is always feasible for a correctly admitted finite source box: choose a boxed x with its fixed states and large enough finite s. Numerical infeasibility or a positive numerical optimum is not a proof.

`phase_model.npz` contains the numerical CSR matrix, endpoints, boxes, objective and continuous mask. `endpoint_map.json.gz` names every original endpoint and exact/rounded RHS; `column_encoding.json.gz` gives every original/fixed/expanded/artificial box. Original models, nominee and fractional-control bytes are copied from once-captured manifest-verified buffers. No backend import, multiplier evaluation, candidate cut evaluation or old point membership replay occurs in preparation.

## One numerical proposal and one exact recipe

Use the already installed scientific interpreter with `-I` only: Python3.12.14 / NumPy2.3.5 / SciPy1.18.1 / HiGHS1.12.0. One call only,60s, one thread, seed0, presolve on, simplex, min-s objective, no warm start, alternative orientation, retry, auxiliary optimization, IIS or dual-ray retrieval. Before that call, cache each backend sparse getter once and independently read back every actual numerical coefficient, endpoint, box, objective entry and continuous declaration. Archive the complete readback and option values.

Preserve every returned raw column value, row value, row dual and column dual in NPZ, with validity flags and selected numeric statuses separately recorded. The one recipe is eligible only for a complete finite row-dual vector with `dual_valid`. Solver optimality is not required for exact proof validity, and solver infeasibility/positive objective alone cannot admit a certificate. No `getDualRay`, normalization alternative or zero-dropping threshold is permitted.

For each lower endpoint, set lambda=max(raw dual,0). For each upper endpoint, set mu=max(-raw dual,0). Interpret each raw binary64 entry as an exact rational before projection; retain all raw/projection records, including zeros and rejected signs. Missing original sides have multiplier0. Combine d=lambda-mu on original row coordinates. This is the only selected multiplier candidate. Recompute q=A^T*d over the entire original matrix, keeping every residual coefficient.

Define beta(d)=sum_positive d*l + sum_negative d*u, with a finite selected endpoint required for each nonzero d. Every source expanded-feasible point satisfies q*x>=beta(d)-tau*||d||1. Two-finite rows satisfy l<=u. Preserve and verify the exact identities:

```text
beta(d)-beta_raw = sum min(lambda,mu)*(u-l) >= 0
sum(lambda+mu)-||d||1 = 2*sum min(lambda,mu) >= 0
canonical_expanded_RHS-raw_expanded_RHS
  = sum min(lambda,mu)*(u-l+2*tau) >= 0
```

Here beta_raw=sum(lambda*l-mu*u), using only present endpoints. The identities do not discard tolerance during cancellation: the final inequality is reconstructed directly from original signed endpoints. The artificial s dual coefficient and approximate solver stationarity are not assumptions of this proof.

Partition original columns into state B and continuous C. From original nominal continuous boxes compute S_C(q)=sum(q_j*upper_j for q_j>=0)+sum(q_j*lower_j for q_j<0). Exact expanded support is S_C+tau*||q_C||1. The globally valid necessary state inequality is:

`q_B*z >= beta(d)-S_C(q)-tau*(||d||1+||q_C||1)`.

There is **no binary tau** because state values remain explicit, and no extra tolerance is added to the derived row. The inequality can involve U/Y/Z and signed coefficients; no U-only or monotonicity conclusion is assumed. For the fixed nominee z0, only exact M=RHS-q_B*z0>0 admits rejection. M<=0 remains a nonseparating null. All original d and q entries, endpoint provenance, support endpoints, norms, cancellation gains and rational gap are archived losslessly.

The same necessary inequality must hold at the B block of the old independently verified **unrounded** common continuous point, raw SHA `90c8b308a6ce8e7671adbe3059887d6ce27489fa3d68aa601c2474b32d2d462a`, review SHA `f442edeb3f90c5d602a1b60cdef1b96b4d560ebbe97fae28c4ca21c6077eadba`. Evaluate this one fixed consistency control, without rounding its states or replaying its full membership. A contradiction causes a hard review stop, not a repaired cut. Fractional states do not invalidate the necessary inequality; no binary-point claim is made about that control.

## Bounds, records and conclusions

One180s overall phase starts before input revalidation;65s remaining is required after the final ready-file write and immediately before the sole60s call. Exact arithmetic checks deadline between blocks and stops at8192-bit numerator/denominator size. No partial proof is accepted. Final `completion.json.final_admission` is authoritative, sampled after full proof/control checks, rehashes and provisional result serialization. Only a strictly positive exact gap admitted before the common deadline is a certificate. A provisional result or a raw solver status cannot override a missing/negative final admission. Final serialization/cleanup outside the sample and any soft solver/phase overruns are explicitly reported.

The run is a single interpreter process, with actual Python PID and parent PID recorded at entry. Root/owner may monitor and terminate only a proven owned process chain if a soft limit is exceeded; no broad process-name kill is permitted. A Windows venv launcher PID does not alone establish descendant cleanup. No conditional child solver or second backend is launched by this runner. Raw solver logs remain private with public hash receipts until separately reviewed.

Invented controls cover a separating signed-dual example and continuous support, both endpoint-cancellation identities including tau, a nonseparating nominee, wrong-sign projection to zero, fractional-control contradiction, inverted intervals/duplicate endpoints, omitted or extra tolerance, exact encoding residuals and the bit guard. They read no scientific inputs and invoke no optimizer. The frozen preparation includes old master input/proof bindings, old25-file output inventory, all full nominee bits, exact endpoint recipe, original cap admission and the fixed control hash before any numerical call. Independent source/prepared review and separate root GO are required.

A success proves this one fixed nominee infeasible under the original expanded joint model and supplies a classical globally valid necessary state cut. It does not establish unrestricted common infeasibility, individual infeasibility, finite order cost, an optimum, or a third physical cause. A null/error/timeout leaves common binary feasibility UNKNOWN. No next master, new candidate or follow-up optimizer is part of this protocol. Independent post-run exact review precedes publication claims.
