# PGLib-UC external benchmark: bounded read-only assessment

**Decision: HOLD for a new certified experiment during this session.** The official CA/FERC families provide a genuine external UC dataset, but none is a modest untouched instance relative to the current implementation. A new native-feature-preserving model/export/checker audit is substantial. This is a scope/readiness decision, not a claim that a particular solver must time out within six hours. No case was solved, altered, generated, shortened or reduced to a generator subset; no package was installed.

## Primary-source identity and license

The official repository is [power-grid-lib/pglib-uc](https://github.com/power-grid-lib/pglib-uc). `git ls-remote` and an isolated shallow read-only inspection copy both identified HEAD/master as **`39a7f38cf4703de92f0291f0c873c2e98c789301`**, committed 2026-04-22, merge message “Updating pyomo model.” The changelog still labels its initial release v19.08; cite the exact commit as well as any release label. No working research repository was changed by the inspection copy.

[LICENSE at the inspected commit](https://github.com/power-grid-lib/pglib-uc/blob/39a7f38cf4703de92f0291f0c873c2e98c789301/LICENSE) gives **CC BY 4.0 for data** and **MIT for software**. Preserve the relevant attribution/license notices; case use should also credit the sources requested by the README. The general formulation paper is Knueven, Ostrowski and Watson, *On Mixed-Integer Programming Formulations for the Unit Commitment Problem*, INFORMS Journal on Computing 32(4), 857–876 (2020), [DOI 10.1287/ijoc.2019.0944](https://pubsonline.informs.org/doi/10.1287/ijoc.2019.0944). The README additionally requests the original FERC test-system citation for FERC cases.

Inspection covered the complete 44-case CA/FERC inventory, the complete `MODEL.tex` and Python model, and the Julia model's declarations, constraints and solver entry point. The `rts_gmlc` family was excluded from the assessment. Official files were read from the pinned Git objects and decoded without running either reference model.

## Complete-family size and history inventory

These counts come from all unmodified JSON files, not from selected generator subsets. Binary/variable counts are inferred from the official Python declarations before presolve, not measured solver sizes.

| Family group | Cases | Native horizon | Thermal units | Renewable units | Declared binary variables | Declared total variables |
|---|---:|---:|---:|---:|---:|---:|
| CA four dated profiles × four reserve levels | 16 | 48 h | 610 | 0 | 146,400 | 305,664 |
| CA Scenario400 × four reserve levels | 4 | 48 h | 610 | 1 | 146,400 | 305,712 |
| FERC Jan–Mar and Oct–Dec, two wind levels | 12 | 48 h | 934 | 1 | 191,760 | 471,552 |
| FERC Apr–Sep, two wind levels | 12 | 48 h | 978 | 1 | 199,824 | 485,232 |

For `G` thermal units, `W` renewable units, total startup-category count `S` and piecewise-point count `L`, the declarations give `T(3G+S)` binaries and `T(6G+S+L+W)` variables. CA has `S=1220`, `L=1488`; the two FERC rosters have `(1193,3026)` and `(1229,3011)` respectively.

CA has 200 must-run units; all 610 units are initially on, with native minimum up/down times at most six hours and startup lags up to 14 hours. FERC has 62 or 136 must-run units and 249 or 303 initially on units; minimum up/down times reach 168 hours and startup lags 336 hours despite its 48-hour horizon. None of the 44 supplied cases has a positive *remaining initial dwell obligation* under the stored initial ages. That does not remove initial-state physics: fixed initial output/status, first-hour ramps, initial shutdown capability and startup-category restrictions remain part of the model.

In each CA roster, 36 units have an on/on ramp smaller than their dispatch range, and 36 have a startup/shutdown capability below maximum output. Corresponding FERC counts are 479/923 or 568/956. Thus the current RTS-specific ramp-redundancy shortcut is invalid here. CA offers native reserves of 0%, 1%, 3% or 5%; FERC has positive native reserve profiles. Retaining all requirements is essential.

Concrete untouched file identities for reproducible follow-up:

| File at the pinned commit | SHA-256 | Git blob |
|---|---|---|
| `ca/2014-09-01_reserves_1.json` | `ae2c0bbf7be38a34e3167a2bb839c33b0f1b8bcced51a5b4c0f9ef46fd759831` | `256dd82e0a414a1ac638ec144c8fcf670407426f` |
| `ca/Scenario400_reserves_1.json` | `8bbc9cbf7e8dac47ac3f911f86ea5e974263310eb2ef48f64a807ad99da7d35b` | `1f903643bc5a9c2d38b54968d5af68a076c3f914` |
| `ferc/2015-01-01_lw.json` | `f1a14f5deefc229bcfbb8134b8159277971cde7e4da13ff64fbd728ea2df6622` | `39b3ee21fd69a1935170c6106a231976f9ca6974` |

These are inspection identities, not outcome-selected candidates. The CA chronological first case with positive reserve is a reasonable later fixed candidate if a complete native formulation is audited first. No runtime or feasibility claim has been established for it.

## Native formulation and implementation compatibility

The [official mathematical formulation](https://github.com/power-grid-lib/pglib-uc/blob/39a7f38cf4703de92f0291f0c873c2e98c789301/MODEL.tex) includes demand and reserve balance; initial state/output/history; must-run, commitment and residence constraints; startup-category selection; initial and inter-hour ramps; startup and shutdown generation limits; convex-combination production and cost equations; and renewable bounds. The objective includes no-load/minimum-output production cost and category-dependent startup cost. Its terminal convention follows the finite-horizon equations; no arbitrary post-horizon closure should be introduced.

This is a global-balance UC benchmark, **not a DC-network transfer**. The JSON generator schema inspected does not provide native fuel/emissions labels sufficient to transplant the existing “23 fossil units excluding nuclear” energy cap. A cost-capped order experiment would ask a different, explicitly specified question. Also, the current fixed-first/last-48-hours protocol leaves no interior in these native 48-hour instances; it cannot be reused verbatim.

The [Python reference](https://github.com/power-grid-lib/pglib-uc/blob/39a7f38cf4703de92f0291f0c873c2e98c789301/uc_model.py) imports Pyomo, builds its model at module scope and immediately invokes a solver. Its default is CBC, with option mappings for CBC, GLPK, Gurobi and SCIP; HiGHS is not listed. It provides no solver-free callable builder or exact CSR/row-provenance export. Its configured 1% MIP gap is neither an exact certificate nor a fixed wall-time protocol. The Julia file states testing with Julia 1.1, JSON 0.21, JuMP 0.19 and Cbc 0.6 and uses the older `with_optimizer` call. No compatibility run was made.

A bare Codex-runtime `pip show` found no Pyomo or Egret distribution in that runtime. That probe also did not find HiGHS even though the ongoing research uses a configured solver environment, so it is **not** an inventory of every project-specific dependency path. Missing dependency readiness remains unverified; no install or import-time model execution was attempted.

## Exact export and independent checking: feasible in principle, not ready

The model is linear and can in principle be assembled/exported with stable variable and row identifiers, original integer masks and exact hashes, retaining all native costs and constraints. But a trustworthy port needs an independent row-by-row comparison with the pinned reference formulation and a separate physical checker covering initial ramps, reserves, category eligibility and piecewise costs. A float-export certificate concerns that assembled binary64 model, not automatically the exact decimal interpretation of the original JSON.

The current finite-column-box verifier rejects the reference's explicitly unbounded cost variables and dispatch/reserve variables lacking explicit upper bounds. Implied finite bounds could be derived from generation and convex-combination rows, but their redundancy must be proved and audited; arbitrary finite replacements would change the problem. Alternatively, the verifier needs a carefully reviewed extension for unbounded columns and exact ray cancellations. Neither has been implemented here.

The existing U-only recovery proof also does not carry over automatically. Startup/shutdown coordinates now participate in generation limits, costs and startup-category/history logic. Removing fictitious simultaneous transitions can affect later category eligibility. Keep the full official binary declaration unless an appropriate equivalence proof is independently established; do not silently reuse the previous auxiliary relaxation.

Before any later external claim, require an unchanged complete case, frozen native formulation/export, an independently accepted baseline, documented arithmetic semantics and a prespecified question/cap/order/time budget. An LP infeasibility certificate could establish a negative; a timed-out MIP without a verified point remains UNKNOWN. None of these outcomes has been observed in this assessment.

**Practical conclusion:** the dataset is suitable for a subsequent genuine external UC study, but there is no verified small CA/FERC instance or ready native-feature-complete export/checker within the present workflow. A rushed reduced or constraint-suppressed case would not answer the requested external-transfer question. Preserve the completed evidence and record this arm as HOLD, rather than presenting an unaudited solver run as external validation.

Raw Git-byte source bindings: `MODEL.tex` SHA-256 `e612d71922cf5b19a2f8e7903c8ac6b25a0953e5065c368c94571752f360b6aa`; `uc_model.py` `ca340c71fe78627c3fab2a2f356b4b2ec3a650c8e9883d6ef645aa2ea1b534ea`; `uc_model.jl` `d8a393b7eabbee8f09534a1e7d62b00659c9e3a01b540df2768e1d13ec6cfeda`; `LICENSE` `b5ececfa64eb67fd5b0e5c135624f0f9004b938d399150e644f9641b659e628c`. Windows checkout converted these text files to CRLF; the reported source hashes use their LF Git bytes, with Git blob SHA-1 and byte sizes independently matched to `git ls-tree`. The three JSON identity files retain their Git byte sizes unchanged. Repository and local arithmetic inventory inspected on 2026-09-26 UTC / 2026-09-27 Dubai. No subscription material or credentials were accessed.
