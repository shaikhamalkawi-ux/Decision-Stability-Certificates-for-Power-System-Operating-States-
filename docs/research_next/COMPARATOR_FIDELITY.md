# Published chronology comparator: fidelity and observation contract

27 September 2026. Initial source-only assessment after the open-ended continuation. No author package import, installation, clustering, UC model construction, optimizer, or computation on the archived paired inputs was performed. Closed research8h/v3 artifacts were not changed. Companion metadata: `results/research_next/comparator_sources.json`.

## Decision

**Proceed to a bounded, reviewed adapter for an authentic author-preprocessing observation test. Do not claim an existing counterexample to Auer's method.** A lossless operational adapter for all 107 encoded coordinates is unnecessary for this first question: a declared projection into supported author inputs is sufficient, with the omissions and numerical conversions reported. Conversely, an arbitrary 107-column TSAM invocation must be labeled an adapted clustering baseline, not the publication's pipeline.

There are three different comparisons, which must not share a result label:

1. **Observation test on our fixed pairs:** does the actual author representation of a declared input projection distinguish the two inputs? This can be decided without UC optimization, though the author's k-medoids preprocessing itself uses an optimizer.
2. **Author-native end-to-end test:** reproduce the published reduced model and its intended reconstructed reference on a supported author case. This measures the author's question, with its own assumptions, and does not inherit our archived feasibility labels.
3. **Operational approximation test against our untouched reference:** preserve the native 48-hour dwell and all original reference constraints; explicitly declare every reduced-model approximation and verify any claimed operational schedule against that full reference. The approximation need not have identical physics. It must not silently redefine the reference.

The next useful step is (1), following adapter/source and environment gates. A future version of (3) needs a model-level protocol, not merely a data adapter. Lack of such a protocol is a scoped hold on optimization, not a reason to abandon comparison.

## Primary source and immutable code

