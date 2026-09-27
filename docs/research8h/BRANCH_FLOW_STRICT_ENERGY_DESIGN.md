# Design only: strict energy bounds in the flow-conserving variant

This prospective follow-up is separate from the closed branch-flow capped arm and from every old independently rounded angle model. It is a design for review, not authorization to prepare models, solve, reconstruct, or change a checker. The capped arm's strict identity/control positives and two capped negatives must first finish independent post-run review and close their inventory.

## Fixed question and cases

For the same January identity and ordinary HOD seeds 26093200 and 26093201, ask whether each distinct flow-conserving, uncapped binary model has a finite optimum and a rigorously positive optimal fossil-electricity penalty relative to the identity. Keep both ordinary cases regardless of failed reconstruction, missing lower bound, or an interval crossing zero. No new cases, integer search, cap choice, schedule search, or claim of formulation novelty is proposed.

Build exactly three full uncapped models by deleting only the single fossil-cap row from the just-closed full branch-flow models. Preserve every other sparse coefficient, row endpoint, box, original binary mask, native package, source-hour permutation, graph and objective. Thus each full model has 34512 rows, 29400 columns and 12096 binary U/Y/Z coordinates. Use the existing 23-fossil electricity objective, excluding nuclear. The old cap remains 23195 in its closed parent models; it is absent from these new models.

The identity upper bound reuses the closed strict rational identity point and its exact fossil-energy sum. Preparation must rebind that same point to the cap-deleted identity model and check exact membership there. It must not rerun its basis proposal or reoptimize its fixed schedule. The identity lower bound instead comes from a new globally relaxed LP with all original U/Y/Z variables free within their original boxes: this is necessary for a bound on the best binary identity schedule, rather than only the inherited schedule.

## Predetermined target schedules and proposals

Use only U/Y/Z from each old closed accepted point:

- `results/research8h/hour_of_day_uncapped/seed_26093200/mip/recovered_vector.npz`;
- `results/research8h/hour_of_day_uncapped/seed_26093201/mip/recovered_vector.npz`.

Bind these files, their original full-mask acceptance records and their native/source-hour provenance. Require all 12096 selected states to be exactly zero or one and canonical. The old accepted dispatch is not a strict witness for the new model. Reuse its schedule only. Compare the old native packages and permutations to the corresponding new parent case; no remapping or replacement is allowed.

For each target, substitute that fixed schedule in the new uncapped full model. Verify every constant row exactly, including all 16032 constant-state rows, and preserve every continuous coefficient and bound. Verify that the remaining rows separate into 168 blocks of 103 P/theta/flow coordinates and 110 rows. If a preparation assertion fails, retain the failure and do not silently choose another schedule. Minimize the same fossil objective in each fixed-schedule numerical proposal. A failed proposal or reconstructed point excludes no alternative schedule.

## Exactly five LP calls and one arithmetic phase

If separately approved, freeze all three full models, both fixed-schedule proposals, schedules, maps, source/checker/protocol and all input bindings before the first call. The fixed order is:

1. identity full continuous relaxation, 60 seconds;
2. target 26093200 full continuous relaxation, 60 seconds;
3. target 26093201 full continuous relaxation, 60 seconds;
4. target 26093200 fixed-schedule proposal, 60 seconds;
5. target 26093201 fixed-schedule proposal, 60 seconds.

Each uses the reviewed HiGHS 1.12 simplex settings, one thread, seed zero, presolve off and no warm start. There are zero MIPs, retries, alternate bases or conditional additional calls. Calls continue in the declared order after a numerical failure while the prospective guards permit. Compare the accepted solver matrix, endpoints and objective to each frozen model before its sole `run`. Preserve raw numerical points, row duals, basis, logs, statuses, times and truthful attempted-call flags, including post-call I/O failures. Row-dual extraction uses the returned solution and causes no new solve.

All five numerical calls precede one shared 900-second exact-arithmetic phase. The full execution phase is capped softly at 1800 seconds, with the absolute 04:00 UTC cutoff sampled before calls and between arithmetic steps. Each numerical call needs at least 65 seconds remaining in both the phase and UTC budgets, checked again after launch-decision I/O. As a conservative feasibility gate, recommend starting this arm only while at least 1500 seconds remain until 04:00 UTC (latest 03:35 UTC), after all preparation reviews. This allows the configured 300 numerical plus 900 arithmetic seconds and 300 seconds for loading/checking/I/O; soft-limit overshoots remain possible and must be reported. If reviews finish too late, retain the unexecuted design rather than shorten limits or omit a case.

