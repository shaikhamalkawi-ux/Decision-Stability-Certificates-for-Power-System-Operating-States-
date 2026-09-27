# One official Julia/JuMP OR-LIB export

2026-09-27. Prospective source contract, before any native scientific import, read, build or export. Environment acquisition is separately authorized and does not establish model fidelity. The exporter is `src/researchnext_julia_export.jl`. Execution requires the completed environment receipt, source review and a separate explicit one-run decision. No optimizer is attached or called, and the twelve closed OR-LIB optimization calls are not repeated.

## Fixed input and environment

Exactly the identity, native penalized-service case is eligible: `results/research_next/orlib_preflight/solver_prepared01/inputs/selected_case.json.gz`, SHA256 `6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe`. It is the synthetic ten-unit, 24-hour, one-bus, no-line case already selected. No permutation, hard-service variant, target selection or cost modification is permitted. The later comparison target is the unchanged `identity__native_penalized.json` beside it, SHA256 `5abc7c12289d6428081f49646553863abaa041abfd4bac6215d7d49130b2f725`.

The candidate environment is official Julia1.6.7 Windows x64, UnitCommitment0.4.0 at `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`, JuMP1.15.1, MathOptInterface1.20.1 and PackageCompiler1.7.7. Its actual resolved Project, Manifest, dependency tree hashes, runtime checksum and install log must be archived. The isolated depot/project under `.work/researchnext_julia_export/attempt01` remains separate from the user's global environment. No package deletion, source patch, resolver fallback or export-time installation is allowed. A package or import failure remains an environment/export failure, not a scientific result.

The exporter accepts six positional arguments:

```text
CASE_GZIP ENVIRONMENT_RECEIPT EXPECTED_RECEIPT_SHA OUTPUT_DIR PROJECT_MANIFEST EXPECTED_MANIFEST_SHA
```

`ENVIRONMENT_RECEIPT` must be the new acquisition receipt with status `READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD`. Its external SHA and the active project Manifest SHA are supplied by the reviewed preparation record, not inferred from an untrusted input. The executable checksum, sole depot, selected versions, full UnitCommitment revision and every recorded native source checksum are checked before reading the case. The reviewed source/protocol and these arguments must be hashed in a separate pre-execution record. `OUTPUT_DIR` must be fresh, under the new `results/research_next/orlib_julia_export/` arm; source enforces freshness and an existing parent, and the execution launcher/review fixes the permitted location. Nothing in the frozen Python arm is modified.

Launch with `--startup-file=no --history-file=no --project=<isolated project>`, the same sole `JULIA_DEPOT_PATH`, `JULIA_LOAD_PATH=@;@stdlib`, and one Julia/OpenBLAS thread. Package auto-precompilation is disabled as in acquisition. No exporter network or Pkg resolution operation exists. JSON serialization uses the pinned native package's already declared `UnitCommitment.JSON` dependency binding; the isolated project need not acquire another direct dependency.

## One read, one build, no optimization

The only native scientific calls are `UnitCommitment.read(local_gzip)` once and `UnitCommitment.build_model(instance=instance, optimizer=nothing, formulation=UnitCommitment.Formulation(), variable_names=true)` once. Native parsing, migration, repairs, initial state and default formulation remain active. `read_benchmark`, `optimize!`, solver attachment, hard-service restriction and artificial finite boxes are absent. The cached backend must report `NO_OPTIMIZER`.

The exporter records the parsed scenario, unit, reserve, demand, cost-segment and startup fields; it asserts the selected horizon/roster and absence of other asset classes. It writes durable read-attempt and build-attempt receipts before their respective calls, and a build-return receipt afterward. An exception preserves the attempted counts and available outputs. A source/import failure before these receipts is recorded by the external process log and does not justify another attempt.

