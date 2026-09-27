# One isolated setup from the admitted General archive

Prospective infrastructure protocol; source review precedes execution. No scientific model import/build/export, optimizer or repetition of the twelve closed ORLIB solves is authorized by this protocol. The source is `src/researchnext_julia_setup_after_registry.py`, invoked once with `--setup-once` under Python `-I -S` only after root review/GO.

## Inputs fixed before execution

Reuse the existing verified Julia 1.6.7 runtime read-only. Require runtime ZIP SHA256 `63e14aa2e056f76f4a8f79eb8b4ed6698e3817eb3584e12b030f26f36e70cce6` and executable SHA256 `29ebe4b29362a2e380848dd4803e67343fe1779207b4970390418a1d495da67f`. Bind the local Pkg source files recorded in `JULIA_AFTER_REGISTRY_SETUP_PLAN.md`.

Use the already downloaded private General archive, SHA256 `53e48326acc56f53ac4527a41e7362a29622d3bf9d406234c5ddc05566869211`, with acquisition receipt `86eeaf107b46baaabd4abc88b54507b934822956d18d0d917e4ccda2682788d5` and full inventory `cc8d9ce6757ffc70a1347ab3bf9e74a2bbaba87f4131bb3737746a52c19f0f42`. It contains 61,167 regular files at General commit `416a13c3e4888af4b245812d8f4ab040a042c38f`, Git tree `f39bab42a09b8a82574435c6e402e598b3200dc3`. No registry acquisition request is made by this driver.

The standalone code derives logging, process-cleanup and package-inventory logic from closed `src/researchnext_julia_setup_attempt02.py`, SHA256 `962722972cf97e811a44fb9630058cb768a48ec95413acda49f469d873df5352`. It checks that binding and contains its own functions; it does not import or edit the historical driver. Native-source bindings remain the closed 18-file receipt `6038d94eca340f7f0bf759330aa57f30d3930834fb4e1eccd8ff824c61fbd927`.

## Single attempt and normal network access

Create fresh `.work/researchnext_julia_export/setup_after_registry01/` and `results/research_next/orlib_julia_export/setup_after_registry01/`; refuse either existing directory. Use a new project, depot and temporary directory. Copy no old package cache. Preserve attempts01/02, registry_acquire03 and their outputs.

The 3600-second total soft allocation starts before input verification and includes extraction, readback, package resolution and readiness checks. Guard immediately before the one Julia launch. Actual elapsed time and any cleanup/closure overrun are authoritative. Failure, timeout or mismatch closes the attempt without a retry, fallback version, alternate registry, dependency removal or automatic continuation.

Stream only regular tar payloads admitted by the frozen inventory into `depot/registries/General`. Reject links/reparse components, traversal, reserved/case-colliding paths, unexpected members, changed sizes/modes/hashes and any missing payload. Re-read all extracted files and reconstruct the exact Git tree. Keep the seeded registry plain: neither `.git` nor `.tree_info.toml` may exist. Recheck all files and the tree after successful package installation. The original compressed archive, inventory and receipt remain read-only.

Use child-local `JULIA_DEPOT_PATH`, `JULIA_PROJECT`, Windows `JULIA_LOAD_PATH=@;@stdlib`, `JULIA_PKG_SERVER=""`, thread counts one, `JULIA_PKG_PRECOMPILE_AUTO=0`, TEMP/TMP and `--startup-file=no --history-file=no`. This selects direct package/artifact routes with normal TLS. Reject inherited Julia no-verification host settings. Do not change global settings, inject certificates or disable TLS validation. Pkg's normal internal dependency acquisition/build behavior belongs to the single call; the driver does not import UnitCommitment or call its modeling/solving APIs.

Exactly one Julia launch performs exactly one `Pkg.add` call with four PackageSpecs, unchanged from the reviewed earlier plan:

1. `https://github.com/ANL-CEEESA/UnitCommitment.jl`, revision `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`; require installed version 0.4.0.
2. JuMP 1.15.1.
3. MathOptInterface 1.20.1.
4. PackageCompiler 1.7.7.

Do not combine a version argument with UnitCommitment's repository revision; Pkg rejects that form. A newly resolved Manifest records this audit environment, not the authors' original historical environment.

## Durable evidence and closure

Before importing Pkg, Julia writes and flushes a controlled stage line using Base functionality. It records another after import, then a durable pre-call marker immediately before the single `Pkg.add`, and a returned marker only afterward. A pre-call marker proves attempted entry at the sole source call site; it does not prove successful resolution. Python records the owned PID, launch time and command, drains stdout/stderr separately into private incremental logs, and periodically observes only that known parent and direct children. Cleanup output uses a separate private file.

The cleanup guard encloses the entire post-Popen region, including launch-record and log-thread creation. On any exception or timeout, terminate only that owned process tree and record any cleanup/liveness error. A failed log write cannot prevent the termination attempt. No other research process is stopped.

Readiness requires successful exit, direct version/revision checks, actual Project/Manifest/package inventory, selected native-source bindings, unchanged reused archive/runtime/source/protocol, complete durable logs, and unchanged pinned registry. Record raw Windows checkout SHA256 values; verify the 18 source files against pinned upstream blobs after a read-only CRLF-to-LF comparison, without rewriting them. Package inventory records actual dependency versions and reported tree hashes. This source correspondence is not runtime coefficient equivalence.

On failure preserve partial Project/Manifest/inventory and controlled stages when present. Save accurate invocation/attempt counts, elapsed time, current stage and private-log hashes. Raw network/installation logs stay private pending enterprise-TLS review. `READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD` authorizes no export automatically; all other outcomes remain `SETUP_FAILED_PRESERVED_NO_RETRY`. A timeout is not evidence of package incompatibility. Official Julia coefficient fidelity remains `NOT_TESTED` until the separately reviewed export and comparison finish.
