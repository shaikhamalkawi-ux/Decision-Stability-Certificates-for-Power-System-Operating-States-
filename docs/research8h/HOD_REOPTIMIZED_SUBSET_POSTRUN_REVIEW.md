# Independent post-run review: fixed HOD subset LPs

Verdict: PASS for all four exact expanded continuous points and complete accounting. Neither fixed restriction yields an LP contradiction on these two HOD inputs: each restricted expanded LP has a verified point. This does not establish binary feasibility for either the restriction or the full model, and it does not reverse the separately certified full-model negatives.

| Fixed entry | Continuous expanded membership | Original state coordinates not exactly binary | Solver seconds |
|---|---|---:|---:|
| 26093200 / two_cc | Pass | 245 | 0.3505886000057217 |
| 26093200 / locality48 | Pass | 273 | 0.7735474000219256 |
| 26093201 / two_cc | Pass | 255 | 0.3303891000105068 |
| 26093201 / locality48 | Pass | 382 | 0.7631160999881104 |

The reviewer decoded each archived matrix, box and point, applied a zero integrality mask explicitly, and recomputed every exact rational row/box residual using the previously reviewed standalone kernel. Each complete result matched its archived check. All points are expanded-only, not strict nominal points. The nonbinary counts use exact comparison with zero and one; no rounding of state values occurred.

All 155 frozen input bindings matched, and a snapshot of every producer file matched before and after review. The schedule and complete four-entry denominator were preserved. Every case has one solver banner, the declared LP30/simplex/presolve-off/thread-one/seed-zero options, successful post-decision clock rechecks and a single recorded call. Total solver time was 2.2176412000262644 seconds; phase time was 6.278909800021211 seconds. Solver, phase and UTC overruns were zero.

No accepted ray, normalized energy bound, target binary witness or additional optimizer call exists in this arm. Its four positive control/rule memberships remain supported by the separately completed independent prepared review. The previous six failed coefficient-transfer candidates remain unchanged. The result is a negative finding about the sufficiency of these two fixed LP explanation rules for this perturbation family, not a claim that the full unit-commitment decision is feasible or that no other explanation can succeed.

The reviewer ran one archived post-run replay, exit 0, with zero optimizer imports/calls and no producer import. Evidence is `results/research8h/hod_reoptimized_subsets_independent_review/postrun_review.json`, SHA256 `6ed59296e66737a113acb73b1d4ff0c2a5c47ccec1f65de3d0198d8ac4ce6bf8`; its independent source is `postrun_review.py`. No producer source, protocol or result was edited.
