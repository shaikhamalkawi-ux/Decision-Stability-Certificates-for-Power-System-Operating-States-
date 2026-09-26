# Seasonal cap continuation: independent post-run review

Verdict: PASS for archived-input integrity, result classification and arithmetic replay. **All four ordinary binary outcomes remain UNKNOWN.** There is no certified negative and no accepted target binary witness. This continuation does not satisfy the augmented two-week negative-evidence criterion; only the earlier January success remains in that set.

Independent replay source: `results/research8h/seasonal_cap_postrun_review.py`, SHA-256 `3b975cfd52a8cb58c78e94318c79b9f028b2985f7b3e3c8fa3b82226730b6282`. Evidence: `results/research8h/seasonal_cap_continuation/independent_postrun_review.json`, status `INDEPENDENT_POSTRUN_REVIEW_PASS`. The script completed with exit code 0 and zero optimizer calls.

All 271 frozen entries matched their sizes and SHA-256 before and after replay, under manifest `d5ae06005d333ee20b6ef5a466c72fd7c5530462ada923fc83a07e26b14e8055`. The prepared controls, source and model inputs therefore remain those independently reviewed before execution. The two April cases retain cap 43,131 MWh and the two October cases retain cap 125,172 MWh; no cap, seed or reference was replaced.

| Case | LP seconds | Fractional original state coordinates beyond 1e-5 | MIP seconds | Final binary conclusion |
|---|---:|---:|---:|---|
| April 26093400 | 22.286 | 537 | 306.859 | UNKNOWN |
| April 26093401 | 29.777 | 604 | 300.092 | UNKNOWN |
| October 26094000 | 27.971 | 658 | 301.528 | UNKNOWN |
| October 26094001 | 26.100 | 911 | 300.169 | UNKNOWN |

The producer records four numerically feasible continuous LP points. This separate post-run review additionally checks every archived LP point using independent scaled-integer arithmetic against every row and column bound **with integrality relaxed**. All four are exact members of the uniformly expanded continuous model, and all four fail strict nominal membership. This strengthens continuous-admission evidence only; it cannot become binary feasibility. Exact non-0/1 counts on the original binary coordinates are 538, 650, 792 and 976 respectively, distinct from the tolerance-based counts in the table.

Every MIP exhausted its configured 300-second limit without a solver incumbent; no raw/recovered target vector exists to verify. No dual certificate exists. The review retains this absence instead of treating a timeout or fractional LP point as a positive or negative binary result. The previously accepted identity/class controls remain outside the ordinary-case denominator. October's class control was an identity draw, as documented in the prepared review.

Source options/results and one HiGHS header per log support exactly four LP calls followed by four MIP calls in the fixed order. File-log timing also places all LP completions before the first MIP and shows sequential MIPs within this arm. Configured totals were 120 LP seconds plus 1,200 MIP seconds. Actual LP time was 106.134722 seconds and MIP time 1,208.647303 seconds, totaling 1,314.782025 solver seconds. The MIP soft-limit overrun totals 8.647303 seconds. The execution/check phase was 1,344.254309 seconds against its 2,400-second allocation, with no phase overrun. These are per-arm runtime records, not a machine-isolated performance benchmark.

The original initial-arm gate remains `NOT_MET_INSUFFICIENT_ELIGIBLE_WEEKS`. The later continuation's certified-negative month list is empty; the augmented list is `[January]`, and `augmented_at_least_two_weeks` is false. This is informative nonconfirmation under the prescribed budget, not evidence that chronology never matters in April/October or that their binary targets are feasible.

Native physical reports and previous preparation checks were checked for consistency; this replay did not rebuild the CSV-level network. It used the existing reviewed stdlib reader and separate exact integer-dyadic point arithmetic. No producer artifact, original result or solver parameter was modified.
