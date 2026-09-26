# Fixed July rules on the known January negatives

The fixed two-unit rule rejected **0/2** January negatives; the fixed 48-hour dwell-window rule rejected **1/2**. Three restricted models have verified continuous witnesses. This records both the failure and the partial success of transfer; no unit, window, target or cap was tuned after these outcomes.

The two January full-model negative labels were already known before this four-call experiment. It is a post-label fixed-rule, out-of-week assessment on the same RTS network, not blind prospective prediction or new-network validation. The January background retains full DC network constraints and the 23-fossil-unit cap B=23195 MWh, with zero named-unit mean rows. The earlier July transfer background had named means and no DC network, so this is not an isolated season-only comparison.

| January seed | Fixed rule | Solver status | Verified outcome | Solver seconds | Fractional U/Y/Z entries |
|---|---|---|---|---:|---:|
| 26093100 | two_cc | Optimal | Continuous subset admission | 1.236 | 210 |
| 26093100 | locality48 | Optimal | Continuous subset admission | 3.877 | 294 |
| 26093101 | two_cc | Optimal | Continuous subset admission | 1.350 | 208 |
| 26093101 | locality48 | Infeasible | Exact robust rejection | 3.091 | — |

The three admissions pass direct archived-matrix row and column checks at tolerance 1e-5. A separate independent Fraction replay also verifies every finite row and column bound exactly after outward expansion by the exact binary64 value of 1e-5. Thus they are exact feasible points of the explicitly expanded restricted continuous models, while nominal exact feasibility is not claimed. They do not establish binary feasibility, and do not change either full January model's prior exact rejection. Their nonzero fractional U/Y/Z counts also prohibit treating these vectors as binary witnesses. No case is UNKNOWN.

The seed26093101/locality48 ray gives exact rational separation 2369799.1068306575 (approximate displayed value), remaining positive at 2365743.236275444 after every finite row and column bound is widened by the exact binary64 value of 1e-5. The ray's arbitrary scale means these numbers are not energy penalties in MWh. The selected sign-admissible candidate projects 23 inadmissible raw multiplier entries to zero; raw and projected evidence are both retained. The proof has 1268 nonzero row multipliers. Exact numerator/denominator pairs are archived in its certificate and replay.

The two-unit model has 19985 rows; the locality model has 28689 rows; both have 23016 columns. Independent preparation checks matched every selected parent row, coefficient, bound, label and objective. All static, network and cap rows and all column bounds remain unchanged. The locality rule confines only minimum-up/down row supports to hours60–107 inclusive; transition and exclusivity remain global. Its rejection therefore does not show that a standalone 48-hour data segment is sufficient. Weekly cap and other background data remain necessary parts of the tested model.

Both exact expanded-model positive controls are inherited from january_identity/constructive_vector.npz and seed_26100100/constructive_vector.npz. Their exactly binary U/Y/Z and full exact feasibility under uniform outward expansion were already audited. Deleting rows with indexed bounds, while keeping columns and bounds unchanged, preserves those same witnesses under identical expansion, including cap23195+tau. No additional native replay, full-model solve or control solve was performed. The exact claim concerns the explicitly expanded encoded model, not nominal exact feasibility or physical measurement uncertainty.

Exactly four LP calls used HiGHS1.12.0 simplex, presolve off, one thread, random seed0, and 30-second limits. No retry or extension was used. Timings are from a shared busy host and are not a performance benchmark. All59 frozen source, protocol, input, model and control-audit hashes still match. The post-run support_metadata_annotation.json preserves and corrects inherited summary labels only; proof arithmetic, models and frozen sources are unchanged.

Source: src/research8h_seasonal_rule_transfer.py. Frozen protocol: docs/research8h/SEASONAL_RULE_TRANSFER_PROTOCOL.md. Machine-readable outcomes: results.json, summary.csv, coverage.json and completion.json. Exact positive inheritance: positive_inheritance_proof.json. Independent saved-artifact replay is reported separately in INDEPENDENT_REVIEW.md and independent_review.json.
