# Independent OR-LIB prepared archive review

PASS, 2026-09-27. This is a byte, schema and input-transport audit of the already prepared archive, not a model rebuild, solver run, witness check or Julia/JuMP export comparison.

Trusted manifest: `prepared01/manifest.json`, SHA256 `8cf0b37220f521cd1365c4a0ad05199bafb0a634eeb28cc0642c1e31b4c3b205`. The single review checked all 25 payload hashes and sizes, the complete 26-file inventory including the manifest, safe unique paths, and unchanged bytes at close. Fourteen pinned upstream files, the compressed/raw selected case, normalized case, adapter/protocol snapshots and six models are bound. The raw decompressed case SHA256 is `3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308`.

Every model has 4,384 rows, 2,472 columns and exactly 960 binary coordinates: all U, Y, Z and startup-category D coordinates for ten units and 24 hours. Names and sparse coordinates are unique; all variable bounds and objective coefficients are finite. For each order the hard-service variant has identical rows, costs and binary mask and differs only in the 24 curtailment upper bounds (native load versus zero). Shortfall and single-bus net-injection boxes remain zero.

The identity and the two prospectively declared orders match exactly. Reverse and left-rotate each change 16 interior positions and keep the first and last four source hours fixed. The full load/reserve/penalty package multiset is preserved. The audit checks every changed load/reserve row endpoint and curtailment upper bound/cost against its declared source hour; every other row coefficient, endpoint, column, cost and binary coordinate is identical to the corresponding identity model. Raw load and reserve arrays agree with the normalized case; the absent raw penalty field uses 1,000 throughout. The pinned `upstream/src/instance/read.jl` lines 187–188 explicitly supplies that default.

The separate selected-builder source review supplies the source-level normalization rationale. This prepared-archive review does not independently execute or reconstruct that native builder and retains `runtime_JuMP_matrix_equivalence: NOT_TESTED`. It establishes no scientific feasible/infeasible or operating-cost outcome. This adapter-preparation PASS is distinct from the later solver-preparation receipt required by the solver harness.

The review ran once, exited zero, and took 0.586120399995707 seconds internally. It imported only standard-library modules, with zero adapter imports, model rebuilds, witness calls or optimizer calls.

Stable review artifacts:

- `INDEPENDENT_PREPARED_REVIEW.py`: SHA256 `8b4f5e4417ac75645f866f06df9b369f2e7fd671e3172af3b91456dec391fd97`.
- `INDEPENDENT_PREPARED_REVIEW.json`: SHA256 `29bbf8a5e661bc9027262a004fc6c2a66c3df1ef687eaab29dfdfbba9586a3e8`.

No archived producer file was modified.
