# Original January energy intervals: source-only portability assessment

Status: feasible as a small additive, external standard-library replay supplement. This assessment inspected source, archived JSON records and the final ZIP's manifest metadata only. It did not import a mathematical checker, evaluate a scientific bound or witness, run an optimizer, extract or alter the final package, or implement the proposed wrapper. Existing scientific results and manuscript v3 remain unchanged.

## Fixed package and scope

The unchanged final ZIP is `.work/research8h_delivery/DSC_Temporal_Research_2026-09-27_Final.zip`, 127,416,288 bytes, archived SHA256 `e4d9b181668a68b0f7db1c0cc8c30182ac56c0a461c1dbd5a37fb63d933a6aa9`. Its trusted outer manifest is `4c9f6db4561470775c5e567956c48825de44a6700b0cdcd1607ca50770089409`; its manifest-bound `PACKAGE_PROVENANCE.json` identifies Git20 commit `3f51758b521967739131701b106be60036a3fdd4`.

The proposed replay covers exactly the two original unrestricted first-week January optimum-energy intervals, seeds 26093100 and 26093101, with their shared identity dependency. It does not replay unrelated HOD, fresh-week, strict-flow or seasonal-follow-up cases and does not imply full repository or all-energy coverage. The identity must be checked again in its role as the common denominator/reference enclosure for these two omitted intervals.

## Concrete archived dependencies

All three continuous lower-bound models are under `results/research8h/energy_lp_refinement/{january_identity,seed_26093100,seed_26093101}/`. Each contains `matrix.npz`, `bounds.npz`, `objective.npz`, `original_integrality.npz`, `row_metadata.csv.gz`, `retained_parent_rows.npz`, `raw_duals.npz`, `projected_row_dual.npz`, `exact_lower_bound.json`, `exact_stationarity_residual.json`, `prior_bounds.json`, `model_and_upper_binding.json` and `result.json`. The archived models have 34,680 rows and 23,016 columns.

| Role | Upper vector | Parent model and full binary mask |
|---|---|---|
| Identity | `results/research8h/seasonal_transfer/january_identity/constructive_vector.npz` | The same directory contains the capped parent, native arrays, metadata and `integrality.npz`; delete only its unique fossil cap to obtain the refinement model. |
| Target 26093100 | `results/seasonal_uncapped/seed_26093100/recovered_vector.npz` | The same directory contains the uncapped parent and `original_integrality.npz`; its matrix and bounds must equal the refinement copy. Its capped ancestor is `results/research8h/seasonal_transfer/seed_26093100/`. |
| Target 26093101 | `results/seasonal_uncapped/seed_26093101/recovered_vector.npz` | Corresponding uncapped parent/full mask and capped ancestor, with the same relationships. |

Upper vector SHA256 values, respectively: `7c534f8691c761815224ac43773259da5a8e1d3eb2aa892dcb64dc46541672db`, `a04c939390345bb4bad9a0ef7c98ee72c3e6c691c390799730031bfb2f75b8f2`, and `60952e52d7457b056db6dd7eddc81862846ac55b5d819051f1a196ded3244302`.

`refined_brackets.json` and `relative_penalty_bounds.json` supply the selected archived intervals, with SHA256 `bd1e8e061a26f82bdb8e0697e03ea4b3f97664b6ee19c21d4886950e85fd1cfd` and `5dff4825a3cb8509564fb2c44cd27160b43c2cf0d79e01cd0c2e557f38fdfccd`. The prior derivations remain in `results/research8h/energy_price_bounds/` as historical evidence.

Independent original check records include `energy_lp_refinement/independent_review.json` (SHA256 `94c10b498dc600f92d55c77987325a106d7dcbb64f201a284a8295b756528401`) and `energy_price_bounds/independent_review.json` (`d70d955763a5aa7aa7c6a3ac0f889a2786e112939493452ad2bf51e6030bfd1d`). The former independently replayed the three refined dual bounds and selection/interval arithmetic while inheriting already bound upper witnesses. The latter checked source relations, objective, prior bounds and interval arithmetic while binding prior full-point audits. The proposed supplement would directly replay the three full point memberships as well.

