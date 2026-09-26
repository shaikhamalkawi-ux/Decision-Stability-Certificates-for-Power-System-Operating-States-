# Prospective transfer: both fixed rules cover eight new same-week negatives

Both previously learned rules rejected all eight fresh ordinary twins that the full LP rejected. Every negative has an exact rational certificate for the archived binary64 model, robust to outward `1e-5` relaxation of every finite row/column bound. Neither rule falsely rejected any of the eight independently verified positive controls.

All 16 cases and all 48 planned LPs were retained. The sample froze at `2026-09-26T19:57:05.605902+00:00`, before the first transfer solve. The phase completed in **727.906 seconds** (about 12.1 minutes), within the frozen 20-minute budget. Every LP used the same configured 30-second cap; none was rerun or extended. Solver wall times can slightly exceed a configured cap because of solver stopping granularity; both time-limited runs are preserved as unresolved.

| Case seed | Kind | Full LP | Fixed two-CC rule | Fixed locality48 rule |
|---|---|---|---|---|
| 26092700 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092701 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092702 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092703 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092704 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092705 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092706 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092707 | Ordinary | Exact rejection | Exact rejection | Exact rejection |
| 26092800 | Positive control | LP admitted | LP admitted | LP admitted |
| 26092801 | Positive control | LP admitted | LP admitted | LP admitted |
| 26092802 | Positive control | LP admitted | LP admitted | LP admitted |
| 26092803 | Positive control | Time limit; unresolved | LP admitted | LP admitted |
| 26092804 | Positive control | LP admitted | LP admitted | LP admitted |
| 26092805 | Positive control | LP admitted | LP admitted | LP admitted |
| 26092806 | Positive control | Time limit; unresolved | LP admitted | LP admitted |
| 26092807 | Positive control | LP admitted | LP admitted | LP admitted |

There are **24 exact robust negatives**, **22 verified continuous LP admissions**, and **2 unresolved solver runs**. The restricted-rule coverage denominator is the eight ordinary twins with full-LP exact rejection: two-CC coverage **8/8**, locality48 coverage **8/8**. No unknown outcome was recoded as admission or rejection. Positive-control false rejections are **0/8 cases** for each rule. The two unresolved full-LP runs remain solver-unknown, while those cases separately possess verified binary witnesses for the modeled DC network, native dwell and on/on-ramp requirements. Their positive labels come from those witnesses, not from the time-limited solver.

## What was fixed and what changed

Every case uses the same repaired July target means for all 41 units and the same source parameters. Ordinary seeds 26092700–26092707 permute all 72 interior hourly packages jointly, leaving the first/last 48 hours unchanged. Packages include load, availability, the seed dispatch and all thermal statuses. Each reordered seed passes the static/DC-network checks. Rejection is established by the LP certificates, never merely by an invalid replay of that particular seed schedule.

Positive seeds 26092800–26092807 permute packages only within identical complete 24-bit commitment classes. There are 21 classes in the interior, with 62 potentially movable hours. Their full U sequence stays pointwise identical to the repaired witness, and Y/Z are recomputed. All eight pass native chronology, rounded output coupling, on/on ramps, DC nodal/aggregate balance, branch limits and all three corresponding matrices before the first LP. Their serialized seed vectors are checked against each model again during the run.

All 16 generated orders are distinct, and none duplicates the 17 recorded development orders. Ordinary moved-hour counts are 72, 72, 71, 72, 71, 71, 72, 72; positive counts are 55, 50, 52, 55, 56, 49, 50, 47. A separate read-only reviewer reproduced every order/hash from the seed recipe and published commitment witness. No duplicate was discarded or replaced.

The full LP has 24,305 rows. The two-CC model has 9,609: only `107_CC_1` and `118_CC_1` retain transition, exclusive-transition, minimum-up and minimum-down rows. All other units retain static output bounds and their complete means. This tests the two units jointly; it does not isolate either unit alone. The locality model has 18,313 rows: all-unit transition/exclusivity remains global, while only dwell rows with complete direct variable support in hours **60–107** survive. All three keep the original 18,984 columns and column bounds. Rules, unit identities and window placement were never changed per case.

## Evidence and reproducibility

Each case directory contains its frozen permutation, complete numerical case arrays, generation/control checks, and three model directories. The model directories retain matrices, bounds, row metadata with original row IDs, solver status/logs, and either a checked continuous vector or dual-ray/certificate artifacts when obtained. `sample_freeze.json` and `input_manifest.csv` bind the sample and source; `coverage.json`, `summary.csv` and `completion.json` retain all outcomes. `model_column_order.json` identifies P/U/Y/Z columns and the full thermal-bit order; `environment.json` records the runtime versions.

Every selected negative certificate was replayed from disk with exact rational arithmetic and its robustness check. Every admitted LP vector was replayed against its archived model. The two timeouts have no verified solver vector and are retained with that status; their separately checked positive seed vectors remain archived. The separate post-run audit **passed**: all 32 restricted matrices and row bounds exactly match the corresponding full-model row subsets, all column bounds and input/sample hashes match, and there are zero positive-control or cross-model contradictions. Its 48 outcome records comprise 24 verified exact certificates, 22 verified continuous vectors and the two explicitly unresolved outcomes; no artifact was invented for a timeout. Results are in `post_run_audit.json` and `archive_replay.json`.

Run `python src/research8h_transfer.py --verify-archived` for solver-free replay of recorded outcomes. Run `python results/research8h/transfer/audit_artifacts.py` for replay plus the cross-model/source-binding audit. Existing prospective run directories are protected against overwrite.

## Interpretation limits

This is **prospective rule transfer to new seeds within the same repaired July week** after selecting the rules on earlier development cases. It supports those fixed rules on these eight ordinary permutations. It does not establish generalization to new weeks, networks, target means or permutation mechanisms. The positive controls deliberately use a different constrained generator and share the original commitment sequence; zero false rejections here is a feasibility-control result, not a population-specificity estimate.

All-week means and static information remain global. The locality model additionally keeps global transition linkage, including dependence just outside its direct-support window. Its success is not a claim of 48-hour raw-data sufficiency or minimum temporal memory. Continuous LP admission alone never establishes UC feasibility. The exact negative arithmetic concerns the archived floating-coefficient mathematical models, while numerical positive witness checks use the stated `1e-5` tolerance; neither establishes omitted AC physics or physical measurement exactness.

The transfer process ran one simplex LP at a time with HiGHS `threads=1` and presolve off. Other experiments ran concurrently on the shared machine. `execution_context.json` records that condition; elapsed times are execution logs, not an isolated performance benchmark or a measured speedup claim.
