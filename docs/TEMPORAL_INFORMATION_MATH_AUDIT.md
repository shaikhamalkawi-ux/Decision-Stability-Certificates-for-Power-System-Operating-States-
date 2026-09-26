# Mathematical audit of the paired-order experiment

Status: prospective design review, before inspection of new permutation outcomes. This note audits the existing residence-certificate implementation and the proposed experiment; it does not certify an implementation that has not yet been reviewed. No claim of methodological novelty is made here.

## The precise question and a valid positive result

Let an hourly package contain every time-varying exogenous input used by the selected model, together with the associated static dispatch witness. At minimum this includes nodal demand (and fixed rooftop-PV treatment), generator lower/upper availability, and any hourly line limits or other time-dependent restrictions. A permutation must act on the entire package, never on demand, availability, or generation independently.

The baseline is the verified, repaired July schedule, not the original static July schedule. Freeze its complete generator-energy vector and its numerical interpretation before constructing permutations. Under equal hourly weights a row permutation preserves every generator mean, the joint empirical distribution of the included snapshot variables, and all distribution-only functionals of that joint law. It generally does not preserve transitions, lag distributions, clock-hour associations, or physical plausibility of a weather sequence.

A baseline verified feasible under the declared network/commitment model, paired with a permuted instance proved infeasible even after dropping network constraints, establishes this limited result: the declared order-free joint empirical law and unit-energy totals do not determine chronological mean admission in this model. A failed replay of the permuted baseline dispatch is insufficient: another dispatch schedule with the same means might be feasible. The negative member therefore needs a valid necessary-condition contradiction or a complete infeasibility solve for the appropriate relaxation.

This is a synthetic counterexample experiment. It is not a causal field intervention, a frequency estimate for actual weather, evidence of universal operational failure, or a proof that a newly proposed statistic is minimally sufficient.

## Boundary conventions and the 24-hour-buffer issue

The existing recurrence agrees with the manuscript's weak boundary: initial status is free and already mature, no transition from an unknown pre-horizon status is imposed, and residence beyond the final observed hour is not required. Identical conventions must be used in the baseline check, permutation solves, necessary-condition propagation, and compact checker.

The archived July unit table contains minimum-down times of **48 hours** for `123_STEAM_3` and `121_NUCLEAR_1`; their minimum-up times are 24 hours. Therefore preserving 24 rows at either end does not place the modified interior farther from the boundary than every native residence time. It only preserves those edge rows. The design owner confirmed a change to **48 hours at each end before any paired-order code execution or outcomes**. This leaves 72 interior rows and supports the narrower statement that the buffer covers the maximum native residence duration. Even that is not a theorem of independence: weekly energy targets and balance-derived bounds couple distant hours, and interior/edge transitions remain part of the same problem.

Archive both the new synthetic position and original row identity. An original timestamp used as a provenance tag must not be presented as the new chronological time. State which time attributes are part of the distribution being claimed identical; arbitrary row permutations generally change clock-hour conditioning with respect to the synthetic position.

## Audit of the existing necessary-condition code

Reviewed `src/v8r1_rts_residence_certificate.py` and the residence conventions in `src/v8r1_rts_seasonal.py`.

`propagate` starts with valid coordinate bounds and tightens them using hourly aggregate balance, each generator's total energy, and the thermal off/on output gap. Each rule is a necessary condition. Its outward tolerances weaken the deductions. A bound fixed point is useful for strength, but exact convergence is not required for validity: any finite sequence of sound deductions remains sound. A 1,000-iteration stop must be reported as a stop, not silently described as a fixed point.

`reachability` stores status, residual residence obligation, and attainable online counts. At the first hour the residual is zero, consistent with a free mature initial status. A switch creates duration minus one subsequent obligations; no final maturity condition is imposed. This also handles residence durations zero and one. The independently exhaustive checks for horizons 1--9 and durations 0--4 support implementation correctness on those cases; they are not a mathematical proof for all horizons.

