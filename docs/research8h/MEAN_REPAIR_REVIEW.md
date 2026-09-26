# Independent review of the continuous mean-repair bound

Review started 2026-09-27 Dubai. This file owns only mathematical and implementation-review notes. No solve was run by this reviewer and no runner, protocol or result was edited.

The protocol and complete runner have now been reviewed, and all five archived objective bounds have been independently recomputed without importing the runner or invoking an optimizer. No mathematical blocker was found. This was a post-launch review, not a preflight gate: the root had authorized the process before the implementation-review request reached it. The source itself froze all five models before its first solve. No outcome-based source change was made for this review.

## 1. What the repair variable measures

For unit \(i\), let \(\mu_i\) be the frozen original mean target and \(S_i>0\) its native nameplate PMax. Let \(H=168\), with the existing archived average-row coefficient convention. The intended LP minimizes one common variable \(\epsilon\in[0,1]\), subject to

\[
\mu_i-\epsilon S_i\le \overline P_i\le\mu_i+\epsilon S_i,\qquad i=1,\ldots,41.
\]

It retains the same continuous service-cap model, including the original aggregate balance, fixed hydro, native dispatch availability, relaxed thermal states/transitions/residence rows and the same 23-fossil-unit upper cap. It adds no DC-network constraints or integrality.

The band must be encoded with two linear rows per unit:

\[
\overline P_i+S_i\epsilon\ge\mu_i,\qquad
\overline P_i-S_i\epsilon\le\mu_i.
\]

The objective is exactly \(c_\epsilon=1\) and zero on every other column. This is a Chebyshev-type repair metric: the optimum is the smallest attainable maximum of \(|\overline P_i-\mu_i|/S_i\), subject to the model and \(\epsilon\le1\).

A positive lower bound means at least one target must deviate by that fraction of its own nameplate scale. It does not say every unit must move, that each unit changes by that percentage of its original target, or that total fossil energy/demand changes by that percentage. All mean targets may move in either direction. Candidate unit deviations describe one fractional solution, not uniquely necessary physical changes.

## 2. Exact lower bound from arbitrary row multipliers

Write the archived LP as

\[
\min c^\top x,\qquad l\le Ax\le u,\qquad L\le x\le U,
\]

with finite variable bounds \(L,U\). Let \(d\) be any finite signed row-multiplier vector. If \(d_i>0\) but the selected lower row bound is infinite, set \(d_i=0\); likewise set \(d_i=0\) if \(d_i<0\) and its selected upper row bound is infinite. Reject NaN/nonfinite multipliers and malformed inputs. Zero multipliers contribute zero without evaluating zero times infinity.

Define

\[
\beta(d)=\sum_{d_i>0}d_i l_i+\sum_{d_i<0}d_i u_i,\qquad
q=c-A^\top d.
\]

For every feasible \(x\), signed multiplication of the appropriate row side gives \(d^\top Ax\ge\beta(d)\). Therefore

\[
\begin{aligned}
c^\top x
&=d^\top Ax+q^\top x\\
&\ge\beta(d)+\sum_{q_j\ge0}q_jL_j+\sum_{q_j<0}q_jU_j
=:\operatorname{LB}(d).
\end{aligned}
\]

This is a valid lower bound even if \(d\) is not dual feasible, the solver stopped early, its row-dual convention was misunderstood, or some inadmissible signs were projected away. Such defects may make the bound weak, but cannot make the displayed proof invalid if the final bound is recomputed correctly. Finite-box residual correction is essential; omitting \(q\) or treating a small floating residual as exactly zero would invalidate the argument.

Because the original variable box has \(\epsilon\ge0\), \(\max(0,\operatorname{LB})\) is also a valid lower bound for that original LP. Preserve the raw bound as well. The zero multiplier vector must produce raw LB=0. A bound greater than one implies infeasibility of the capped repair domain, rather than an attainable repair above the allowed range.

### Exact arithmetic and the encoded-model scope

Convert each archived binary64 coefficient, objective coefficient, finite bound and multiplier individually with Fraction.from_float (or equivalent exact binary decomposition). Perform products, summations, residual signs and comparisons in rational arithmetic. Do not compute a floating \(A^\top d\), row-bound sum, dot product or residual first and rationalize only its rounded result.

