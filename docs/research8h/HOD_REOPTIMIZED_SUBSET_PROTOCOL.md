# HOD fixed restricted-model LP follow-up

This is a post-label, same-week explanation study specified after all six fixed-ray arithmetic candidates failed to separate. A failed supplied multiplier does not determine restricted-model feasibility. Retain the six nulls, the earlier original-January rule failures and all new entries. This arm adds no new perturbation, unit/window search, sparse optimization or primary replication.

## Gates

Source: src/research8h_hod_reoptimized_subsets.py. Output: results/research8h/hod_reoptimized_subsets. Separate --prepare-only and --run-prepared modes. Root reviews source/protocol before preparation. Preparation imports no numerical solver package and performs no optimizer call. It freezes all inputs/models/rules/controls before any target result. Independent prepared PASS and a separate explicit root execution GO are mandatory. Frozen source, protocol and input files then remain unchanged. Old arms are read only.

## Exactly four unchanged models

Order is fixed: seed26093200/two_cc, seed26093200/locality48, seed26093201/two_cc, seed26093201/locality48. Copy the already independently mapped subset archives from hod_fixed_ray_transfer/models exactly, with their original full U/Y/Z masks. Independently compare each actual row, row bound, column bound, original-row map and semantic label to the parent HOD full model under the unchanged rule. Their LP integrality is relaxed for this study; no binary solve occurs.

- two_cc: keep all four temporal families only for107_CC_1 and118_CC_1; retain every static/network/cap row and every column/box.19,985 rows and23,016 columns. This removes other units' transition/exclusivity rows too, so it is not dwell-only.
- locality48: keep transition/exclusivity globally. Keep a complete dwell row only when every actual nonzero U/Y/Z coordinate lies in hours60 through107.28,689 rows, including1,023 minimum-up and1,001 minimum-down rows,23,016 columns. This is not an isolated48-hour model.

Both retain the full168-hour DC/static background and fossil cap23,195MWh, with no unit-mean targets. Retained model rows, nonzero proof rows and raw input data are distinct quantities.

Bind the prior106-input manifest, all six candidate archives/exact outcomes, their complete independent root review, the HOD125-input manifest, actual models and all local preparation/checker source dependencies. The old rule implementation and stdlib exact kernel are pinned by hash. Preparation generates no new subset rule.

## All declared positive controls

Use both previously exact-expanded original-binary positive HOD inputs: january_identity and seed26100200. Apply both unchanged masks, giving four declared control/rule memberships. Bind their full models, original masks, vectors, completed independent full-point review and old subset maps. Prove exact row deletion with all boxes/columns unchanged; existing full expanded membership then implies all four reduced memberships. No new control solve or point repair. Strict nominal membership is not claimed. Any inconsistency halts preparation.

## One bounded LP per entry

Exactly one attempted LP per scheduled entry unless its start guard fails: zero objective, simplex, presolve off, threads1, random seed0, time limit30 seconds. Maximum configured solver time120 seconds. No MIP, warm start, retries, replacement case, alternate objective or ray-recovery optimization. The300-second soft phase starts at entry to run-prepared, before manifest checks and loading. Immediately after solver/model construction and immediately before each solver.run, require at least35 seconds remaining both in that phase and before2026-09-27T04:00:00UTC. Write the initial admission decision, then recheck both clocks after that file write immediately before solver.run. Preserve the original decision and the final recheck timestamp/remaining budgets; keep the final recheck in memory until the call or no-call skip returns. Record skipped calls and zero solver time, actual call timestamps, actual duration, soft-limit/phase/cutoff overruns and the complete four-entry denominator. Limits/guards are not hard process deadlines. Root coordinates shared-host use.

Use getDualRayExist only to ask whether the completed LP already has a ray. Call getDualRay only when that status is OK and existence is true. No existing ray means no recovery attempt; the outcome remains UNKNOWN unless an exact returned continuous point passes. The installed highspy1.12.0 API documentation was inspected with an import-only probe; no solver object/model/run was created by that probe.

## Exact outcomes

Save any returned primal and ray. Test finite returned primals as exact binary64 numbers against every row/box using a zero integrality mask. Classifications are:

- CERTIFIED_EXPANDED_INFEASIBLE: a complete exact Farkas separation remains positive after every finite row/column endpoint is widened by tau=Fraction.from_float(1e-5).
- VERIFIED_EXPANDED_CONTINUOUS_POINT: an exact continuous point belongs to that widened restricted model. It does not establish binary feasibility or reverse the known full-model negative.
- UNKNOWN: no accepted proof/point, a numerical-only label, strict-only separation, unavailable ray, invalid returned values or a guard skip. Preserve diagnostics separately.

For an already available ray, the exact fixed candidate order is raw signed vector followed by explicit projection of entries selecting infinite row endpoints to zero. Preserve raw values, the complete removed-row list and both exact candidate checks. No sign reversal, thresholding, further projection, window/unit tuning or adaptive support search. Select the first exact-expanded separating candidate. A numerical ray or successful solver status alone is never evidence. If both an exact expanded point and separating ray pass on the same model, halt on contradiction.

The exact checker computes the complete signed row combination, finite-box maximum and widened-endpoint gap; no floating summation establishes a certificate. Bind the chosen ray to matrix/bounds/labels, raw ray and frozen manifest. Report retained row counts separately from nonzero multiplier counts, family counts and temporal unit/hour support; do not count bus or branch IDs as generating units.

## Optional direct energy meaning, fixed before execution

For every accepted ray with strictly negative cap multiplier, remove that cap term and divide the remaining signed multipliers by its absolute value using exact rational arithmetic. On the cap-deleted restricted matrix and unchanged box, independently recompute the objective lower bound for the actual fossil-cap coefficient vector: beta+min_box(c-A^T*d)*x, widened by subtracting tau times the two L1 norms. Compare with a direct widened-endpoint calculation and the identity L=B+tau+expanded_ray_gap/abs(cap_multiplier). It must exceed B+tau. Preserve normalized rational multipliers, stationarity residual, exact lower bound and MWh margin. This arithmetic adds no solve. An absent/nonnegative cap coefficient yields an explicit unavailable status. No finite upper, exact optimum or actual dispatch cost is inferred. Ray gaps before this normalization are not MWh.

## Interpretation and stopping

Success shows only sufficiency of an already fixed temporal restriction on complete global background. A locality proof is not a claim that raw observations outside48 hours are unnecessary; a two_cc proof does not identify two uniquely necessary generators. A verified continuous point excludes a linear Farkas contradiction for that expanded restriction, while the full UC result remains intact. Keep every null/UNKNOWN and all four entries. No further numerical study or sparsity search is authorized by any result. Independent post-run hash/proof/point/energy/accounting replay and root review are required before publication. This is an explanatory application of established LP certificates, not a new IIS method, minimum-information theorem, external-network replication or field trial.
