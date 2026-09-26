# Independent review of commitment-transition-preserving twins

Review completed after all 16 fixed cases finished and before the separate
first-four MIP extension. The original script, protocol and result files were
not edited. Their frozen script/protocol hashes were independently confirmed.

## Findings

The main global preservation claim passes. The reference has 48 distinct exact
24-bit thermal commitment states and 167 observed adjacent-state pairs. For all
16 archived permutations, an independent checker encoded each commitment vector
as a 24-bit integer and recomputed the complete pair-count dictionary. Every
dictionary matched the reference and the stored transition-count table exactly.
All 16 raw orders and commitment sequences are distinct in the original report.

There is one wording error in the frozen protocol: the two boundary pairs are
not both individually fixed. The left pair at hours 47 to 48 is unchanged, but
the right pair at hours 119 to 120 changes in seeds 260926106, 260926108 and
260926115. The final head remains the original U[120]. The right boundary pair
is included among the 72 edges being permuted, so its count is preserved as part
of that edge multiset, rather than necessarily staying at its original position.
The internal-only pair multiset need not be preserved separately from this join.
This correction does not invalidate the exact global pair-count result. The
first four cases selected for the MIP extension also preserve that right pair
individually, as observed after generation.

The original right pair is state 6 to state 6 in the archived state dictionary.
The observed changes are:

| Seed | Source hour moved to position 119 | Original pair | Observed pair |
|---|---:|---:|---:|
| 260926106 | 104 | 6 to 6 | 4 to 6 |
| 260926108 | 118 | 6 to 6 | 13 to 6 |
| 260926115 | 104 | 6 to 6 | 4 to 6 |

State 6 is `000000110000000110110001`, state 4 is
`000000110000000100110001`, and state 13 is `000100110000000110110001`,
using the archived 24-unit column order. Each changed edge still belongs to the
unchanged global transition multiset.

The correct Euler argument is: edges indexed 48 through 119 represent all
transitions from U[48] through U[120]. A contiguous Euler trail starts at U[48],
uses every labeled edge once, and ends at U[120]. Its edge-tail payloads provide
the 72 reordered packages. The fixed left join is preserved; the interior plus
right join preserves the entire selected edge multiset; all suffix transitions
remain fixed. Together these yield equality of all 167 global transition counts.

The independent reconstruction also checked every order is a permutation,
hours 0 through 47 and 120 through 167 stay fixed, native row IDs and stored
state IDs agree, and inverse restoration of the full nodal-load, availability,
dispatch and commitment package array matches the archived SHA256. The complete
41-unit means agree within 1e-9 MW. These are full snapshot-package invariants,
not invariants of demand or availability transitions between consecutive hours.

All 16 continuous solutions were reloaded and independently multiplied by their
archived sparse matrices. Every row and column bound passed 1e-5; the maximum
residual across cases was 2.3237589630298316e-10. Each matrix/bounds file matched
its stored hash. An independent run-length check reproduced 4 through 12 dwell
violations in the directly permuted seed schedules. Those violations rule out
only that particular replay. Consequently all 16 full-unit chronological
admission verdicts correctly remain UNKNOWN after the LP phase.

## Literature and interpretation boundary

These states are the complete endogenous commitment vectors of one particular
dispatch witness. Auer and colleagues instead connect representative periods
through transition probabilities and expected boundary values, including
extensions for multistep constraints and binary variables. The present test
does not implement or falsify their formulation. Their current version is
arXiv v2 dated 15 July 2026, with authors Auer, Gaugl, Klatzer, Tejada-Arango and
Wogrin; use that complete author list or “Auer et al.” in a future formal
reference. [Primary paper, sections 2 and 3](https://arxiv.org/html/2510.18555v2).

Matching a first-order transition table need not preserve run lengths, which
the invalid seed replays illustrate. An operational insufficiency counterexample
requires a verified feasible original schedule and proof that no alternative
schedule admits the same means in the reordered instance. The current LP-phase
outcomes have not established such a counterexample or established sufficiency.
Alternative commitment schedules need not reproduce the seed's transition
counts, because those counts are descriptive summaries, not feasibility-model
constraints in this experiment.

## Prospective next step

The separately authorized extension fixes seeds 260926100 through 260926103 and
one 60-second full-unit, no-network mixed-integer feasibility solve per case.
Its own protocol is `MARKOV_MIP_PROTOCOL.md`; it retains all 41 individual means
and physical unit chronology. Verified witnesses establish only no-network
admission. Explicit numerical infeasibility, unverified limits and positive
incumbents are reported separately. No earlier UNKNOWN record is overwritten.
