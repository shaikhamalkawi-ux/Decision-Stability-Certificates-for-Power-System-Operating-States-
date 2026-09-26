# Strict modeled-equivalence energy pooling: completed diagnostic

All eight archived-week min-up/down rejections survive replacement of the 41 individual weekly mean equalities by 26 strictly matched group-mean equalities. No run timed out or remained unresolved. HiGHS 1.12.0 returned Infeasible for each case under the frozen 60-second, one-thread, seed-zero budget.

| First week of 2020 | Prior individual-target status | Pooled-target status | Solve time (s) |
|---|---|---|---:|
| January | Infeasible | Infeasible | 0.375 |
| February | Infeasible | Infeasible | 0.578 |
| March | Infeasible | Infeasible | 0.407 |
| April | Infeasible | Infeasible | 0.266 |
| May | Infeasible | Infeasible | 0.313 |
| June | Infeasible | Infeasible | 0.344 |
| July | Infeasible | Infeasible | 1.109 |
| October | Infeasible | Infeasible | 0.594 |

The groups retain equality of all 55 non-identifier source fields and the complete annual represented availability profiles. The exclusions are the two unit identifiers and the author model's artificial index cost tie breaker. All source cost curves and derived base marginal costs remain equal. There are 8 nonsingleton groups, including 7 thermal groups; 24 thermal units remain distinct physical/commitment units within 14 thermal energy groups. The 6-unit hydro group retains each individual fixed native output.

The nonsingleton memberships are `101_CT_1–2`, `101_STEAM_3–4`, `102_CT_1–2`, `102_STEAM_3–4`, `113_CT_1–4`, `115_STEAM_1–2`, `123_CT_1/4/5`, and `122_HYDRO_1–6`. The complete inventory is in `group_inventory.json` and `group_members.csv`. Groups with identical `Unit-specific` source emissions placeholders are explicitly flagged: represented equality is not a claim of actual emissions equality. This experiment has no emissions constraint or objective.

For each group G, the replacement is

`sum(t=0..167) sum(j in G) p[t,j] = sum(j in G) E[j]`.

Every original per-unit equality implies its group equality, so the original feasible set is contained in the grouped feasible set. Each generator retains its own output, commitment, startup and shutdown variables. Hourly balance, conditional bounds, fixed hydro, native dwell times and weak horizon boundaries are unchanged; the network is relaxed. The grouped MILP has 24,290 rows and 18,984 columns, differing from the individual-target version only by removing 15 mean equalities. This is weekly energy redistribution, not hourly trace swapping or aggregation of physical units.

These results rule out the explanation that the eight reported rejections arise solely from preserving distinct energy labels inside these precise modeled-equivalence groups. They do not establish robustness to broader technology-class pooling, altered costs/parameters, actual emissions equivalence, different weeks, or a different chronology/boundary model. Rejections are numerical MILP solver statuses with retained logs, not independently checked analytic infeasibility proofs. No feasible witness was available for these eight cases.

## Frozen provenance and later extension

The original protocol and script were frozen at `2026-09-26T19:12:00.208247+00:00` before the eight grouped solves. Their byte-exact snapshots are retained as `frozen_protocol.md` and `frozen_run_script.py`; SHA256 values match `pre_run_freeze.json` and the original input manifest:

- Protocol: `b484ac351170baeb568ba71221dd92f3d78f3d59816bc81dc8b07a39a6fc0995`.
- Script: `feccebfb34439fbfb9e11998fec12e7517ef316da3bda7ba7d22d57dc84a26d2`.
- Group inventory: `6dbdc291ebd15539569ccef0b8edd622702362020ac84d61d6b99b8aee1508b6`.

The working script/protocol were subsequently extended, transparently after these outcomes, to check four previously selected repaired-July chronology twins. Therefore the original manifest's script/protocol paths now refer to extended working files; use the two byte-exact snapshots for the original run hashes. All other original inputs and results are preserved. The separate extension and its own pre-run freeze are recorded under `../equivalence_twins/`.

Replay the original sample with the current `src/temporal_equivalence_audit.py --source-v3 <portable_inputs> --output <new_output>`; replay the separate extension with the additional `--twins` flag. Existing result directories are refused. The original frozen script is an audit snapshot whose ROOT assumption requires the normal `src` location if executed; it is not a standalone entrypoint from this results directory.
