# V8R1 mathematical and editorial corrections

Date: 2026-09-26. Worktree: `dsc-v8r1-evidence/3`; branch: `codex/v8r1-evidence`.

This record documents corrections actually applied to `manuscript/source/main_core.tex` and `supplement/source/supplement.tex`. It addresses the original `FINAL_MATH_SYMBOL_AUDIT_2026-09-26.md` and the subsequently assigned editorial/cross-reference items from `FINAL_EDITORIAL_CROSSREF_AUDIT_2026-09-26.md`. No numerical result file, solver implementation, bibliography, publication record, or availability statement was edited by this subtask. Main and supplement sources were handed back to the integration owner after the checks described below.

## Mathematical corrections applied

| Original issue | Applied correction | Evidence and scope |
|---|---|---|
| General proposition incorrectly guaranteed an attained minimum | Replaced the finite problem's `min` with `inf`; required admissible joint laws to have finite first moments; specified nonnegative lower-semicontinuous convex costs; added sufficient attainment conditions: nonempty feasible set, compact supports, and finite continuous costs. | The original counterexample `C=[0,infinity), c(y)=exp(-y)` no longer contradicts the proposition. The statement of attainment now covers bounded generation supports with continuous L1 costs. |
| Reduction lacked an accessible proof | Added the conditional-barycentre/Jensen direction and the converse finite atomic coupling. | Uses the actual joint law on source-atom index and transported state; preserves the mean constraint. |
| Mean lower bound and support premium followed a general weighted cost without specialization | Explicitly fixed all reported ground costs to full-coordinate L1, with `A_i=I_d`, before defining the means, `M`, and the gaps. Defined `rho_C` shorthand and restricted finite premium reporting to admitted target means. | Prevents interpreting the full-coordinate mean bound as valid for arbitrary linear cost maps. No cost used by an implementation was changed. |
| Incomplete first-use definitions | Defined source atom count/dimension, point masses, weights, joint/marginal/conditional laws, support and expectation, finite first moments, L1 norm, cost-map dimensions, source/target means, positive part, all-ones vector, and affine reduced coordinates. | Definitions accompany the relevant equations. The supplementary GB formulas now explicitly define `M`, `W_1`, and the shape gap. |
| Chronological boundary and variable domains were implicit | Stated `T=168`, `t=0,...,T-1`, binary status/start/stop indicators, `y_{g,0}=z_{g,0}=0`, a free first observed status, no pre-horizon transition, and transition/minimum-time constraints only for `t>=1`. Specified no terminal residence-time extension. Defined power bounds and mean-deviation variables. | Directly checked against `src/native_minud_independent.py:16,24–37` and `src/reproduce_chronology_repairs.py:38–55`. The displayed sums were retained because they match this indexing. |
| AC balance lacked an explicit power-unit convention | Defined voltage magnitude, angle, and complex phasor separately; defined generator/demand powers, generator-to-bus set, admittance, and conjugation; inserted `S_base=100 MVA` on the nodal equation's right-hand side. | Matches `src/run_ac_shared.py:13,35–42,55–56,76–77`. Powers remain MW/MVAr and voltage/admittance per-unit. Both branch terminals are explicit in the supplement. |
| Ideal AC minimum and returned local values shared notation | Kept `R_t^AC` for the ideal minimum and introduced `hat R_t^AC` for the returned unregularized L1 witness cost. Updated the main figure/table and hourly supplementary table. | A feasible witness upper-bounds the ideal minimum. No global-optimality claim was introduced. |
| “Nonconvex objective” was inaccurate | Replaced it with a statement about the nonconvex program and locally computed value. | The L1 objective is convex; the AC feasible constraints are nonconvex. |
| AC numerical regularization was absent from the formulation narrative | Disclosed the implementation's `1e-8 sum_i (V_i-1)^2` and explicitly excluded it from reported witness costs. | At 24 buses and voltage bounds `[0.95,1.05]`, this term is at most `6e-10` in the implemented objective. No code or output was changed. |
| Equality of medians was overinterpreted | Replaced the supplementary explanation with a precise statement that the reported medians agree, without asserting equality at every hour or coordinate. | The per-hour July table has several L1 witness costs slightly above their active losses; the revised statement accommodates those entries. |
| Strict numerical bounds used nearest rounding | Used outward rounding in formal inequalities and bracket tables; used “approximately” with nearest-rounded prose values. March's three-decimal lower bound in the ladder is rounded downward. | Six-decimal July strict bracket: `[8.020508,11.926297]` MW; three-decimal bracket: `[8.020,11.927]` MW; supplementary ten-decimal bracket: `[8.0205084642,11.9262964643]` MW. These are presentation bounds on the same archived values, not new optimization results. |

The mean-repair linearization's signs were retained: `mean(p)-d^++d^-=mu_T` gives `mean(p)-mu_T=d^+-d^-`, and nonnegative deviations minimize to the L1 norm. The scale/reallocation identity was retained because it is algebraically correct.

