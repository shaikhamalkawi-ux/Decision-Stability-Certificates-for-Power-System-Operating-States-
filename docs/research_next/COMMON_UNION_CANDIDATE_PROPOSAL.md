# A single deterministic common-schedule candidate

Design/theory only, 2026-09-27. No witness array has been decoded, candidate evaluated, model assembled, or optimizer called for this proposal. The ongoing frozen COMMON_SCIP call is unchanged. This is a classical schedule construction suggested by the newly independently accepted individual day321 witness, not a novelty claim or an automatic continuation of another arm.

## Candidate and source conditions

Use precisely the old first-January identity constructive witness at `results/research8h/hour_of_day/january_identity/constructive_vector.npz` and the newly accepted point at `results/research_next/day321_local_repair/run01/candidate_vector.npz`. The latter is root-verified as an expanded individual day321 positive; it does not itself supply a common commitment. Before any future construction, bind full digests from their closed provenance, both individual acceptance records, the complete original common-model archive, native specification and roster. Require identical unit/time coordinate interpretation and native minimum-up/down values. No alternative input witness or schedule is selected if a gate fails.

For each thermal unit separately, let a and b be its two exact binary U sequences on hours0,…,T−1, with T=168. Start with their pointwise union:

`w[t] = max(a[t], b[t])`.

Find the maximal zero runs of w. Fill a run with ones **only if** it has an on-hour immediately before and after it, and its integer length is strictly less than that unit's native minimum-down D. Initial and terminal off runs are retained. All qualifying runs are filled in one deterministic pass; filling one maximal off run cannot shorten or create another off run. Call the result u*. For each t≥1, set y*[t]=max(u*[t]−u*[t−1],0), z*[t]=max(u*[t−1]−u*[t],0); set y*[0]=z*[0]=0. Use this same complete U/Y/Z schedule in both worlds.

This construction only turns additional hours on. It does not permute an input schedule, change the chosen pair, alter either cap, or select an objective-driven best union. Record the union additions and gap-fill additions separately, unit by unit, together with every initial/terminal run left untouched. No such counts or schedule values have been evaluated in this design stage.

## Residence proposition under the actual boundary convention

Assume a and b satisfy the same per-unit native minimum-up M and minimum-down D, where an observed transition at t≥1 requires the new state through `min(T,t+length)`, the initial state is already mature, and no obligation extends beyond the horizon. These are the exact conventions in the pinned prior native-check function; M or D may be zero.

**Union preserves minimum-up.** If w rises at t≥1, both inputs were off at t−1 and at least one rises at t. That input must stay on over every required hour of its clipped M-hour interval, and hence so must w. A run that begins at hour0 inherits the mature-state convention and creates no initial startup obligation. Thus every observed startup in w satisfies the native rule.

**Filling the stated off runs preserves minimum-up.** Filling a complete interior zero run merges neighboring on runs. It removes intervening transitions and never creates a new startup at an earlier previously-off initial/terminal boundary. The merged run begins at the start of an existing on run and contains its entire required on interval. Minimum-up therefore remains satisfied.

**The filled sequence satisfies minimum-down.** Every remaining interior off run has length at least D. An initial off run has no in-horizon shutdown and is mature by convention. A terminal off run stays off through the horizon, satisfying the clipped requirement even when its length is less than D. No other off runs are created. Canonical y*/z* then satisfy the transition equations and never activate both at once. For D=0 no run is filled; the argument remains valid. All-on/all-off sequences and M or D exceeding the remaining horizon are covered by the same clipped rule.

The proposition is about **residence and canonical state transitions only**. It relies on both input schedules having passed those discrete tests exactly, not merely a numerical integrality tolerance. It does not establish feasibility of arbitrary additional state restrictions, time-varying output boxes, minimum generation, on/on ramps, hydro constraints, DC flows or the fossil caps. More on-hours may create precisely those difficulties; turning a unit on is not a monotonic physical-feasibility improvement.

## A bounded prospective LP, if root judges it useful

The new individual control makes this different from the earlier fractional diving restriction: it combines two complete independently accepted binary schedules, then repairs only a residence property with the proof above. It is a concrete cheap candidate, with no claim that it is optimal, minimal, likely feasible or exhaustive. If a common schedule has already been independently accepted from the ongoing SCIP arm, there is no need to execute this follow-up merely to fill time.

If authorized while the common question remains unresolved, freeze exactly this one u*/y*/z* candidate and verify its full discrete/native residence and original binary-box compatibility before a solver call. A failed discrete admission is retained without another construction. Copy the original joint matrix and row intervals unchanged; replace only each of the12,096 shared state-variable boxes by its exact candidate0/1 value. Keep the original full mask for final acceptance; the proposal solver can treat the fixed variables as continuous. Both worlds retain separate P/theta, all physical constraints and their original23,195MWh caps. This is a restriction of the original common problem, not a model relaxation or new energy target.

Propose one fixed60-second continuous HiGHS LP on that joint restriction, one thread, seed0, presolve on, zero feasibility objective, with a300-second soft phase and65-second start guard rechecked immediately before the sole call. Use the existing scientific environment; no warm start, alternate objective, additional schedule, separate per-world solve, retry or parameter tuning. These are proposed limits, not execution authorization. Root may review the source/protocol and frozen archive before deciding whether this single call is warranted.

For a returned point, require every raw fixed state to be within exact tau of its **prescribed** bit, set only those bits exactly, and preserve all continuous bytes. Replay the complete unchanged joint and both original world models with their full binary masks under `tau=Fraction.from_float(1e-5)`, plus both unchanged native checks. Verify exact equality to the entire prescribed schedule in both projections. No clipping, redispatch or transition repair after the LP is allowed.

Only the full expanded/native acceptance establishes a common commitment and therefore both individual feasibilities. It makes no nominal tau=0 assertion. An infeasible numerical LP, timeout or rejected point excludes no other shared schedule; the unrestricted common question remains UNKNOWN. Even an exact separator of this fixed restriction would exclude only this candidate. Preserve all failed admissions and outcomes and leave the ongoing/closed SCIP result untouched.

## Why the next step is bounded and what is missing

The residence argument does not require new scientific arithmetic, and candidate construction is a linear scan of24×168 state bits. Actual union size, compulsory output, cap headroom and dispatch feasibility remain uncomputed. The decisive missing evidence is one fully verified paired dispatch for this exact schedule. A single fixed-schedule LP can seek that evidence at much lower search cost than another unrestricted integer search, while its failure carries only the explicitly limited heuristic meaning above.
