# Independent efficient-setup source review

Status: `PASS_SOURCE_ONLY_REVIEW`; no blocker found. Reviewer `/root/find_deposit/gb_docs` returned this review on 2026-09-27 after reading the complete 440-line source, complete protocol and exact no-index diff against the preceding driver. This records returned evidence, not a scheduled review.

- Source: `src/researchnext_julia_setup_efficient.py`, SHA256 `b3ed859e6d7a8416ea8fc76b8184e8362c121e81952c854b748b0972e323fd00`.
- Protocol: `docs/research_next/JULIA_EFFICIENT_SETUP_PROTOCOL.md`, SHA256 `6879b4d3a03110931a060a18f9d00aaf107d5bb66ac5ddf6a92fe1c9e850b670`.

The cached `ensure_dir` function creates directories exclusively, checks directory type/reparse flags, and preserves path confinement under the explicit assumption that external processes do not replace verified paths concurrently. Complete pre/post no-follow traversal verifies exact regular-file and implied-directory sets, every content SHA256 and size, and the Git tree. Exact inventory rejection subsumes the previous specific `.git`/`.tree_info.toml` checks. The source still rejects unsafe names, links/sparse/special entries, duplicate/case collisions and changed archive size/mode/hash.

The diff confirms unchanged four PackageSpecs, sole Julia/Pkg call, process-local environment and normal TLS, durable stdout/stderr guards, owned-tree cleanup and version/native-source readiness checks. Fresh paths, launch flag and 1800-second soft allocation agree with the protocol. The efficiency change does not promise an observed runtime or solve the adversarial pathname-replacement race.

The reviewer performed no imports, execution, tests, live-attempt enumeration, extraction, network request or edits. This is a source gate only, not successful environment setup, coefficient equivalence or scientific evidence. Root's separate explicit launch authorization remains necessary.
