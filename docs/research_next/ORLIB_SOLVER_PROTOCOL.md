# OR-LIB10 bounded solver extension

Prospective source-stage amendment, 2026-09-27. No scientific optimization is authorized by this file. The source-derived encoding and case contract remain exactly those in `ORLIB_TRANSFER_PROTOCOL.md`, SHA256 `4fb15c1525405561a7c9ce19f5d4bb01dde55ff014b70bd55173d067f929f04a`, and adapter `researchnext_orlib_uc.py`, SHA256 `e2b137f6a7ba23d1a9b12663ee1deee7bf2a3fffdd1f95d4718fb9ba37d17dc1`. The additional pinned top-level builder review establishes the unused mfg projection for this selected composition only. Runtime Julia/JuMP export identity remains **NOT_TESTED**.

This pilot concerns native encoded operating cost on an independent synthetic one-bus UC dataset. It is not an HOD, network, fuel, emissions, field-data or fossil-electricity replication. Both service variants, all targets, failed candidates and unknown outcomes must be retained. Old RTS artifacts remain unchanged.

## Fixed inputs, sequence and execution budget

The adapter's single reviewed preparation supplies six exact encoded models: identity, reverse source hours4–19 and left-rotate those hours by one, each with `native_penalized` and `hard_service`. Native curtailment is a real variable with its source penalty. The hard-service variant changes only its upper bounds to zero; no other row, cost, column bound or binary coordinate changes. There is no cap, RNG, new case, target tuning, warm start or retry.

Use precisely this sequence: identity native MIP then LP; identity hard-service MIP then LP; reverse native MIP then LP; reverse hard-service MIP then LP; rotate native MIP then LP; rotate hard-service MIP then LP. This is at most six MIP calls and six LP calls. Each MIP receives300 seconds, one thread, random seed0, presolve on and relative MIP gap1e-8. Each LP receives30 seconds, one thread, seed0, simplex and presolve off. The MIP retains all960 original binary coordinates, including the single startup-category variables. The LP relaxes all of them and is used only for objective lower bounds.

The allocation is2700 seconds including initial verification and subsequent exact arithmetic. It is a soft limit, with a remaining-time admission guard of call limit plus5 seconds after model construction. A small admission/call-ready record is written, then the guard is checked again immediately before `solver.run()`. A skipped call records `NOT_RUN`, zero calls and zero solver time. No absolute UTC deadline is imposed in this newly resumed research phase. Solver runtime limits and five-second padding do not promise a hard wall-clock bound; actual starts, ends and overruns are recorded. Shared-host runtimes are not benchmarks.

The reviewed runner imports installed NumPy/HiGHS only within the authorized run. No download, install, Julia execution or native optimizer is used. No new environment is created.

## Preparation and independent gate

`prepare-run` requires a trusted adapter-manifest hash and a fresh output directory. It reads every adapter-prepared file, checks exact lengths/hashes and the complete inventory, validates the pinned raw case and fourteen native source files, and rebuilds all six encodings with the reviewed adapter to require exact JSON equality. It checks960 binary columns per model, finite column boxes, and exact equality between service variants except the declared C upper bounds. It copies immutable input snapshots and the solver source/protocol; it rereads source inputs before closing. Runtime package version metadata and the fixed sequence/options are recorded without importing or calling an optimizer.

An independent prepared review must check the manifest, input transport, native schema/defaults/initial history, six models, full binary masks, objective, finite-box justification, C-only service restriction and exact expanded witness/lower-bound semantics. The external review JSON must contain `status: PASS_PREPARED_ORLIB`, `run_manifest_sha256`, `adapter_sha256` and `solver_sha256`. Its bytes and expected hash are separately supplied to `run-prepared`; this prospective schema does not claim such a review already exists. Root's separate explicit execution decision remains necessary after that gate.

The run revalidates all bound inputs before creating an exclusive `execution_started.json`, refuses a previous execution marker, and preserves failures/partial files. Source and prepared inputs cannot be silently altered or re-prepared after outcomes. A final check verifies all frozen bytes again. No automatic recovery run is provided.

A caller-owned ledger records the current model, call type and setup state. Immediately before the actual solver call it increments the attempted-call count and records its start; immediately after return it records the returned-call count and end. Exceptions during the call, solution/info retrieval, exact checks or later output writes are reported with this ledger in `execution_failure.json`, preserving the distinction between attempted and returned calls. Pre-call guard skips remain zero attempts. A completed run requires its result counts to equal both ledger totals. The bookkeeping-only source revision does not invalidate the archived earlier synthetic arithmetic checks; their original tested-source binding remains explicit.

## Upper witnesses and exact acceptance

The raw returned MIP column/row values and duals are archived before acceptance. A numeric solver status, objective or gap alone proves no feasible UC point. A candidate is considered only when the complete vector is finite and correctly sized, and all960 original binary coordinates lie within the exact binary64 value of1e-5 of0 or1. The sole declared transformation is nearest-integer rounding of every binary coordinate once. Every continuous coordinate retains its exact stored binary64 bytes; there is no redispatch, segment repair or continuous rounding.

