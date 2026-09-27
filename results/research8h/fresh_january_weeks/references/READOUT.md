# Fresh January reference weeks: completed reference stage

Both fixed fresh windows supplied a verified full-network binary reference in the archived model with every finite row and column bound expanded outward by exactly `Fraction.from_float(1e-5)`. The exact original binary masks, native no-cap checks, and raw/recovered numerical checks pass. Both points fail strict nominal membership by small numerical residuals; neither is an exact nominal-model witness or a proven optimum.

| Native window | Verdict | Fossil energy (MWh) | Numerical solver lower bound (MWh) | Numerical relative gap | Actual solver seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| January 8–14, rows 168:336 | VERIFIED_REFERENCE_EXPANDED_MODEL | 26269.05353649975 | 25880.647222005326 | 0.014785698843498441 | 600.3705776999996 |
| January 15–21, rows 336:504 | VERIFIED_REFERENCE_EXPANDED_MODEL | 47840.28339873613 | 47469.07509248424 | 0.007759324984719601 | 600.3401202000096 |

The fossil objective contains the same 23 units, excluding the nuclear unit. Exact fossil sums are stored in each `result.json`. Each 600-second call ended at the time limit with a feasible incumbent. Exactly two sequential calls ran, without retries or warm starts. Actual optimization time was 1200.710697900009 seconds, a combined 0.710697900009-second soft-limit overrun. The complete reference phase took 1213.7337654999865 seconds, within its 1800-second budget. All 48 input-manifest hashes pass after execution.

Eligibility is therefore retained for both preselected weeks. Target caps will be calculated from these exact incumbent sums using the frozen ceiling rule, not from numerical lower bounds or a claimed optimum. The reference-stage authorization did not authorize target solves; those require frozen target archives, independent review, and separate root GO. All four intended ordinary cases remain in the denominator.

The windows and seeds were approved before the root inspected the previous hour-of-day outcomes; this is not a claim that approval preceded the existence of those previous outcomes. Earlier arms, historical UNKNOWN results, and their gates remain unchanged.

Independent outcome review is archived separately under `results/research8h/fresh_reference_postrun_review/`; it is not part of the producer's input manifest.
