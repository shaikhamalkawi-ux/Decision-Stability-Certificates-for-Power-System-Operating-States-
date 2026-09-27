# Final delivery source and README review

Status: SOURCE REVIEW PASS after the README command correction. Prospective source review only, completed 27 September 2026. No package construction, extraction, source imports, synthetic checks, optimization or mathematical replay was performed for this review. This is not an assertion that a final ZIP exists or that it has passed a replay.

## Reviewed files

| File | SHA256 |
|---|---|
| `.work/research8h_delivery/package_final.py` | `9aac608ce91a409a748b08a748049cf12d7cf2ae2752538e3050c6bf4b61ca8d` |
| `.work/research8h_delivery/README_FINAL_AR.md` | `8b8f9c9cc9df0eb6fef9e8a243e71104efcaeef5e6fde8dea6cef8ac4b6c85b5` |

The initial README command for `replay_new_closed_results.py` omitted two required arguments. The final reviewed README supplies both, adds the complete strict-wrapper command and names the complete strict protocol path. No unresolved command/schema issue remains in these source versions.

## Builder scope and integrity

The builder requires the exact supplied 40-character Git commit to equal HEAD and a declared checkpoint count of at least 18. It starts from the independently frozen Checkpoint05 ZIP with SHA256 `495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7`, checks that ZIP's CRC and listed member sizes/hashes, then overlays regular committed blobs under the stated documentation/results/reproducibility paths. Under `src/`, only filenames beginning `research8h_` are refreshed; other baseline source modules retain their archived bytes. Each overlay's working-tree bytes must match its selected Git blob.

Every supplied checkpoint manifest must exist and match the payload's exact bytes, SHA256 and size. The final path checks reject absolute, drive-qualified, backslash and parent-traversal paths, noncanonical separators, and case-colliding names. A fresh ZIP is written from byte buffers rather than extracting or copying link entries; its member inventory, CRC and every declared payload hash/size are checked before the partial file is renamed. The output manifest binds all payloads and excludes itself. Its SHA256 is recorded in the external `FINAL_VERIFICATION.json`, alongside the whole-ZIP SHA256, exact delivery commit and strict evidence commit.

These source checks rely on the authenticated, previously reviewed Checkpoint05 base and supplied commit, not an arbitrary untrusted ZIP or unconstrained source tree. Execution must preserve verification assertions (do not use Python `-O`). This source review does not independently authenticate a future Git commit, inspect a future payload inventory or establish that all historical manifest checks will pass. A conflict must stop construction rather than be silently rehashed or overwritten.

The authoring task reports that a separate strict-replay candidate01 stopped before mathematical replay because a broad source overlay conflicted with a historical source version. That failed attempt remains retained and diagnosis is ongoing. The final builder's narrower `research8h_` source filter is consistent with preserving such legacy files, but this static review does not declare the eventual final package validated or the separate candidate failure resolved.

## Exact wrapper interfaces and package compatibility

Read-only inspection of the three existing argument parsers and provenance paths confirmed:

| Wrapper | SHA256 | Required arguments |
|---|---|---|
| `reproducibility/replay_closed_research.py` | `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85` | `--package-root`, `--report-dir` |
| `reproducibility/replay_new_closed_results.py` | `073d04a21dac59fc34926912ac3a58b6399b32e40017584047828608a5606b51` | The preceding two, plus `--expected-package-manifest-sha256`, `--package-evidence-commit` |
| `reproducibility/replay_strict_flow.py` | `52dbe3b74c1709a36ab23b31768a8e1f1c24a1daa00df2abba7b03bd2e96fad7` | The same four arguments as the new-results wrapper |

All README invocations now match those parsers and use Python `-I -S`. Each report directory must be new and external to the extracted package. For the new-results wrapper, the trusted final outer-manifest digest and reviewed delivery commit come from the independently checked external final receipt. That wrapper records the delivery identifier without making a remote Git query. The oldest wrapper's internal `520fe5974a4d92892906c42ce51a9d12ef304d3a` identifier describes historical evidence scope; it is not the final package commit.

The builder's `STRICT_FLOW_CANDIDATE.json` is exactly the strict wrapper's expected three-key object: schema `strict-flow-candidate-v1`, scope `strict-flow-capped-and-uncapped-v1`, and evidence commit `579ecf20452b7838fdc5802744b24f597af5e1c7`. That Git17 evidence identifier is intentionally distinct from the later final delivery commit. The README uses it explicitly for strict replay and points to `docs/research8h/PORTABLE_STRICT_FLOW_REPLAY_PROTOCOL.md`.

The strict wrapper accepts a complete outer inventory with additional final manuscript/review files; it does not require the smaller candidate's file count or outer digest. It does require all added files to appear in the new outer manifest, the externally supplied digest to match that final manifest, and every pinned historical input/helper/review binding to remain unchanged. Therefore the final receipt's `outer_manifest_sha256` is the correct expected-digest argument; the old candidate digest must not be reused. The native-source addendum and its explicit path maps remain pinned by the wrappers rather than reconstructed from host-only inputs.

## README science and delivery wording

The numerical strict and seasonal intervals match the closed results already reviewed for manuscript version 3. The README distinguishes expanded angle-model evidence from the separate zero-expansion flow model, retains the sixth January capped UNKNOWN and seasonal 26094001 without a finite upper, and keeps the later positive for 26094000 separate from its historical capped-run record. It does not add the seasonal unrestricted targets or strict reuses to the six hour-conditioned targets. The existing Zenodo DOI is scoped to frozen V8.

The three wrapper scopes, same-host relocation limitation, absence of native raw-model rebuilding, and incomplete coverage of the overall research package are stated. The older two unrestricted first-week energy intervals remain outside their combined replay scope. The delivery text distinguishes local integrity checks, uploaded-file metadata and an actual downloaded-byte hash comparison; the final upload receipt must establish whichever checks are claimed. No delivery/readback success is inferred from this source review.

Final package preparation and any replay require their own concrete inventory/hash and execution gates. This memo authorizes no new experiment, optimization or publication action.

## Inherited-byte guard and typography delta

Source-only PASS for builder SHA256 `72c463c8bf837f37065f9de26f2b69b5746c46dc88868e313ecdef068b7373ff` and README SHA256 `0c55a196e72f4048983aaa0121e36ae65954b63253fc28fcaa19e05858d8a86c`. The builder now asserts exact equality before assigning any Git overlay path already present in the inherited payload dictionary. A conflicting inherited file therefore stops construction instead of replacing its bytes. The corresponding provenance flag `inherited_payload_bytes_unchanged: true` is supported by that guard for inherited files processed by the Git overlay; the separately regenerated top-level packaging metadata remain the declared exceptions from the original builder.

Removing only the added assertion and provenance field in memory reconstructs the preceding reviewed builder SHA256 `9aac608ce91a409a748b08a748049cf12d7cf2ae2752538e3050c6bf4b61ca8d` exactly. Reintroducing only the removed Arabic tatweel in memory reconstructs the preceding README SHA256 `8b8f9c9cc9df0eb6fef9e8a243e71104efcaeef5e6fde8dea6cef8ac4b6c85b5` exactly. Thus the README delta has no scientific or command change.

The authoring task reports a separately closed diagnosis of the candidate01 conflict and complete dependencies under the narrow overlay. This delta review checks the newly added source guard, not that diagnostic execution or a future final ZIP. No builder or replay was executed here. The original failed candidate remains a retained attempt rather than a successful replay.