For a thermal unit with constant positive minimum and maximum output, any feasible online count must satisfy the unit-energy inequalities. Rejecting when the intersection of reachable counts and energy-compatible counts is empty is sound. Keep the complete count set: replacing it by its minimum and maximum can miss holes. A passed necessary condition means **not rejected**, never admitted.

The constant-output-bound assumption is checked in the existing main routine and must remain an explicit check for permuted inputs. Zero-minimum-output units need different count treatment. Network omission is valid for proving rejection because the no-network set contains the network-feasible set; its admission does not establish network admission.

## Compact certificate: an implementable independent checker

Use a small, declarative JSON record per rejected permutation. Include hashes of the canonical inputs, exact permutation, horizon and time step, model/boundary version, all tolerance values, selected unit identifier, native output/residence parameters, target energy, a list of forced-status facts, and the empty-intersection claim. Treat certificate-supplied numbers as claims to verify, not as trusted inputs.

A practical checker independent of the current bitset routine can:

1. Verify file hashes and the permutation bijection; verify preserved edge rows and equality of the full hourly-package multiset and energy vector.
2. Reconstruct the conservative necessary bounds directly from canonical input arrays. A separate implementation with documented outward numerical slack is preferable; importing the producer's `propagate` is a reproducibility check, not an independent implementation of that stage.
3. Verify each retained on/off fact against the reconstructed bound, including a recorded separation margin. Reject a fact whose margin does not clear the specified threshold.
4. Compute reachable counts using a different state representation: triples `(status, saturated_age, online_count)`, where the initial age is already mature, a stay increments age up to the current status's minimum duration, and a switch is permitted only from a mature state. No final maturity test is applied. Impose only the retained facts.
5. Recompute the outward energy-compatible integer counts from canonical unit parameters and energy. Accept the certificate only if their intersection with the independently computed reachable counts is empty.

This approach is compact in the certificate payload but may still read and process the full data. It should be described honestly as a compact explanation with independently checkable provenance, not as proof that only those observed hours are sufficient input.

For a particularly transparent core, a forced pattern on at `a`, off at `b`, and on at `c`, with `a < b < c`, is impossible if `c-a-1 < D`: the longest possible intervening off run is shorter than minimum down time `D`. The analogous off/on/off pattern contradicts minimum up time `U` when `c-a-1 < U`. Such a three-fact proof does not need the online-count recurrence after the facts themselves are established. Some valid rejections will require the energy budget and a larger core.

## Numerical meaning

The current defaults are power tolerance `1e-5 MW` and weekly energy tolerance `168e-5 MWh` for 168 one-hour periods. Generalized code should compute the latter from horizon and time step, not retain the literal 168. Preserve constant unit parameters from their authoritative decimal representation where practical.

Every certificate should distinguish physical quantities, algebraic tolerances, and integrality checks. For rejection, propagate conservative bounds and report forcing/energy separation margins. For a positive witness, report all residuals after binary rounding and verify network flow equations, line limits, hourly availability, fixed hydro, power/status linkage, residence, native ramps, balance, and target means independently of the optimization status.

Floating-point checks are numerically verified witnesses/certificates under the declared tolerances, not automatically formal exact-arithmetic proofs. A larger outward-tolerance sensitivity can show that a rejection is not a threshold accident. Formal certification would additionally require directed interval arithmetic or exact rational verification of every relevant derivation. Do not silently clip a baseline witness or edit its energy vector; any repair must be explicit and reverified.

## Certificate minimization and holdout

A deterministic greedy deletion of forced-status facts can yield an **inclusion-minimal** core: after the process, deleting any one remaining fact destroys the contradiction. It does not establish minimum cardinality, minimum memory, minimum number of raw measurements, or unique explanation. State whether the energy constraint and all original bounds remain fixed during minimization. A core's time span is an explanation span, not a proven required model memory.

