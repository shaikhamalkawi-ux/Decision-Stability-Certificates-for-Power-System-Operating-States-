# Prospective continuous named-unit mean-repair radius

Freeze the five declared cases before their new outcomes: identity and the existing ordinary July permutations with seeds 26092600, 26092601, 26092602 and 26092603, in that order. Use their immutable `results/research8h/service_cap` continuous LPs, preserving every original constraint, finite variable bound and the identical 23-fossil-unit energy cap, 180555.9189139999 MWh. The states and transitions remain continuous. There is aggregate balance but no DC network, binary requirement or new permutation/target/cap selection.

Append one scalar epsilon in [0,1], with objective minimize epsilon and zero cost on all existing variables. Read each of the 41 original named-unit mean equality rows from the corresponding frozen `results/temporal_information/lp_certificate` archive. If its archived row is a_i x = mu_i, append the two upper inequalities

```text
 a_i x - S_i epsilon <=  mu_i
-a_i x - S_i epsilon <= -mu_i.
```

Copy a_i and mu_i exactly from the archived binary64 coefficients and equality bounds. Do not recompute or retune the target means or replace the stored 1/168 coefficient. S_i is the generator's native `PMax MW` nameplate from the pinned portable RTS source, matched by exact UID and column order. Require all 41 S_i finite and strictly positive and verify all archived hourly availability caps are at most S_i. Report and stop before optimization on any mismatch rather than rescaling. The precheck confirms positive nameplates 12–713.5 MW and no hourly-cap excess.

Thus epsilon is the maximum absolute change in a named-unit mean divided by that unit's nameplate, not relative error divided by the original mean. For example epsilon 0.001 permits 0.1% of each nameplate in mean deviation. This is a continuous, aggregate-balance mean-repair radius under the same fossil service cap. It is not binary/network repair, measurement uncertainty, emissions sensitivity or a guarantee of physical implementability.

Reconstruct the correspondence between each service-cap model and its original model after mean-row deletion. Verify cap support and value, all original finite column bounds, unit order, target-row supports/coefficients, and source availability in the exact archived permutation. Save scales, targets, source-row mappings, model matrix/bounds/objective/row labels and source hashes for all five cases before the first solve. Bind the runner, this protocol, native source/model files, existing archive hashes and generated model hashes. Do not edit any existing artifact.

Run exactly one HiGHS LP per case, sequentially: simplex, presolve off, one thread, random seed zero, 60-second limit. No retries, extra optimization, option tuning, warm starts, adaptive case selection or changes to targets, scales or cap. Save solver version/options/status/timing/objective, raw returned primal and row/column dual vectors, and all outcomes. Identity is a positive control expected near epsilon zero; its existing witness is checked before solving with the unretuned archived coefficients. Tiny binary64 discrepancies do not license changing means or tolerances.

Check every returned primal against the full archived matrix and bounds at absolute tolerance 1e-5. Independently tabulate the 41 mean values/deviations using the archived rows, normalized shifts, fractional state count and fossil energy/cap residual. Compute exact rational mean-row values from the saved binary64 primal as an audit quantity. A passing numerical vector provides only a tolerance-qualified primal upper estimate for the radius, not a rigorous upper bound on the exact LP optimum unless exact feasibility has separately been proved. Preserve any negative epsilon or small residual rather than silently altering the raw solution; any displayed nonnegative upper estimate must be labelled as such.

For a rigorous lower bound without another solve, archive the raw row-dual d. Reject nonfinite entries. Explicitly form a projected candidate by zeroing d_i>0 when row lower bound is -infinity, or d_i<0 when row upper bound is +infinity; preserve the raw and projected vectors and projection counts. With l<=Ax<=u, L<=x<=U and objective c, compute exactly

```text
beta(d) = sum(d_i*l_i : d_i>0) + sum(d_i*u_i : d_i<0)
q       = c - A^T d
LB(d)   = beta(d) + sum(q_j*L_j : q_j>=0) + sum(q_j*U_j : q_j<0).
```

Every multiplication, sum and sign decision for q uses rational interpretations of the archived binary64 values (`Fraction.from_float`), including the objective and finite box bounds. This is a valid objective lower bound for any such d; it does not require exact dual stationarity, dual optimality, or an Optimal solver status. Preserve the raw LB; max(0,LB) is additionally valid for the nominal model because epsilon>=0. Report the exact numerator/denominator and the decimal approximation without calling it the exact minimum.

Also compute LB_relaxed = LB - tau*(sum(abs(d))+sum(abs(q))) with tau the exact binary64 value of 1e-5. It bounds the model after outward expansion of every finite row and variable-box bound by tau. Label this a mixed-units numerical-robustness bound, not physical uncertainty. Do not apply the nominal epsilon>=0 clamp to that expanded model, whose lower epsilon bound is -tau. A positive relaxed lower bound demonstrates that the need for mean relaxation survives this explicit numerical expansion.

Report all five outcomes, exact lower bounds and tolerance-qualified numerical primal upper estimates separately. Exact-mean infeasibility may coexist with a small repair radius; no qualitative threshold for practical materiality is selected after seeing outcomes. The outcome does not establish binary or DC-network feasibility at the reported epsilon. Check every bound source/model hash again after the run, and have a separate reviewer replay the bounds and primal evidence without optimization.
