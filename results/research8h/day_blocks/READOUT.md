# January whole-day permutation test

**Result: one verified expanded-model positive, zero certified negatives, four UNKNOWN cases.** All five nonidentity orders remain in the denominator. No conclusion of infeasibility follows from the four timeouts.

The three interior 24-hour days (hours 48–119) were tested in every nonidentity order, keeping the first/last 48 hours fixed. Complete joint hourly packages, hour of day and each within-day profile are preserved. The full native DC network, 23-fossil-unit cap of 23195 MWh and absence of individual-unit mean targets are unchanged. This is a model experiment, not a field intervention.

| Interior day order | LP stage | Binary stage | Final result |
|---|---|---|---|
| 132 | Numerically admitted fractional point | Time limit, 505.424 s | UNKNOWN |
| 213 | Numerically admitted fractional point | Time limit, 303.766 s | UNKNOWN |
| 231 | Numerically admitted fractional point | Time limit, 417.489 s | UNKNOWN |
| 312 | Skipped by prospective route | Inherited constructive witness | Verified feasible in expanded model only |
| 321 | Numerically admitted fractional point | Time limit, 306.944 s | UNKNOWN |

The four LP points pass the archived numerical residual check but contain 263, 252, 247 and 263 fractional state coordinates, respectively. The MIP logs show no incumbent. These outcomes establish neither binary feasibility nor infeasibility for those four cases.

The 312 witness was independently checked using the stdlib-only exact verifier against every archived row and box bound and the original 12,096 binary U/Y/Z coordinates. It passes the uniformly outward-expanded bounds at the exact binary64 value of tau=1e-5, and its preserved native physical check passes. Its tiny nonzero nominal residuals mean that it is **not** a strict nominal-model point. Its fossil energy remains the inherited approximately 22964.941239556443 MWh.

All 148 frozen hashes and sizes were independently verified after completion, with no mismatch. The original pre-solve source/protocol, five-order family and routing are unchanged. Four LP calls preceded four sequential MIP calls; the constructive case used zero calls. Actual LP time was 28.145 s and actual MIP time 1533.624 s. The MIPs had configured 300-second soft limits but overran them by 333.624 s in total. The measured phase lasted 1595.668 s, within the 2100-second phase allowance. Timings are not a benchmark.

This experiment found no certified counterexample for the day-preserving family. It does not prove day aggregation sufficient, and the previous arbitrary-hour negative results should not be generalized to this family on the present evidence. These are five transformations of one January week, not five independent weeks.

Details: `docs/research8h/DAY_BLOCK_POSTRUN_REVIEW.md`; numerical accounting and bindings: `postrun_independent_review.json`. The reviewer performed no optimization and modified no frozen artifacts.