With 16 seeded permutations, report all 16 outcomes, including unresolved solves and lack of a necessary-condition rejection. They share one week and are not independent systems or representative historical samples. Predeclare the seed generation, preserved blocks, solver budgets, and deterministic rule selecting cases for full MILP confirmation. Selecting an example after examining outcomes is legitimate illustration when disclosed; it cannot be called a prespecified test case.

The initial 16 permutations can be a development experiment. Once any certificate rule or tuning is chosen using them, lock that version before evaluating a separately seeded holdout, preferably also another verified feasible week. Soundness can be proved from valid mathematical deductions; holdout evaluates coverage and runtime, not logical soundness. A universal information-sufficiency claim would require a theorem and a substantially different experiment.

## Decision gates

- Proceed with an order-information counterexample claim only if a verified positive baseline and a valid negative permutation coexist under the same declared energy targets, units, tolerances, and boundary conventions.
- If permutations only violate direct replay but alternative schedules remain admitted, report sensitivity of that replay, not mean-admission impossibility.
- If the necessary-condition checker finds no contradiction and solves time out, the result is unresolved, not evidence for or against existence of a counterexample.
- If the baseline fails its independent check, stop interpretation and resolve that discrepancy before searching for negatives.
- If compact cores are found, report their actual size and dependencies. Leave minimal-information and novelty claims open.

## Implementation review and observed pilot results

Reviewed the subsequently implemented `src/temporal_information_pilot.py`, `src/check_temporal_core.py`, the frozen protocol, the complete 17-row summary (identity plus 16 permutations), the positive-witness residual report, and the first selected negative's complete solver termination record. This addendum records outcomes without changing seeds, buffers, target means, model, selection rule, or certificate procedure.

The paired construction is consistent with the design. A single row permutation is applied to availability, nodal net demand, and the witness dispatch/status package. Exact inverse restoration checks the complete matrix, and the complete target mean used by every selected solver remains the original repaired witness's mean. The first four permutations are selected irrespective of screening results. The no-network optimization contains all unit-level commitment variables and the declared balance/energy requirements; it is correctly treated as a relaxation of the network problem. No implementation defect invalidating these model comparisons was identified in this review.

The positive control has zero residence and binary violations. The recorded maximum nodal-balance residual is approximately `7.96e-12 MW`, with branch excess approximately `2.84e-14 MW`. Its independently evaluated constraints support a numerical network-feasible witness under the stated tolerance.

The first four selected permutations each terminate with HiGHS status `Infeasible` in approximately 2.94--3.44 seconds, below the fixed 60-second budgets. They are therefore four numerically solver-established negative members paired with the positive witness. The inspected first solver log reports complete infeasible termination, not a timeout or absence of an incumbent. This supports an order-information counterexample in the declared model. It remains numerical optimization evidence, not an independently checked exact-arithmetic infeasibility certificate.

The existing single-unit necessary-condition screen returns `UNKNOWN` for **all 16 permutations**. It consequently explains none of the four solver-confirmed rejections, and no compact core is produced. The other 12 permutations retain unresolved chronological admission because they were not selected for full solves. Their replay violations are not additional rejection evidence. This is a material negative result for the proposed compact-screen coverage, and must appear beside the successful paired-order result. It neither proves that compact certificates are impossible nor permits a minimum-memory claim.

The independent age-based checker passes 2,261 exhaustive/boundary comparisons and provides an independent implementation of residence/count logic. In this pilot it does not independently establish the four solver rejections, since no rejected status core reaches it. It also does not independently reconstruct bound propagation. The term "independently certified compact rejection" is therefore unsupported for these four cases.

The first inspected MIP terminates after its root node. That alone does not establish infeasibility of the original continuous relaxation: MIP presolve can exploit integrality. Any later LP/Farkas or alternative-formulation audit must be recorded as additional validation and use the same frozen instance. A subsequent stronger screen would be a new method and require a newly locked validation design; the existing held-out same-week cases should not be retroactively treated as unseen after being inspected.

