# Prospective seasonal service-cap test: design recommendation

Prepared 2026-09-27 Dubai, before the proposed seasonal twin outcomes. This document is a design recommendation, not a report of executed cases and not an amendment to existing protocols. Freeze an execution protocol, source hashes, reference selection, cap formula, seeds, model construction and solver budgets before generating any target labels.

Read-only sources used: SEASONAL_REFERENCE_PROTOCOL.md, SERVICE_NETWORK_MIP_PROTOCOL.md, TRANSFER_PROTOCOL.md, LITERATURE_CERTIFICATES.md and KGRAM_PRIOR_ART.md in this directory. No source, result or existing protocol was modified. No solver or additional literature search was run.

**Recommendation:** use the first January, April and October weeks as three out-of-week tests; retain July as development. Generate two ordinary order twins and one constructive positive control per eligible held-out week. Audit every hourly network condition using permuted reference schedules. Then run one capped full-network LP per ordinary twin, followed by binary feasibility only when the LP does not supply a verified negative. This requires six planned LPs and at most six planned MIP calls.

## 1. Question and limits

The primary question is:

> After removing every individual-generator mean target, can a new ordering of the same complete hourly service packages still prevent binary DC-network operation under a fixed aggregate fossil-energy budget with at least 1% headroom over a verified reference?

The two members of a pair have the same multiset of complete hourly physical inputs, reference fossil-energy sum and fixed first/last 48 hours. They do not have the same time-stamped chronological demand trajectory: changing that ordering is the experimental intervention. These are synthetic ordering tests, not operating instructions or field experiments.

A certified rejection would establish order sensitivity for the stated model and budget without imposing the original 41 named-unit means. It would not establish a defect in physical service at every budget, an emissions or economic optimum, AC feasibility, contingency security, or insufficiency of exact higher-order factor statistics.

January, April and October are out of the development week, but share the RTS-GMLC Area 1 network, source revision and year 2020. This is out-of-week replication within one system; it is not a new-network or external-site validation. The six ordinary twins are nested within three weeks, not six independent seasonal samples.

## 2. Reference eligibility and a cap that does not depend on twin outcomes

Use only the final returned schedules from the four already frozen seasonal reference solves. Their native inputs, generator order, physical checks and protocol/source hashes must pass the requirements in SEASONAL_REFERENCE_PROTOCOL.md. Do not rerun references, choose a different incumbent from a later solve, substitute another week, or require a favorable reference MIP gap to enter the test.

For each month \(m\), define \(E_m\) as the exact rational sum of the stored binary64 dispatch values over the 23 native fossil thermal units and 168 one-hour intervals. Fuel membership is Coal, Oil or NG; exclude the sole nuclear thermal unit 121_NUCLEAR_1. Then fix

\[
B_m=\left\lceil \frac{101}{100} E_m\right\rceil\ {\rm MWh}.
\]

The ceiling is to a whole MWh, computed from that rational sum. It gives at least 1% headroom when \(E_m>0\), adds less than one MWh of rounding, and avoids an ambiguous floating-point cap convention. Archive the exact \(E_m\), integer \(B_m\), \(B_m-E_m\) and relative headroom. A zero-energy reference stays in the design with \(B_m=0\); report that percentage headroom is undefined.

This is a deterministic **reference-based fossil-energy benchmark cap**, not an independently prescribed policy cap and not a CO2 cap. Fossil MWh weights all 23 included units equally; different fuel emission factors are not represented.

A valid reference incumbent need not be optimal. Record its solver status, incumbent energy, lower/dual bound and gap. If \(E_m^\star\) is the unknown true reference optimum, the witness gives \(E_m^\star\le E_m\); the chosen cap may therefore be much looser than 1% above the true optimum. This can reduce rejection frequency but does not invalidate a rejection. Do not label a zero-objective feasibility run “fossil-energy optimal.”

No verified reference means NO_REFERENCE for that month. Its predeclared target cases remain listed as not run; do not replace them. A failed reference verification is not a negative transfer outcome. July's verified reference is an additional implementation/identity check only and never enters the held-out denominator.

## 3. Fixed sample and positive controls

Use the following seeds, in the listed order:

| Week | Ordinary twin seeds | Positive-control seed | Role |
|---|---|---|---|
| January, first 168 source hours | 26093100, 26093101 | 26100100 | Held-out week |
| April, first 168 source hours | 26093400, 26093401 | 26100400 | Held-out week |
| October, first 168 source hours | 26094000, 26094001 | 26101000 | Held-out week |
| July, first 168 source hours | None in this design | Identity reference only | Development/context |

Use numpy.random.Generator(numpy.random.PCG64(seed)). Every ordinary twin permutes exactly the zero-based source indices 48 through 119; indices 0–47 and 120–167 remain fixed. There is one draw per seed. Retain identity permutations, duplicates, low-change draws and unfavorable results without replacement.

