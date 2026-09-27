# Prospective direct-code transfer for the existing OR-LIB reverse target

27 September 2026. **DESIGN ONLY.** No new target was generated, no target row/point/dual arithmetic was performed, and no Julia import, native build, optimizer, environment change or implementation was run for this document. It proposes one new actual-code export and subsequent exact checks, each subject to source/prepared review and explicit execution authorization. All closed sources, freezes, outputs and historical ledgers remain immutable.

## Fixed question and denominator

Use only the already declared `reverse_4_19__native_penalized` target of the OR-LIB10 pilot. This is a **post hoc implementation-fidelity extension of a known positive source-derived result**, not a newly selected scientific target or a prospective discovery sample. The original two native-penalized targets and two hard-service target outcomes remain in their original denominator; rotation and hard service are outside this one-case extension and must remain visible as not transferred to the actual native code.

The zero-based order already stored in the frozen target model is

`[0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]`.

It reverses indices 4 through 19 inclusive, retaining the first/last four source hours. It preserves the joint input-package multiset, not clock position, adjacency, ramp feasibility or remaining initial-obligation invariance. This one-bus synthetic UC case remains distinct from transmission-network validation and the RTS fossil-electricity objective.

Question: does the existing accepted target vector and fixed signed-dual proof yield a native-expanded target cost bracket after an **actual target** UnitCommitment.jl export establishes the necessary nominal correspondence and containment premises? Only after that gate may the new target bracket be combined with the already closed native identity bracket. Identity correspondence alone is insufficient.

## Inputs and exact future target transport

Preserve the official compressed case, SHA256 `6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe`; its original decompressed SHA is `3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308`. Its embedded LICENSE and SOURCE fields remain intact. The actual JSON has `Buses.b1.Load (MW)`, a 24-entry `Reserves.r1.Amount (MW)` array of zeros, and Parameters containing only Time and Version: the curtailment penalty is an absent-field native default, not an explicit series to replace.

A future separately reviewed preparation will capture these exact bytes and the **stored** order from the old target model. In a fresh output, it may serialize a deterministic gzip with only the load array and explicit reserve array mapped by that order. No default field is inserted, generator/history/cost field changed, schema repaired by the preparation, or original file overwritten. All unchanged JSON subtrees and all original scalar binary64 values must compare exactly; the reserve array must remain the same zeros. The unchanged absent penalty field preserves the same native default. No scientific target selection or severity tuning occurs. The preparation must reject an unexpected time-varying generator/cost field rather than extend the transformation silently.

Archive the new plain JSON/gzip, source/destination row map, decompressed and compressed hashes, exact unchanged-field comparison, and per-destination binary64 input transport. Check against both the original normalized case plus its archived order and the old target model's load balance endpoints, native curtailment upper bounds, reserve endpoints and penalty coefficients. This is a transport/premise gate, not a rebuild or modification of the old adapter model. The parsed official target export must later agree with this same expected transformed instance, including unchanged native initial history and every unit field. No candidate or dual is transported to different chronological coordinates: both old target records already use destination-hour coordinates.

The new derived gzip is a test input, not a newly hosted official benchmark case. Its hash differs from the old adapter's preserved original-case hash. The already-reordered native input and the old adapter's original input plus stored order are different descriptions of the intended same numerical instance. The bridge must establish that exact instance and model semantics, not claim whole-file equality across those unlike metadata representations.

## One bounded actual native export

