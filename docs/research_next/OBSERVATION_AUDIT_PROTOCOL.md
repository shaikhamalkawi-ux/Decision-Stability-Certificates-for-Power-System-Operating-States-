# Prospective exact observation audit of six existing HOD pairs

This is additive work after protected Git21 (`d0c4be05899b70797902f191f0062ac898ea7137`). It preserves all prior source, results, labels and deliveries. Initial authorization is source/protocol drafting and focused synthetic fixtures only. Preparation and the single actual audit require separate parent review gates. No optimizer, clustering, installed package, UC witness/certificate replay or published-method execution is part of this protocol.

## Question and fixed denominator

Do several explicitly defined observations distinguish the already known HOD-preserving paired inputs? A distinction is useful evidence about observation scope. It is not an error, infeasibility, accuracy or runtime result for a representative-period method. Outcomes and UC labels are already known, so this is a post-label diagnostic, not fresh validation or a novelty test.

The six ordinary comparisons are fixed before new calculations:

| Week | Archived identity | Ordinary targets | Class control |
|---|---|---|---|
| January1 | `results/research8h/hour_of_day/january_identity` | 26093200,26093201 | 26100200 |
| January2 | `results/research8h/fresh_january_weeks/targets/week_2_identity` | 26093210,26093211 | 26100210 |
| January3 | `results/research8h/fresh_january_weeks/targets/week_3_identity` | 26093220,26093221 | 26100220 |

Retain all six, including target26093211's archived binary UNKNOWN, duplicate draws and null observations. Each week also supplies its fixed class-control comparison and an identity self-comparison, outside the ordinary denominator: twelve comparison roles total. No additional seed, target replacement, metric sweep or comparison selected by an outcome is allowed.

## Exact input and provenance contract

Each168-hour input row has exactly107ordered physical numeric coordinates:41`pmin`,41`pmax`,one independently archived aggregate`net`,and24`nodal`entries. Generator and bus order come from the archived model metadata and must agree within each week. Do not reconstruct aggregate net from the nodal sum, drop fixed hydro lower bounds, reduce to marginal features, or omit a component presumed redundant.

`rows`, `source_hour`, CSV source indices and RNG data are provenance, not observation coordinates. U/Y/Z, dispatch, certificates and feasibility labels are not clustering or observation features. The labels are merely retained context in the final table. Do not use time-stamp IDs as a hidden distinguisher.

Preparation binds selected native arrays, model metadata/matrix/bounds/full masks/labels, permutation and preservation records, constructive-control records, old outcome ledgers, the two old preparation manifests, this source/protocol and the pinned standard-library NPZ reader. Selected preparation artifacts must match their old manifest entries. Preparation hashes bytes only; no observations are evaluated before the run gate.

At execution, validate all NPZ keys/shapes/dtypes, finite physical values, unique unit/bus identities,168source positions and the complete107coordinates. Verify the actual permutation is a bijection, preserves `t mod24`, fixes hours0:48and120:168, and agrees with every source-index representation. Reordering and inverse-reordering every physical component must be bitwise exact, including signed zero. Identity source rows must be the fixed native ranges0:168,168:336or336:504.

Check common coefficient matrices and full masks within each week. Check column bounds follow the P-hour package permutation while other column bounds stay fixed, and row bounds follow the corresponding hour/family/unit key; time-independent row bounds and cap remain unchanged. Row metadata and time-invariant model metadata must agree. This links the observation to the archived model inputs without solving or repeating a primal/dual certificate. Existing static/native/positive-control admission is inherited evidence, not newly established feasibility.

## Three declared observations

Numeric equality means exact equality of finite archived binary64 values, with+0and-0as the same number. No rounding, tolerance or hash comparison establishes observation equality. For a lossless portable description encode each numeric value with canonical`float.hex`, normalizing zero to+0. Keep separate bitwise provenance diagnostics. Use a shared per-week dictionary sorted lexicographically by the entire107-coordinate content; dictionary IDs stand for values, never source-hour IDs.

