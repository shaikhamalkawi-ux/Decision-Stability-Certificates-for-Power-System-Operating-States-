# Offline native provenance addendum

This new addendum preserves the exact 17 native/model/processed files referenced outside the research worktree by the assessed published and newly closed experiment manifests. It is 3,734,672 bytes of native payload: eight upstream RTS-GMLC CSVs, one author-owned model, and four author-generated dispatch/hour-summary pairs. Every copied byte matches every referring frozen hash and size; no conflicting provenance was found. No optimizer or model reconstruction was run to create this addendum. Existing releases and historical manifests were not edited.

This addendum is separate from older releases that deliberately excluded raw inputs. Their nonredistribution descriptions remain historical statements about those releases. This directory explicitly supplies the limited upstream subset described below under its original notice.

## Attribution and applicable terms

The raw benchmark data are provided by the U.S. Department of Energy (DOE), National Renewable Energy Laboratory (NREL), and Alliance for Sustainable Energy, LLC (ALLIANCE). We credit **DOE/NREL/ALLIANCE** for these data. No endorsement by these organizations is claimed.

The eight CSVs are unchanged copies of the existing admitted inputs from the official [GridMod/RTS-GMLC repository](https://github.com/GridMod/RTS-GMLC), pinned at commit `3ece0d3725c844056132393ee252b3083dd4eab4` (v0.2.3). Individual pinned primary-source URLs and SHA256 values are in `source_bindings.json`. The existing acquisition locks in `src/v8r1_prepare_rts_inputs.py` independently match all eight raw hashes.

The exact full upstream README, including its **DATA USE DISCLAIMER AGREEMENT**, accompanies the raw data at `rts_inputs/raw/RTS-GMLC_v0.2.3/UPSTREAM_README.md`. Its SHA256 is `9643002ac6b0d0eb85351c8477a3155ec082fd0583a17fb20b9756bc17ecba63`. Retain that entire notice with copies of these raw data, credit DOE/NREL/ALLIANCE in publications using them, and observe all of its remaining terms. This is the repository's custom data-use notice, not an inferred SPDX license or a license borrowed from a different dataset. The snapshot reproduces the upstream notice exactly as published, without completing or rewriting its text.

Recommended scientific citation: C. Barrows et al., “The IEEE Reliability Test System: A Proposed 2019 Update,” *IEEE Transactions on Power Systems*, 35(1), 119–127. [DOI: 10.1109/TPWRS.2019.2925557](https://doi.org/10.1109/TPWRS.2019.2925557). Cite the pinned repository revision as well.

The model in `rts_inputs/code/dscgrid_model.py` is project-owned code, separately covered by the exact project MIT notice in `rts_inputs/LICENSE-CODE.txt`. Its LF bytes match the admitted model hash `01d3e67440b1380b62ed68da07e61ac6895b930ada583ffa8af09a370850be78`; it is not upstream RTS code. The derived files in `rts_inputs/processed/` retain the project author-data terms in `rts_inputs/LICENSE-DATA.md`, only to the extent the authors own the rights. Those terms do not replace upstream rights.

## Contents and evidence

`source_bindings.json` lists every original path, portable path, byte count, SHA256, file category, pinned raw-data URL, and referring manifest/hash. Its scope is 44 manifest files in published Checkpoint03 plus 12 from the closed fresh January, HOD uncapped, and fixed-ray arms. Active follow-ups and arbitrary host files are excluded.

`verification.json` records the exact allowlist/count/size checks, zero provenance conflicts, model-normalization check, and unchanged historical evidence. `FILE_MANIFEST.csv` binds every other file in this addendum. Paths in that inventory are relative to this directory. The wider research package has its own separate manifest.

The 17-file mirror is sufficient for the external native bindings identified in these manifests. It is not a claim to bundle every upstream RTS file or every optional legacy experiment input. The annual hourly CSVs retain their exact admitted bytes; no selection, value rounding, calendar conversion, or reordering was performed for publication.

## Relocating unchanged historical manifests

`path_map.json` contains explicit prefix substitutions, with destinations expressed relative to the extracted research package root. Expand those destination roots to absolute paths before passing them to a verifier. Do not edit the historical manifest itself; doing so would change the digest recorded by its certificates.

Map the original research root to the extracted package root, and the original native prefix to its new `reproducibility/native_sources/rts_inputs` subdirectory. For example, from an extracted package, an HOD mathematical ray replay with full input-manifest verification uses:

```text
python -I -S src/research8h_standalone_verify.py ray --model-dir results/research8h/hour_of_day/seed_26093200/lp --certificate results/research8h/hour_of_day/seed_26093200/lp/dual_certificate.json --manifest results/research8h/hour_of_day/input_manifest.csv --path-map "C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3=ABSOLUTE_PACKAGE_ROOT" --path-map "C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs=ABSOLUTE_PACKAGE_ROOT/reproducibility/native_sources/rts_inputs"
```

Replace both `ABSOLUTE_PACKAGE_ROOT` placeholders with the actual extraction path. No solver is needed for that command. Full native physical/model reconstruction is a separate validation layer; merely checking these hashes or a saved mathematical certificate does not perform it. This addendum has been prepared and checked on the existing host, and makes no second-machine claim.
