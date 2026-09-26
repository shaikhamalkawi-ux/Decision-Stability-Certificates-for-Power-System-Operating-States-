# Post-pilot LP certificate readout

The identity has a verified continuous LP solution. All four previously selected reordered cases are LP-infeasible and each now has an exactly checked Farkas certificate for its archived binary64 model. The positive identity's existing binary network witness also passed the independently assembled matrix check; its largest row residual was 6.83e-12.

| Case | Nonzero row multipliers | Distinct hours in supported rows | Uniform bound relaxation threshold |
|---|---:|---:|---:|
| seed_26092600 | 949 | 166 | 0.01919475 |
| seed_26092601 | 656 | 168 | 0.02231694 |
| seed_26092602 | 1017 | 163 | 0.01563107 |
| seed_26092603 | 908 | 168 | 0.02067671 |

Every certificate still separates the constraints after all finite row and variable bounds are relaxed outward by 1e-5 in their respective units. The threshold column is scale-independent under positive rescaling of the entire multiplier vector, but mixes the model's MW and dimensionless bound units; it is not a physical robustness parameter. Exact arithmetic uses rational values of the archived binary64 numbers, not hypothetical exact measurements.

Raw HiGHS rays had tiny sign-inadmissible row multipliers (largest magnitudes across cases 4.55e-13 to 2.04e-10). The initial strict checker rejected these rays. A second run archived the raw rays and explicitly projected each candidate into the row-sign cone. The complete separation was then recalculated exactly; deleted values were never assumed mathematically zero. Both orientations and both raw/projected attempts are recorded.

Each case was solved twice. Initial limits were 60 seconds, final limits 45 seconds, an implementation deviation within the 60-second maximum budget; all actual cumulative per-case solver times remained below 6 seconds. Full details are in development_history.json. No additional solve was performed to alter that historical record.

The source protocol document is unchanged. These cases are post-pilot development, not held-out validation. The certificate supports retain most or all hours, and target-mean rows themselves depend on all 168 hours. This proves four order-dependent impossibility results; it does not establish minimal temporal memory or compressed input sufficiency.

To replay without an optimizer:

```
python src/temporal_lp_certificate.py --verify-archived
```

Replay checks matrix/bounds hashes against each case result and the certificate, then recomputes exact arithmetic from saved multipliers. It also verifies the identity continuous vector. The independently assembled matrices and all bounds are archived; source reconstruction is separately testable from the listed input hashes.