Use the actual saved sparse coefficients. Duplicate entries, if present, must have their actual encoded interpretation respected; source-level coefficients need not reproduce a rounded sparse assembly bit-for-bit. Verify dimensions, finite coefficients/objective, ordered bounds and finite column bounds before checking.

The resulting bound concerns the archived floating-coefficient LP interpreted exactly. For example, binary64 \(1/168\) is not the exact mathematical fraction \(1/168\). This does not break the certificate; it limits its claim. It is not an exact statement about uncertain physical measurements or a differently rounded model.

Save numerator/denominator strings for the final bound and residual-correction quantities. A displayed decimal may be approximate; round downward if presenting it as a strict numerical “at least” bound.

## 3. Optional tolerance-robust bound

If every finite row and column bound is moved outward by \(\tau\ge0\), the same projected \(d\) and exact \(q\) give

\[
\operatorname{LB}_\tau
=\operatorname{LB}
-\tau\left(\sum_i|d_i|+\sum_j|q_j|\right).
\]

This certifies the widened encoded LP. Evaluate the tolerance and all operations exactly as stored. The row and variable coordinates have different physical units, so this is a declared numerical tolerance box, not a uniform physical uncertainty model.

Do not clip this widened-model bound to zero using the original \(\epsilon\ge0\): widening the epsilon lower bound permits \(\epsilon\ge-\tau\). The original nonnegativity bound may still be combined with a certificate when discussing the original model, but the widened model has a different trivial bound.

An epsilon-zero identity vector passing only 1e-5 numerical checks can coexist with a tiny positive raw LB for the exact original model. However, a positive \(\operatorname{LB}_{10^{-5}}\) contradicts an epsilon-zero vector satisfying those same widened row and variable bounds. That contradiction would be a fatal model/checking error, not evidence of identity repair.

## 4. Primal candidates and operational implications

A finite candidate vector that passes residuals at 1e-5 supplies a **numerical fractional candidate objective**, not automatically an exact upper bound. Strict equality rows commonly have tiny nonzero rational residuals. An exact upper bound requires a point proven feasible for the precise certified model, or an explicit proven correction. Do not compute a certified optimality gap by subtracting the exact LB from a tolerance-only candidate objective.

A truly exact feasible fractional point would give a rigorous LP upper bound, but still no operational upper bound for a binary/network model. Rounding U/Y/Z is not a proof of feasibility.

Let \(\mathcal F_{\rm operational}\) be any binary/network repair formulation whose projection into these LP coordinates is contained in this same feasible region and uses the same objective, targets, nameplate scales, cap and input order. Then

\[
\epsilon^\star_{\rm operational}
\ge\epsilon^\star_{\rm LP}
\ge\operatorname{LB}.
\]

The subset relation must be checked, not inferred from a label. Adding integrality, native DC balances, branch limits or stricter boundary histories preserves the implication when all common data and constraints agree. Raising the cap, changing the mean metric, allowing shedding, or changing physical inputs need not preserve it.

Accordingly, a positive certified LB is a necessary operational repair amount under those assumptions. A positive fractional candidate epsilon does not show that any operational repair of that size exists. LP feasibility at epsilon one also does not guarantee binary/network feasibility.

## 5. Required implementation checks

- Exact case set: identity plus ordinary seeds 26092600–26092603, with the same archived service-cap matrices and cap; no outcome-based case selection.
- All 41 original means matched by generator UID, with one strictly positive finite native PMax scale per UID; no silently dropped zero-target units.
- Exactly one added epsilon column in [0,1], with cost one; exactly 82 correctly signed band rows; no old equality-mean rows remain active.
- Service-model submatrix/bounds retained identically, with no accidental extra fossil cap, mean row, DC row or binary integrality.
- Original source/target/scales, runner, protocol, objective, matrix, bounds and multipliers are hash-bound to the result before any checker claim.
- Lower-bound replay performs no optimization and recomputes the exact residual-box correction from archived arrays.
- Raw and projected row multipliers are separately preserved; projection counts and inadmissible bound sides are disclosed.
- Solver statuses, numerical primal residuals, exact LB, optional widened LB and any numerical gap are separate fields with precise labels.

No new prior-art claim follows from using this bound. It is a direct weak-duality/Lagrangian-box calculation; the scientific question is what repair it certifies in these fixed instances.

## 6. Implementation review

