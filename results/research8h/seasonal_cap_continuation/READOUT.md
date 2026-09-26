# April/October cap continuation readout

All four ordinary binary outcomes are UNKNOWN. Each continuous LP returned a numerically checked fractional point; each fixed 300-second U-only MIP timed out without an accepted binary witness. No exact negative was produced. This arm supplies neither a verified positive nor a verified negative for any ordinary binary target.

| Target | LP status | Fractional state coordinates | LP seconds | MIP status | MIP seconds | Raw MIP vector returned | Binary outcome |
|---|---|---:|---:|---|---:|---|---|
| seed_26093400 | Optimal | 537 | 22.286297 | Time limit reached | 306.859021 | False | UNKNOWN |
| seed_26093401 | Optimal | 604 | 29.776913 | Time limit reached | 300.091731 | False | UNKNOWN |
| seed_26094000 | Optimal | 658 | 27.971233 | Time limit reached | 301.527557 | False | UNKNOWN |
| seed_26094001 | Optimal | 911 | 26.100279 | Time limit reached | 300.168994 | False | UNKNOWN |

| Month | Reference fossil MWh | Fixed cap MWh | Class-control changed hours |
|---|---:|---:|---:|
| 04 | 42703.842794399716 | 43131 | 16 |
| 10 | 123932.139824399783 | 125172 | 0 |

The caps use the predeclared exact formula ceil(101 E / 100), where E is the recovered reference dispatch sum over exactly 23 fossil units. The October class control was an identity draw (zero changed hours); it was retained as declared and must not be described as a nontrivial perturbation. April class control changed 16 hours. Both identities and both class controls passed native checks and exact membership in the uniformly expanded binary64 model; their strict membership flags are false.

All four ordinary permuted reference schedules passed native static network/cap checks and exact expanded membership after removing only minimum-up/down rows. Their copied commitment schedules failed dwell checks. Such failures do not prove infeasibility: the unrestricted binary optimization remained unresolved. All four ordinary cases and both intended controls are retained.

The model has one aggregate fossil-MWh cap, zero individual means, 41 generators, 24 thermal units and the full 24-bus/38-branch DC network. The finite-horizon conventions and native constraints are unchanged. Exact positive/negative claims use uniform outward expansion of every finite row/column bound by Fraction.from_float(1e-5); a float tolerance check alone does not prove exact strict membership.

Exactly four LP30 calls completed before four conditional MIP300 calls. Actual LP solve time was 106.134721800 seconds; actual MIP time was 1208.647303000 seconds. Total phase elapsed was 1344.254309000 seconds against a 2,400-second allocation, with 0.000000000 seconds overrun. All individual soft-limit overruns and complete logs are retained; no retry, warm start or adaptive cap was used.

All 271 frozen input entries passed final size/hash checking. Manifest SHA256: `d5ae06005d333ee20b6ef5a466c72fd7c5530462ada923fc83a07e26b14e8055`. Source SHA256: `fe7253d9d6217a26ad3162422e91cc90dba83350526faed1443d54c8500b29ab`. Protocol SHA256: `14349e3ea185f0cd4089ab5d2745afbbd4c7d5240064893b5f3ffe0065b6bbb2`.

No new April/October week has a certified ordinary negative. Augmented evidence still includes only the previously known January success; the at-least-two-week augmented criterion is not met. The original January-only initial-arm gate remains NOT_MET and its old April/October NO_REFERENCE records remain unchanged. This later stronger-reference continuation does not prove that chronology is harmless, and continuous feasibility does not establish binary feasibility.

The separately recorded conditional uncapped follow-up has no eligible exact-cap-negative cases, so no new uncapped MIP or precision LP is triggered. Independent post-run review passed: independent_postrun_review.json and docs/research8h/SEASONAL_CAP_CONTINUATION_POSTRUN_REVIEW.md. It independently rechecked all 271 hashes and established exact expanded membership of all four LP points using separate integer-dyadic arithmetic with integrality relaxed. All four fail strict membership; all four ordinary binary outcomes remain UNKNOWN. No producer result was relabeled. The closed artifact inventory includes the review sidecar.
