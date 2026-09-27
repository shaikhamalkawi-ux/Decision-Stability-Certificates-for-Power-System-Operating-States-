# Independent theory review: finite common-decision refinement batch

27 September 2026. **The cut-transport mathematics and finite-batch scope pass, with the implementation obligations below.** This review covers `FINITE_COMMON_REFINEMENT_BATCH_PROPOSAL.md`, SHA256 `ee165cf64fe72d39d5daa8a9ff7e725b5930587a4a0218b156c36d8a05482cbf`. It is not a source/prepared-data gate or execution authorization. No scientific arrays, saved cut coefficients, control coordinates or solver outcomes were evaluated; no model, optimizer, recurrence or proof replay was run.

The companion sources read were `SCIENTIFIC_DECISION_CYCLE10.md` (`0d3401669aafe6353e9d2296ecf79bc994a7424e6807be32b6b15f1c90959aa4`), `COMMON_PHASE1_PROTOCOL.md` and `COMMON_NOMINEE_PHASE1_THEORY_REVIEW.md`. The initial Phase-I certificate still requires its separate independent admission; the parent's report of a positive margin is not substituted for that gate here.

Reviewer provenance: this memo is the independent `/root/find_deposit` theory/source reading. Child `/root/find_deposit/gb_docs` separately checked only the supplied symbolic rounding argument and returned the same actual-backend and state-box caveats; it did not read or replay scientific evidence. Its general caution that an arbitrary binary-valid cut need not hold for fractional controls does not weaken the stronger fractional-validity property proved for this specific inherited original-row construction.

## 1. Exact cut and outward binary64 transport

Let the inherited Phase-I construction supply the exact necessary inequality

`a · z >= b`,

where `z` contains all original shared state coordinates. Its necessary-condition proof uses the original expanded operational rows, finite continuous boxes and both prescribed tau norm losses. State variables remain explicit. Neither stationarity nor the solver's infeasibility status is the proof. The derivation applies to any state vector that has feasible expanded continuous recourse, including fractional states.

For a positive dyadic scale `s`, put `alpha=a/s`, `beta=b/s`. Let `bar_alpha` be the finite binary64 coefficients actually admitted for the new master row, and define each residual exactly by `e_j=bar_alpha_j-alpha_j`. For every `z` in `[0,1]^n`,

`e · z >= E := sum_j min(e_j,0)`.

Thus `alpha · z >= beta` implies `bar_alpha · z >= beta+E`. Any finite encoded lower endpoint `L <= beta+E` makes `bar_alpha · z >= L` an outward relaxation on that box, hence on all exact binary states. Every coefficient, including an exact nonzero coefficient that underflows to zero, contributes its exact residual. No threshold-based deletion or extra binary tau is needed. Downward conversion followed by one `nextafter` only when the initial finite conversion is too high is valid when exact comparison proves the final inequality; overflow/nonfinite conversion must fail admission.

**Actual backend readback must complete this implication.** If the solver changes or removes an entered coefficient, recording the change alone does not validate the previously computed right-hand side. Either require exact equality to the expected encoded row and fail on any change, or use the actual readback coefficients `tilde_alpha` and explicitly prove

`L_actual <= beta + sum_j min(tilde_alpha_j-alpha_j,0)`.

Also check the actual upper endpoint is positive infinity, that the original state-coordinate map is exact, and that there are no unexpected coordinates. Any allowed recomputation of the endpoint must be prospectively specified before preparation; no alternate scaling, threshold or iterative adjustment after a failed transport. The simplest fail-closed implementation requires the readback to match the intended row. This clarifies, rather than changes, the proposal's omission-or-failure requirement.

Require strict exact origin exclusion for **both** the original exact row and the admitted encoded row. The necessary row can be valid yet numerically too weak to make progress. A tiny exact gap is not a promise that backend feasibility tolerances will exclude the origin; a returned duplicate or inadmissible nominee terminates under the frozen rule rather than triggering tolerance tuning.

## 2. Fractional control and model scope

The inherited unrounded common fractional point must satisfy the **original exact necessary cut**. Its validity follows from its closed expanded-model membership and the same continuous-support derivation. It must not be rounded or repaired for this check.

The transport implication above is only proved on `[0,1]^n`. An expanded relaxation can allow state coordinates outside that box. Unless the archived fractional point is separately known to lie in `[0,1]^n`, do not require it to pass the transported binary-master row or treat failure of that row as a contradiction. This review does not evaluate its coordinates. An actual contradiction of the original exact cut is fatal. Extending transported-row validity to larger state boxes would require a different explicitly declared residual support calculation; it is unnecessary for exact binary nominations and is not an implicit amendment here.

