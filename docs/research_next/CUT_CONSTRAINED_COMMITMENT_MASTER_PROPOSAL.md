# One compact commitment master and one conditional recourse test

27 September2026. **Source/theory proposal only: no new scientific arrays, row coefficients, model, DP, candidate, optimizer or cut value have been evaluated.** Recommend one classical necessary-condition commitment master to nominate at most one new common schedule, followed by at most one fixed-common redispatch LP. Do not extend the full-MIP time limits or retune either failed individual schedule.

## Why this step rather than a larger temporal DP

The two individual original schedules fail transfer in opposite directions. The union and all binary supersets are excluded, but these facts do not exclude a third commitment. The original joint continuous model is feasible. The complete hourly cover floor is below the cap, and the selected-three residence bound has exactly zero improvement. These are closed results, not evidence that all temporal bounds must fail.

A two-hour free-boundary residence block allows every binary on/off pair, so it cannot by itself capture a prohibited short on/off run. Three-hour or longer all-unit covers can capture such runs, but a direct exact DP must retain multiple hourly capacity coordinates (and potentially minimum-output coordinates for the capped energy objective). No small complete state/frontier bound has been established for this archive. A guarded partial table supplies no universal certificate. Increasing the selected-unit set after a null would be a new tuning decision without demonstrated payoff.

The recommended master instead preserves **all** original binary residence/transition constraints and both existing exact energy cuts while omitting spatial dispatch. It seeks the positive discriminator directly: one common schedule with separately verified dispatches. It is a materially smaller necessary-condition search, not another invocation of the original33936-column network MIP. There is no guarantee that the master will be feasible or supply a useful candidate.

## Fixed master variables and original temporal rows

Retain the original12096 U/Y/Z binary coordinates, including nuclear. There are no nonthermal binary coordinates to remove. Do not claim a reduction based on such nonexistent states. Keeping the fixed initial Y0/Z0 columns is harmless and avoids a new reconstruction/projection theorem. All statuses remain free within their actual original boxes; no LP, individual or union schedule bit is fixed and no warm start is used.

Copy the original state-only rows from one world only after exact byte/coordinate comparison proves they duplicate the other world's rows. The earlier admission counted16032 per world; this is an expected archive count, not permission to discard a mismatch. Retain original coefficient values, endpoints, initial boxes, mature free initial U and clipped-terminal semantics. Future admission must verify that every retained discrete row has integral coefficients/endpoints: for exact bits and tau<1 its uniformly expanded relation is equivalent to the nominal discrete relation. Any unsupported row, roster or boundary mismatch stops preparation instead of changing the construction.

Add336 continuous auxiliary fossil-output floor variables `F_it`, two worlds by168hours. These are master necessities, not individual dispatches. Keep both existing82-term inequalities `alpha_i+c_i U<=B+tau`, with their already verified exact rational coefficients and no extra tau. No cut refitting, new support search or inferred symmetry is included.

## Necessary hourly and weekly relations

Use the actual original23 fossil units F, the one nuclear unit N and17 nonthermal generators R; verify this partition against native fuel labels and both original ordered rosters. Let `a_j,b_j` be the exact admitted thermal PMin/PMax coefficients and `l_it` the aggregate lower endpoint. Let `ub_irt` and `lb_ift` be the actual nonthermal upper and fossil lower column endpoints. All formulas below are exact rational interpretations of archived binary64 data, with `tau=Fraction.from_float(1e-5)`.

Define `rho_it=l_it-sum_(r in R) ub_irt-19*tau`. The19 deductions consist of one aggregate expansion,17 nonthermal upper-box expansions and one nuclear thermal-upper-row expansion. Summing these original implications gives

`sum_(f in F) P_ift >= rho_it-b_N*U_Nt`.

Original fossil thermal rows separately give `sum_f P_ift >= sum_f a_f*U_ft-23*tau` and `sum_f P_ift <= sum_f b_f*U_ft+23*tau`. Therefore the master retains

```text
F_it >= rho_it - b_N*U_Nt
F_it >= sum_f a_f*U_ft - 23*tau
F_it <= sum_f b_f*U_ft + 23*tau
sum_t F_it <= 23195 + tau       for each world i
```

Use the valid finite auxiliary box `sum_f(lb_ift-tau) <= F_it <= sum_f b_f+23*tau`. A full original common solution lifts to these variables by taking its actual fossil output sum. Hence every master constraint is necessary; dropping individual dispatch, network, ramps and tighter availability enlarges the feasible set. The nuclear commitment is retained in the conditional lower bound, rather than granting nuclear output when its master status is off.

For an explicit shared hourly integer-capacity row, the same relations imply

`sum_(j in F union {N}) b_j*U_jt >= max_i rho_it-23*tau`.

