# Exact observations on the July 168-hour case

The exact raw exogenous observations in this case are injective over the 168 hours. Their labelled bigram counts and endpoints reconstruct the chronology uniquely. This limits how the finite-alphabet ambiguity question can be connected to the existing RTS experiments; it is not an operational feasibility result.

| Exact observation | Coordinates | Unique states | Repeated state classes | Positions in repeated classes | Distinct bigram types | Successor / predecessor branching states | Self-loop occurrences |
|---|---:|---:|---:|---:|---:|---:|---:|
| Nodal net load + all bounds | 106 | 168 | 0 | 0 | 167 | 0 / 0 | 0 |
| Aggregate net demand + all bounds | 83 | 168 | 0 | 0 | 167 | 0 / 0 | 0 |
| Repaired witness commitment U | 24 bits | 48 | 20 | 140 | 92 | 20 / 20 | 79 |

Every series has 167 adjacent transitions. For U, 120 observations repeat beyond the first occurrence of their state, the largest state multiplicity is 27, and 17 bigram types occur more than once. Branching counts concern distinct successor/predecessor labels, not repeated copies of the same edge. No Euler-trail count was computed.

The exogenous keys contain only the indicated net loads and 41 lower/41 upper bounds: no dispatch, commitment, timestamps, source-row identifiers, or hour indices. Equality uses actual little-endian binary64 bytes. No negative zeros occur, and exact numerical float-tuple class counts also equal 168. State IDs are assigned by lexicographic byte-key order, independently of occurrence time. The aggregate net demand is the actual input to the baseline LP; its maximum difference from summing the rounded nodal net loads is 4.55e-13 MW.

## What is proved

Let x_0,...,x_167 denote either exact exogenous observation sequence and let C(a,b) count its labelled adjacent pairs. All x_t are distinct, so the observed graph is a simple directed path: the start has in/out degree (0,1), the end (1,0), and every other state (1,1). Every edge count equals one. Given the start, its only outgoing edge forces the next observation. Induction forces every subsequent observation. The implementation consumes all 167 edges and recovers the exact sequence and final endpoint. Thus any chronology with the same exact labelled bigrams and endpoints has the same observation order. The labels must retain the actual vectors or collision-checked byte keys; this conclusion does not concern an unlabelled graph or an unordered list of count values.

The 16 existing Markov permutations preserve the full 24-bit U bigram multiset and both endpoints, and all 16 change the U label sequence. They are therefore concrete ambiguity witnesses for that endogenous alphabet. Zero of those 16 preserve either exogenous bigram multiset. They do not supply raw-exogenous bigram ambiguity witnesses, and this audit makes no claim about their operational feasibility.

## Interpretation and limits

A finite-alphabet worst-case theorem can still be embedded in real-valued observations by assigning repeated numerical vectors to its symbols. The present result does not refute such an existential theorem. It establishes that this actual July dataset has an injective raw observation alphabet, for which exact labelled bigrams are lossless and provide no chronology reduction. An empirical claim about a lossy exogenous alphabet would need an explicitly fixed observation map and a new audit. None was introduced here. The selected U alphabet is endogenous to a particular witness, not an input-only summary.

The source DC-network witness passes the existing nodal checker; maximum nodal-balance residual is 7.96e-12 MW and maximum branch excess is 2.85e-14 MW. The 24 nodal net loads were independently reconstructed from native load allocation and rooftop-PV inputs with exact array agreement. Dispatch P was used only for that grounding check, never as an exogenous label. All source hashes were unchanged after the audit. No optimization, quantization, new permutation search, or Euler-trail enumeration occurred.

## Audit artifacts and reproduction

Each alphabet directory contains exact arrays, coordinate labels, complete byte dictionaries, hour-to-state mappings, edge counts, degree tables, coordinate uniqueness diagnostics, and reconstruction checks. `archived_markov_comparison.csv` records every existing permutation comparison. `input_manifest.csv` binds native inputs, source modules, published July targets, repaired witness files, all 16 permutations, the protocol and the audit runner. Source-row/timestamp correspondence is kept separately in `hour_mapping.csv`.

The recorded protocol SHA256 is `828706b35629c9ac73215b27e748b45eb9be17cca6c0fee157e68fb0b786a938`; runner SHA256 is `f9f75e44a7842ebbdc0b1f95898adb97bde5bd31eaad7857192f51eff8495bfd`. Run with the scientific Python environment from the repository root, giving the portable RTS directory and a fresh output directory:

```text
python src/research8h_observation_audit.py --source-v3 PATH_TO_v8r1_rts_inputs --output PATH_TO_NEW_AUDIT_OUTPUT
```

Existing audit results are protected against overwrite. This audit was completed after the immutable Checkpoint01 archive and is not included in that archive.
