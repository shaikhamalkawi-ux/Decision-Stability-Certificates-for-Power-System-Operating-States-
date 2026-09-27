# Original unrestricted-energy supplement: preparation review

Verdict: SOURCE AND PREPARED LAYOUT/RECEIPT PASS. This is a limited preparation gate, not a mathematical replay or an independent repetition of all payload hashes.

The corrected private extraction helper has SHA256 507cd33e67554f2b966de0228d18fd58ebc33e87e346db25f93e77b21a528ffe. Its source was reviewed without execution by this reviewer. Before preparation, ancestor symlink/reparse rejection, Windows path-component guards and file/ancestor collision checks were added. The final helper requires a fresh external directory, exclusive file creation, the exact final20 ZIP size/hash, outer-manifest hash, commit and complete inventory. It checks each ZIP member CRC plus declared byte count/SHA256, rechecks extracted contents, and creates only a receipt outside the immutable package. Normal isolated Python invocation without -O is required because the guards use assertions.

The parent then executed this helper once and reported exit 0. This independent post-preparation read-only check inspected the receipt, actual layout, source identity, actual outer-manifest digest and PACKAGE_PROVENANCE.json. It traversed all extracted paths to reject symlinks/reparse points and compared the complete file-name inventory with the outer manifest. It did not import a wrapper or model helper, parse model arrays, repeat the payload hash pass, or perform scientific arithmetic.

External root: C:/Users/gmalkawi/.codex/research-replays/unrestricted-energy-final20-20260927. At the gate it contained only PREPARATION.json and package/. The package has 4,815 payloads plus FILE_MANIFEST.csv (4,816 files), 579 directories, no links/reparse points, and no reports directory.

Trusted final ZIP SHA256: e4d9b181668a68b0f7db1c0cc8c30182ac56c0a461c1dbd5a37fb63d933a6aa9. Actual outer-manifest SHA256: 4c9f6db4561470775c5e567956c48825de44a6700b0cdcd1607ca50770089409. PACKAGE_PROVENANCE.json identifies commit 3f51758b521967739131701b106be60036a3fdd4 and its SHA256 is 06dbe0aad2bfcc3ae30a32d2e288403655806b2ac91c672e11c48dfdc286e857.

Receipt PREPARATION.json SHA256: 22675d887ccbe78e32b34bccd4baffe5336f25326f23596920889f31d3eb911b. It records the expected source/archive/outer/commit identities and zero scientific computations, producer imports, optimizer calls and network calls. Those preparation declarations agree with the reviewed helper's scope; the full payload CRC/hash execution belongs to the parent's extraction record. The later wrapper must independently prehash its package before any mathematical checks.

No v3, final20 ZIP, package manifest or scientific artifact was changed. The external supplement's source/protocol review and explicit replay GO remain separate gates.