## Additional continuous-relaxation certificate audit

The subsequent `src/temporal_lp_certificate.py` experiment independently assembles the continuous relaxation for identity and the same first four selected permutations. Its development is explicitly post-pilot. The identity's known binary witness passes the new matrix check, and the identity LP also returns a verified continuous point. The four permuted continuous models are infeasible, strengthening their original mixed-integer results. This does not alter the initial screen's four missed rejections.

The Farkas sign convention and bound handling are correct. For a signed row multiplier `y`, a positive component multiplies the lower row bound and a negative component multiplies the upper row bound, yielding a necessary lower bound `b` on `c x`, where `c = y^T A`. For each component of `c`, the variable-box maximum chooses its upper bound when positive and lower bound when negative. Consequently `b > max_box(c x)` is a valid contradiction. The exact outward relaxation deduction is also correct: expanding every finite row bound and each variable bound by `epsilon` decreases the separation by `epsilon * (sum |y| + sum |c|)`.

Raw solver rays contain tiny multipliers with inadmissible signs on one-sided rows. The implementation does not simply declare those entries exact zeros: it creates a distinct candidate by setting inadmissible entries to zero and recomputes the complete rational separation. This is valid because any candidate multiplier satisfying the exact inequality is a certificate, irrespective of how it was obtained. Raw and projected candidates, both orientations, and projection magnitudes are retained. Sign projection alone would not validate a ray without that recomputation.

For an independent check, the reviewer used a separately written, read-only halfspace-summation calculation without importing the producer's certificate checker. Each selected row was converted to an upper halfspace with a nonnegative multiplier. Variable-bound halfspaces then canceled every remaining coefficient. For all four cases the exact result was `0 <= a strictly negative rational`, including after the declared `1e-5` outward expansion. The calculation verified the archived matrix/bound hashes against their result records and reproduced every saved exact separation numerator and denominator.

| Permutation seed | Selected row terms | Variable-bound terms after combination | Largest uniform outward bound expansion retaining this certificate, approximately |
| --- | ---: | ---: | ---: |
| 26092600 | 949 | 8170 | 0.019194749 |
| 26092601 | 656 | 7531 | 0.022316938 |
| 26092602 | 1017 | 7903 | 0.015631071 |
| 26092603 | 908 | 7906 | 0.020676709 |

These expansion values use each bound's own units and the fixed archived row scaling. They are not MW reserve requirements, uncertainty radii for the physical system, or invariant distances. They cover outward changes in bounds with matrix coefficients fixed, not arbitrary changes in coefficients, topology, residence times, or measurements.

The negative certificates are exact for the rational numbers represented by the archived binary64 coefficients, bounds, and multipliers. They are stronger than a solver-status-only report and can be replayed without an optimizer. They are not proofs about unrounded original physical data. Their hundreds of row terms and thousands of variable-bound terms also do not establish a minimum-size explanation or short-memory model.

The executed LP records use a 45-second budget, while the prospective LP document initially stated 60 seconds. This reporting discrepancy was flagged to the design owner for a transparent execution note; it does not change any completed proof, since all five solves finish well below either budget. The mathematical audit must not rewrite the historical pilot selection or claim that this post-pilot method was evaluated on previously unseen cases.

The separate strict-equivalence extension records four infeasible grouped-energy models, retaining all 41 dispatch coordinates and 24 physical thermal commitment processes while reducing energy constraints to 26 groups. This supports the bounded conclusion that these four rejections survive the tested equivalent-unit pooling. The exact rational certificates audited above concern the individual-energy LP models; do not silently transfer those specific certificate files to the grouped models. Likewise, any one-to-five-atom explanations recovered from the earlier known corpus are separate from these four coupled-instance certificates and do not establish external generalization.