MEAN_REPAIR_PROTOCOL.md has been read and matches the mathematical requirements above. Its stronger provenance checks include native availability bounded by nameplate, source permutation replay, copied original mean-row coefficients and post-run hash checks. The prescribed single 60-second LP per case is a fixed acquisition rule; proof replay must add no optimization.

The runner's construction is correct: it verifies deletion of the 41 equality rows from the original archive, retains the service-cap submatrix and bounds, checks native UID/nameplate matching and cap support, copies the original mean-row coefficients, and appends 82 correctly signed rows and one epsilon column. Its exact checker forms q directly in rational arithmetic, selects the correct finite-box endpoint, and applies the unclamped widened-model correction. The nominal nonnegativity clamp is applied only to the nominal model.

The code contains one solver.run call per case and no retry/ray-recovery optimization. The completion record reports five calls. All five cases report a numerical Optimal status and a tolerance-verified fractional candidate; none is presented here as an exact optimum or a binary/network upper bound.

Reviewed SHA-256 bindings:

- Protocol: 46a5de8ce4654442230010ace68c204c03904e30709b2ee97be1b2ac670a4755.
- Runner: 1d3ab964494177c09110ae348e01ed10d69def9ea890555665548851b46c9328.
- Input manifest: 08061747e18efd70ffaf18ad8b69e2ef1ca7a417348251c2e8a0ee7ce1f7753f.
- Initial freeze: 2026-09-26 21:10:27 UTC; all-model freeze before the first solve: 21:12:22 UTC; completion: 21:14:51 UTC.

The independent replay checked the manifest binding, runner/protocol hashes, and each case's saved matrix, bounds, objective, original mean rows and mean inputs against the manifest. It read raw and projected duals, rebuilt q, selected a minimizing box vertex v, and evaluated the algebraically equivalent expression

\[
c^\top v+\sum_i d_i(b_i-A_i v)
\]

with exact rational arithmetic. Here b_i is the selected signed row endpoint. This independently reproduced each saved nominal bound, widened bound and both multiplier/residual norms exactly.

The following decimals are approximations; exact numerator/denominator records remain in each case's exact_lower_bound.json.

| Case | Nominal exact LB, decimal approximation | Widened exact LB, decimal approximation | Numerical candidate epsilon |
|---|---:|---:|---:|
| identity | 0 | -0.000010000000 | 0 |
| seed_26092600 | 0.015220960507 | 0.015215510111 | 0.015220960507 |
| seed_26092601 | 0.020048032575 | 0.020042539300 | 0.020048032575 |
| seed_26092602 | 0.015227588586 | 0.015221953960 | 0.015227588586 |
| seed_26092603 | 0.018081508386 | 0.018075365704 | 0.018081508386 |

All four ordinary cases therefore need a maximum normalized mean deviation of approximately 1.52–2.00% of nameplate in this relaxation; the positive lower bounds survive the specified numerical expansion. This is larger than the tested numerical-tolerance effect. Whether that mean-target displacement is operationally important is a separate question; this study reuses four July development cases and supplies no out-of-week validation.

Independent floating primal checks reproduced the passing verdicts. Maximum matrix/box residuals range from about 1.4e-12 to 2.4e-10. However, exact arithmetic found a nonzero equality residual in the first aggregate-balance row for every saved candidate. The four ordinary candidates also exceed the exact saved fossil cap by approximately 2.89e-11, 1.91e-11, 1.29e-11 and 3.35e-11 MWh, respectively. The identity candidate is about 1.00e-6 MWh below the cap.

These tiny residuals do not invalidate the explicitly tolerance-qualified numerical candidates. They do confirm why their objective values must not be treated as rigorous exact upper bounds, even when solver status is Optimal and the reported decimals nearly coincide with the certified lower bounds.

One reporting gap was sent to the root: the frozen runner tabulates fossil energy through a floating sparse dot product and lacks a separately named exact cap-residual field. The overall matrix check does include that row, so this is not a bound-validity failure. An append-only exact fossil-sum/cap-residual audit was requested from the artifact owner; the independent figures above already quantify it. The frozen source was not edited.

**Final judgment:** the exact lower-bound evidence passes this independent review for all five archived encoded LPs. No additional optimization was run. The inference to more constrained operational formulations remains a necessary lower bound under the subset conditions in Section 4, not a demonstrated feasible operational repair.
