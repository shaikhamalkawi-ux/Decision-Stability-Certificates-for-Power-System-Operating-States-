# Hour-of-day arm: independent prepared-archive review

Verdict: PASS, before target execution. All 125 frozen input/artifact bindings matched their size and SHA-256 before and after the independent replay; the execution marker remained absent. The parent was notified that its final GO gate was satisfied. No optimizer was called by this reviewer.

Manifest: `078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc`. Source/protocol hashes match the preceding code review and the producer's before-generation freeze. Independent replay source: `results/research8h/hour_of_day_prepared_review.py`, SHA-256 `95ed702e7e01367206061ddbf8158fe528d34dc328a3addf4a847ee2586a507b`. Machine-readable evidence: `results/research8h/hour_of_day/independent_prepared_review.json`. Successful replay runtime: 6.778 seconds.

| Case | Changed hours | Source-continuity breaks | Position-wise changed adjacent pairs | Exact static expanded | Exact full expanded | Full violated rows |
|---|---:|---:|---:|---|---|---:|
| Identity | 0 | 0 | 0 | Pass | Pass | 0 |
| 26093200 | 46 | 46 | 61 | Pass | Fail | 348 |
| 26093201 | 56 | 41 | 69 | Pass | Fail | 316 |
| Control 26100200 | 14 | 16 | 22 | Pass | Pass | 0 |

Every ordinary full-point violation belongs to `minimum_up` or `minimum_down`; the counts are violated matrix rows, not separate operating events. The two copied-schedule failures do not prove model infeasibility. All four strict nominal point checks fail; the two positive controls belong exactly to the uniformly expanded model only. Both ordinary cases and the nonidentity control are retained.

The independent script uses the reviewed stdlib NPZ/CSR reader and separate scaled-integer arithmetic for every point/row/column bound. It checks the original 12,096-coordinate U/Y/Z binary mask, projected 4,032-coordinate U mask, canonical transitions and sparse auxiliary structure. It checks the complete fixed fossil cap/zero objective and exact preserved fossil sum. All native hourly arrays and transported P/U/theta packages match their source-hour mappings bitwise. Every local physical row and bound matches its identity source-hour counterpart, every chronological row remains unchanged, and the two LP directory input copies match the parent case bytes.

Every hour maps within its own three-position interior hour-of-day group, preserving both fixed edges and all inverse/bijection conditions. Recorded ordinary groups follow ascending hour order; recorded control groups match the authoritative lexicographic `(hour,U bits)` order. PCG64 implementation itself is source-reviewed, not independently reimplemented here. Native physical-check reports were cross-checked but the underlying native CSV/network assembly was not rebuilt again by this independent replay.

The producer's `changed_adjacent_pair_count` denotes `diff(order) != 1`, i.e. source-continuity breaks. The separate position-wise counts above count `(order[t],order[t+1]) != (t,t+1)`. Complete lists are saved in the independent JSON. The two definitions should not be interchanged.

Review history: the initial replay stopped at a reviewer assertion requiring *bitwise* equality between the control's U sequence and the unpermuted identity. The control transports six signed-zero U encodings differently, while all values remain the identical exact binary sequence because +0 and -0 both denote zero. Only that overly strong reviewer assertion was corrected to exact value equality. Bitwise package-transport checks remain in place, no producer file/seed/point changed, and no optimization or experimental redraw occurred. The successful replay and this correction are recorded separately from experimental outcomes.

Retain the code-review timing qualification: 1,200 seconds is a configured solve/check allocation with soft solver limits and a 305-second MIP-start guard, not a guaranteed wall-clock ceiling. The phase starts after native model loading/manifest validation. This preparation PASS supplies no target LP/MIP conclusion and no evidence of generalization beyond this same-week sensitivity design.
