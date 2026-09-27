# Portable strict-flow replay protocol

This is a new delivery verifier for two independently closed science arms: `branch_flow_encoding` and `branch_flow_strict_energy`. It does not modify either arm, older wrappers, manifests or helpers. Both capped and uncapped scopes are eligible after their independent post-run PASS records. Source/protocol review precedes candidate preparation; independent candidate review and explicit execution authorization precede the single initial relocated replay. No success is claimed before that run passes.

## Fixed command and trust inputs

Run a separately installed ordinary Python interpreter with:

`python -I -S reproducibility/replay_strict_flow.py --package-root ABSOLUTE_PACKAGE_ROOT --report-dir NEW_EXTERNAL_REPORT_DIRECTORY --expected-package-manifest-sha256 TRUSTED_SHA256 --package-evidence-commit TRUSTED_COMMIT`

The wrapper requires isolated mode and no site packages. The supplied outer-manifest digest and evidence commit must come from separately frozen, independently checked candidate provenance. They must not be copied from an unverified package's own claims. The wrapper checks `FILE_MANIFEST.csv` bytes against the supplied digest before importing any package helper.

The candidate must contain an outer-manifest-bound `STRICT_FLOW_CANDIDATE.json` with exactly:

```json
{"schema":"strict-flow-candidate-v1","evidence_commit":"40 lowercase hexadecimal characters","scope":"strict-flow-capped-and-uncapped-v1"}
```

Its commit must equal the external `--package-evidence-commit`. The candidate is independently built from the intended published science commit, then augmented with the reviewed wrapper/protocol and this metadata; its new outer manifest and assembly provenance are reviewed separately. This field and the trusted digest bind the selected candidate; the wrapper does not authenticate a remote Git server or query the internet.

The report directory must not exist and must be outside the package, with neither directory containing the other. Reject link/reparse-point entries, including existing report-path ancestors. Create only external reports. Invalid arguments that prevent a safe report directory may fail before any report is written; once safe output creation succeeds, preserve `failure.json` and all partial reports on an error. Never overwrite a failed attempt.

## Package and historical provenance before math

The initial recursive file inventory rejects symlinks/reparse entries, absolute/traversal/noncanonical paths, duplicate normalized names and case-fold collisions. It must exactly equal the outer manifest's payload set plus `FILE_MANIFEST.csv`. Check every file size and SHA256, including executing wrapper/protocol/helper bytes. Empty ordinary directories are permitted; no unmanifested file is permitted.

Pinned capped manifests are the103-input manifest0981491f and277-artifact inventorya86ee299. Pinned strict-energy manifests are the355-input manifest7ffffe82 and466-artifact inventory89475add. Check full exact hashes in source, not abbreviated strings. Relative artifact paths are rooted at the package. Historical absolute input paths use only the two exact workspace/native prefixes in the published native addendum. No suffix guessing, original-host fallback or network acquisition is allowed.

Follow every bound `input_manifest.json` or `input_manifest.csv` recursively until closure, using the hash already bound by its parent. Validate each record's path/hash/size and reject conflicting aliases. Missing native or historical payloads cause a diagnostic failure, never a silent partial pass. Validate the addendum's pinned24-payload manifest,17-native-file/3734672-byte inventory and exact prefix map. Applicable license/README/attribution files are verified as payloads. The raw generator CSV is pinned to988466f2 and checked against each archived native specification using the existing binary64 hourly conversion convention. This is scalar/native provenance checking, not rebuilding a model from raw time series.

Import only four hash-pinned standard-library helpers: the unchanged strict NPZ/Farkas kernel, generic rational witness checker, capped flow point/native checker and separate uncapped flow point/native checker. No solver runner or third-party package is imported. The latter two retain their distinct cap semantics. The old files remain byte-for-byte unchanged; the wrapper sets no-bytecode mode before imports. Inherited bytecode may exist as bound historical payloads, but no new archive cache/write is permitted.

## Exact fixed replay set