If every b_j is an integer as prospectively admitted, the left side is integral on binary states. Use the exact ceiling of the right side (or its maximum with zero since capacities are nonnegative). The total42*tau loss is one aggregate plus17 nonthermal boxes plus24 thermal upper rows. A noninteger or changing coefficient tuple is unsupported for this first formulation; do not silently round capacity coefficients. This integer-ceiling step need not be valid for the old fractional joint point and is not used to relabel it.

These relations yield an expected master of12432 columns and17212 rows:16032 temporal rows,168 shared capacity rows,2 inherited cuts,1008 hourly F relations and2 weekly caps. Those are prospective structural counts, not an assembled model. The336 finite F boxes are additional endpoint constraints. The inherited cuts and the conditional nuclear/energy floors prevent the master from proposing an arbitrary capacity-only schedule with unaccounted weekly fossil output.

## One finite candidate route

If separately authorized, freeze all original inputs, derived-row rational provenance, exact source/options, two inherited cuts and one zero-feasibility objective before execution. Use the already available numerical SCIP backend, not a new installation or proof-capability claim. Propose one120-second master MIP, one thread, fixed seed0 and first-feasible stopping, with no warm start or repeated candidate. Read back every original/derived row and box before the call. A360-second phase with125-second master and65-second redispatch start guards is the proposed total budget. Do not adapt the selected units, coefficients, objective, caps or solver settings after observing a result.

Save the raw master vector and only consider the first solver-supplied incumbent. Restore a state solely to its unique0/1 value within exact tau, otherwise reject. Verify all original state-only rows/boxes, both inherited cuts and integer-capacity necessities exactly. For admission, discard the artificial solver F values and compute the exact smallest permitted F for those fixed bits as the maximum of the three stated lower bounds; require its upper/weekly bounds. This is a prospective deterministic check of the nominated schedule, not another candidate or dispatch repair. Preserve the raw auxiliary values for diagnosis. A rejected or absent incumbent ends this arm with common UNKNOWN; no second master or candidate is generated.

Only one admitted full state block permits one60-second HiGHS joint redispatch LP on the unchanged original69362-row/33936-column common model, all12096 binaries fixed exactly. Capture the nominated bits/fixed bounds before that call. Cache sparse backend arrays once for complete readback. Keep both original caps, private P/theta, all network/native rows and zero objective. No per-world extra solve, ray/IIS retrieval, new cut generation, polishing, relaxation of free binaries or fallback is planned.

A returned LP point must preserve continuous bytes, restore only the prescribed bits within exact tau, and pass the original complete joint and both world matrices with full masks plus separate native checks. Only this supplies a common positive under the expanded convention. All stages require prospective source/prepared gates and independent post-run verification. No scientific operation is authorized by this proposal itself.

## Conclusions available from each outcome

An exact accepted composite proves a common commitment exists and resolves the pair's existence question positively. It also implies both individual worlds are feasible, while leaving the two historical fixed-schedule rejections valid.

A master numerical infeasibility/timeout without an independently checkable integer proof is UNKNOWN, despite the master being a necessary relaxation. A master-feasible schedule alone is not a network witness. A failed fixed redispatch rejects no other master schedule; without an exact certificate it does not even supply an exact expanded rejection of that candidate. Preserve one candidate and all nulls. No optimum, regret bound, completeness, physical-cause or minimum-information claim follows.

The alternative of a complete multi-hour capacity DP remains mathematically possible but lacks a demonstrated manageable complete certificate here. This proposal recommends only the above single master/recourse route, not both experiments or a sweep.

## Classical attribution and reading scope

This is a Benders-style necessary-cut master with continuous recourse, not a new decomposition method. Existing inspected evidence already covers UC feasibility-oracle/master cuts: Guo et al., *Contingency-Constrained Unit Commitment With Intervening Time for System Adjustments*, DOI10.1109/TPWRS.2016.2612680 (existing ledger L10, relevant SectionIII); and Bertsimas et al., *Adaptive Robust Optimization for the Security Constrained Unit Commitment Problem*, DOI10.1109/TPWRS.2012.2205021 (existing selected §§II–IV reading). Their operational/reference distinctions remain as documented in `CERTIFICATE_ABSTRACTION_PRIOR_ART_PREFLIGHT.md`; no claim is made that either supplies the exact hard-service oracle used here. The Benders1962 historical entry was metadata/indexed-introduction reading only. `SINGLE_UNIT_DP_PRIOR_ART.md` already identifies classical dwell-state/path formulations.

This proposal adds no paper reading or literature-count claim. Its scientific purpose is one bounded attempt to resolve the existing common-schedule question using already established methods and exact admission, not to turn the earlier failed candidates into a general impossibility theorem.