The [Auer et al. v2 paper](https://arxiv.org/html/2510.18555v2), dated 15 July 2026, was inspected at Sections 3.1–3.3 and 4.1, with the operational-assessment definition checked in 4.3.1. It replaces predecessor boundary values by transition-weighted values and relaxes affected binary variables. Its Section 4.1 reference reconstructs the horizon using selected representative days; it deliberately removes input-aggregation error from the edge-handling comparison. That reference is not the original unclustered chronology. No losslessness or exact UC-feasibility guarantee is assumed here.

The paper-linked `research/MarkovTransition` **tag**, previously resolved to `ce97428aa225037dcbcd848889ef55f3b67c17ba`, and its InOutModule gitlink `8b1f53a75d152645e5ff8c7d5f417befaf316da5` are retained. Relevant immutable raw files were read again; previously recorded response-byte hashes for Markov.py, Utilities.py, CaseStudy.py and power.py matched, with additional helper/storage/environment hashes now recorded. Here “tag” denotes a Git tag, not a separate algorithm called TAG. No branch-main substitution was made. Line numbers below count physical source lines, including blank lines; web-rendered line numbers differ.

The [pinned environment](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/environment.yml) specifies Python 3.12.11, pandas 2.2.3, Pyomo 6.9.2, TSAM 2.3.9 and Gurobi 13.0.0. Our existing scientific environment is not automatically a reproduction of it. TSAM internals and solver tie behavior were not audited in this assessment; an attempted direct TSAM source URL did not return usable content. No license availability was assumed.

## What the actual route retains

The [pinned Utilities.py](https://raw.githubusercontent.com/IEE-TUGraz/InOutModule/8b1f53a75d152645e5ff8c7d5f417befaf316da5/Utilities.py), lines 101–623, has two distinct layers. Clustering uses demand and capacity-weighted VRES/inflow features, by default aggregated across buses, with technologies separate; `maxInvestment` normalization and Gurobi are defaults. It calls k-medoids with 24-hour periods and rescaling disabled. After selection, it copies **original medoid-day demand by bus, VRES profiles by generator, and inflows**, rather than retaining only the aggregate clustering features. It also writes occurrence weights and the hour-to-RP mapping Hindex. Therefore comparing only clustering features is incomplete. The actual merge can repeat a bus's demand across multiple technology/generator records before summing; the adapter must inspect the resulting feature table rather than assume it equals a simple physical load sum. Do not silently fix that implementation during replication. The advertised disaggregated route is not selected here.

The [pinned CaseStudy.py](https://raw.githubusercontent.com/IEE-TUGraz/InOutModule/8b1f53a75d152645e5ff8c7d5f417befaf316da5/CaseStudy.py), lines 845–883, extracts one RP label per day and counts directed transitions **including last day to first day**. It produces both row-normalized successor and column-normalized predecessor matrices. Construction also has unit-scaling and bus-merging options; the adapter must make these explicit. The existing `apply_representative_periods` call updates Hindex but not the cached transition matrices. The publication runner writes and reloads CaseStudy, which refreshes them. An isolated wrapper must likewise call the pinned transition routine on the new Hindex, or use an audited reload. Stale cached matrices are not an author observation.

For a one-scenario UC-only configuration without storage or other Hindex-dependent constraints, a proposed complete observation is

`O_UC = (selected full supported RP profiles, RP weights, within-RP durations, N, fixed model/configuration data)`.

Both probability matrices are determined by integer N under the stated circular convention; retain their actual floating values too to audit what the code consumed. Compare modulo all RP label permutations. R=3 has six possible permutations; bus/unit/technology labels and within-day positions cannot be permuted. Day IDs, provenance hour IDs and medoid source indices are not scientific distinguishing features by themselves.

This is **configuration-specific**, not a universal contract for LEGO. [storage.py](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/LEGO/modules/storage.py), lines 153–175, uses ordered moving-window counts derived from Hindex for long-duration storage. If these constraints are active, the observation must additionally retain the consumed window-count sequence, its positions/boundaries and initial/final storage rules. Hindex is also used for full-horizon reconstruction and dispatch evaluation. Those downstream tasks can distinguish inputs even if a UC-only reduced observation collides. A complete module-dependency audit is required before an equality claim.

## Dwell and boundary fidelity

The [pinned runner](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/research/MK/Markov.py), lines 390–422, clips MinUpTime and MinDownTime to the RP length **before** creating its full-hourly `Truth` object. Its ordinary 24-hour route would thus also give that internally generated reference a clipped 48-to-24 requirement. This is a reference mismatch for our question; it is not evidence that the paper hides the difference. Using the runner unchanged would not test our untouched native model.

Clipping can be a declared approximation in a reduced comparator, while an independently constructed full reference retains 48 hours. [thermalGen.py](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/LEGO/modules/thermalGen.py), lines 43–55, also relaxes early commitment/start/stop domains according to dwell lengths. These are method behavior, not a full binary witness. [LEGOUtilities.py](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/LEGO/LEGOUtilities.py), lines 57–103, supplies predecessor-weighted wrapped sums. This inspected route does not establish an arbitrary multi-RP 48-hour extension simply by disabling the clip. Neither clipping the reference nor inventing that extension is allowed under an unchanged-native claim.

Our free finite-horizon boundaries and the author's circular RP transition convention differ. Preserving 48 raw hours at both ends does not make them equivalent. This difference is harmless for a declared observation test, but material for a full operational comparison.

## What the HOD pairs preserve—and what they do not

Let X_t be the archived joint 107-coordinate package and X'_t its existing HOD permutation. The already defined construction preserves the multiset of X_t within every clock hour, the complete unconditioned multiset, and the first/last 48 raw packages. Static model data are shared. Any deterministic per-hour projection f applied identically to both inputs therefore also preserves its clock-conditioned multiset. This is a logical consequence of the permutation, not a new computed result.

| Information | Implication of the existing HOD construction |
|---|---|
| Same-hour joint values and all single-hour marginals/means | Preserved before any chronology-dependent preprocessing. |
| Raw first two and last two days | Preserved. |
| Complete interior 24-hour day trajectories | Not guaranteed preserved: different hour slots draw from different source days. |
| Adjacent-hour pairs, run lengths, multi-hour windows | Not guaranteed preserved. |
| Medoid choices, RP profiles, occurrence weights | Not guaranteed preserved: clustering sees daily trajectories. |
| Day-cluster transition counts/probabilities | Not guaranteed preserved. |
| LDES Hindex window counts | Not guaranteed preserved. |
| Fixed raw outer day implies same cluster label there | False in general: global re-clustering can change assignments or representatives. |

“Not guaranteed” is not an empirical assertion that a particular pair differs. Temporal_checker's separate reviewed baseline audit will examine raw daily and adjacent-hour observations. It will not execute Auer's clustering, and its outcomes must not be renamed author-method outcomes.

## Concrete first comparison proposal

Keep the previously specified R=3, 24-hour author-default route. Fix all six targets: 26093200/01, 26093210/11 and 26093220/21, paired with their respective January week identities. Retain the capped UNKNOWN case. Include each archived class-preserving control and one repeat identity per week to expose uncontrolled preprocessing/ties. Class-preserving controls need not have equal representations; only repeated identical inputs serve as determinism controls. No K/R sweep or replacement based on equality outcomes.

Before clustering, implement only a transparent schema adapter and fixtures. Map nodal net demand as the declared demand signal; map renewable availability to the documented capacity-factor/rating fields; map hydro's supplied time series as an inflow signal **without pretending that inflow preserves our mandatory-dispatch constraint**. Common ratings and identities are metadata. Exclude the independently rounded aggregate-net equation explicitly. Report every division/multiplication/scaling difference, missing/duplicated row and feature-selection multiplicity. A lossless round trip is required only for fields claimed lossless; a declared numerical projection is still a valid, narrower observation experiment. No dummy buses or hidden custom features.

Freeze the adapter's exact projection, author options, native-table schema, source/dependency hashes, normalization, solver settings and tie policy before any clustering. Preserve the actual feature table, selected full medoid tables, Hindex, freshly computed N/probabilities and static configuration. The representation-only wrapper must not build or solve the UC models. Its optimizer count includes k-medoids. An existing Gurobi installation/license may be checked without purchase; a backend change requires an explicit labeled implementation variant, not a silent substitution.

If repeated identity results disagree, or the returned features/assignments violate the declared contract, retain the attempt as unresolved and diagnose the concrete cause. Otherwise compare complete observations exactly modulo RP labels; report numeric differences separately. Equality of the declared projection's observations plus differing archived full-model labels establishes only a collision for that projection/comparator configuration. Inequality establishes that it distinguishes this pair, not accuracy, feasible schedule recovery, or speed advantage.

## Strongest alternative and novelty kill tests

[Merrick, Bistline and Blanford, author preprint v2](https://arxiv.org/html/2105.03707v2), Sections 3.4 and Appendix A.4, is the strongest inspected sufficiency comparison. Its storage-planning representation includes state weights, transition matrix and residence duration separately. Its sufficient lossless conditions require equal within-state demand/availability, deterministic predecessor/successor structure and equal residence lengths. It is not a minimality theorem, nor a general binary-UC guarantee. HOD snapshot equality supplies none of the omitted linkage conditions. The 2024 journal version was not body-read; equivalence with the 2021 preprint is not assumed.

The [official US-REGEN repository](https://github.com/epri-dev/US-REGEN) was checked at commit `5f0d2cca8d2eb2a9a20f3bf7c9b19394d75c9284`; its README specifies a GAMS/solver environment and separately distributed input data. A paper-specific standalone executable aggregation recipe was not established. Use the inspected theorem as a conceptual comparator now; do not manufacture an algorithm under Merrick's name. This bounded review does not prove that no such replication route exists.

Discriminating stop/kill criteria for proposed claims:

- If any complete author observation differs, that pair cannot support a claim that the author representation loses the relevant distinction. If all six differ, abandon that empirical collision claim for this corpus.
- If equality arises only after dropping a consumed feature, it is our truncated observation's collision, not the published method's.
- If the claim is merely that chronology, transition probabilities, or residence duration matter, the inspected prior art already establishes that direction. Auer and Merrick are novelty kills for that broad framing.
- If a future reduced-model failure vanishes against the correct reconstructed reference, attribute the result to input aggregation or the different reference question rather than to Markov boundary handling.
- If a claimed full binary dispatch exists only because the reference was clipped or boundary-relaxed, reject that operational claim. Conversely, a valid approximation can still be benchmarked honestly despite differing constraints.

The defensible opportunity is a precise, independently verified stress test with a faithful comparison and explicit failure attribution. This source assessment establishes a practical route to that comparison, not its outcome or methodological novelty.
