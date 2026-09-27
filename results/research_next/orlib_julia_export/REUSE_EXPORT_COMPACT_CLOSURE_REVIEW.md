# Compact independent reuse export closure review

Status: PASS for the bounded closure review, 2026-09-27. Reviewer: `/root/find_deposit/gb_docs`.

This review read the saved launcher completion and native execution/read/build/return/completion ledgers, checked output bytes and selected source/preparation hashes, and inspected raw JSON schema/count metadata. It did not run Julia, import or execute the exporter, build a model, call a solver, use the network, replay the 433 input bindings, or compare coefficients.

The ledgers progress from zero reads/builds to one read, then one build, then build return and successful completion. All retain zero optimizer calls and no retry. The launcher records one Julia invocation, exit code 0, no stream errors, and no surviving owned parent. These are consistent saved-ledger/source records, not independent operating-system process telemetry.

The native timestamp interval is 24.003 seconds, below 120 seconds. Launcher monotonic elapsed is 430.98828890000004 seconds, below 600 seconds; the independent difference of its exact timestamp strings is 430.988528 seconds. Both reported overruns are zero. The final completion-receipt write is explicitly excluded from the elapsed sample.

All 10 public output artifacts listed by the launcher match their recorded byte lengths and SHA256 values. Principal bindings:

| Artifact | SHA256 |
| --- | --- |
| Launcher completion | `637d72f5fd632ffac7904b49571f79e34271df1b3ce0766eee8009086ac82ad4` |
| Native completion | `5328052ad2d29636013efea6fcf70e90853336cb8fceac81b4e5bbc1a4a1a75c` |
| Raw model | `028ca4d025389eecd6fa91dc278b32f262a358eede3dece50d05080cc61b0160` |
| Parsed instance | `f47bec57919401282d15d2a091291a9489e00557f5276db4062c19d8f444e139` |
| Export preparation | `348efe5b5a98baacb082b4bd11bd58974f50517b4ac02d9d2a78c7928c70bd5b` |
| Launcher source | `da982ca456ed4ed83f0050c8c92c9d10460dcff46b60ef27c5233f262a601fbb` |
| Exporter source | `969f7cf9780c940185ee48ba505c6b8da7a94c4bb86f700c56c4136eb8e01320` |
| Export protocol | `bf16b49f9fe4ed7dd17b6a85f6653f1665676b200e6a79c86ec156d59dfc36eb` |

Preparation remains `PREPARED_OFFLINE_EXPORT_NO_JULIA`, with 433 binding records and zero scientific calls. Current source/protocol hashes match the reviewed frozen versions and the closure records.

The raw schema is `official-orlib-MOI-raw-binary64-v1`: 2,712 variable entries, 2,712 semantic aliases, 960 binary indices, and 8,080 total constraint entries. Its typed metadata reports 4,384 scalar affine rows. Metadata retains `NO_OPTIMIZER`, `NOT_COMPARED`, no mfg omission, no added finite boxes, and no coefficient normalization. This compact review does not establish alias bijectivity or coefficient equivalence.

The attained status remains `OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON`. Inherited limits remain unchanged: no full physical registry readback, no blanket installed-package tree rehash, and no claim of an OS filesystem/network sandbox. Private log contents were not inspected or admitted for publication.
