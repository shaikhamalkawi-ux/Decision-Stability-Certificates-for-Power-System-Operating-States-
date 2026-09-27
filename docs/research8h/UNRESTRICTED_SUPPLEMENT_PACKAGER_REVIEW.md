# Unrestricted-energy supplement packager source review

Status: SOURCE REVIEW PASS. Read-only prospective review on 27 September 2026; no package creation, mathematical replay, source import/compilation, optimizer, network call or main-archive rehash was performed.

Reviewed source: `.work/research8h_delivery/package_unrestricted_supplement.py`, SHA256 `05f6a24268d02f047aa1754f6bd6d5ea668f37088802256b4d7dacc46134656a`. This is the revised source requiring an explicit repository location. The earlier `e91a656b…` version inferred its repository from the script's location and is superseded before execution.

## Interface and fixed scope

Required arguments are `--expected-commit`, `--repository-root` and `--output-dir`. The selected repository's HEAD must exactly equal the supplied forty-character commit and its immediate parent must be final Git20 commit `3f51758b521967739131701b106be60036a3fdd4`. The explicit repository argument permits an archived copy of the packager to operate against the intended checkout rather than assuming the script lives in `.work`.

The source requires a clean tracked working tree and index. Its only payload allowlist is the new `results/research8h/verified_checkpoint21_manifest.csv`, plus that manifest itself. The exact Git20-to-Git21 change set must consist only of additions for precisely those paths. Modified, deleted, renamed or additional tracked changes fail the gate. The numerical checkpoint identifier does not imply a payload count: the actual payload count is the number of declared manifest rows, with one additional ZIP member for the manifest.

Every allowed path must be a canonical relative path under `docs/research8h/`, `reproducibility/` or `results/research8h/`. The source rejects traversal, absolute/drive/backslash paths, trailing-dot/space components, Windows reserved names, duplicate or case-colliding paths, source symlinks/reparse points and such components between each file and the repository root. The source archive contains regular byte-buffer entries, not copied link attributes.

## Integrity chain

For every payload and the manifest, the packager obtains the blob directly from the specified commit using read-only `git cat-file --batch`. It verifies the blob size and SHA256 against the manifest and requires exact equality with the corresponding working-tree bytes. The additive Git diff binds manifest membership; the explicit commit binds the bytes being queried. There is no fallback to an older file, inferred manifest entry or uncommitted result.

The output directory must not already exist, its parent must exist, and existing output-path components must not be links or reparse points. The ZIP is created with exclusive mode. Readback verifies the complete ordered member inventory, CRC and actual bytes of every member, then checks that all source payloads and the packager source remain unchanged. A separate `SUPPLEMENT_VERIFICATION.json` records the commit, parent/main-package identifiers, manifest and whole-ZIP hashes, byte/member counts and source hash.

The packager has no extraction or mathematical operation and does not read or write the main final ZIP, manuscript v3 or uploaded files. The recorded `main_package_modified: false` describes this program's operations; it is not a fresh byte scan of the main archive or a claim about concurrent external actions. The fixed main-ZIP SHA256 in the receipt identifies the required existing input delivery for later replay. It does not mean the small supplement is a self-contained copy of that main delivery.

The source uses Python assertions as its verification gates and must not be invoked with `-O`. Standard `python -I -S` is appropriate. A failure must retain diagnostics and receive separate review; this source review does not authorize a retry, change the declared cases or substitute hashes. Actual commit/manifest membership, output ZIP and any upload/readback require their own concrete integrity gates.

## Scientific and provenance wording to preserve

The associated `PORTABLE_UNRESTRICTED_ENERGY_PROTOCOL.md` fixes only the two original unrestricted January cases, 26093100 and 26093101, and their common identity. The supplement extends reproducibility coverage; it adds no experiment, solver run, network, season or scientific endpoint. It must distinguish the supplementary delivery commit from the main mathematical input's Git20 commit and outer-manifest digest.

The replay wrapper runs externally against the extracted main package. Its source digest, package outer digest and evidence commit are explicit trusted arguments. The historical first run also uses `--initial-run`; future reproduction should omit that expired historical-start gate, as the protocol states. Exact expanded original-mask membership remains distinct from nominal strict membership; three model/point/lower roles and two intervals remain the fixed denominator. The prior-bound values are historical provenance, not a fallback for failed newly replayed lower bounds.

The source review makes no claim that the new mathematical replay or independent closure has passed. It also does not relabel the original final-package coverage statement: that statement was accurate for its closed delivery, while a later successful supplement can explicitly close the two-interval replay gap. The main package, v3 manuscripts and existing delivery records remain immutable.

No blocking source issue was identified in the reviewed version. The eventual artifact review will be written separately after packaging, outside the checkpoint21 payload manifest, to avoid recursive self-inclusion. An Arabic usage guide and any final receipt must be checked at their own final hashes before delivery.
