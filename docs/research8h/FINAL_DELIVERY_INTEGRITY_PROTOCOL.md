# Independent final delivery integrity audit — prospective protocol

Status: source implementation only. No final-ZIP audit has been executed under this protocol. Actual execution requires the concrete final archive, completed independent candidate02 preparation/replay gates, externally supplied trusted arguments and a separate explicit execution instruction.

Source: `results/research8h/final_delivery_independent_review.py`, SHA256 `d6baf4b275e6395865b3a5c6031ed85b738f5b4d0e85f60d8bbae599648ec9f7`.

## Purpose and scope

Establish that the actual final ZIP contains unchanged bytes for the strict-flow candidate whose mathematical replay has separately passed, while independently checking final archive integrity, complete inventory, checkpoint coverage and local Git blob identity. This is an integrity/coverage audit, not a second mathematical replay. It makes no optimizer, network, native-assembly or extraction call and imports no scientific or replay module.

Three archives are inputs: the immutable Checkpoint05 base, the independently gated strict candidate02, and the actual final delivery ZIP. The fixed base SHA256 is `495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7`, with 88,756,097 bytes and 3,501 payloads. Candidate02's final digest, outer-manifest digest and payload count must come from its independent frozen gate; the prospective preparation expects 4,566 payloads but this protocol does not claim that preparation has passed. No failed candidate is substituted or retried by this audit.

## Exact metadata exceptions

Every candidate02 payload must be present and byte-for-byte identical in the final ZIP except these two root payloads:

- `FILE_ALLOWLIST.txt`: regenerated and checked against the complete final member inventory, including itself and the outer manifest.
- `PACKAGE_PROVENANCE.json`: regenerated and checked against the expected delivery commit, overlay count, checkpoint checks and integrity declarations.

The root `FILE_MANIFEST.csv` is not a payload in its own manifest. Each archive's outer manifest is validated separately; candidate and final outer digests intentionally differ. No nested manifest, science result, native input, source, wrapper, protocol or `STRICT_FLOW_CANDIDATE.json` is an exception. In particular the latter must remain the identical three-key strict metadata object with scope `strict-flow-capped-and-uncapped-v1`, schema `strict-flow-candidate-v1`, and evidence commit `579ecf20452b7838fdc5802744b24f597af5e1c7`.

The strict evidence commit is distinct from the later final-delivery commit. The final receipt's `outer_manifest_sha256` is the correct strict-wrapper manifest argument for the final ZIP; the earlier candidate digest cannot be reused for that enlarged package.

## Fixed checks

1. Bind the executing source, final verification receipt, candidate replay summary, candidate ZIP/manifest and reviewed final README to externally supplied SHA256 values. Validate the expected final commit and declared checkpoint count. No trust value is silently inferred from an untrusted package.
2. Check every filesystem input component for links/reparse points. Inspect all three ZIP inventories without extracting. Reject absolute/escaping/noncanonical paths, invalid Windows components, file/ancestor collisions, case collisions, duplicate members, links/special entries, encryption and unsupported compression. Verify every member's CRC, length and SHA256 and exact manifest membership.
3. Verify every Checkpoint05 payload is unchanged in candidate02. Compare every non-exempt candidate02 payload against the final ZIP by actual streamed byte equality, not only equal recorded hashes. This includes all strict evidence, historical dependencies, native addendum and wrapper bytes.
4. Require the externally bound candidate replay summary to report strict replay PASS with the same candidate outer digest and evidence commit: five strict points, two selected negatives/eight ray candidates, three lower bounds/fifteen multiplier candidates, two penalty intervals, no optimizer/network/native reconstruction, and unchanged package files. The root task separately requires independent review of this replay; this integrity script does not replace that gate.
5. Reproduce the final builder's selected local Git overlay at the explicit expected commit. Check every final selected payload's Git blob hash. Require exact final inventory equality to the base plus that overlay and the declared generated packaging files. The executing audit source itself must be committed and byte-identical in the final ZIP.
6. Read every checkpoint manifest from 01 through the declared final count and check all its payload sizes/hashes against the final archive. Require matching checkpoint and overlay accounting in both external receipt and regenerated provenance. All currently existing checkpoint01–18 CSV headers were inspected read-only and are exactly `path,bytes,sha256`.
7. Verify whole-final-ZIP SHA256, auxiliary MD5, size, member count and outer-manifest digest against the externally hash-bound final verification receipt. Rehash every input at closure to detect changes during the audit. Record both allowed metadata differences explicitly.

Git operations are read-only local `rev-parse`/`ls-tree` calls. Remote publication is externally attested by the root task's exact `ls-remote` match and final delivery receipt; the audit does not invent a remote receipt or make a network query. Additional final documentation/results receive inventory/Git checks, not a new scientific verification merely because they occur in the same ZIP.

## Invocation and output contract

Use standard-library Python with `-I -S`. The separate execution instruction must supply:

- `--repository`, `--baseline-zip`, `--candidate-zip`, `--candidate-replay-summary`, `--final-zip`, `--final-receipt`.
- `--expected-self-sha256`, `--expected-candidate-sha256`, `--expected-candidate-manifest-sha256`, `--expected-candidate-summary-sha256`, `--expected-receipt-sha256`, `--expected-readme-sha256`.
- `--expected-commit`, `--checkpoint-count`, `--expected-candidate-payloads`.
- `--report-dir`: a new private directory strictly beneath the repository's `.work/research8h_delivery`, with no input inside that report directory.

The audit never writes into a ZIP, candidate package or tracked evidence directory. Its private `integrity_review.json` records status, source and input hashes, exact counts/commit, permitted exceptions, scope and elapsed time. A failure preserves its report and does not trigger a retry, package modification or mathematical replay. A PASS establishes delivered-byte identity and archive coverage for the previously checked candidate evidence. It does not establish a new scientific result, complete replay of every research arm, native-data assembly, second-machine replication or successful remote upload/readback.

## Source gate record

The root task completed a full static read of source `d6baf4b2…` and reported SOURCE PASS. A complementary child static comparison against packager `72c463c8bf837f37065f9de26f2b69b5746c46dc88868e313ecdef068b7373ff` also reported PASS, with no concrete blocker in the inventory algebra, metadata exceptions, byte comparisons, Git selection or private output logic. Neither reviewer executed the source, compiled/imported it, inspected ZIP bytes by running the audit, or repeated mathematical verification.

One operational binding is explicit: `--expected-readme-sha256` must describe the packager's UTF-8 text bytes after its newline normalization. A read-only check of the currently reviewed README found its raw bytes already equal those normalized bytes, both with SHA256 `0c55a196e72f4048983aaa0121e36ae65954b63253fc28fcaa19e05858d8a86c`. Any later README revision needs its own reviewed digest; a mismatch fails rather than being silently normalized by the audit. Concrete package execution remains pending regardless of these source gates.
