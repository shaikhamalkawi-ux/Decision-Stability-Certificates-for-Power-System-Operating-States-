# Independent preparation review: exact fixed schedule

Verdict: PASS for the separately authorized single numerical-basis attempt. This is preparation verification, not a feasible-point or optimizer result.

The reviewer imported only the pinned standalone NPZ/CSR reader, not the producer or rational reconstruction/checker modules. It verified all 34 frozen bindings in input_manifest.json (397fdbdd982ec11dc7265d842733df40fc0ad66a22922ea40e06cfebdaf03da9), all 34,680 original rows and the 12,096-coordinate original binary mask. Every one of 16,032 constant rows satisfies its exact original bounds after the fixed-state substitution. All 168 continuous blocks retain 65 coordinates and their original column boxes and fossil objective.

For each hour, the reviewer independently recomputed the original aggregate-minus-24-nodals coefficient vector and right side, verified the exact power-of-two normalization, all retained original rows, and the complete transformed binary64 proposal: 18,648 rows and 10,920 columns. All proposal coefficients and endpoints equal the corresponding exact rational transformed values; the conversion-difference ledger is empty. This confirms row equivalence of the supplied proposal. A numerical solver point still requires exact original-model replay.

The existing capped identity differs in constraints only by row 24264 with cap 23195; its cap coefficients equal the uncapped fossil objective and all remaining rows, boxes and binary masks agree. Its own stored optimization objective is zero because it is a feasibility archive. The reviewer separately verified the native 23-unit fossil roster and existing binary64 hourly ramp conversion/minimum-residence conventions. This does not reconstruct the network from raw data.

Two reviewer-development failures were retained without changing producer inputs: attempt 01 incorrectly demanded identical optimization objectives for the capped feasibility and uncapped energy archives; attempt 02 used the unsupported CSV encoding alias utf8-sig. The final review correctly checks the capped zero objective and uses utf-8-sig. These were reviewer errors, not optimization attempts or scientific null cases. The final read-only pass took 2.8492832 seconds, with zero optimizer calls and zero actual basis reconstructions.

Final reviewer source SHA256: c872b9d5e4dda64054ed07633f50de961a01ef1444ab5c3ade2c416e58c7d296. Result SHA256: e5f1d58cacd663a5b256c8aec8eafdefc5287ad69a7c7aee9f50a87de297ba15. Reviewed producer source remains 733f57ae928c72dcf063c224e728d1ad1a01d52e93c068f63147d988c16e3a77; rational checker 9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d; protocol d3b3c39a62ca74e2b09cb46e456da5ab2812092eb9c9c25d548a7718e548acab.

A complete strict witness still requires all 168 exact hourly candidates, the original full model and native checks, and independent post-run verification. A failed fixed-schedule basis attempt is not a proof of full unit-commitment infeasibility.
