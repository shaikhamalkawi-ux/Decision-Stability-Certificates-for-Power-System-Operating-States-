# Hour-of-day arm: independent post-run review

**Verdict: PASS.** Both prespecified ordinary hour-of-day permutations have exact infeasibility certificates for the full-network continuous relaxation with every finite bound widened by tau = Fraction.from_float(1e-5). They therefore reject the corresponding expanded original-binary model. The identity and commitment-class control remain verified expanded binary positives. No strict-model positive or new independent-week result is asserted.

## Replayed evidence

The separate stdlib-only replay is results/research8h/hour_of_day_postrun_review.py, SHA-256 8c4db9f2c91193aa6e92591cfb64f1061db035fa0ea1967a261c3bd9390a30cc. It imports the previously reviewed standalone archive/ray checker and the independently written scaled-integer point checker, not producer model or optimizer modules. It completed once, exit zero, in 14.895 seconds, with zero optimization calls. Detailed exact fractions and artifact hashes are in results/research8h/hour_of_day/independent_postrun_review.json.

All 125 frozen bindings match before and after replay. Manifest SHA-256 remains 078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc. The copied LP matrix/bounds/mask/row metadata agree with their original prepared model files. New ray, result, log and execution-accounting files were separately hashed before/after review. Prior prepared review established the package permutations, 48-hour fixed edges, hour-of-day preservation, cap 23195 MWh, native arrays and original 12096-column binary mask.

| Ordinary case | Exact robust ray gap (approximate) | Nonzero row multipliers | Raw entries projected to zero | LP seconds |
|---|---:|---:|---:|---:|
| seed_26093200 | 17111.125630529 | 1442 | 48 | 2.7841651 |
| seed_26093201 | 25458.316298779 | 1706 | 29 | 3.0732249 |

The raw rays select infinite endpoints and correctly fail the independent checker. Recomputing the prescribed sign-cone projection from each archived raw ray exactly reproduces the accepted sparse multiplier vector. No silent projection is performed by the independent certificate checker. The exact strict and expanded separation fractions both match the archived fractions. Direct widened-endpoint evaluation agrees with the norm deduction. Sparse CSV multipliers and row-family support also agree; both proofs use the fossil-cap row and dwell rows, and have no mean-target row. Gap magnitudes depend on ray scaling and are **not** energy penalties or margins measured in MWh.

The two positive controls have all 12096 original state coordinates exactly binary and pass every expanded row/column bound. Both fail nominal strict membership by tiny residuals: maximum exact row violation about 2.5498885e-11 and column violation 2.1552538e-11. Their exact fossil energy is 1654798412944827657145 / 72057594037927936 MWh, approximately 22964.941239556443. Both ordinary transported points also pass the exact expanded static model, while failing full dwell feasibility. Their failure as particular schedules is not the reason for the model-infeasibility verdict; the independently checked separating rays supply that reason. Stored native physical checks pass for both controls; this replay does not independently reassemble the raw native dataset.

## Calls and history

Exactly two existing solver logs each contain one HiGHS invocation. Their total reported solve time is 5.85739 seconds; the reported allocated phase is 8.3902264 seconds. There are no MIP folders/calls and no LP soft-limit overruns. The 1200-second setting is a phase guard, not a hard wall-clock guarantee; entry validation/native loading precede the reported phase.

An optional tracing wrapper was stopped before the successful direct frozen invocation. The preserved producer record reports zero optimization, no frozen execution marker and no solver artifacts at that termination. Its 167.93 seconds are not solver time. This reviewer checks the preserved record, source/input hashes and current two logs, but cannot independently reconstruct past process state. It is not relabelled as a solver retry or omitted from the development history.

## Interpretation

These pairs preserve the **entire joint hourly package distribution conditional on hour of day**, in addition to the full multiset and fixed boundary packages. They therefore address the specific explanation that arbitrary reshuffling only broke day/night placement. They still change within-day trajectories and chronological adjacency. They are synthetic order interventions on the same January week, not observed weather trajectories, an additional season, an operational field trial or a general failure of all methods using chronology. Two prespecified negative cases and two positive controls support a scoped benchmark claim; they do not establish a population success rate or priority over established aggregation/certificate methods.
