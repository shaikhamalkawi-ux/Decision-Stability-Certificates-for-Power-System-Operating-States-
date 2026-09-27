# Fresh January weeks: hour-of-day-preserving target results

Three of four fixed ordinary targets have independently replayed exact infeasibility certificates in the expanded continuous model and therefore in its binary subset. These negatives occur in both fresh January weeks. The remaining target is UNKNOWN after its sole 300-second binary search returned no incumbent. Both week identities and both preselected hour-of-day/commitment-class controls have independently checked full-network binary positive witnesses in the same expanded-model convention.

| Week | Ordinary seed | Fixed fossil cap (MWh) | Changed hours | Final binary-model verdict | LP seconds | MIP seconds |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| January 8–14 | 26093210 | 26532 | 46 | CERTIFIED_INFEASIBLE_EXPANDED_MODEL | 5.354152000014437 | No call |
| January 8–14 | 26093211 | 26532 | 51 | UNKNOWN; time limit, no incumbent | 4.879603999987012 | 300.4468343000044 |
| January 15–21 | 26093220 | 48319 | 44 | CERTIFIED_INFEASIBLE_EXPANDED_MODEL | 5.313145699998131 | No call |
| January 15–21 | 26093221 | 48319 | 48 | CERTIFIED_INFEASIBLE_EXPANDED_MODEL | 4.626020700001391 | No call |

The denominator is all four preselected ordinary cases. Exactly four LP calls ran first, followed by the one conditional U-only MIP. Total LP time was 20.17292240000097 seconds; MIP time was 300.4468343000044 seconds, including a 0.4468343000044-second soft-limit overrun. The target phase took 337.61820259998785 seconds within its 2100-second budget. There were no retries, substitutions, additional references, or target optimization calls. All 246 frozen input bindings pass after execution. The 04:00 UTC cutoff and phase guards applied at actual optimizer call sites. Independent replay also establishes that seed 26093211's LP point is exactly feasible in the expanded model with integrality disabled and is genuinely nonbinary; this does not change its UNKNOWN binary verdict.

## What was preserved and what was checked

The two windows are native rows 168:336 and 336:504, the fixed lowest unused January weeks. Each permutation fixes the first and last 48 hours, preserves hour of day, and jointly permutes every native hourly physical package. The reference dispatch/commitment/angle payload roundtrips bitwise through each permutation and its inverse, and the exact fossil sum is unchanged. All four permuted reference schedules pass the exact static model and native static-network/cap checks. Their full schedules fail dwell constraints; that failure by itself is not an infeasibility argument. The three exact Farkas certificates establish unrestricted model rejection independently of that copied schedule.

The full-network reference energy sums are 26269.05353649975 and 47840.28339873613 MWh. The caps are the exact integers `ceil(101 E / 100)` computed from their archived binary64-rational sums, using the same 23 fossil units and excluding nuclear. There are no individual-unit mean equalities. The references are verified feasible incumbents, not proven optimal schedules.

Class-control seeds 26100210 and 26100220 changed 25 and 2 hours respectively. Both retain the reference's exact numeric binary U schedule and pass full expanded membership after canonical Y/Z reconstruction. Signed zero has equal numeric binary meaning; separate physical-payload inverse checks remain bitwise. Neither control was redrawn. The second control's small number of changes is retained in the evidence.

## Exact certificate scope

All accepted positives and negatives use the archived binary64-coefficient mathematical model with every finite row and column bound expanded outward by exactly `Fraction.from_float(1e-5)`. Positive controls and references fail strict nominal membership by small residuals; exact expanded membership is the admission convention. The three negative rays also separate the strict model. This uniform mixed-unit expansion is a declared computational convention, not a physical measurement uncertainty model.

| Negative seed | Nonzero row multipliers | Nonzero combined columns | Hours labeled on supported rows | Exact robust gap, displayed approximately |
| --- | ---: | ---: | ---: | ---: |
| 26093210 | 1701 | 5442 | 141 | 5865.97893763795 |
| 26093220 | 1365 | 4691 | 154 | 986.3627626007343 |
| 26093221 | 1450 | 4935 | 153 | 1195.2714764285124 |

The gaps are unnormalized ray units, not MWh penalties. Exact numerators/denominators, complete raw rays, every tested orientation/sign-cone projection, selected sparse multipliers, and model/manifest hashes are archived per case. Raw candidates selecting infinite row bounds were rejected; sign-admissible projections were accepted only after complete exact separation was recomputed. Each proof uses the global cap over all 168 hours and 3864 fossil dispatch coordinates, its reference-energy dependency, and variable bounds. Row/hour support is not minimum information or minimum memory.

This arm supplies fresh-week, within-January replication under hour-of-day-preserving rearrangements of one RTS Area-1 network. It is not evidence of cross-network, cross-season, AC-security, or field-operation performance, and it does not establish the unknown fourth case. It does not alter the original seasonal arm's unmet eligibility gate or the later April/October UNKNOWN outcomes. The design was approved before the root inspected the previous hour-of-day results; it was not approved before those outcomes existed.

Independent reference replays, prepared-target review, and negative-certificate replays are retained in the separate review artifacts. The independent final ledger at `results/research8h/fresh_targets_postrun_review/final_ledger.json` passes all four classifications, exact continuous-point scope, call/log accounting, absence of a MIP incumbent, and final input/ray/result hashes. No reviewer optimizer calls were needed.
