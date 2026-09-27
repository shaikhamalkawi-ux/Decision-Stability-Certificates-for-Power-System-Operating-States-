# Native reverse target: raw export closure

**Closed: `OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON`.** The sole authorized execution completed with exit code 0 on 27 September 2026. It used the unchanged official UnitCommitment.jl package to read and build the already fixed `reverse_4_19__native_penalized` OR-LIB target once. There were zero optimizer calls, package resolutions, requested network calls, or retries. No target coefficient comparison, candidate verification, bound transfer, or cost-difference calculation was performed in this arm.

The exported model has **2712 variables, 960 native binary declarations, and 4384 scalar affine rows** (8080 constraint records including variable-domain records). The parsed instance and raw model preserve the official encoding; these counts alone establish no equivalence with the earlier source-derived model.

The destination-to-source order is `[0,1,2,3,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,20,21,22,23]`. Preparation changed only the stored load and reserve arrays. The absent penalty field stayed absent; the pinned parser's default penalty remains relevant. Generator, history, cost and other source fields were retained. This is a post-label fidelity extension of one previously fixed synthetic, one-bus UC target, not a new target, network validation, or decision-regret result. Rotation and hard-service cases remain outside this export.

## Provenance and timing

The environment is Julia 1.6.7, UnitCommitment.jl 0.4.0 at commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`, JuMP 1.15.1, MOI 1.20.1 and PackageCompiler 1.7.7. The 445-binding preparation is `prepared/prepared.json`, SHA256 `631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675`. Its admitted target gzip has SHA256 `0acc7728ebab28731f6f2bbc5a97025db1c4381a1a4016f798e040dd72f073d8`. The declared inherited environment and local-storage trust assumptions remain unchanged; no complete physical registry or installed-tree verification is newly claimed.

The launcher ran from **12:22:01.867902 to 12:29:30.251762 UTC**, taking **448.3842046 seconds** within its 600-second allocation. Official read-to-export completion took **98.941 seconds** within the 120-second native allocation. Both recorded overruns are zero. Julia launch-to-official-read took 267.5176661 seconds and includes import plus pre-read admission; it is not a pure import benchmark. The launcher elapsed field excludes writing its final completion receipt. The recorded owned Julia parent exited; all bound inputs remained unchanged. Initial session records are historical running-state records; the completion receipts are authoritative.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `run01/official_raw_model.json` | 8630839 | `8cd0adfe027727c1d0599a1a291c8e0b289995bc1749b72f13dfe6795289e6d6` |
| `run01/official_parsed_instance.json` | 401554 | `455814d618b3a84fe7d4bd4e2027155f8917d5a9dd57721b76ece2e472bfc227` |
| `run01/completion.json` | 87473 | `71a3b644ba77340c006f43c4b564155f144032ef46f328c100b0c35b231ac03b` |
| `launcher01/completion.json` | 7902 | `d52d7b7488d8f3978d3e0278e7f4a142b82cf3354618d5384dd5e551b1942977` |

## Review and limits

The parent completed the full source/protocol and independent prepared-input gate before execution (`ROOT_PREPARED_REVIEW.json`, SHA256 `11a81548e39a2acc31da012ec9d1ee287c036e79b2a14efab6914b30afa3e5e1`). The separate compact post-run review passed (`COMPACT_EXPORT_CLOSURE_REVIEW.md`, SHA256 `7bd7955da8b2e63ce8011b33aed0921fb64e02634fe580f434138e4b38f4955d`), checking selected bindings, actual payloads, ledger progression and timing without repeating the 445-binding preparation or performing mathematical comparisons. That reviewer authored the transport helper; its memo discloses this and does not represent an independent review of that helper's own implementation.

`final_artifact_inventory.csv` binds the public arm files and its five source/protocol/design dependencies; paths are repository-relative, and the inventory excludes itself. Private logs remain outside the public inventory pending publication review. Every earlier source, preparation, execution and review file is preserved. A native target objective-difference claim requires the separately gated exact model comparison and point/lower-bound transfer; it is **not established by this export closure**.
