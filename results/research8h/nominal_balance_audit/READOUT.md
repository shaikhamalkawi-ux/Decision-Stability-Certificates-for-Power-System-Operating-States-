# Exact balance-redundancy audit: null separation result

All 672 tested aggregate-minus-nodal balance combinations lose exact algebraic redundancy when the archived binary64 coefficients are interpreted as rational numbers. None yields a separating box certificate, either in the strict nominal model or after uniform `1e-5` finite-bound expansion. This audit therefore does **not** establish nominal infeasibility, and a nonseparating test does **not** establish feasibility.

| Original week | Hours | Exactly redundant | Strict separating combinations | Expanded separating combinations | Maximum absolute RHS difference (MW) |
|---|---:|---:|---:|---:|---:|
| January | 168 | 0 | 0 | 0 | 1.3145040611561853e-13 |
| April | 168 | 0 | 0 | 0 | 1.2789769243681803e-13 |
| July | 168 | 0 | 0 | 0 | 2.4868995751603507e-13 |
| October | 168 | 0 | 0 | 0 | 1.4921397450962104e-13 |

Every difference has 15 nonzero angle coefficients. Its right-hand side lies within the exact range attainable over the supplied column box; that range is approximately `[-2.5001041393725872e-11, +2.5001041393725872e-11]` MW. Both signed orientations were retained for every hour. The expanded calculation includes the original 25-row multiplier norm as well as the combined-column coefficient norm, rather than treating the combined equality as one independently widened row.

The original read-only audit completed once with zero optimization calls and preserved all 15 frozen input bindings. A separate replay independently decoded the NPZ/NPY arrays and used common-denominator integer arithmetic, without importing the audit's Fraction implementation or standalone verifier. It reproduced every coefficient, right-hand side, box endpoint, strict/expanded classification, and both signed gaps for all 672 records / 1,344 orientations. It also rechecked every frozen file's size and hash before and after its run. The replay exited successfully; its machine-readable status is `INDEPENDENT_INTEGER_DYADIC_REPLAY_PASS` in `independent_replay.json`.

Evidence bindings:

- Original summary SHA-256: `4f318fbe5510721ba68c9cd057a7efa441fa0f29e3b06f71283e6a64b3ac3328`.
- Original freeze SHA-256: `fff9aedad3f9b29df7b4cfdb67ff1c906653d9c152e385419966263fc522bd4f`.
- Independent replay source SHA-256: `852614e1d77ee4f2b4c88b97edb04e6296e3984663f372750aecc453f9ce567d`.
- Independent replay result SHA-256: `94651de2095f3555c7462101722155434b51b017cab383dfa164ddc6eebd9d74`.

The scope is this fixed balance-identity diagnostic over the four original reference models. It neither proves general numerical stability nor checks all possible row combinations or the extra relations imposed by other network/operating constraints. It does not explain away the nominal residuals of saved positive vectors, justify changing the tolerance, or alter the separately verified expanded positive and negative results. No archived coefficient, model, witness or previous outcome was repaired or replaced.

The independent replay ran once after the original summary existed, on Python 3.12.14 with `-I -S`. Review-script compilation produced no experimental output or optimizer call. Its 1.933-second arithmetic runtime and the original audit's 614.500 seconds are recorded for provenance, not as a performance comparison.