Replay exactly five full strict rational points: capped January identity and control26100200, then uncapped January identity and ordinary26093200/01. Each uses29400 losslessly decoded reduced rational coordinates and the original12096 U/Y/Z binary mask. Check every model row/box at tau=0, the native fossil objective and complete native rules. Capped points require the actual23195 row; uncapped points require its absence. Compare the entire replay report to its archived accepted report and recompute exact fossil energy.

Check each full uncapped model is its corresponding full capped model with only that cap row deleted: all retained sparse coefficients/endpoints, boxes, masks, objective and native/package/graph/specification byte copies match. Do not transfer any old angle-model bound or point by assumption. Validate the control's fixed14-position native/package permutation, exact P/theta/flow transport, unchanged canonical states and exact energy equality. Direct native ramp checks still apply.

Replay all eight fixed ray candidates, four per capped ordinary case. Reconstruct positive/negative raw and sign-only projected candidates from the saved raw solver ray; no coefficient threshold or new support search is permitted. Validate actual model/bounds/raw-ray/row-label/manifest bindings. Independently recompute strict and exactly `Fraction.from_float(1e-5)` expanded gaps with all original finite boxes. Preserve raw-candidate rejection reasons and nonseparating candidates, verify the fixed selection rule, and require both selected strict and expanded separations for these closed outcomes. Numerical infeasibility status is not the proof.

Replay all fifteen retained objective-lower candidates, five per uncapped full model: zero,+raw,+projected,-raw,-projected. Use exact `r=c-A^T y` and selected finite-row beta, then `L=beta+min_box(r*x)` at tau=0. Compare every sparse residual, term and rejected sign combination, then verify the largest-bound selection with fixed-order ties. Require the native23-fossil objective excluding nuclear. No numerical stationarity tolerance, solver dual bound or previously calculated display value is trusted.

Recompute both finite optimal-energy difference intervals and relative intervals using the strict lower/upper enclosures. Require L<=U; percent formulas require positive identity lower and nonnegative target lower. Compare exact fractions, positivity flags and both-case denominator to the closed outcomes. The bounds enclose unknown binary optima; they do not assert exact global optimality.

Check the closed three-call and five-call ledgers and actual solve-time totals, all168 capped identity hour statuses, and all336 target hour statuses/coordinate mappings against the accepted full points. Time-total summation alone allows1e-9 seconds of absolute difference for floating summation across interpreter versions; every rational scientific comparison remains exact. This is direct membership/ledger replay, not basis reconstruction or another numerical solve. Historical optimizer calls remain8; wrapper optimizer calls are0.

## Focused checks, execution and readout

The fixed synthetic-only checks cover six unsafe path forms, objective residual/upper-box arithmetic and the exact five-candidate sign-projection order. They read no science model/native data and invoke no optimizer. Do not repeat the old35-kernel test suite without a relevant change. Any source-only fixture run is separate from, and cannot establish, relocation success.

After source PASS, construct a concrete candidate in a fresh directory outside the worktree from the independently verified published payload. Record the original release digest, candidate outer digest, exact evidence commit, approved added files and all preparation provenance. The original published ZIP stays unchanged. Independently validate candidate completeness/path safety and trusted bindings before the single authorized initial replay. Reports are in a different fresh external directory; run with `-I -S` from the relocated candidate rather than relying on the original working directory.

Rehash the full file set and all bytes after mathematics and require exact equality to the initial snapshot. A final PASS reports five strict points,two selected negatives,eight ray candidates,three selected lower bounds,fifteen lower candidates,two penalty intervals,0 optimizer/network calls and no package writes, plus interpreter/platform/time and trusted package bindings. Preserve first failures, including missing payloads or schema defects. Any corrected attempt uses new candidate/report bindings under a separate review; do not overwrite or quietly repeat.

This validates offline mathematical evidence and available provenance in a distinct flow-conserving DC model. It does not reconstruct the physical models, reproduce solver discovery, rerun on a second machine, establish field operation or retroactively change the old angle-model results. A local fresh-directory relocation must be described as such.