Reuse the accepted isolated Julia1.6.7 environment: UnitCommitment0.4.0 at commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`, tree `619a6b12e1005425e6ac08c4c45e445bb0a6f134`; JuMP1.15.1, MOI1.20.1, PackageCompiler1.7.7. Preserve actual Project `02e2d39820e8f8b03404d75ff1970764c68309e6afee996571d229c4cf84690a`, Manifest `2434d5a9878bd443e95e339dd0b71e1632bc61988fd1272af54461f6bad9d831`, package inventory `76f9343b5519f590e25d5d97c6f34e080f146a650dd32478240cdee973f8ea5d` and READY receipt `fd3f2db6f0a62ecb0733ef903ff5ac0760b6375f7c723f14e536983ad1839872`.

Use the same two admitted depots in the same order and exact active project. Bind the runtime executable, direct loaded-module paths, 18 native source blobs and selected installed/registry metadata through their existing inventories. No whole-registry extraction or whole installed-tree scan is needed. Inherit the explicit non-adversarial local-mutation/storage assumption and incomplete physical whole-tree verification; checking recorded package tree identifiers is not a full installed-file rehash. No Pkg.add, resolution, registry update, network operation, version drift, patch or global environment change is permitted.

Create new path-bound exporter/launcher sources and new output/prepared directories if implementation is authorized; do not relax or edit the closed identity launcher's case guard. Freeze their complete source/protocol/transitive bindings before execution. Exactly one `UnitCommitment.read` with the native defaults/repair, then one `build_model(instance=..., optimizer=nothing, formulation=UnitCommitment.Formulation(), variable_names=true)`, is allowed. There is no optimize call. Record attempted/returned read/build markers before each call and preserve failure or partial output without retry.

Proposed limits match the admitted identity export: 600 seconds for the launcher including import, validation and closing hashes, and 120 seconds for the native read/build/export subphase beginning at the official-read marker. The final completion-record write alone is excluded as explicitly documented. Record actual elapsed/overrun and owned-process cleanup. A cold import or timeout is an unresolved infrastructure outcome, not target infeasibility. Reusing warmed caches is allowed but no timing-speed claim follows.

Export every actual variable, every typed domain/affine constraint with multiplicity, constants and exact binary64 bits, complete aliases, every ZeroOne declaration, parsed native fields and objective constant/sense. Do not project mfg, add boxes, normalize coefficients or claim equivalence inside the exporter. The historical identity shape suggests 2,712 raw variables, 960 binaries and 4,384 affine rows; measure the target and fail the later fixed comparison if these premises differ, rather than silently alter the contract. Raw success remains pending comparison.

## Exact target correspondence required before any transfer

A distinct, independently reviewed comparator must establish all of the following for the new raw export and the frozen old target model, without rebuilding either:

1. All parsed system/unit values equal the original normalized case under the frozen order, including the default penalty, initial signed ages and powers, above-minimum ramp/startup limits, dwell, segments and single startup category. Migration/repair must not introduce an unaccounted target change.
2. A complete semantic alias bijection maps all 2,712 raw variables to 2,472 retained coordinates plus exactly 240 mfg variables; all 960 binary declarations agree. The destination-hour interpretation is unchanged.
3. The complete affine row multiset, including duplicates, matches exactly after moving constants to endpoints and, if needed, reversing whole-row sign. No positive rescaling or numerical tolerance is allowed. All objective coefficients, constant and minimization sense must match.
4. The omitted mfg variables have only their nonnegative domains and zero constraint/objective support; zero gives a valid lift. Every domain difference is enumerated. The only allowed differences are the same 480 nominal Q/R upper boxes justified by actual headroom rows and 24 N=0 boxes justified by actual equalities. All other domains, including target-specific curtailment bounds, must agree.

A failure is a fidelity/premise failure, not evidence of a cost increase or target infeasibility. Preserve differences and stop; do not repair the model, reinterpret a coefficient discrepancy, substitute another target or regenerate the old proof. Keep nominal projection equivalence separate from expanded-set containment. An independent postrun gate must accept the actual target comparison before a native cost-transfer claim.

## Fixed saved-evidence upper/lower transfer

Let tau be exactly `Fraction.from_float(1e-5)`. Expand each finite raw-native row and variable-bound endpoint by tau while retaining all 960 ZeroOne domains exactly. Reuse only the archived target candidate, unchanged, with mfg=0; no new snapping, clipping, dispatch adjustment or optimizer. Replay every raw native row/domain and full objective. Record strict nominal membership separately, preserving a null strict upper if any nominal endpoint fails.

Reuse only the target's archived raw LP row multipliers and its already selected signed-row proof. Recompute the same sign projection, every row contribution, all 2,472 residuals `r=c-A^T*d` and the complete finite-box bound; require exact agreement with the original rational proof and selected bound. No alternative multiplier, lower-bound selection or zero-dual fallback is introduced.

Under the actual checked headroom/domain premises and exact binary U, native expansion implies each Q/R upper is at most width+2*tau. Hence apply the fixed correction

`L_target_native = L_target_adapter_expanded + tau * sum_QR min(r_j,0)`.

Also compute the direct widened-endpoint/box-support expression and require equality. This is containment, not expanded-model equality. Bind every proof to the actual target raw export, correspondence review and original saved proof. A rejected upper leaves a lower-only result; invalid premises admit no transferred bound. Negative/zero/weak bounds and all failures are retained without clipping or selection. Proposed arithmetic allowance: one 120-second soft pass after a separate reviewed preparation/GO, with no Julia or optimizer.

If both target bounds are admitted, combine them with the unchanged, independently accepted identity-native bounds using the signed interval

`[L_target_native - U_identity_native, U_target_native - L_identity_native]`.

Store exact rational endpoints, all input proof hashes and outward-rounded presentation. Retain an interval crossing zero or a null caused by missing upper. Do not reuse the old adapter difference as though it were the native result. No arithmetic for this new correction or difference has been performed for this design.

## Meaning and fixed evidence bindings

A strictly positive lower endpoint would strengthen the evidence that chronology changes the best achievable **encoded native UC objective** for this one existing synthetic case, under the explicit mathematical expansion. It would close an actual-code fidelity gap. It is not decision regret: each chronology's optimum is allowed its own informed commitment. A regret/information-loss result requires a separately defined common decision or policy, information class and comparison with informed decisions. This arm imposes no common decision. It also does not identify which ramp/dwell/curtailment mechanism causes the difference, prove methodological novelty or supply independent transmission-network validation. No paper is added to the reading count.

Paths below are under `results/research_next/orlib_preflight/solver_prepared01/` unless stated otherwise. These existing hashes were read and checked for planning; no new scientific result is inferred from them.

| Fixed input | SHA256 |
|---|---|
| `inputs/reverse_4_19__native_penalized.json` | `a8bb82c4397957c6bdf4264d4265fca7144a09282b819aa15880ab60e22db4bb` |
| `outputs/reverse_4_19__native_penalized/mip/candidate_vector.json` | `ce8812ec5e37eb9e3bc98f0b71e4ccd768653b97b4dfd12c3aa4c28993ed8152` |
| `outputs/reverse_4_19__native_penalized/mip/result.json` | `967753dcc81dcebeb5f9f04c986dbb88d0bbf964a49491c5e1e555816a6bbee8` |
| `outputs/reverse_4_19__native_penalized/lp/raw_solution.npz` | `933ffdce78ba1408f9fcfc520313e499b4325f1dcfb151b1afe80fe8ef7e7ef9` |
| `outputs/reverse_4_19__native_penalized/lp/signed_dual_bound.json` | `f4a23b8e50969dd900e833d4bb44b3d39614f0fbd2601e3e7ffc29d2073665c0` |
| `outputs/reverse_4_19__native_penalized/lp/result.json` | `aff006235c7ec2fca8e397eca7bcf501d7351d89c3987694a7167a7f9441aa49` |
| Original 96-output manifest | `2713685311e705ea0c9b6080dee2594e9d077d37aea844efb0e093f722cf9a52` |
| Closed independent six-model result review, sibling `orlib_preflight/INDEPENDENT_SOLVER_RESULT_REVIEW.json` | `a465a16acf67ca9a0925376f2a2b7d4338a24bac9bb276258d134f930d11f358` |
| Closed identity native comparison, `orlib_native_compare_schema2/INDEPENDENT_POSTRUN_REVIEW.json` | `50191cce91e6a4e8479500bfa0a1740b03d812848ee37620480b3e41ce584080` |
| Closed identity native bracket, `native_expanded_identity_independent_review/postrun_review.json` | `8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1` |

The final three sibling-arm paths are relative to `results/research_next/`, as named, rather than the solver directory. Implementation, new input materialization, export, comparison and bound arithmetic remain unexecuted and require their own reviewed gates; this design grants none automatically.