Prospective execution uses one external 600-second process ceiling, including first package import/compilation, parsing, building and serialization. This refines the preflight's proposed 120-second build/export-only allowance to avoid hiding cold-import cost in another run. It is not a performance benchmark or hard operating-system latency guarantee. On timeout terminate only the owned process tree, preserve all partial files and actual start/end/elapsed/overrun, and report incomplete export. No automatic retry, version substitution or second model build follows. The external launcher must archive its command/environment, PID, exit code and log even when the Julia source cannot produce a receipt.

## Raw export semantics

Enumerate the JuMP cached MOI backend using all variable indices and all present function/set constraint types. For each typed constraint, save its raw index, diagnostic name, function, affine terms and constant, and set endpoints. Include variable-in-set bounds and `ZeroOne` declarations. Unsupported function or set types fail explicitly rather than being dropped. Record every objective term, constant and sense. Store every Float64 as its exact 16-digit UInt64 hexadecimal representation; decimal strings are diagnostic only. Infinities, signed zero and any anomalous value remain visible in those bits.

Native object-dictionary variable containers supply semantic family/key/index aliases. Verify that aliases cover all backend variables exactly once. Names do not establish mapping by themselves. Enumerating backend rows preserves native duplicate and unnamed constraints, including the PWL equalities overwritten only in a native dictionary. No deduplication, coefficient recomputation, row rescaling, finite bound addition or mfg deletion is performed. Counts are measured and reported, not forced to match the anticipated 2712 variables, 960 binary coordinates and 240 additional mfg variables.

Record `official_parsed_instance.json`, `official_raw_model.json`, all attempt receipts and `completion.json` or `failure.json`. Completion binds both output hashes and verifies unchanged case, receipt, Manifest, source and recorded native source files. The external closure inventory binds every output and the source/protocol. Successful serialization has status `OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON` and `comparison_status: NOT_COMPARED`; it cannot be reported as runtime coefficient equivalence.

## Separate subsequent comparison, not an export claim

After raw export closure, an independently reviewed standard-library comparator may map the recorded semantic coordinates to the archived Python model without another Julia build or optimizer. That comparator is not implemented or executed by this source contract. Its required comparison is exact binary64/rational, with full row multiplicities, native binary mask and objective. Permitted row orientation changes must swap bounds and be recorded; no tolerance-based coefficient matching or silent arithmetic reassociation is allowed. A one-ULP disagreement remains a disagreement.

Projection of mfg is admissible only after the raw runtime export shows all 240 variables have zero objective and no active row terms except their nonnegative bounds; the nominal lift is mfg=0. Added finite Python Q/R upper bounds and N=0 are separately justified nominal restrictions from headroom/nonnegativity/binary bounds and the one-bus equality. They are not native raw bound identity. Any unexpected term, binary, initial-state condition, multiplicity or coefficient prevents an unqualified equivalence claim and must be retained in a mismatch report.

Even exact nominal equivalence under declared projection/boxes does not equate the models obtained by independently expanding all their finite bounds by tau. Redundant bounds, normalization and coordinate choices affect that expanded set. Existing certified cost intervals remain attached to their exact archived Python models. Identity-only runtime inspection cannot claim that all other five models were independently exported. The former `NOT_TESTED` record remains immutable; a new independently reviewed sidecar states only the attained comparison layer.

## Primary source grounding

The frozen source uses the [native reader](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/instance/read.jl), [native instance structs](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/instance/structs.jl), [builder](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/build.jl), [MOI1.20.1 attributes](https://github.com/jump-dev/MathOptInterface.jl/blob/v1.20.1/src/attributes.jl) and [MOI caching-state API](https://github.com/jump-dev/MathOptInterface.jl/blob/v1.20.1/src/Utilities/cachingoptimizer.jl). The latter explicitly supplies `Utilities.state(::CachingOptimizer)` and `NO_OPTIMIZER`. The upstream UnitCommitment repository has no recovered root Manifest at the selected commit; this is a recorded compatible audit stack, not a claim to recover its authors' original environment.
