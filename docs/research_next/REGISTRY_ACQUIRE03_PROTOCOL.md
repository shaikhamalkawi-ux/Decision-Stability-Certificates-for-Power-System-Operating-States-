# Registry acquisition03: one archive, no environment setup

2026-09-27 — prospective protocol. Closed Git25/checkpoint04 artifacts and both previous attempts remain unchanged. Source: `src/researchnext_registry_acquire.py`. The current authorization covers implementation and source review; actual network acquisition requires the parent's explicit reviewed execution decision. No user permission question is needed. No Julia, Pkg, native model read/build/export or optimizer follows automatically.

## Fixed resource and scope

Acquire General commit `416a13c3e4888af4b245812d8f4ab040a042c38f` from `https://codeload.github.com/JuliaRegistries/General/tar.gz/416a13c3e4888af4b245812d8f4ab040a042c38f`, with expected full Git tree `f39bab42a09b8a82574435c6e402e598b3200dc3`. These are the same official pins as closed attempt02; they were obtained from the official GitHub metadata endpoint and recorded previously. The archive's SHA256 is measured after transfer, while the independently fixed Git tree controls source-content admission.

Use a fresh `.work/researchnext_julia_export/registry_acquire03` for archive/raw logs and `results/research_next/registry_acquire03/run01` for selected public records. Refuse either existing directory. The driver runs only with `--acquire-once`; this is not a retry/resume switch. The preserved attempt02 partial archive must remain SHA256 `bcad8b91e05724c484a7f991fe4cca99257ed9ec0ccc6cdf5f246b8ed2991210`. No partial bytes are reused or overwritten.

## One bounded Windows curl transfer

Use the existing Windows System32 curl executable, recording its checksum. Disable curlrc loading for this process so undeclared user options cannot introduce retries or disable validation. Use HTTPS-only original/redirect protocols, normal TLS validation, five redirects maximum, zero retries, a 30-second connection timeout and a 100,000,000-byte compressed-size limit. Stream output directly into the new private file; do not accumulate 1 MiB Python reads or continue a partial transfer.

The **600-second total phase allocation includes** prior-file checks, network transfer, gzip/tar/Git-tree validation and admission. Curl's own maximum time is the remaining whole seconds at launch; the parent wait and validation loops also check the same deadline. This is a configured bound with actual wall time and any cleanup/closure overrun reported, not a guarantee about operating-system latency. A late completed download without time for validation remains unadmitted. No fallback endpoint, range request, altered package version, certificate injection or TLS bypass is permitted.

Record one attempted curl invocation and its owned PID/start before waiting. A cleanup guard covers process creation and every later launch-record/wait operation; on failure it attempts to terminate only that process tree and then the still-running owned parent if necessary. Raw stdout metrics, headers, stderr and termination diagnostics remain private. Do not print or publish full curl `%{json}`, certificate chains, network addresses or raw redirect URLs. Public transfer metadata is limited to numeric HTTP/status/timing/byte/TLS-result fields, effective scheme/hostname, redirect hostnames and recorded content-length/transfer-encoding values. Missing metadata remains missing; a parser failure does not become a success.

Admission requires curl exit0, HTTP200, HTTPS, reported TLS verification result0 and agreement between reported download bytes and the actual private file size. Failed/partial bodies and all diagnostics are retained without another request. No request is made by syntax inspection or by later local archive validation.

## Complete local archive validation

Consume the entire gzip stream through EOF with standard-library gzip, enforcing a 2,000,000,000-byte decoded limit. This verifies the CRC and size trailer; tar's early terminator alone is insufficient. Then inspect every tar member without extracting files into a filesystem or depot. Require the exact archive root, canonical relative UTF-8 paths, no traversal, backslashes, NULs, colons, Windows reserved names or trailing spaces/dots. Reject duplicate/case-colliding members, links, special/sparse members, unexpected directory payloads, more than 250,000 members or any regular file larger than 32,000,000 bytes. The total payload limit is also 2,000,000,000 bytes.

Read each regular member completely; record its SHA256, byte count and executable/nonexecutable Git mode. Reconstruct exact Git blob and tree SHA1 objects using Git's name ordering and require the full pinned tree, including modes and file multiplicity. Require Registry.toml and reject empty directories not implied by the admitted file tree. Check that all bytes after the final tar member are zero, include at least the two terminating 512-byte blocks and leave a decoded length divisible by512. This rejects hidden trailing content. Source bytes are never normalized or rewritten.

The standard-library diagnostic may read the local archive more than once; these are integrity passes, not extra acquisitions, package operations or scientific runs. Write the complete regular-file inventory only after the checks pass. Recheck the preserved partial02 and new source/protocol hashes before success. Hash every resulting public/private artifact without copying raw diagnostics into public output.

## Closure and limits

The only success status is `READY_PINNED_REGISTRY_ARCHIVE_ONLY`. It means that this archive passed transport, complete gzip/tar validation and exact source-tree admission. It does not establish package resolution, Julia importability, nominal model equivalence or the equality of expanded optimization models. Any failure becomes `ACQUISITION_FAILED_PRESERVED_NO_RETRY` with the stage, attempted-call count, partial archive hash, actual elapsed time and private diagnostic hashes retained.

All setup/scientific pins remain Julia1.6.7, UnitCommitment0.4.0 commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`, JuMP1.15.1, MathOptInterface1.20.1 and PackageCompiler1.7.7. A separate reviewed setup plan is required after registry closure. The current `runtime_JuMP_matrix_equivalence: NOT_TESTED` label remains unchanged.
