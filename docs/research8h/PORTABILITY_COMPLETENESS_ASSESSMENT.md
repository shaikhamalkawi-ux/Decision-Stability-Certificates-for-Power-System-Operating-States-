# Portability and provenance completeness assessment

Assessment date: 2026-09-27. This was a read-only inventory and source review, with no optimization, native reconstruction, repeated mathematical smoke test, or second-machine execution. The published artifact inspected was `DSC_Temporal_Research_2026-09-27_Checkpoint03.zip`: 60,850,325 bytes, 2,664 members, package SHA256 `4e1315dffaa6d02e55db5af225b4b0e9d3a8106ee6ba070c43d0fbad000868c6`, Git commit `a4a9fd9b3ed18b28cd93c525c52b10ba9badbbc8`.

## Current completeness

The published ZIP supports saved-model mathematical replay for its included certificates and points. It is not an offline-complete native-provenance bundle. Its provenance explicitly excludes the then-active fresh January and hour-of-day uncapped arms. Those arms are now closed locally, but their presence in a later Git checkpoint does not put them into this unchanged ZIP.

| Evidence layer | Checkpoint03 | Newly closed local evidence / limitation |
| --- | --- | --- |
| Package integrity | Portable `verify_package.py`, `FILE_MANIFEST.csv`, and allowlist | Add new files to a newly named package; do not replace the old ZIP or old manifests |
| Original HOD negatives and controls | Complete matrices, bounds, original masks, points, rays, and checker are included | Existing same-host relocation report covers a selected subset, not all evidence |
| Fresh January weeks 2/3 | Excluded by package provenance | Closed: two references, four ordinary targets (three negatives, one UNKNOWN), two identity and two class controls, independent reviews |
| HOD uncapped finite-energy arm | Excluded by package provenance | Closed: two accepted original-binary witnesses, two exact objective lower bounds, inherited identity bounds and resulting intervals |
| Fixed-ray HOD transfer | Not in Checkpoint03 | Six completed nonseparating candidates; preserve their null outcomes, not only accepted certificates |
| Native source inputs | Eight processed dispatch CSVs and acquisition/source code included; raw inputs excluded | Exact native inputs must be acquired or bundled before full historical input-manifest verification |
| Execution environment | Pinned scientific Python dependency list and recorded solver versions included | Stdlib mathematical checker needs no optimizer; new solver reruns need the scientific stack and are not promised to reproduce timing/incumbents bitwise |

Root's completed relocation smoke test extracted 19 package-verified members and replayed two HOD negative rays and two binary positive points, plus 35 checker fixtures, using isolated `python -I -S`. It ran on the same Windows host. This assessment did not repeat it. That result establishes selected mathematical relocation, not full native assembly, all historical manifests, a second machine, or general parser correctness. See `RELOCATION_SMOKE_READOUT.md` and `results/research8h/relocation_smoke/summary.json`.

## Full-manifest inventory

Across 44 CSV/JSON manifest files inside Checkpoint03 and 12 manifest files from the newly closed fresh, HOD uncapped, and fixed-ray arms, the external native bindings resolve to one original prefix and 17 distinct files, totaling 3,734,672 bytes. Each currently available source file was checked against its frozen SHA256 and byte count. This is an inventory of the selected published/closed evidence, not arbitrary host files or active follow-ups.

Original prefix:

`C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs/`

| Relative group | Files | Bytes | Checkpoint03 status |
| --- | ---: | ---: | --- |
| `raw/RTS-GMLC_v0.2.3/` bus, branch, generator and Hydro/Load/PV/RTPV/Wind hourly CSVs | 8 | 3462535 | Contents absent |
| `code/dscgrid_model.py` | 1 | 5694 | Exact LF bytes absent; recoverable from included project model by its documented CRLF-to-LF normalization |
| `processed/month_{01,04,07,10}_first_week_dispatch.csv` | 4 | 249865 | Same contents included under `reproducibility/data/processed/rts/`, but not under the historical native prefix |
| Corresponding `processed/*_hourly_summary.csv` | 4 | 16578 | Exact contents absent; existing preparer regenerates them from fixed native calendars |

The model's exact LF hash is `01d3e67440b1380b62ed68da07e61ac6895b930ada583ffa8af09a370850be78`. Its normalized included source matches that value and length. Four of the 17 external contents already exist elsewhere in the package. Thirteen additional exact contents are needed to close this native byte-provenance gap; mirroring all 17 avoids fragmented per-file remaps.

For the original HOD input manifest, 116 of 125 entries are already present at the corresponding relative package paths with matching hashes; the remaining nine are the eight raw CSVs and LF model. The fresh-reference, fresh-target, and HOD-uncapped input manifests contain 48, 246, and 92 entries respectively. Their new outputs/source/protocols must be added alongside the same nine native source artifacts. Matching a common matrix or mask elsewhere by digest does not establish the new case's provenance or supply its missing bounds, vectors, or certificates.