Metadata-only comparison against the trusted final outer manifest found all 59 refinement input bindings, all 49 prior-audit input bindings and all 55 uncapped input bindings, with matching declared hashes and sizes and no missing paths. Their manifest hashes are `b85b1260ded4d4f0a2576c921a4d84581360bfe7adddac361d5ad8826fd6e32d`, `53d531d6817984ed857e60471087eae6099332a43be62b8da37fe85bf7b99e49` and `59ad33b7ef6c6854d9acb3bcca837a521b10dd695711124e204c5c6f4e3a5352`. This is dependency availability assessment, not a new full-byte or mathematical replay.

## Minimal sufficient acceptance boundary

Use the three new LP-derived bounds as the sole mathematical lower endpoints. For each case, reproduce raw-to-projected sign admissibility, compute the exact row term and finite-box residual bound, and deduct `Fraction.from_float(1e-5) * (row_dual_l1 + residual_l1)`. Match all archived exact components and sparse residuals. Require this independently recomputed new bound to equal the archived selected lower endpoint and to be at least the stored prior value. Reject any dominance or selection mismatch. Do not fall back to an unverified prior or use an unverified maximum.

The weaker prior derivations therefore need only remain hash-bound historical provenance; their balance/ray calculations need not be replayed. Checking dominance over their stored values verifies selection arithmetic, not those prior proofs. This narrower route was independently recommended by the mathematical reviewer and accepted by the parent before implementation.

For all three uppers, check every original row and box with the exact uniform finite-bound expansion, and require the complete 12,096-coordinate U/Y/Z mask and exact binary values. Recompute the fossil energy directly from the vector and objective. Explicitly preserve strict-versus-expanded membership; no strict feasibility is assumed. Check every cap-only row/bound relationship and the original full masks, rather than trusting inheritance flags. The objective must equal the deleted cap row and exactly the 168-by-23 Coal/Oil/NG dispatch coordinates identified from native `gen.csv`, excluding nuclear; all other coefficients are zero.

Derive the two optimum differences from verified bounds as `[L_T-U_I, U_T-L_I]`. With positive `L_I` and nonnegative `L_T`, derive the relative interval as `[L_T/U_I-1, U_T/L_I-1]`; percentage endpoints multiply by 100. Compare exact archived numerator/denominator fields and outward display strings. Keep chosen-incumbent excess separate from optimum-to-optimum difference.

## Reusable code and native scope

The pinned standard-library kernel `src/research8h_standalone_verify.py`, SHA256 `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`, already reads the actual NPZ/CSR schema and checks original-mask expanded membership. The pure arithmetic `objective_lower` and `intervals` helpers in `reproducibility/replay_closed_research.py`, SHA256 `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85`, fit these lower-bound and interval schemas. Import only pinned, source-reviewed pure helpers; never invoke their unrelated replay workflow or import old solver runners.

Native `gen.csv` and all archived native inputs are present through the reviewed offline native-source addendum. Verify their hashes, exact native-array inheritance and fuel roster. Bind the old identity `raw_reference_check.json`/`rounded_reference_check.json` and target `native_no_cap_check.json`/`exact_point_check.json` records. The new mathematical claim is exact membership and objective bounds for the archived expanded binary64 model. A small supplement need not reconstruct the native network or repeat the prior numerical physical checker; it must say that those native physical audits are inherited and hash-bound. The strict-flow native checker is for a distinct representation and must not be applied here.

## External execution and cost

A separately reviewed wrapper/protocol can live outside the final package and require `--expected-self-sha256`, the trusted final outer digest, and the expected Git20 commit checked against `PACKAGE_PROVENANCE.json`, in addition to package/report paths. The source/protocol and new reports can later be delivered as a small supplementary archive. The final ZIP, manuscript v3, original manifests and old wrappers stay unchanged.

Use `python -I -S`, pinned helpers, no bytecode, no network/optimizer, canonical path remapping with unknown roots/aliases rejected, no host fallback, and a new report directory outside the package. JSON path strings must be decoded once and their Windows separators handled explicitly. Verify package/provenance bindings before any helper import and compare file inventories after execution. Preserve any first failure; no automatic retry.

Estimated same-host runtime is approximately two to four minutes including complete package hashing, three full point checks and three dual-bound checks. This is a planning estimate, not a measured result or guarantee. A prospective 300-second soft phase guard checked between fixed stages, with unfinished roles explicitly recorded, would bound the initial run without losing the three-model/two-interval denominator. Preparation, source review and independent gates also require time. No implementation or execution is authorized by this assessment itself.