Permute complete hourly packages jointly, including every nodal demand component, fixed rooftop-PV withdrawal, generator availability, fixed hydro dispatch and the reference dispatch/status/angle rows used for checking. Preserve native generator and network identities. Source timestamps remain provenance attached to the source-row mapping; destination order defines the synthetic chronology.

For a positive control, partition those 72 interior source rows by the exact full 24-bit reference thermal-commitment vector. Traverse classes in first-occurrence order and randomly permute source indices within each class using the single declared generator. Assign each permuted row back to that class's original destination positions. The complete U sequence is then unchanged pointwise. Compute startup/shutdown indicators from adjacent U rows; never permute old transition indicators.

Positive-control dispatch and angles move jointly with their physical hourly inputs. The fossil sum is unchanged, native on/on ramp limits are analytically redundant as documented in the reference protocol, and dwell validity follows from the unchanged status chronology. Nevertheless, verify all these facts directly. A control may equal identity; retain it and report its changed-hour count.

Before the first target solve, archive all nine intended case identifiers, generated orders, source bindings, input arrays, matrices, bounds, integrality masks and control checks for the available references. No seed, cap, unit subset, time limit or test week may change after observing target outcomes.

## 4. Controls that rule out an hourly/network explanation

Perform these audits before optimization:

1. **Identity positive:** each verified seasonal reference must satisfy its own full binary network model under \(B_m\), with zero individual-mean rows. Check July as well if its reference exists.
2. **Ordinary-twin static/network positive:** use the ordinary row permutation of reference P, U and angles. Each hour must pass dispatch bounds, thermal coupling, renewable availability, fixed hydro, nodal balance, angle bounds, branch ratings and independent DC reconstruction. The whole permuted dispatch must satisfy the cap because its fossil sum remains \(E_m\). Do not require this candidate to pass residence checks.
3. **Chronological positive control:** the commitment-class control must additionally pass transitions, startup/shutdown exclusivity, direct up/down runs and native on/on ramps. Its matrix check is against the same full model used for targets.
4. **Round-trip and schema checks:** inverse permutation restores every complete package; time/source mapping, generator fuel membership, network branch order, objective and mean-row absence are checked independently.

Thus every ordinary twin has a constructive hourly-network-feasible dispatch under the same cap when temporal residence restrictions are removed. A later temporal rejection cannot be explained merely by one hour having no static DC-network dispatch. Permuting a seed schedule and observing a bad dwell run is still not proof that no alternative schedule exists.

Use the established 1e-5 physical and matrix tolerance, save unrounded residuals, and compare the exact rational fossil sum with the frozen cap. Positive controls require both matrix verification and independent native checks. Any verified negative certificate contradicting a passing control is fatal: preserve the records and stop for diagnosis. A failed control construction also stops target execution for diagnosis; it is not silently excluded or replaced.

## 5. Smallest useful two-stage solve design

All models use the full 24-bus, 38-branch native DC network and all 41 decision generators. Retain all native dispatch conditions, fixed hydro, renewable curtailment bounds, source angles and line ratings, and the 24 thermal status/startup/shutdown structures. Remove every individual mean row. Add only the frozen aggregate fossil-energy upper bound.

Keep exactly the seasonal-reference boundary conventions: free mature initial statuses, zero initial startup/shutdown, within-horizon residence enforcement with truncation after hour 167, no cyclic closure and no new terminal requirement. Keeping 48-hour edge blocks fixed does not make the result invariant to other boundary conventions.

### Stage A: full continuous network relaxation

For all six ordinary twins, in month/seed order, run one continuous relaxation of the complete capped binary model: P and angles remain continuous, and U/Y/Z are relaxed to their stated bounds. Use a zero feasibility objective, HiGHS simplex, presolve off, one thread, seed zero and 30 seconds per call. Assert that this is exactly the binary model with integrality removed.

If the solver reports infeasible and supplies a ray, use the existing independent exact-rational certificate checker on the archived binary64 matrix, bounds and multipliers. Require positive separation after all finite bounds are relaxed outward by 1e-5 in their own units. Bind the certificate and row metadata to input/model hashes. Certificate checking may perform arithmetic, but may not hide an extra optimization or ray-recovery solve.

No valid certificate from that one solve means the result is not a certified negative, even if the numerical solver says Infeasible. Preserve the status and route the case to Stage B. A verified LP primal vector is only continuous feasibility.

### Stage B: fixed binary feasibility routing

Run one MIP for every ordinary twin not already rejected by a passing exact LP certificate. This routing is fixed in advance and seeks a stronger label; it does not select favorable cases. Use the same archived matrix/bounds, restore all 24 units' U/Y/Z integrality, zero objective, HiGHS presolve on, one thread, seed zero, relative gap target 1e-8 and 120 seconds. No warm start, commitment fixing, adaptive cap, retry or time extension.

A positive result requires a saved passing binary network witness, with all checks required by the seasonal reference protocol and exact fossil-sum recomputation. A solver's optimal status for the zero objective establishes no fossil minimization.