The two nominal 23195 MWh cap endpoints, the uniform exact binary64 tau convention, the original expanded membership test and exact original bits retain their different roles. The cuts are necessary for the declared expanded operational model; they do not certify strict nominal membership. No tolerance is added to the new cut during exact nominee admission. A master point is a necessary-condition candidate, not a full UC witness. A final positive must satisfy the unchanged expanded original joint model and the inherited complete binary/native acceptance checks. Its claim concerns the same pair, caps and information timing, not small regret or the author's operational reference.

## 3. Finite execution contract to freeze

The eight-round/24-call upper bounds give finite termination without any convergence theorem. At every productive iteration the next exact cut rejects its originating nominee, which passed the earlier master. That is real exclusion of one previously admitted point; it neither proves a minimal cut nor makes the iterations independent cases. No exact global binary infeasibility claim follows from backend Infeasible, eight rejections, a timeout or a missing cut.

Before source/preparation admission, freeze these concrete details:

- The precise power-of-two scaling rule, all-zero coefficient case, finite/underflow/overflow behavior and exact endpoint/readback checks. A constant nonprogressing cut stops. A supposedly valid constant contradiction conflicts with the inherited feasible fractional control and fails admission.
- The exact raw-candidate admission convention. Preserve the already declared binary policy; do not introduce undocumented snapping, continuous repair or additional candidates. Compare full state values as well as the stored hash when enforcing duplicates.
- One actual-call ledger with attempted calls recorded immediately before each optimizer invocation, including failures after launch. The previously closed initial Phase-I is a prerequisite, outside the at-most-24 new calls and eight new nominations.
- The meaning of 2400 seconds: use a declared soft phase with remaining-time checks immediately before each call, or an enforceable owned-process deadline. Record loading/checking/closure time and any overrun. A sum of solver limits alone is not an overall wall-time guarantee. Missing remaining time terminates rather than launching another attempt.
- Every stop condition, including invalid/nonprogressing cut, exact-control contradiction, duplicate nomination, invalid candidate, resource failure and the final round. Preserve all partials, raw duals/vectors, actual readback, exact margins and UNKNOWNs. There is no automatic ninth round or alternate cut recipe.

Independent final replay must check every new exact claim and actual row implication, preserving the already closed premises by their bindings. It need not rerun the historical scientific computations or optimizer.

## 4. Scientific value and repetition risk

My preceding Cycle10 memo recommended exactly one updated nomination and one recourse test. The research lead has prospectively chosen **one batch of up to eight** nominations, before its new outcomes. This is an explicit change in the recommended search budget and algorithmic trajectory, not a claim that the two plans are identical. The earlier recommendation and this decision should both remain in the record.

Eight rounds are defensible as a single bounded classical feasibility-refinement search when each new round uses a valid new restriction and stops at the first null. That differs from rerunning the unchanged timeout with more time. Its useful discriminator is still a full common witness; each unsuccessful productive round adds only a pointwise exclusion. The batch can close the computational branch honestly as UNKNOWN even if all eight cuts are valid.

There is additional repetition risk: several cuts may encode the same hourly capacity mechanism, and counting them as separate empirical confirmations or a success rate would inflate the evidence. Report one adaptively refined trajectory on one already selected pair, its complete call/termination ledger and the final common-feasibility verdict. Do not infer information insufficiency, stronger transfer, generic convergence or novel Benders theory from its length. Stop after the declared batch regardless of available time. A publishable delimited conclusion can retain UNKNOWN with the already established observer collision and fixed-policy contrasts; it must not imply that a common action is absent.

The parent's later source-only inquiry about a common hourly cut template is outside the reviewed frozen proposal. If a valid template can be proved and seeded across predetermined world-hours, it may avoid rediscovering equivalent local constraints. That requires a **separate, before-run amendment and universal necessity proof**, exact transport/readback for every inserted row, and honest disclosure that its selection was motivated by the first cut. It is neither an already admitted seed nor a predeclared new positive benchmark. This review makes no claim about the actual 24-row support or its applicability at other hours.

**Disposition:** no algebraic blocker to the declared finite batch. Resolve the readback implication, original-versus-transported fractional-control distinction, deterministic encoding and timing/ledger conventions in the source/protocol before implementation is admitted. The separate initial-certificate, source, preparation, execution and post-run gates remain in force.