1. **HOD joint snapshots plus fixed edges:** for each h=0,...,23, the multiset of complete rows at t mod24=h, together with the ordered first48and last48rows. Retain multiplicities. This is the established shared observation and must be independently confirmed; a failure is an input/provenance error, not a new counterexample.
2. **Whole contiguous-day multiset:** the multiset of seven ordered24-by107day profiles, formed at the archived week boundaries. Day occurrence order is discarded; order inside each day is retained. The fixed edge context remains common. This unclustered baseline is not a representative-day algorithm and makes no compression or solver-benefit claim.
3. **Directed joint-hour transitions plus endpoints:** the multiset of167ordered adjacent row pairs, together with ordered first and last rows. There is no last-to-first edge. This is a raw, unclustered transition baseline, not Auer TAG or a learned/aggregated Markov representation.

For each multiset report exact equality, matched occurrence multiplicity and removed/added occurrences. Also report changed chronological day positions and changed chronological adjacent-value pairs, separate from multiset changes. Report complete-row uniqueness, changed physical row positions and changed coordinate counts by the four declared component groups. Source continuity breaks (`source[t+1] != source[t]+1`) and literal changed adjacent source-index pairs are separately named provenance diagnostics; they do not substitute for comparisons of actual physical values.

If all168complete input rows are distinct, test the conditional losslessness of the raw-transition observation by reconstructing the unique path from its directed-edge multiset and endpoints and matching the exact full row sequence. Verify all edges are consumed, path length/endpoints and absence of branching. If raw rows repeat, report that the stated uniqueness-based reconstruction premise is not established, without substituting another criterion or claiming general losslessness. This is an instance-specific information diagnostic, not a new theorem or a bounded-memory result.

Archive the canonical token dictionary and complete three observations for every identity, ordinary target and class control. Raw sequences may be stored as provenance for reconstruction checks, but are explicitly outside the first two observations. Compare actual objects; content digests are audit aids only. Repeat identity observation construction to check deterministic serialization. Class controls need preserve HOD/edges; no presumption is made that they preserve day or transition observations.

## Published-method boundary and interpretation

The existing Auer v2/TAG code-fidelity assessment remains separate. Until the real paper-linked native preprocessing contract and faithful adapter are established and prospectively reviewed, report `PUBLISHED_COMPARATOR_NOT_EXECUTED`. Do not label these generic day/transition counters as an execution of Auer, TSAM, Merrick, Orgaz or another published method. No clustering backend is called. A future authentic comparator is a separate protocol amendment/arm, never silently appended after seeing these results.

An observation that distinguishes a known positive/negative pair is sufficient to reject the claim that this pair proves information loss for that observation. It does not establish accuracy or sufficiency for all inputs. The raw-transition uniqueness condition may make this baseline lossless on these particular continuous-valued inputs; that would say little about clustered transitions. Preserve these limits even if every pair is distinguished.

## Execution, fixtures and closure

Source: `src/researchnext_observation_audit.py`; fresh additive output root: `results/research_next/observation_audit/`. Modes separate synthetic fixtures, hash-only preparation and the single prepared run. Exclusive preparation/run markers prevent quiet retries. Fixed preparation manifests and source/protocol hashes are rechecked at entry and close. A300-second soft run phase is checked between fixed cases; any remaining roles retain explicit NOT_EVALUATED status. A failure retains partial reports and the complete six ordinary/six control denominator. There is no old06:00UTC cutoff; user authorization was explicitly renewed without expiry.

Focused fixtures test joint-versus-marginal content, signed-zero equality versus byte provenance, whole-day permutation, a single changed107thcoordinate, multiset multiplicities, endpoint-sensitive noncyclic transitions, conditional unique-token reconstruction and repeated-token nonclaim. They use invented arrays only and do not execute old tests or inspect scientific arrays.

After one authorized run, perform a bounded independent review of input bindings, observation definitions, count identities and declared scope. Do not repeat scientific computations without a concrete unresolved concern. No broad novelty, weather plausibility, field/AC/security, independent-network or published-method performance conclusion is authorized by this audit.
