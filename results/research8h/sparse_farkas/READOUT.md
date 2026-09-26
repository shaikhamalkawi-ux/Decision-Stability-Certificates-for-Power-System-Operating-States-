# Sparse proof extraction results

All four archived order-dependent infeasibility results now have smaller exactly replayed Farkas proofs. The fixed greedy group order completed in every case without a timeout or budget stop. The chronology constraints appearing in all four final proofs belong only to units `107_CC_1` and `118_CC_1`; other units' static constraints, target means and bounds still matter.

| Case | Chronological rows | Chronological referenced hours | Final row-anchor hours | Total proof rows | Exact variable-bound terms |
|---|---:|---:|---:|---:|---:|
| seed_26092600 | 435 to 44 | 164 to 51 | 22 | 222 | 6133 |
| seed_26092601 | 223 to 53 | 103 to 46 | 26 | 232 | 6140 |
| seed_26092602 | 428 to 68 | 160 to 53 | 35 | 259 | 6192 |
| seed_26092603 | 379 to 45 | 145 to 54 | 24 | 233 | 6170 |

Every final proof passes exact rational checking for the archived binary64 model and continues to separate after all finite row and variable bounds are relaxed outward by 1e-5. All 41 mean equalities, 8,273 static rows and 37,968 variable bounds were retained during the search. Global target-mean dependencies still span 168 hours. Thus the table measures proof support, not raw information compression or minimum temporal memory. Referenced hours include the preceding variables used by dwell inequalities, which is why row-anchor counts alone would overstate compression.

The finite design made 175 LP deletion attempts, accepting 21. Total reported LP compute was 53.767 seconds and summed case wall time was 105.501 seconds, below the 840-second overall and 195-second per-case caps. Each solve had at most 12 seconds. The protocol and executable hashes were fixed before these runs and remain unchanged. All failed group deletions and their continuous vectors (when returned) are archived; exact checks are required for every accepted deletion and coefficient-pruning candidate.

Seed 00 is development and the other three are post-pilot coverage under the same fixed method. The group search and Farkas method are not claimed novel, and these reductions do not prove global or inclusion minimality. The useful empirical finding is that chronology for two units suffices to preserve the four global impossibility conclusions within these relaxed models.

Reproduce optimizer-free verification with:

```
python src/research8h_sparse_farkas.py --verify-archived
```

Replay validates model hashes, exact multipliers, reported support and every nonzero exact variable-bound contribution; it does not import HiGHS. Earlier models and results remain unchanged.