The historical experiment manifests use original absolute paths. Relocation requires explicit prefix mappings while preserving the manifest bytes and their original SHA256. `research8h_standalone_verify.py --manifest` expects the original CSV header order `path,sha256,bytes`; it cannot be given the outer package or artifact inventory with header `path,bytes,sha256` as a substitute. Outer package integrity and experiment-provenance verification are distinct checks.

## Native distribution permission and proposed addendum

The exact pinned upstream README contains a **DATA USE DISCLAIMER AGREEMENT**, even though there is no standalone LICENSE file in the pinned Git tree and the repository API does not label an SPDX license. The notice grants permission to copy/distribute the data, conditional on retaining the entire notice and crediting DOE/NREL/ALLIANCE in resulting publications; it also restricts endorsement and supplies warranty/liability terms. Use that actual notice, not a license inferred from another repository or from the dataset's public availability. [Pinned upstream README](https://raw.githubusercontent.com/GridMod/RTS-GMLC/3ece0d3725c844056132393ee252b3083dd4eab4/README.md).

The pinned README is 4,778 bytes with SHA256 `9643002ac6b0d0eb85351c8477a3155ec082fd0583a17fb20b9756bc17ecba63`. The upstream release points to the same commit used by the eight existing download locks. [Official releases](https://github.com/GridMod/RTS-GMLC/releases).

Compact addendum, prepared after explicit root approval:

```text
reproducibility/native_sources/
  README.md                         # attribution, scope, mapping and checks
  FILE_MANIFEST.csv                 # exact new-file sizes/hashes
  path_map.json                     # original prefix -> portable rts_inputs
  rts_inputs/
    code/dscgrid_model.py            # exact project-owned LF copy
    processed/                      # exact four dispatch/summary pairs
    raw/RTS-GMLC_v0.2.3/
      UPSTREAM_README.md            # entire pinned README/notice, unchanged
      ...                           # eight exact upstream CSVs
```

All 17 data/model files were copied after checking the exact allowlist and every referring original hash/size. The full pinned upstream README and existing project code/data notices accompany the respective files. `source_bindings.json` and `verification.json` report zero conflicts, zero old-manifest modifications, and zero optimizer calls. The author-model copy is separately identified as project-owned, not relabeled as upstream RTS code. This closes the identified external native-byte gap when the addendum and newly closed results are included in a later package; it does not retroactively add files to Checkpoint03. The existing setup route remains useful, but a reader with the addendum need not use the network merely to satisfy these 17 historical bindings. Root's independent review and eventual package verification are distinct from this preparation check.

## Recommended single replay entrypoint

The existing `src/research8h_standalone_verify.py` is the portable kernel for exact ray and point replay. Its packaged and current bytes match SHA256 `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`. For example, after a new package includes the closed fresh arm, this command uses no solver:

```text
python -I -S src/research8h_standalone_verify.py ray --model-dir results/research8h/fresh_january_weeks/targets/seed_26093210/lp --certificate results/research8h/fresh_january_weeks/targets/seed_26093210/lp/dual_certificate.json
```

Without `--manifest`, this verifies the certificate's bound model/raw-ray/row-label hashes and exact separation, while explicitly reporting that full experiment-manifest provenance was not replayed. Full provenance additionally requires an unchanged original manifest and mappings from both the original research root and original native prefix to the extracted package and addendum absolute paths.

For one command covering **all newly closed mathematical evidence**, recommend a separate, fixed-case `reproducibility/replay_closed_research.py --package-root PATH --report-dir NEW` wrapper. This is a proposal, not an implemented or executed entrypoint. It should verify the package/addendum and remapped experiment manifests first, then:

1. Replay the three fresh negative rays, both fresh references, all four fresh identity/class controls, and both HOD uncapped recovered points using the original full binary masks. In the uncapped arm, the correct mask is `original_integrality.npz`; its `integrality.npz` is the projected U-only optimizer mask.
2. Retain the fourth fresh binary UNKNOWN, explicitly distinguish its expanded continuous-only point, and retain all six fixed-ray nonseparating results as expected outcomes.
3. Recompute both HOD exact objective lower bounds from `matrix.npz`, `bounds.npz`, `objective.npz`, and projected row duals, with exact residual/finite-box/tolerance terms. Recompute upper sums from verified original-binary points, replay the inherited identity bound, and reconstruct the reported intervals.
4. Write fresh reports without replacing archived results; run no optimizer and perform no data acquisition.

The current standalone CLI has only `self-test`, `point`, and `ray`; it does not implement objective lower bounds or all-case orchestration. The closed independent HOD review contains exact objective-bound arithmetic, but its current main routine directly resolves original-host manifests and writes a producer-side review file. It should not be advertised as a ready-to-run, relocation-safe all-evidence entrypoint. A future wrapper needs independent review and its own relocation test; the existing four-case smoke test is not evidence that such a wrapper already works.
