# Prospective isolated setup after registry admission

Status: DESIGN ONLY. This document neither launches setup nor authorizes a scientific import, model build, coefficient export or optimizer. The single registry-acquisition attempt is separate; setup can proceed only after its final admission receipt and a separately reviewed setup driver.

## Fixed inputs and rationale

Keep Julia 1.6.7 Windows x64, UnitCommitment commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5` (0.4.0), JuMP 1.15.1, MathOptInterface 1.20.1 and PackageCompiler 1.7.7. The runtime ZIP was verified against SHA256 `63e14aa2e056f76f4a8f79eb8b4ed6698e3817eb3584e12b030f26f36e70cce6`; its existing executable has SHA256 `29ebe4b29362a2e380848dd4803e67343fe1779207b4970390418a1d495da67f`. Reuse that runtime read-only. A newly resolved manifest would be an explicitly recorded audit environment, not a recovered historical authors' manifest.

The candidate registry is the official General commit `416a13c3e4888af4b245812d8f4ab040a042c38f`, tree `f39bab42a09b8a82574435c6e402e598b3200dc3`. The registry acquisition must finish `READY_PINNED_REGISTRY_ARCHIVE_ONLY`, with its archive SHA256, full file inventory and exact tree match. No incomplete archive from attempt02 may seed the environment.

## Local source grounding

The checked Julia runtime contains Pkg source at `.work/researchnext_julia_export/attempt01/runtime/julia-1.6.7/share/julia/stdlib/v1.6/Pkg/src/`:

- `Pkg.jl`, function `pkg_server` (lines 23–28): an explicitly empty `JULIA_PKG_SERVER` returns `nothing`. This is a process-local route choice, not a certificate bypass.
- `Types.jl`, `collect_registries` (around lines 925–943): scans each depot's `registries/<name>/Registry.toml`, reads and verifies the registry metadata, and records the actual directory.
- `Types.jl`, `clone_default_registries` (around lines 900–923): default registry installation is conditional on installed registry discovery. A verified General tree in the isolated depot is therefore a concrete route around the previous absent-registry state.
- `Types.jl`, `update_registries` (lines 1152–1249): mutation/download branches require `.tree_info.toml` or a `.git` directory. A plain pinned archive tree with neither is discovered but has no update branch. This supports retaining the pinned snapshot without modifying Pkg internals; setup must assert neither marker exists and rehash the registry afterward.
- `API.jl`, `add` (line 153 onward): package addition invokes registry update as part of its normal sequence. Disabling the package server does not disable package acquisition: package sources and artifacts can still require their official direct upstream routes.

The local file SHA256 bindings are `Pkg.jl` = `c5fb5ff466afecdeafd9aec8c1579a907625a2a10c014992243884936018ab6b`, `Types.jl` = `8c3933c01dfdd1cc8af575594064eeb6433e5b777b586edc59cf2e9ed36dcada`, and `API.jl` = `ed80ac79c48fc6a33b28ab9a6ad639a517ff605cecebcf9601228f7392e2c172`.

These are source-grounded expectations, not evidence that the future Julia setup has run successfully. No internal Pkg state will be patched and no global Git, PATH, registry, certificate or application setting will be changed.

## Proposed one-attempt implementation contract

1. Create a fresh private directory such as `.work/researchnext_julia_export/setup_after_registry01/`, with separate project, depot, temporary directory and incremental stdout/stderr logs. Refuse existing output. Leave attempts01/02 and registry_acquire03 unchanged.
2. Bind the admitted registry archive and inventory by exact hashes. Validate every member against that inventory while streaming regular files into the fresh `depot/registries/General` directory, using explicit safe path checks and no link extraction. Recompute all file hashes and the same Git tree before Julia. Do not add `.git` or `.tree_info.toml`.
3. Use only child-process environment variables: fresh `JULIA_DEPOT_PATH`, fresh `JULIA_PROJECT`, Windows `JULIA_LOAD_PATH=@;@stdlib`, `JULIA_PKG_SERVER=""`, fresh temporary directories and disabled automatic precompilation as previously proposed. Keep normal TLS verification; any network failure is preserved without a fallback certificate remedy.
4. Make one bounded Julia launch and one `Pkg.add` call containing the same four fixed PackageSpec entries: UnitCommitment URL plus full commit, JuMP 1.15.1, MathOptInterface 1.20.1 and PackageCompiler 1.7.7. Check UnitCommitment's declared version 0.4.0 after install; do not supply both version and repository revision in that PackageSpec, which `API.jl` explicitly rejects. The actual driver must copy the already reviewed scientific pins exactly and reject any mismatch; it must not silently substitute versions or delete dependencies.
5. Emit and flush durable markers immediately before and after `using Pkg` and immediately before and after the single `Pkg.add`. Keep stdout/stderr separate from cleanup logs. Record the owned Julia PID, starts/ends, execution stage and periodic owned-process CPU/state observations only. Guard the entire post-Popen region so all failure paths clean up that process tree.
6. Proposed total infrastructure allocation: 3600 seconds, including extraction, checks and package acquisition. This is a soft allocation with recorded cleanup overhead. No retry, alternate registry, resolver fallback, new package version or automatic resume follows failure.
7. A successful setup receipt requires actual Project/Manifest files, `VERSION`, installed package versions and UnitCommitment source-tree binding to the pinned commit. Preserve raw Windows checkout hashes and separately document any proven CRLF/LF difference against upstream blobs. Compare registry bytes/tree before and after setup. Archive selected safe provenance; keep raw logs private until checked for enterprise TLS details.
8. Environment readiness authorizes no scientific action automatically. The already drafted one-identity official-Julia export source/protocol requires its own final environment-compatible review and explicit execution gate. It performs no optimizer call; the original twelve ORLIB solves are not repeated.

## Possible outcomes and limits

Successful registry admission only resolves a source-acquisition prerequisite. A later dependency-resolution, package-source or artifact failure remains an infrastructure outcome unless the actual resolver provides a concrete compatibility error. No package incompatibility, native coefficient identity or model-fidelity result may be inferred from timeout, missing manifest or a partial download. The official runtime coefficient comparison remains `NOT_TESTED` until a completed export and independent normalized-encoding comparison establish otherwise.

Before implementation, the exact PackageSpec list, environment variables, source/protocol hashes, duration, fresh paths and receipt schema must be reviewed against this plan. The placeholder setup path and allocation above are proposals, not a completed or already started attempt.