The candidate must then pass both the adapter's exact sparse-matrix check and independent source-equation check, using exact `Fraction.from_float` arithmetic for coefficients and vector values. All binary coordinates must be exactly0 or1. Every finite row and column bound is widened uniformly by tau, where tau is `Fraction.from_float(1e-5)`; infinite row sides stay infinite. This mixed-unit numerical convention belongs to the explicit encoding and is not measurement uncertainty or an invariant under row rescaling. Native-style direct ramp/dwell/startup/segment/reserve/balance/cost checks all remain required.

An accepted exact objective is an upper bound for that expanded **full-binary** model. A nominal upper is also reported only if both exact checkers have zero nominal violations. Nominal and expanded claims stay separate. The saved segment objective must equal the independently calculated encoded objective. Canonical greedy segment cost is only a diagnostic, never replaces saved cost, and is null outside its nominal domain as specified by the adapter. A rejected or absent candidate yields no upper bound; the historical numeric status is still retained. An LP primal is never used as a UC upper witness.

## Exact lower bounds without a dual-feasibility assumption

Write the encoded LP as minimizing c^T x subject to l<=Ax<=u and finite column box L<=x<=U. Let d be the archived signed row multipliers. Reject nonfinite multipliers, and project d_i to zero whenever its sign would select a missing row side: d_i>0 with l_i absent, or d_i<0 with u_i absent. Archive raw and projected multipliers separately. Define, entirely in exact fractions of the stored binary64 inputs,

`beta = sum(d_i*l_i for d_i>0) + sum(d_i*u_i for d_i<0)`,

`q = c - A^T*d`,

`LB0 = beta + sum(q_j*L_j for q_j>=0) + sum(q_j*U_j for q_j<0)`.

For every nominal feasible vector, signed multiplication of the corresponding row sides and minimization of q over the finite box prove objective>=LB0. No stationarity tolerance or numerical solver bound is substituted for this proof. Under uniform expansion of all finite row/column bounds,

`LBtau = LB0 - tau*(sum(abs(d_i)) + sum(abs(q_j)))`.

The same expression is a valid lower bound on the expanded LP and hence its full-binary restriction. Store the exact stationarity residual, raw bound, slope, projected rows and all rational endpoints. A zero-dual box bound is also always derived after an executed LP; choose the maximum of this bound and the valid solver-dual bound separately for nominal and expanded models, as fixed before results. The expanded bound is never silently clipped at zero: even columns with nominally nonnegative bounds are expanded below zero. Numeric optimization status is retained, but the exact bound remains valid for arbitrary admitted d. If no LP call is allowed, leave its lower bound absent rather than adding a hidden call.

Synthetic source checks exercise both multiplier signs, small and large nonstationary duals, infinite-side projection and the expanded zero-dual value of negative tau. They read no scientific inputs, build no scientific models and call no optimizer.

## All signed target-minus-identity intervals

For each service variant independently, let [L_I,U_I] and [L_T,U_T] be exact bounds for the identity and target full-binary expanded encoded optimum. Accepted finite binary uppers establish nonempty feasible sets; finite boxes establish finite cost. When all four quantities exist, report the full signed interval `[L_T-U_I, U_T-L_I]` for optimum_target minus optimum_identity. Preserve negative or zero-crossing intervals. Retain all four target/variant records; absent upper/lower components yield explicit null intervals and `UNKNOWN_MISSING_FINITE_BRACKET` rather than inferred infeasibility or zero difference. A lower bound exceeding an accepted upper is fatal and preserves the audit trail.

No ratio, carbon claim, energy claim, equivalence of native/hard-service results or global optimality assertion follows merely from solver status. An incumbent and its lower bound may bracket an optimum without identifying it exactly. Independent post-run replay of raw-vector transport, all960 binaries, both exact checkers, signed dual arithmetic and all interval records is required before scientific publication.

## Commands after their separate gates

Source-only arithmetic fixtures (standard library only):

```text
python -I -S src/researchnext_orlib_solve.py self-test --report NEW_SYNTHETIC_REPORT.json
```

After source/protocol approval and explicit preparation authorization:

```text
python -I src/researchnext_orlib_solve.py prepare-run --input-root ADAPTER_PREPARED_DIRECTORY --expected-input-manifest TRUSTED_ADAPTER_MANIFEST_SHA256 --adapter src/researchnext_orlib_uc.py --solver-protocol docs/research_next/ORLIB_SOLVER_PROTOCOL.md --output NEW_SOLVER_PREPARED_DIRECTORY
```

After independent prepared PASS and explicit execution authorization:

```text
python -I src/researchnext_orlib_solve.py run-prepared --root SOLVER_PREPARED_DIRECTORY --expected-manifest TRUSTED_RUN_MANIFEST_SHA256 --review-report INDEPENDENT_PREPARED_REVIEW.json --expected-review-sha256 TRUSTED_REVIEW_SHA256
```

The preparation/run commands use the existing scientific environment. Only the synthetic arithmetic command uses `-S`, because real solver execution requires installed NumPy/HiGHS. This protocol is a prospective amendment; it does not assert any solve or scientific outcome.