The original audit independently checked clipping of the 48 AC DC-target vectors to their source bounds. Its largest changes were approximately `4.11e-12 MW` in March and `4.31e-12 MW` in July. That source-data check was not rerun during this text-editing subtask, and no target or clipping implementation was modified.

## Editorial and cross-reference corrections applied

- Added explicit main-text callouts to the methodological comparison, July repair, AC results, and GB tables; introduced the information-restoration figure near its results.
- Added six missing supplementary table labels and all supplementary table callouts, retained the hourly longtable label, and converted the evidence ledger into a numbered captioned table. At the handoff checkpoint the main source had eight tables and one figure, and the supplement had eight tables; all were explicitly referenced in prose.
- Clarified table captions: no-network admission scope, shape-share denominators, Elexon dates and percentage denominators, first target-day hour, returned AC witness values, and voltage/loading units.
- Defined the raw AC residual's numerical scaling rather than implying that the largest implemented violation has one common physical unit. The AC implementation combines MW, MVAr, and MVA-squared constraint functions; raw residuals retain those units.
- Replaced the reused `|Delta|` column names in repair/cross-solver tables with explicit absolute-change/difference wording.
- Corrected the limitation that previously called every empirical law a week: the power-system model laws are hourly weeks, whereas the Elexon laws are half-hourly days.
- Expanded first relevant uses of AC, DC, UC, DRO, OPF, LP, MILP, MIP, NLP, rooftop photovoltaic terminology, and PV/PQ bus-control terminology. Introduced fixed-pattern as a synonym of fixed-commitment. Added standalone operational-code definitions without rewriting the GB/Elexon scientific result paragraphs reserved for integration.
- Removed “reader-facing findings,” draft-history descriptions of the static baseline, the conversational machinery sentence, “V8” from the supplementary section heading, unexplained software-name use in the independent-verification description, and the first-Colab-attempt narrative. Replaced the baseline date shorthand with the exact archived file pattern and timestamped-row selection.
- Added the portable fixed-commitment solver budget/initialization description from `src/run_ac_fixed_fast2.py`: 250 iterations and 0.4 CPU seconds per initial guess, using source-data and available previous-hour guesses. This does not claim that wall-clock-sensitive counts are physical success rates.

### Verified operational-code terminology

The DF expansion “Dispute Final” was verified in the [Elexon settlement-run glossary](https://www.elexon.co.uk/bsc/glossary/2nd-reconciliation/). The operational codes were checked against the official [Elexon interface definition](https://bscdocs.elexon.co.uk/interface-definition-documents/neta-interface-definition-and-design-document-part-1-interfaces-with-bsc-parties-and-their-agents) and [RURE API documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/RURE): Minimum Non-Zero Time (MNZT), Minimum Zero Time (MZT), Run Up Rate Export (RURE), and Run Down Rate Export (RDRE). These definitions were read on 2026-09-26. No inferred chronology calibration was added.

## Verification at source handoff

Both wrappers were compiled twice using installed MiKTeX/pdfLaTeX with `-interaction=nonstopmode -halt-on-error`; outputs were isolated under `.work/math_syntax_main` and `.work/math_syntax_supp`. Both returned exit code zero. The second-pass logs had no undefined references, multiply-defined labels, or overfull boxes. MiKTeX emitted only an external installation-update reminder on stderr, and ordinary underfull-box messages remain in the logs.

A direct source-label check returned:

| Source | Table/figure labels | Missing prose callouts | Unresolved references | Duplicate labels |
|---|---:|---:|---:|---:|
| Main | 9 | 0 | 0 | 0 |
| Supplement | 8 | 0 | 0 | 0 |

`git diff --check` reported no whitespace errors. Compilation was a syntax/reference check, not final visual QA. At this checkpoint the main PDF had nine pages and the supplement seven; final pagination and visual inspection are explicitly deferred until the other agents' scientific results are integrated. No generated PDF from this subtask is a release artifact.

## Handoff and unresolved scope

The integration owner is adding the expanded RTS chronology analysis, native-ramp redundancy explanation, GB parameter audit, and broader Elexon evidence. Accordingly this subtask does **not** certify the final scientific claims, final abstract, final page budget, journal-specific upload choices, or full-study reproducibility. It also did not rerun any solver.

The following original text was explicitly left for that integration because it lies inside scientific paragraphs the integration owner reserved: the main GB “held” sentence, the supplementary GB “workstream ... held” sentence, and the conclusion's “new warm-started” / “correctly holds” wording. Those are pending editorial integrations, not endorsed final wording. The integration owner was also asked to generalize “hourly dispatch state” in the mathematical introduction to “observed dispatch state” so the wording directly covers the operational half-hour observations.

Bibliography fixes, archive availability statements, and deposition/publication were outside this subtask. The scoped mathematical corrections above resolve the identified formulation defects; they do not by themselves establish that the integrated manuscript is ready for submission.
