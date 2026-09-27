# Closed native-expanded reverse cost comparison

**Independent post-run replay PASS.** The unchanged reverse/native-penalized target now has a checked certificate on the actual UnitCommitment.jl encoding under the declared mathematical endpoint expansion. Its signed optimum-cost difference from the independently closed identity is bounded by the outward six-decimal interval **[9972.898506, 63039.576470]**, in encoded UC objective units. The positive lower endpoint survives the target-specific containment correction.

The authoritative interval is

`[111201534240145780850057637442434037732943053161 / 11150372599265311570767859136324180752990208,`

` 21966086441831056243936642064517185594305761991 / 348449143727040986586495598010130648530944]`.

It equals `[L_reverse-U_identity, U_reverse-L_identity]`. The target lower/upper are approximately [1939365.3348704537, 1976293.0344030275]; the exact fractions remain in `run01/result.json`, `run01/signed_difference.json` and the independent report. The Q/R correction is approximately -0.014192088255340178. Neither the source-derived target proof nor the closed identity proof was replaced with a newly chosen dual or candidate.

The independent implementation verified all 2712 lifted coordinates, 4384 affine constraints, 3696 variable-constraint records and 960 exact binary declarations, together with the full native objective. The 2472 retained candidate coordinates stayed unchanged; only 240 disconnected mfg coordinates were lifted to zero. Expanded membership passes for the exact binary64 value of 1e-5. Strict nominal membership fails, with maximum violation `55/35184372088832`; the nominal upper therefore remains absent.

The reviewer reconstructed the 4384 raw signed multipliers, all 2472 residuals, the original selected proof, the 480 Q/R support correction and a direct interval-minimum bound. It rechecked actual target headroom relations and N equalities, inherited the independently accepted full nominal comparison for the remaining domains, and independently checked reference roles, exact endpoint subtraction and outward rounding. No expanded-model equality is asserted.

One producer arithmetic run took **22.2671693 seconds**; one successful independent arithmetic replay took **1.5929311 seconds**. Both were on the same host, with zero optimizers, Julia calls, model builds or new candidates. The reviewer adapts the distinct independent identity checker; it imports neither producer arithmetic nor shared mathematical helpers. All 499 original bindings, 34 copies and eight producer output files remained unchanged.

A first reviewer adaptation stopped in its initial provenance loop at a stale identity prepared-review path, before decoding scientific payloads or evaluating a point/dual. Its source and `FIRST_REVIEW_FAILURE.json` remain intact. The additive schema2 reviewer corrected provenance/schema and included the intended difference checks; no scientific input or producer file was edited. There was one successful full replay, not an undisclosed scientific retry.

This closes **one post hoc actual-code fidelity extension**, preserving the original two target orders × two service variants. Rotation/native and both hard-service target results remain untransferred. The difference concerns two separately informed optimal encoded costs, including production segments, startup and penalized curtailment. It is not decision regret, exact nominal optimality, fossil MWh, calibrated monetary impact, physical uncertainty, independent-network validation, a field result or a new algorithm.

Closure anchors:

- Producer result: `c0e81da4ca275b185820e8616cc3d81c995f666d977ee1e62199a846ed8ce23f`.
- Successful reviewer source, `../native_expanded_reverse_independent_review/postrun_review_schema2.py`: `187d25a96459ad4202a5340b551d09c244686626a0ed60526476e665a1313c2f`.
- Independent report, `postrun_review_schema2.json` in that directory: `44eaa3634ce474a0c587b0022bfb03e7b4de347403ee38ede7388d1810313e20`.
- Independent memo, `POSTRUN_REVIEW.md`: `2d5ddaac20c81674122d0a21027af8082b56b546a520fdc1f91f59c9f438530b`.

`final_artifact_inventory.csv` inventories this complete public arm, all five independent-review files (both source attempts and failure included), and the source/protocol/proposal/containment documents. It uses repository-relative paths and excludes itself. It is an arm inventory, not a claim to package an executable Julia environment or every external transitive dependency. Earlier pending-status records, source freezes, copied inputs, producer inventory and outputs are preserved; this final readout is appended and no scientific check was rerun for it.
