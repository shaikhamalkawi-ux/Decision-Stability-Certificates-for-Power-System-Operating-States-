# Independent strict branch-flow energy post-run review

Verdict: PASS. One independent replay completed in 53.302400200016564 seconds with no optimizer or producer-source import. All 355 frozen inputs, all 453 producer files snapshotted before replay, and the separately pinned raw GEN source remained unchanged.

Every original row, finite column bound and all 12,096 binary states of the three 34,512-row / 29,400-column uncapped flow models were checked with exact rational arithmetic at tau=0. All three full points pass. The identity is the unchanged inherited strict point; both targets use their prospectively fixed schedules. Direct native checks also pass availability, hydro, committed output, exact nodal-sum conservation, branch-flow definitions/incidence/limits, canonical transitions, clipped residence and on-on ramps. Raw GEN bus/category/thermal/dwell/hourly-ramp data agree with the frozen native specifications. No old rounded aggregate balance was restored and no uncapped check silently ignored a failed cap.

All 15 predetermined lower-bound candidates were re-evaluated independently from their actual matrices, objectives and signed multipliers, including every residual coefficient and finite-box correction. Invalid endpoint signs remain rejected. The first largest valid candidate is +1_projected in each of the three models. No numerical objective, stationarity claim or solver optimum status substitutes for these exact bounds.

Both targets retain all 168 hourly reconstruction records; all 336 candidate hourly row/box memberships pass independently and agree with the assembled full points. The five numerical calls total 9.714922999992268 seconds. Producer arithmetic was 388.1135927000141 seconds and the full phase 404.7295330000052 seconds, without skips or overruns. The durable initial start passed the fixed 03:35 UTC admission gate. Per-call admission records and reviewed post-I/O guards were checked; there is no separately archived timestamp for the exact post-I/O run instant.

## Certified intervals

Endpoints below are rounded outward to six decimal places. Exact rational values in the report are authoritative.

| Case | Lower fossil MWh | Upper fossil MWh |
| --- | ---: | ---: |
| January identity | 22616.830716 | 22964.941240 |
| seed_26093200 | 23532.980654 | 23952.175431 |
| seed_26093201 | 23824.881499 | 24024.798984 |

| Target | Difference of binary optimum energies, MWh | Relative difference, % |
| --- | ---: | ---: |
| seed_26093200 | [568.039414, 1335.344714] | [2.473506, 5.904208] |
| seed_26093201 | [859.940259, 1407.968267] | [3.744578, 6.225312] |

The difference formula is [LT-UI, UT-LI], not a comparison of two supposedly optimal incumbents. Both lower endpoints are positive and both targets have finite strict binary upper witnesses. Thus these are finite strict optimum-difference enclosures in the separately declared flow-conserving DC encoding. They neither establish exact optima nor relabel results in the earlier rounded angle/aggregate encoding. They are the same two January paired cases, not additional replications or field evidence. No method-priority claim follows.

## Stable evidence

- Reviewer source: results/research8h/branch_flow_energy_independent_review/postrun_review.py; SHA256 6f6c53d69c2a7eb594d697b631140481b2c614eea8bade846b3cabebede0a76a.
- Reviewer report: results/research8h/branch_flow_energy_independent_review/postrun_review.json; SHA256 ccd2bf67e39d985082707f97116276b3534c11dbbbd20430fe3637bc49739985.
- Producer prepared manifest: 7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7.
- Additional raw GEN binding: 988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068.

The producer may append a final readout/inventory after parent review while preserving all files checked here.
