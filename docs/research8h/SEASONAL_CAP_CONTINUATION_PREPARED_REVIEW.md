# Seasonal cap continuation: independent prepared-archive review

Verdict: PASS. The solver-free independent replay finished with exit code 0 before an execution marker existed. It checked all 271 manifest entries before and after the replay, with zero size/hash mismatches. The parent and executor were informed after completion that the standing conditional execution gate was satisfied. This memo records preparation evidence only, not target LP/MIP outcomes.

Frozen manifest SHA-256: `d5ae06005d333ee20b6ef5a466c72fd7c5530462ada923fc83a07e26b14e8055`.

Source SHA-256: `fe7253d9d6217a26ad3162422e91cc90dba83350526faed1443d54c8500b29ab`.

Protocol SHA-256: `14349e3ea185f0cd4089ab5d2745afbbd4c7d5240064893b5f3ffe0065b6bbb2`.

Independent replay: `results/research8h/seasonal_cap_prepared_review.py`, SHA-256 `3de77675460d103298ac17dc7851144362a3ecb87a1e77ec80f522622259433a`. Evidence: `results/research8h/seasonal_cap_continuation/independent_prepared_review.json`. Runtime was 45.183 seconds; optimization calls were zero. The script uses the previously reviewed stdlib NPZ/CSR reader and independently implements scaled-integer exact point arithmetic; it does not import the experimental exact-point checker or optimizer packages.

| Month/case | Cap (MWh) | Changed positions | Exact static expanded point | Exact full expanded point | Failed full rows |
|---|---:|---:|---|---|---:|
| April identity | 43,131 | 0 | Pass | Pass | 0 |
| April 26093400 | 43,131 | 72 | Pass | Fail | 824 |
| April 26093401 | 43,131 | 71 | Pass | Fail | 878 |
| April class 26100400 | 43,131 | 16 | Pass | Pass | 0 |
| October identity | 125,172 | 0 | Pass | Pass | 0 |
| October 26094000 | 125,172 | 70 | Pass | Fail | 1,324 |
| October 26094001 | 125,172 | 71 | Pass | Fail | 1,460 |
| October class 26101000 | 125,172 | 0 | Pass | Pass | 0 |

Every failure in an ordinary copied schedule belongs to `minimum_up` or `minimum_down`. Counts are violated matrix rows, not independent physical events. They do not establish infeasibility of the corresponding optimization model. All eight strict nominal point checks fail; accepted positive controls are exact members of the uniformly expanded model only.

The October class-control draw is exactly the identity order. It was retained as required by the fixed protocol, and must not be described as an independently perturbed positive control. April's class control changes 16 positions while retaining the entire U sequence.

The exact April reference energy is `6154272335876697791701 / 144115188075855872` MWh (about 42,703.8427944); October is `558140738732395069817 / 4503599627370496` MWh (about 123,932.1398244). Independent rational summation over the 23 native fossil units reproduces both cap records as `ceil(101 E / 100)` and every permuted point's unchanged energy. These references are feasible incumbents, not proven optima.

For each identity, removing exactly its single fossil-cap row recovers the original reference's full sparse physical matrix, bounds and original binary mask. Every local physical row of every reordered model was compared coefficient-for-coefficient, after its hour-coordinate mapping, to the identity's corresponding source-hour row; all column and row bounds were also checked. All chronological rows retain the identity formulation. All five native input arrays, complete P/U/theta packages, source row identifiers, fixed edges, exact bijections and reconstructed Y/Z values match their prescribed mappings. The cap row has exactly 3,864 unit coefficients, with no mean rows, and the objective is zero.

Every original mask contains exactly 12,096 U/Y/Z binary coordinates; every projected mask contains exactly 4,032 U coordinates. Independent sparse-row inspection confirms the transition/exclusivity/residence structure, initial Y/Z bounds, and absence of auxiliary coordinates from other families needed by the U-only recovery proof. Each original family has 4,008 rows. LP matrix/bounds/mask/metadata copies match their parent case bytes.

Native numerical physical-check results were read and cross-checked, and the generating/checking source had already been reviewed. This replay independently checks the archived matrix, inputs and exact points; it does not rebuild the native network from its original CSV source or separately reimplement NumPy PCG64. Source review supplies those two implementation checks. The original reference and initial seasonal outcomes remain unchanged; this later continuation cannot retroactively pass the original failed replication gate.
