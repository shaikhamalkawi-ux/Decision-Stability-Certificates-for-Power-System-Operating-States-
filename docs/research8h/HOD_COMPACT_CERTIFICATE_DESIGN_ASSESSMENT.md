# Design-only assessment: compact explanations for HOD negatives

**Recommendation: optional fixed-rule transfer, with a solver-free reuse screen first.** This is a modest explanatory addition, not the next primary novelty claim. Fresh-week replication and uncapped finite-energy bounds have higher evidential value. No computation, model generation or solver is authorized or performed by this note.

## Existing rules and what is already known

Read sources: LOCALITY_PROTOCOL.md, TRANSFER_PROTOCOL.md, SEASONAL_RULE_TRANSFER_PROTOCOL.md and the completed seasonal_rule_transfer/READOUT.md and coverage.json. The established July rules were already tested on the two original January full-network capped negatives: two_cc rejected 0/2; locality48 rejected 1/2 (seed26093101). The other three restricted models have independently exact-verified expanded continuous witnesses. These previous failures and successes must remain alongside any HOD extension.

Reuse these rules without changing units, hours or background:

- **two_cc:** retain transition, exclusivity and both dwell families only for 107_CC_1 and 118_CC_1. This gives 19985 rows, including 1336 temporal rows, with all 23016 columns/bounds unchanged. It is not a rule deleting only dwell rows: the other units' transition/exclusivity rows are also removed. Calling it a dwell-only ablation would be incorrect.
- **locality48:** retain all global transition/exclusivity rows; keep a complete minimum-up/down row only if every hour-indexed variable in its actual nonzero support lies in [60,107]. No shortened rolling sum or endpoint-only test. This gives 28689 rows, including 1023 minimum-up and 1001 minimum-down rows. It directly addresses a restricted set of dwell constraints, but is not an isolated 48-hour model.

Both retain all 18649 static/network/cap rows, including the full-week cap23195, and all original column bounds. The earlier source matrices and current HOD matrices share the same dimensions and model semantics; the new hourly bounds and package order must still be bound and checked explicitly. HOD negatives are seeds26093200 and26093201; neither rule is selected using their dense-ray support.

## Zero-optimizer candidate reuse before LPs

There are two deterministic proof-candidate routes, requiring exact verification on the target bounds rather than any solver:

1. Reuse the already certified seed26093101/locality48 multiplier vector. Match rows by original parent row identity/family/hour/UID, require coefficient equality and the same selected-row mask, and evaluate the exact separation against each HOD locality48 bound set. A prior certificate does not transfer automatically when RHS or boxes change. There is no previous January two_cc ray to reuse; its previous outcomes were admissions.
2. For each existing full HOD ray, set multipliers on rows excluded by each fixed rule to zero and retain the others verbatim. Recompute the entire exact signed-row plus finite-box separation, including uniform expansion. This can produce a valid restricted certificate but need not do so. Failure to separate is a failed candidate, not evidence of restricted-model feasibility.

Use the checker to test supplied candidates; do not silently repair them, retune a window, choose units from current support, or treat dropping terms as automatically sound. Candidate provenance must identify whether it came from the old January locality certificate or the new full HOD proof. Freeze the ordered candidate list and rules before arithmetic. These are zero-optimizer checks, not literally zero-cost computations or a sparse optimization algorithm.

## Smallest bounded LP follow-up if still useful

If root elects to run this extension, freeze exactly the 2 x 2 case/rule matrix before any restricted-model outcome. Order: seed26093200/two_cc, seed26093200/locality48, seed26093201/two_cc, seed26093201/locality48. Reuse a successfully verified exact candidate without another solve. Each remaining entry may receive one LP30, simplex/presolve off/thread1/seed0, zero objective, no retry or ray-recovery solve. Maximum configured solve time is 120 seconds, with a separately fixed soft phase and cutoff guard. This note does not authorize those calls.

Before the first check/solve, prove exact indexed row-subset equality, unchanged bounds/columns, complete static/network/cap retention, and fixed mask counts. Original full-binary identity and HOD-class control seed26100200 are already exact expanded positives. Row deletion preserves their feasibility; bind those points and completed reviews rather than solving controls. A contradictory negative control halts the arm. Do not infer nominal exact control membership from expanded membership.

For each entry, report: exact expanded negative certificate; exact expanded continuous point for the restricted model; or UNKNOWN. A continuous point does not reverse the already proved full-model negative or establish binary feasibility. Preserve all four entries even when a reuse certificate avoids an LP. Rule coverage has the fixed denominator of two known full HOD negatives and is explicitly post-label, same-week, changed-perturbation-family transfer.

## What would be learned, and what would not

A successful locality48 transfer shows that the HOD-preserving cap conflict already follows with only the fixed central dwell rows reinstated on the global background. A successful two_cc result shows sufficiency of that two-unit temporal subsystem together with every static/network/cap assumption. Neither identifies necessary units, a unique physical cause, a minimum row set or an irreducible infeasible subsystem. Failure of both rules is an informative limitation of previous explanations; do not search for replacements in this bounded arm.

Record retained temporal rows separately from the nonzero temporal multipliers in the resulting certificate. These rules contain hundreds/thousands of temporal rows and potentially dense global support; call them restricted explanations, not automatically small certificates. Minimum memory or raw information requirements cannot be inferred: the cap and many retained background rows depend on all168 hours, and globally retained transitions link across the locality boundary. Sparse Farkas/IIS methods are established prior art. Any successful four-entry extension strengthens a transparent evidence format and mechanism description, not methodological priority or external generalization.

**Stop criterion:** if no fixed candidate/LP gives an exact robust restricted negative, report that these two old rules did not explain the HOD negatives under the stated budget. If they do, retain the smallest successful *examined rule description* only as a display choice, while reporting both rules and every outcome; do not call it globally minimal. Further shrinking, new units/windows or new optimization objectives would require a new explicitly prospective design.
