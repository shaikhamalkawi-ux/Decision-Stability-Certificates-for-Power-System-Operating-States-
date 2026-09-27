# Portable fixed-state certificate verifier: source review

27 September 2026. **Mathematical/source review PASS for the stated archived-model scope. One loader trust defect was found and corrected before freezing.** This is not a review of an assembled portable bundle or an execution of its scientific certificate. Reviewer `/root/find_deposit` read the complete verifier, preserved development sources/receipts and the pinned decoder's parsing/model-validation path and import guard. No closed scientific arrays, certificate arithmetic, optimizer or native assembly were replayed.

## Reviewed versions and authorship

The independently reviewed initial verifier was `src/researchnext_portable_state_cut.py`, SHA256 `c8d79c7e477f1d8f8ae9f3f41193a936cdbf869177199e4dbf866878554618b6`. The parent then explicitly authorized this reviewer to preserve that exact file as `pre_review_source.py` and author the narrow loader fix. The resulting source SHA256 is **`8a1774b6ab342abf60e2b21f673f56905cc07d66c5eb283ce350703c0976e625`**. Therefore the full original mathematical review is independent; the loader patch and its invented control are reviewer-authored and require the parent's separate delta read. They must not be described as independently reviewed by their own author.

The only production changes are a captured-source loader and replacing the previous decoder import with it. `reconstruct()` is AST-identical to the preserved source. The decoder pin remains `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`; no mathematical, input-schema or certificate-acceptance rule changed.

## Exact reconstruction

The decoder validates the CSR representation, finite binary64 coefficients, indices, dimensions, duplicate-column exclusion, finite ordered column boxes and permitted row endpoints. Its NPZ path uses standard-library ZIP/NPY parsing, explicit array types and payload-size checks, without pickle or NumPy. Its guarded CLI does not run on import.

The verifier requires a complete original binary mask and exactly one admissible exact 0/1 value for every marked column. Canonical rational strings reconstruct the signed row weights and tau. Each nonzero row weight must select a finite lower endpoint when positive or upper endpoint when negative. It then independently forms the full exact `q=A^T d` and selected-endpoint sum `beta` from archived binary64 numbers, with no small-coefficient threshold.

For finite continuous boxes, the computed necessary row is

`q_B · z >= beta − support_[L,U](q_C) − tau*(||d||_1+||q_C||_1)`.

The sign-dependent support and both expansion losses are correct. State variables remain explicit, so no extra state-box tau is deducted. Every full residual coefficient and each reconstructed scalar must equal the stored rational claim; strictly positive exact right-minus-left margin establishes rejection of the named fixed state. No solver optimality, dual stationarity or provenance of the arbitrary signed multiplier is needed for this algebra. Those solver-history claims are appropriately outside this verifier's scope.

The certificate binds the nominee and all five declared model-role files. The column/origin JSON files are bound as bytes, not used to recreate physical semantics. The result therefore certifies the supplied expanded matrix and fixed state, not native physical mapping, the old fractional control, an operational author's model, strict nominal feasibility or global common-binary infeasibility.

## Path/hash trust and corrected loader defect

An independently supplied manifest hash is the trust anchor. The verifier requires exactly ten declared role paths, their byte counts/hashes, confined resolved payload paths, executing-verifier byte equality, the fixed decoder-source hash, and certificate-to-model/nominee hashes. Payload hashes are checked again after the mathematical reconstruction. The loader pin is meaningful only together with a trustworthy external manifest/verifier distribution; a hash copied from an arbitrary replacement bundle is not authentication.

The original `SourceFileLoader.exec_module()` could read a matching adjacent `.pyc` even with `sys.dont_write_bytecode=True`. Thus hashing `decoder.py` alone did not ensure that those source bytes were executed. The authorized fix reads decoder source once, verifies those captured bytes, then directly `compile`/`exec`s them in the registered module. It neither reads nor executes an adjacent decoder bytecode cache. Module registration is retained for the decoder's dataclasses.

One deliberately constructed harmless cache test reproduced the defect and checked the fix: an unchanged invented source defined marker `source`, while a valid timestamp/size-matched bytecode cache defined `cached`. The old import read `cached`; the new loader read `source`. A wrong source digest was rejected before module registration/execution. All fixture and verifier bytes remained unchanged. This test executed no real decoder or scientific bundle.

These checks are not a hostile concurrent-filesystem/TOCTOU guarantee. The manifest is hashed and parsed in separate reads, and payloads are checked before and after use under a stable-local-files assumption. Confined internal links are not categorically rejected, and undeclared inert files are not a full-directory inventory failure. The later bundle-preparation check should bind the concrete ordinary files and external published manifest. The returned `external_paths_read=0` denotes no external **evidence dependency** in the intended bundled CLI, not an instrumented audit of interpreter/standard-library I/O or a claim that a caller cannot run an identical verifier copy elsewhere. No broader sandbox/security claim is warranted.

## Development history and controls

The preserved first development failure (`ATTEMPT01_CONTROL_FAILURE.json`, SHA256 `291d621e6c016fdb5f6666c7e6790c2912da96b94239998aeb067edee7994c06`) is a wrong invented assertion: `3/4−2` was expected as `−1/4` instead of `−5/4`. The correction changes that test expectation, not the reconstruction. The original invented-control PASS receipt (`CONTROL_PASS.json`, `612a8282ce6801d04651eeb82d5928a938906d541f56b4320a9221e41580e132`) remains unchanged and bound to the pre-loader source.

The additive stale-cache control source is `STALE_CACHE_CONTROL.py`, SHA256 `9021cc53ce447e5a1adb841705fa5d060179b07131e901adcd6cf5063812e5c8`. Its sole run exited zero. `STALE_CACHE_CONTROL_PASS.json`, SHA256 `b9c006f4e79e920e9bfaa83b1837e88bad80df066ceaa3edc29a0df50f22149a`, records the new source binding, unchanged reconstruction AST, reproduced old-loader behavior, corrected execution, digest rejection and zero scientific/optimizer calls. Synthetic source/cache files are retained privately under `.work/portable_state_cut_invented_control01`; they are not scientific payloads.

**Disposition:** the mathematical reconstruction is suitable for a solver-free standalone fixed-state certificate check. The identified cache defect is resolved by the authored narrow patch, subject to the parent's separate source-delta review and subsequent concrete bundle gate. A later relocated successful run would be packaging/reproducibility evidence on its actual host, not a new scientific result, independent discovery or second-machine replication.

**Closure addendum:** the parent independently read the final `8a1774b6...` loader delta and invented receipt and reported acceptance, with review memo SHA256 `61bf3d28f8be7a4302f7536b6a6b5617b8c279fb02c650c18ddbd8b00a3e5ae4`. The separate authorship/delta gate is therefore closed. No unresolved source-mathematics or intended stable-bundle path blocker remains. The parent reports a newly frozen ten-file bundle and scratch copy; this source review has not inspected, admitted or executed those concrete packages.