The three constructive controls need no optimization: their independently checked binary witnesses already establish their labels. Solving them again would spend time without strengthening that evidence.

Maximum solver allocation is 6×30 + 6×120 = 900 seconds. If a phase wall limit is needed, predeclare 20 minutes from the first LP, inclusive of postprocessing. Do not start a scheduled MIP with less than 125 seconds left; mark it NOT_RUN_BUDGET. Do not redistribute unused time into longer calls. Record generation, verification, proof checking and total wall time separately from solver time.

## 6. Outcome labels and what they establish

| Evidence | Allowed label and interpretation |
|---|---|
| Passing exact certificate for the outward-relaxed full LP | CERTIFIED_INFEASIBLE: the encoded full binary model cannot meet the cap; no MIP call needed. |
| Passing full binary network witness, regardless of MIP optimality/time-limit status | VERIFIED_FEASIBLE: an alternative chronological service schedule exists under the cap. |
| Verified LP witness, but no verified binary witness | LP_FEASIBLE / BINARY_UNKNOWN: no binary conclusion. |
| MIP reports Infeasible without an independently checked integer proof | NUMERICAL_MIP_NEGATIVE: useful solver evidence, reported separately from exact negatives. |
| LP infeasibility status without a valid ray; MIP timeout without a passing incumbent; verification failure; unrun call | UNKNOWN with the exact reason; not a positive or a certified negative. |
| Missing verified seasonal reference | NO_REFERENCE / NOT_RUN; not evidence for either hypothesis. |

An independently checked integer infeasibility proof would permit a stronger label, but implementing a new proof pipeline after outcomes is outside this minimal design.

A capped rejection plus the static/network control attributes the obstruction to chronological restrictions under the given cap. It does **not** show that the cap itself is indispensable: the same chronology might remain infeasible even without it. To claim an energy penalty or specifically budget-induced failure, a separate prospective uncapped binary witness is needed. Do not silently add an uncapped run only when it helps a desired narrative.

If such an uncapped witness exists under a separately frozen arm, and the capped model is certified infeasible, then its minimal required fossil energy exceeds \(B_m\), while the identity optimum is at most \(E_m\). This would establish a gap exceeding \(B_m-E_m\), without needing reference optimality. Without uncapped feasibility, report inability to meet the cap rather than a finite energy increase.

## 7. Transfer and practical novelty gates

Report all six intended ordinary outcomes, including duplicates, missing references and unknowns, and all control checks. Use week-level tables before pooled counts. A timeout-heavy result is inconclusive; all six verified positives mean no service-cap counterexample was found in the declared sample. Failure of original named-unit targets must not be substituted for this missing service result.

A minimal continuation gate for an operational order-effect claim is:

- all available constructive controls pass;
- at least one certified ordinary negative occurs in at least two of the three held-out weeks;
- each negative survives the fixed 1% incumbent-based headroom and the outward-tolerance certificate check;
- no result depends on reselecting weeks, budgets, seeds or solver limits.

This is a predeclared replication gate, not a significance test, publication criterion or proof of novelty. One held-out negative is a valid case study but weaker transfer evidence. The sample is too small to estimate a general rejection rate reliably.

The core design evaluates **phenomenon replication**, not transfer of a learned diagnostic. For a screening-method claim, add an explicitly frozen comparison before any target solve: the existing two-CC rule for 107_CC_1 and 118_CC_1, with its exact row-family definitions, evaluated on the same service-cap models without retuning. Report certified coverage relative to full LP negatives, undefined coverage when there are none, all positive-control errors, and total acquisition/solve/check cost. Learning the rule under named-unit means and testing under a pooled cap is a change of formulation as well as week; do not attribute every difference solely to seasonal generalization.

The prior-art memos already establish temporal aggregation, LP/IIS diagnosis, weighted conditional proof supports, exact checking and feasibility-driven refinement. This small study cannot make those methods new. A practical method contribution would still require a larger held-out comparison against direct LP followed by MIP, standard IIS/conditional deletion filtering, and an appropriate chronology-aware aggregation method, charging source access and proof-generation costs. A shorter certificate alone is not a speed, information or acquisition advantage.

Do not claim this experiment refutes Auer's Markov representative-period formulation or proves the k-gram theorem on native hourly data. Ordinary permutations preserve complete snapshot multisets, not all transition or longer-factor counts. Keep the theoretical construction, endogenous Markov pilot and this seasonal service test explicitly separate.

## 8. Audit package

Save the frozen protocol/hash and timestamp, native source revision and row mappings, reference provenance and optimization gaps, exact cap derivation, orders/seeds, all matrices/bounds/integrality/row metadata, witness and certificate files, full solver logs/options/version, independent residuals, and a complete scheduled-outcome table. Preserve prior failed and unknown experiments.

The resulting contribution, if the gate passes, is a transparent out-of-week service-cap stress test with constructive positives and certified negatives. The design itself is not novel, and passing it does not establish that the manuscript is ready for publication.
