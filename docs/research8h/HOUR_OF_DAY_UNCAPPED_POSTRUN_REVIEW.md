# Independent hour-of-day uncapped continuation review

PASS. Both full original-binary witnesses and both exact objective lower bounds were replayed without an optimizer. All 92 frozen bindings and reviewed result hashes matched. Detailed audit: results/research8h/hour_of_day_uncapped/independent_postrun_review.json. Reviewer source results/research8h/hour_of_day_uncapped_postrun_review.py SHA256 a5fd773243a05b13224a5265ab093160232e0996c6271e863e125f2feb9f3909.

For both recovered vectors, all 12,096 original binary coordinates, U recovery and canonical Y/Z transitions were checked; P/theta bytes match the raw incumbent. Exact scaled-integer evaluation accepts every uniformly expanded row/box and rejects strict nominal membership. The raw continuous vectors also satisfy every expanded row/box. Stored native no-cap checks pass. Native-model provenance and exact cap-row deletion were checked at the separate prepared gate; this review does not rerun the producer's native assembler.

The raw duals were independently projected only at inadmissible one-sided endpoint signs, and the archived projected vectors match exactly. Signed row sums, residual coefficient box minima and tau widening were independently recomputed as exact fractions. Both direct widened endpoints and the norm formula agree. No solver optimality, exact stationarity or LP-primal optimality is needed for these lower bounds.

| HOD target | Exact lower MWh (display) | Verified binary upper MWh (display) | True optimal energy increase MWh (display) | True optimal relative increase (display) |
|---|---:|---:|---:|---:|
| 26093200 | 23531.307857236814 | 23952.175430556470 | [566.366617680373, 1336.352661465332] | [2.466222804%, 5.908927900%] |
| 26093201 | 23823.063084396388 | 24024.798983556408 | [858.121844839945, 1408.976214465271] | [3.736660311%, 6.230046233%] |

These decimals are descriptive approximations; exact rational endpoints and outward-rounded versions are authoritative in energy_brackets.json. With independently replayed identity lower L0=22615.822769091137 and feasible incumbent upper U0=22964.941239556443, the optimum difference is bounded by [Lt-U0, Ut-L0], not by subtracting two claimed optima. Positive denominators justify [Lt/U0-1, Ut/L0-1] for the relative penalty. These are finite intervals because both target binary witnesses were accepted. They concern the uniformly expanded binary64 models, not strict nominal optimality or observed physical operation.

Calls were two 600-second MIPs followed by two 60-second LPs, with both MIPs ending at their time limits. Actual totals were 1200.4058258 MIP seconds and 3.0431587 LP seconds; the MIP soft-limit excess totals 0.4058258 s. Phase elapsed 1215.8691980 s stayed within the 2100 s soft allocation. All four actual-call guard admissions and chronological call order were checked. No identity solve, retry or new optimizer call occurred in the review.

Reviewer development history: the first replay stopped because its strict NPZ reader was incorrectly told that raw_duals.npz contained only row_dual; the actual archive also contains column_dual. A second replay reached accounting and stopped because the review loop accumulated calls per case instead of chronological order. The reviewer schema was corrected and calls sorted by their actual start timestamps before comparison with the prescribed order. The third replay passed in 5.986 s. Only this new reviewer source changed; producer source, protocol, models, outputs and arithmetic rules were untouched.
