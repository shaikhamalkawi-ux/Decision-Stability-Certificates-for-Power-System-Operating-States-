# Source-only reuse proposal after efficient setup closure

**Proposal only; no new execution or implementation.** The efficient attempt closed before Julia with zero Pkg/scientific calls. Its receipt `bdfae531e4721bf617444d1014e6d3917b93468d10e1472056511e42017c5989` proves completion of the declared extraction loop, but explicitly does not establish completion of the whole on-disk registry readback. Do not relabel that result or repeat extraction.

## Proposed narrower trust contract

Inherit the admitted compressed archive (`53e48326acc56f53ac4527a41e7362a29622d3bf9d406234c5ddc05566869211`), its completed gzip CRC/ISIZE/EOF/full Git-tree admission receipt (`86eeaf107b46baaabd4abc88b54507b934822956d18d0d917e4ccda2682788d5`), and complete inventory (`cc8d9ce6757ffc70a1347ab3bf9e74a2bbaba87f4131bb3737746a52c19f0f42`). General remains commit `416a13c3e4888af4b245812d8f4ab040a042c38f`, tree `f39bab42a09b8a82574435c6e402e598b3200dc3`.

The completed efficient extraction checked every archived payload's size/mode/SHA, every path/type/case collision, exclusive writes, and each created file's type/reparse flags and size. It wrote all 61,167 files. The new contract would rely on those controlled writes under the explicit assumption that no external process or storage fault changed unselected registry bytes afterward. It would not claim an independent full on-disk registry hash or adversarial race protection.

Before package resolution, verify actual `Registry.toml` against its frozen inventory SHA; parse and bind its exact registry UUID and package paths. Check only the materialized registry root/ancestors and the small selected metadata paths for links/reparse entries. Require absence of `.git` and `.tree_info.toml`; require that the reused depot contains only the prior registry, with no previous package/artifact/clone caches. No scan or re-extraction of all 61,167 contents is proposed.

## Fresh writable environment, preserved registry

Use a new `setup_reuse01` project, writable depot, temporary directory and private incremental logs. The proposed Windows `JULIA_DEPOT_PATH` is **exactly two explicitly pinned isolated paths**, fresh writable depot first and preserved `setup_efficient01/depot` second; no empty entry or user-global depot. The second depot is read-only by the workflow contract, not an OS-enforced immutable mount. Do not change its permissions or files. This is an explicit environment-provenance adjustment from the previous single-depot proposals.

Local pinned Julia1.6.7 Pkg source supports this layout:

- `Types.jl` 907–946: `clone_default_registries` consults `collect_registries()` across all depots; `collect_registries(depot)` discovers `registries/<name>/Registry.toml`. Existing General in the second depot avoids an empty-registry default installation.
- `Types.jl` 1152 onward: default `update_registries` targets registries in `depots1()`. Its mutation branches require `.tree_info.toml` or `.git`; the preserved plain registry has neither. No explicit registry update call is proposed.
- `Operations.jl` 27–36: `find_installed` searches existing depots but selects `depots1()/packages/...` for new packages. The reused depot has no old packages. Clone/scratch/log paths in the inspected code also use the first depot.

These source paths support the intended normal Pkg behavior. They do not prove arbitrary dependency build scripts cannot write elsewhere. Normal trusted official package execution and absence of external concurrent writers remain assumptions. Check `Registry.toml`, selected registry metadata and absence of update markers after the package call; do not label those selected checks a full post-run registry rehash.

## Same package call and meaningful final bindings

Propose one Julia launch and one `Pkg.add`, with a **1800-second package/setup phase** that excludes re-extraction and full-registry scanning. Keep Julia1.6.7 and its existing runtime/executable hashes, UnitCommitment revision `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`/version0.4.0, JuMP1.15.1, MathOptInterface1.20.1 and PackageCompiler1.7.7. Keep `JULIA_PKG_SERVER=""`, normal TLS, disabled startup/history/auto-precompilation, one thread, flushed import/Pkg markers, owned-process cleanup, fixed fresh outputs and no automatic retry or version change.

After the single call, bind actual Project/Manifest and package inventory. Verify every direct version and UnitCommitment revision, require installed package sources in the new writable depot, and require the already fixed 18 native source files to equal upstream blobs after the declared read-only CRLF-to-LF comparison while preserving raw SHA256 values. The pinned UC commit's tree is `619a6b12e1005425e6ac08c4c45e445bb0a6f134`, read from the existing pinned local bare Git object; compare that reported source-tree identity separately from the selected physical source checks.

For registered packages actually present in the resolved inventory, verify their General `Package.toml`, `Versions.toml`, `Deps.toml` and `Compat.toml` when present against the frozen archive inventory, then check UUID/name and the selected version's declared tree against the resolved metadata. Record which metadata were checked. Repository-tracked UnitCommitment uses its explicit revision/tree route; stdlibs use the pinned runtime. Resolver candidates that were considered but not installed are not claimed as individually re-read.

**Windows source caveat:** Julia1.6.7 `Operations.install_archive` (around lines 612–620) explicitly skips the unpacked Git-tree comparison on Windows because of executable-bit handling. Therefore normal Pkg success must not be described as independent full-content Git-tree verification of every installed package on this host. Its `install_git` path (around lines 640–677) selects the requested GitTree object. The proposed narrower readiness claim binds normal-TLS official acquisition, reported Manifest tree identities, exact versions/revision, selected registry metadata and actual native-source blobs. It leaves blanket whole-package rehash unclaimed. Any stronger claim would need a separately specified check, not an assumption.

The old exporter currently requires one depot. Before any scientific export, a new explicit source/preparation revision must bind both isolated paths and the actual ready Manifest/receipt; preserve the former exporter/protocol history. Coefficient export remains one separately gated identity native read/build with no optimizer. Successful setup alone is not coefficient equivalence.

## Readback algorithm assessment and fallback

The efficient checker builds its expected dictionaries/sets once, uses one no-follow stat and one content read per entry, and has no per-file ancestor walk or repeated whole-array/set materialization. The final Git-tree builder concatenates bytes repeatedly within each directory, an avoidable quadratic copying term; the source alone does not establish its measured cost, and it is reached only after traversal. A single owned-process counter observation showed low CPU relative to wall time; it does not identify an antivirus/storage cause or checked-file progress. Do not claim measured profiling.

If the narrower contract is rejected, the fallback is one separate read-only full verification phase on the preserved materialized tree, with a longer fixed allocation and durable per-file progress, followed by a separately budgeted package call. It would perform no extraction. Do not launch another combined 1800-second extraction/readback timeout. No option in this proposal is already authorized for execution.
