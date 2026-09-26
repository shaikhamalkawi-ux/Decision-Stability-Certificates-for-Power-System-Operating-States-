# Independent day-block post-run review

Verdict: **PASS for archive integrity, routing and reported classifications, with observed solver time-limit overruns explicitly retained.** The reviewer ran no optimizer and changed no frozen source, protocol, input, result or solver log. New review/readout files are separate from the pre-solve manifest.

## Integrity and sequence

All **148/148** frozen manifest entries were independently rehashed and checked for byte count after completion: zero mismatches. Manifest SHA-256 remains `5f15b13ce9b15abb1ff6256a4e10fc568ab5384e01a324160b0e522b31c8927d`. The frozen source/protocol identities remain those approved in the code/prepared reviews: source `43441ca2da48c6d8acc2574461502f6f74a4f0f4a3b32ad653c5fd794a5f6a8b`; protocol `b557ac53749616f13c600ddf2b02712e3fbd307083659dea05e65c108a659933`.

The full denominator is retained in the declared order: 132, 213, 231, 312, 321. The saved source and log creation/last-write times agree on four LP calls first, in order 132/213/231/321, followed by four sequential MIP calls in that same order. Every log contains one HiGHS run header. All four LP logs completed before the first MIP log began. The 312 case has no LP result/log and no MIP directory, as prescribed by its pre-solve constructive positive. No certificate was generated or negative case certified in this arm.

## Outcomes

| Case | LP record | MIP record | Final classification |
|---|---|---|---|
| 132 | Optimal; numerical point check passes; 263 fractional state coordinates | Time limit; no incumbent | UNKNOWN |
| 213 | Optimal; numerical point check passes; 252 fractional state coordinates | Time limit; no incumbent | UNKNOWN |
| 231 | Optimal; numerical point check passes; 247 fractional state coordinates | Time limit; no incumbent | UNKNOWN |
| 312 | Skipped using exact constructive positive | Skipped | Verified feasible in expanded model only |
| 321 | Optimal; numerical point check passes; 263 fractional state coordinates | Time limit; no incumbent | UNKNOWN |

The LP classifications are numerical admission of fractional continuous-relaxation points under the recorded tolerance. They do not establish binary feasibility. The MIP logs independently report infinite primal bound, solution status `-` and time-limit termination; their directories contain no returned raw/recovered point. Thus the four UNKNOWN classifications are appropriate. Solver status is not converted into a proof of infeasibility.

## Exact inherited witness

The independent stdlib verifier already rechecked `days_312` using exact Fraction arithmetic, all matrix rows/box bounds and the original 12,096-coordinate U/Y/Z binary mask. Its final report is `results/research8h/standalone_verifier/final/day_312_point.json`, SHA-256 `fba3deb96b97d89dd31fbe3d8c7f7fa160ad79261afc9569df3256ad04607077`, from verifier source `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`. The post-run audit rehashed every input named by that report and confirmed equality; no redundant reoptimization or additional point solve was performed.

The witness is exactly binary and passes the uniformly expanded model at `tau=Fraction.from_float(1e-5)`. It fails strict nominal membership because the exact largest row violation is approximately `2.5498884647111388e-11` and the largest column violation approximately `2.155253753244324e-11`. The frozen native physical report also passes. Neither check justifies a strict nominal-model positive. Prior preparation independently verified all five static copied-witness controls and both source positive controls; those bound files remain unchanged.

## Budget accounting

Configured allocations for the calls actually made were 4×30=120 LP seconds and 4×300=1200 MIP seconds, totaling 1320 solver seconds. Recorded actual LP time sums to **28.144544899987523 s**. Actual MIP times were **505.4242418000067, 303.7663046999951, 417.48933749998105 and 306.9437764000031 s**, summing to **1533.623660399986 s**. The MIP calls exceeded their configured soft limits by **333.62366039998597 s in total**. These overruns must not be hidden or described as four completed 300-second wall-clock runs.

The total recorded solver time is **1561.7682052999735 s**; the phase elapsed time is **1595.668305899977 s**, including about **33.9001006000035 s** of other phase work. This run remained within the declared 2100-second phase allowance. The phase starts after native model loading; it is not a bound on all surrounding application/startup time. Source and recorded per-case limits are unchanged; no adaptive longer allocation or retry is evidenced. Shared-host execution and these overruns preclude a timing-performance claim. This audit does not independently reconstruct concurrency of other arms.

## Scientific interpretation

There is one certified expanded positive, zero certified negatives and four unresolved cases among the five nonidentity day orders. The test preserves complete 24-hour profiles, hour-of-day alignment and fixed first/last 48-hour input packages, while changing inter-day order. It currently supplies **no certified day-order counterexample**. It also does not establish that all five orders, or day aggregation generally, are feasible. The earlier arbitrary-hour counterexamples must not be presented as a demonstrated failure of this more restrictive day-preserving family.

Machine-readable accounting, log timestamps and witness bindings are in `results/research8h/day_blocks/postrun_independent_review.json`; the concise result is in that directory's `READOUT.md`.
