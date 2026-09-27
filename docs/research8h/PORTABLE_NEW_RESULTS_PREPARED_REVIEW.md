# Portable new-results candidate: independent prepared review

Verdict: PASS for a separately authorized wrapper replay. This gate performed archive/filesystem hashing and inventory checks only; it did not import the wrapper, run its fixtures or replay mathematics.

The reviewed candidate is .work/portable_new_results_candidate01/package, derived from Checkpoint05 science commit 9000fcc74886cc942b52f8070ff6cf382db63591. Base ZIP SHA256 495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7 (88756097 bytes); candidate ZIP SHA256 d098c9b6154fcfa02645c1395d55e338fb04fb3c4ef7dd9bad35548463d01ad9 (67347208 bytes). The candidate outer manifest is 4fbe3109b23ce965c13cc1f26bce12f99e4aad65e52c93ec51bc670d753a9534 and the prepared freeze is 0b02331d14718871d30a7c0f933f07047f851459dbdfa09b4202714b76111c89.

Independently checked both ZIP inventories and every contained payload against its manifest, then the complete extracted inventory and payload hashes. All 3501 base payload bindings are preserved. Exactly the reviewed new wrapper and protocol are added, producing 3503 payloads plus FILE_MANIFEST.csv. Their source hashes remain 073d04a2… and 72093987…. The old helper and standalone kernel retain c6cf226a… and 708c3843…. The 3504 files and all directories are regular/link-free: 521 descendant directories, or 522 counting the package root. ZIP link/reparse/special-file entries and extracted link/reparse/special files were explicitly rejected, satisfying the code review's link condition.

The prospective results/research8h/portable_new_closed_replay/checkpoint05_candidate01 report directory was absent and lies outside the package. Execution authorization is separate; no replay result is inferred from this PASS.

Evidence: results/research8h/portable_new_results_independent_review/prepared_review.py SHA256 5e648464f676a6135d7ab2cdce2f9937dfa19bffeadf23feb365d02cb43baf79; prepared_review.json SHA256 3180c40d3e4ca4fce19ef4192d5954e9a70db41abd81eeed2de167b836c16102. Completed read-only audit exited 0 in 17.574937 seconds.

One earlier reviewer-only attempt stopped because it unnecessarily required a single CSV field order. The historical base uses path,bytes,sha256; the candidate uses path,sha256,bytes. The preserved attempt01 source/report records this. The corrected reviewer validates the same unique named fields regardless of order. Candidate, original ZIPs and producer source were unchanged. No optimizer or mathematical retry occurred.
