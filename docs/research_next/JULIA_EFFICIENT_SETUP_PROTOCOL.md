# Efficient isolated Julia setup — prospective infrastructure attempt

This is a new separately reviewed setup, not a continuation or mutation of `setup_after_registry01`. The earlier attempt was explicitly interrupted before Julia after measured local extraction progress projected insufficient useful setup time. Its partial files, source and protocol remain unchanged. No scientific hypothesis or optimizer call is retried here.

Executable: `src/researchnext_julia_setup_efficient.py`, one invocation under Python `-I -S` with `--setup-efficient-once`, only after root source review and explicit GO. Fresh private path `.work/researchnext_julia_export/setup_efficient01/`; fresh results path `results/research_next/orlib_julia_export/setup_efficient01/`. Refuse either existing directory. The **1800-second total soft allocation** includes verification, extraction, full pre-readback, Julia/Pkg and full post-readback. Actual elapsed and cleanup overrun are reported. This budget is a prospective limit, not a performance promise.

## Scientific and acquisition inputs remain fixed

Read-only Julia 1.6.7: runtime ZIP SHA256 `63e14aa2e056f76f4a8f79eb8b4ed6698e3817eb3584e12b030f26f36e70cce6`, executable SHA256 `29ebe4b29362a2e380848dd4803e67343fe1779207b4970390418a1d495da67f`.

Already admitted General archive SHA256 `53e48326acc56f53ac4527a41e7362a29622d3bf9d406234c5ddc05566869211`; receipt `86eeaf107b46baaabd4abc88b54507b934822956d18d0d917e4ccda2682788d5`; inventory `cc8d9ce6757ffc70a1347ab3bf9e74a2bbaba87f4131bb3737746a52c19f0f42`; commit `416a13c3e4888af4b245812d8f4ab040a042c38f`; Git tree `f39bab42a09b8a82574435c6e402e598b3200dc3`. No new registry download. Full archive SHA equality binds the earlier completed gzip CRC/ISIZE/EOF, tar-tail and complete tree admission, without assuming a partial archive is usable.

Keep exactly one Julia launch and one `Pkg.add` containing UnitCommitment repository revision `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5` (require installed version 0.4.0), JuMP 1.15.1, MathOptInterface 1.20.1 and PackageCompiler 1.7.7. No dependency deletion, version substitution, source patch, resolver fallback, cache copying or automatic retry. Bind the prior 18-file native source receipt `6038d94eca340f7f0bf759330aa57f30d3930834fb4e1eccd8ff824c61fbd927` and the three already pinned local Pkg source files.

The standalone driver copies reviewed logic from `researchnext_julia_setup_after_registry.py`, SHA256 `926d2022f2df0b61624a455054ee4dd519290974f67fcff1145f2d4337c5e6c5`, checks that hash and never imports or edits the old driver. All version, runtime, native-source, logging, cleanup and readiness checks are retained.

## Concrete filesystem efficiency change

Verify the fresh extraction root and ancestors once. Validate every tar name lexically and reject absolute paths, traversal, reserved Windows components, case collisions, duplicate entries, links, sparse/special entries, nonzero directory payloads, unexpected files and changed size/mode/hash. Create each directory exactly once under an already verified parent and immediately check one `lstat` record for directory type and reparse flags; cache that verified directory. Exclusive file creation rejects any pre-existing leaf. Check its resulting `lstat` record for regular type, reparse flags and exact size. Payload hashes are verified against the complete frozen inventory before writing.

Path confinement follows from the verified root plus construction only from validated relative components under cached verified directories. This avoids repeated ancestor scans and repeated resolution of the same root. The explicit assumption is that external processes do not replace paths in this fresh private directory concurrently. This is not adversarial race-proof; the previous repeated pathname checks were not race-proof either.

Full verification still occurs **before Julia and after Pkg**. Traverse using `os.scandir`, obtain one no-follow stat per entry, reject links/reparse entries and every unexpected file or directory, and require exact complete sets of all 61,167 files and their implied directories. Read every file, check byte length/SHA256 and reconstruct the exact Git tree. Git executable modes are the modes already checked against the tar inventory, rather than an invented Windows permission equivalence. A `.git` or `.tree_info.toml` addition is outside the admitted inventory and fails this verification. The pinned plain registry remains unchanged and cannot silently update.

This removes demonstrated redundant source-level metadata operations. It does not assume a measured fraction of the old delay, diagnose antivirus/storage behavior, or guarantee that the new attempt reaches Pkg within its allocation. No benchmark/preliminary extraction is performed before the authorized attempt.

## One package call and durable observations

Use a fresh isolated project/depot/temp with child-only `JULIA_DEPOT_PATH`, `JULIA_PROJECT`, Windows `JULIA_LOAD_PATH=@;@stdlib`, `JULIA_PKG_SERVER=""`, thread counts one, automatic package precompilation disabled, and `--startup-file=no --history-file=no`. Normal TLS stays enabled; inherited Julia no-verification-host settings fail. No global environment, trust store, Git, PATH or application change occurs. Pkg's ordinary dependency acquisition/build behavior is within the one package call; the driver never imports UnitCommitment or calls its read/build/solve APIs.

Stages separately record extraction, full pre-Julia registry readback, the sole Julia resolution call, metadata verification and full post-Pkg registry readback. Julia writes flushed durable markers before/after Pkg import and immediately before/after `Pkg.add`. Pre-call markers indicate attempted entry, not success. The owned Julia PID and command are saved. Incremental stdout/stderr, separate cleanup log and owned parent/direct-child observations remain private until checked for enterprise TLS details.

The complete post-Popen region has the reviewed owned-process cleanup guard, including launch-record and log-thread failures. The timeout or an exception terminates only the owned Julia tree; no other research process is touched. There is no automatic second attempt.

## Exact closure scope

Success requires actual Project/Manifest/package inventory, fixed versions/revision, complete logs, the same registry before/after, unchanged archive/runtime/source/protocol and all native-source bindings. Preserve raw installed hashes and separately verify exact read-only CRLF-to-LF correspondence to the 18 upstream blobs; do not rewrite source. The actual reported package tree hashes and resolved Manifest define this audit environment, not the authors' original environment.

On failure preserve partial files and actual invocation/attempt counts. Status is either `READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD` or `SETUP_FAILED_PRESERVED_NO_RETRY`, with actual elapsed and overrun. A timeout or infrastructure interruption is not package incompatibility or scientific evidence. No READY status automatically authorizes native scientific import, official coefficient export or optimizer execution. The already drafted exporter needs its separate environment/path-bound gate.