At most 336 target hours are reconstructed, each once with the reviewed 8192-bit exact arithmetic guard, fixed HiGHS endpoint interpretation and deterministic Bareiss pivot rule. No identity-hour reconstruction is repeated. An unavailable basis, singular/inconsistent system, bit limit, infeasible candidate or phase limit is retained as an explicit unresolved hour. Every target retains a `NO_UPPER` status until all its hours and its full strict/native acceptance pass.

## Exact lower-bound certificates

For a full uncapped model with row bounds l<=Ax<=u, finite column boxes L<=x<=U, and objective c, any multiplier vector y with finite selected row endpoints gives

`beta(y) = sum_i y_i * (l_i if y_i>=0 else u_i)`

`r = c - A^T y`

`lower(y) = beta(y) + sum_j r_j * (L_j if r_j>=0 else U_j)`.

This is a lower bound on every feasible continuous point and therefore every binary point. It requires no numerical stationarity or trusted solver objective/bound. Reconstruct beta and every residual coefficient from the unchanged archived sparse matrix using exact binary64-to-rational conversion. Retain every residual and box contribution; no small coefficient is discarded. The model here is strict, at tau=0.

Freeze the finite candidates `zero, +raw, +sign-projected, -raw, -sign-projected`, where projection removes only entries selecting an infinite row endpoint. If no finite returned dual is available, evaluate the zero candidate alone. Archive every candidate, including rejected sign combinations, with model/objective/raw-dual hashes and lossless rational results. Select the largest verified exact lower bound in this fixed list, with candidate order breaking exact ties. This selection cannot invalidate the lower-bound property and is not a post-outcome extra solve. A weak valid bound is retained without tuning.

The reviewed stdlib NPZ kernel can load the models; the existing generic rational point checker can verify all rows/boxes/masks and calculate exact objective sums. The objective lower-bound formula is the already reviewed residual-plus-finite-box construction from the closed portable wrapper, but new orchestration must use strict tau=0 explicitly and bind the new variant's objective and cap-only deletion. No old objective lower bound is transferred across model encodings.

## Explicit uncapped native checker and strict acceptance

Do not call the existing capped variant-native checker and ignore its failed cap rule. Create a separate new uncapped checker, preserving the old checker bytes. Its physical checks must match the reviewed capped variant checker exactly except that the weekly fossil-cap rule is absent and reported as absent. The checker must verify the model has no cap row and all full original binary states remain constrained. Copy and compare the native-check body prospectively, or expose the difference in a new independently reviewed implementation; do not mutate the old helper.

The new checker retains exact native nodal sums and incidence, flow definitions/limits, availability and hydro rules, committed output, binary/canonical transitions, mature initial state and clipped residence, plus native on/on ramps using the rationalization of the existing binary64 hourly conversion. Full unchanged matrix/box checks retain angle bounds and the pin. This remains a DC model with exact archived coefficients, not exact physical measurements or AC/security feasibility.

Encode accepted full rational points without float conversion and bind their uncapped matrix/bounds/objective/mask. Require complete tau=0 membership and all uncapped native checks. The exact fossil sum supplies an upper bound U on the minimum of the full binary model, irrespective of numerical optimality. If the full check fails, archive the candidate and precise reason, but do not claim a finite upper bound.

## Interpretation, gates and missing evidence

For each case with a verified strict lower L and upper U, report `[L,U]`. Require exact L<=U. Any contradiction triggers a hard review stop. For target i and identity I, the exact optimal-energy penalty lies in `[L_i-U_I, U_i-L_I]`. Report a rigorously positive penalty only if the lower endpoint is strictly positive and both cases have strict finite uppers. If L_I>0, the relative interval is `[100*(L_i/U_I-1), 100*(U_i/L_I-1)]`; otherwise omit a finite percentage upper bound. Preserve crossing-zero intervals and `NO_UPPER` cases without replacing them. Neither a feasible point nor an interval is an optimum proof by itself.

The capped variant negatives alone do not establish finite uncapped cost. The missing evidence is strict uncapped target admission and an objective bound sufficient to exclude the identity's upper energy, not another capped infeasibility status. The proposed arm addresses that gap with five continuous solves and exact arithmetic, while reusing already declared schedules only. Plausible runtime is a few minutes of reconstruction based on the closed 168-hour arm, but no completion or positive outcome is assumed. Code review, full prepared archive review, separate execution GO and independent solver-free post-run replay remain required. All old model claims and denominators stay unchanged.
