# Independent OR-LIB exact outcome review

PASS, 27 September 2026. One standard-library replay checked the closed six-model run without producer imports, model rebuilding, optimizer calls or a new scientific experiment. All 29 frozen inputs and 96 output-manifest entries matched their hashes; the complete 127-file producer snapshot remained unchanged. Trusted completion, intervals and output-manifest SHA256 values are respectively `e67b5049f77191848ef0700f2e5698d84c8992eeb31aac5e20d22290878a8cf6`, `84d1dfe74d8a115ebffc336e03840cdcae174982138fb1bbf3eadd92de6dbc8c` and `2713685311e705ea0c9b6080dee2594e9d077d37aea844efb0e093f722cf9a52`.

All four available MIP candidates were reconstructed from the saved raw NPZ vector: identity in each service variant and both native-penalized targets. Every one of the 960 U/Y/Z/D coordinates is an exact binary value after the single declared near-integer snap; every continuous coordinate retains its raw binary64 bytes. Exact fraction arithmetic independently checks all 4,384 rows and 2,472 column boxes. A separate named-variable evaluation checks transitions, dwell and initial history, above-minimum ramps, segments, production/headroom, startup/shutdown limits, reserve, curtailment, nodal balance and operating cost without reading matrix row coefficients. The two objective evaluations, canonical-cost domain diagnostics and both exact maximum violations match the archived checks.

All four points belong to the uniformly expanded encoding at `tau = Fraction.from_float(1e-5)` and **none belongs to the nominal encoding**. Their maximum nominal violations are approximately6.44e-12,8.16e-12,1.56e-12 and2.55e-12 in the order above. Small residuals are not silently promoted to strict feasibility. The saved segment objective, including curtailment penalty where present, supplies each upper bound; no greedy segment repair or numerical optimality assertion replaces it.

The review independently recomputes all twelve retained lower-bound candidates: six zero-dual box floors and six signed solver-row candidates. It verifies sign projection against missing row sides, every rational stationarity-residual coordinate, the signed endpoint sum, nominal finite-box correction, complete uniform-expansion penalty and both selection maxima. These are valid exact lower bounds for the archived encoding without assuming numerical dual feasibility or optimal status. In particular the reverse hard-service LP's numerical Infeasible status does not convert its objective-bound record into an exact infeasibility certificate.

All four signed target-minus-identity interval records match exact fraction arithmetic, including the missing-upper cases:

| Service variant | Target | Certified expanded optimum-cost difference interval |
|---|---|---|
| Native penalized | Reverse4–19 | [9,972.912698410166, 63,039.56215423082] |
| Native penalized | Left-rotate4–19 | [-5,614.286603710794, 76,443.48692503407] |
| Hard service | Reverse4–19 | Unknown; no accepted target upper |
| Hard service | Left-rotate4–19 | Unknown; no accepted target upper |

Displayed endpoints are decimal approximations; the report retains the exact numerator/denominator endpoints. The reversal interval is strictly positive for the expanded native-penalized model. The rotation interval crosses zero and supplies no sign determination. The two hard-service targets have numerical MIP Infeasible statuses, but no replayed exact infeasibility proof or finite target upper; their null intervals and UNKNOWN labels remain intact. This is encoded operating cost on the selected converted one-bus instance, not fuel, emissions, a network/field result, HOD preservation or equivalence to the original quadratic benchmark. Runtime Julia/JuMP export equality remains NOT_TESTED.

All twelve attempted/returned calls, their fixed model/kind ordering, options, admission receipts, numerical statuses, durations and final result copies agree. Producer solve time sums to203.2320852999983seconds and the complete phase was232.1192841999873seconds; all call limits and the2,700-second phase allowance were respected. Shared-host runtime is not a benchmark. The independent replay exited zero after2.7915445000107866seconds internally, with zero optimizer calls. A draft reviewer syntax-only check caught and corrected an extra parenthesis before the sole actual replay; no producer change or repeated scientific replay occurred.

Stable artifacts:

- `INDEPENDENT_SOLVER_RESULT_REVIEW.py`: SHA256 `c1190b9885d1c1cc81978b40864cb8411c9e2717f4584f172769cfb41a775d88`.
- `INDEPENDENT_SOLVER_RESULT_REVIEW.json`: SHA256 `a465a16acf67ca9a0925376f2a2b7d4338a24bac9bb276258d134f930d11f358`.

The report binds all producer files and includes all four point outcomes, six selected bounds with their twelve retained candidates replayed, all four interval records and the explicit scope limitations. Existing producer scientific artifacts were not edited.
