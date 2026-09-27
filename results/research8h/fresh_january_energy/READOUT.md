# Fresh January uncapped energy qualification

Producer results are closed; independent post-run replay is required before publication. All four prescribed targets are retained regardless of their prior capped labels. No source, protocol, case or solver limit was changed after the 378-file freeze.

| Week | Target | Binary upper status | Exact lower, floor MWh | Binary upper, ceiling MWh | Optimum difference interval MWh | Relative optimum interval % |
|---|---|---|---:|---:|---|---|
| 2 | seed_26093210 | VERIFIED_BINARY_UPPER | 26843.071532 | 27692.932211 | [574.017996, 1815.622131] | [2.185149, 7.016271] |
| 2 | seed_26093211 | VERIFIED_BINARY_UPPER | 26358.110476 | 28181.300147 | [89.056939, 2303.990067] | [0.339018, 8.903515] |
| 3 | seed_26093220 | VERIFIED_BINARY_UPPER | 48922.359897 | 49324.625240 | [1082.076498, 1856.243776] | [2.261852, 3.910485] |
| 3 | seed_26093221 | VERIFIED_BINARY_UPPER | 48889.107475 | 49926.768980 | [1048.824076, 2458.387516] | [2.192345, 5.179001] |

All values concern the same uncapped uniformly expanded original-binary models. The rows remove only each target's frozen fossil-energy cap; there are no named-unit mean targets. Fossil output means electricity from the native 23 Coal/Oil/NG units over one-hour intervals, excluding nuclear. It is not fuel, emissions or financial cost.

Exact objective lower bounds come from signed row multipliers, finite-box residual correction and uniform finite-bound widening by Fraction.from_float(1e-5). The unchanged reference binary witnesses supply the weekly upper bounds. Accepted target witnesses must satisfy every widened row/column bound and all 12,096 original binary coordinates, plus the native no-cap check. Strict nominal flags are reported separately in summary.csv; tolerance-expanded membership is not strict membership or exact optimality.

For each week the optimum difference is enclosed by [L_target - U_identity, U_target - L_identity]. The separate excess over the chosen reference incumbent uses [L_target - U_identity, U_target - U_identity]. Relative optimum bounds use [L_target/U_identity - 1, U_target/L_identity - 1] only with positive lower bounds. These are different quantities. Rational records in energy_brackets.json are authoritative; displayed intervals round outward. A NO_UPPER case establishes neither finite uncapped feasibility nor a finite difference interval. Nonpositive or zero-containing intervals are retained unchanged.

The append-only new_cap_implication.json compares each exact uncapped lower bound with the original cap plus exact tau. Only a strict inequality L > B+tau proves exclusion under that old expanded cap. It records any new implication for a historical UNKNOWN without modifying the historical capped ledger.

| Target | MIP status | MIP seconds | Numerical gap | LP status | LP seconds |
|---|---|---:|---:|---|---:|
| seed_26093210 | Time limit reached | 600.246668 | 0.03053509177595077 | Optimal | 1.288450 |
| seed_26093211 | Time limit reached | 600.127971 | 0.064551575439956 | Optimal | 1.653628 |
| seed_26093220 | Time limit reached | 600.169075 | 0.008041673351391478 | Optimal | 2.641324 |
| seed_26093221 | Time limit reached | 600.343442 | 0.020724580532467205 | Optimal | 2.979178 |

Completed calls: 2 identity LPs, 4 target MIPs and 4 target LPs; zero new identity MIPs. Phase elapsed 2434.342626 s against the 3600 s soft allocation; phase overrun 0.000000 s, UTC cutoff overrun 0.000000 s. Actual solver soft-limit overruns total 0.887156 s.

The admission-to-recorded-start latency audit found 0 observed discrepancies; maximum decision-to-start latency was 0.009250 s. allocation_audit.json preserves every decision and actual timestamp. The phase-at-start check extrapolates the recorded monotonic remaining time using wall-clock latency, and does not establish a hard filesystem-latency bound. Actual starts/ends and observed overruns remain authoritative.

These are two previously fixed January weeks of the same isolated Area 1 model. They are not independent-network replications, field interventions or claims about realistic reconstructed weather. The same original initial/terminal conventions, native arrays, DC network and no-storage scope remain in force. Solver timings on the shared host are not performance benchmarks.

Prepared manifest SHA256: `44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a`. All 378 frozen bindings were rehashed after completion. The producer summary and this readout make no claim that the separate independent post-run gate has already passed.
