# Data and code availability

The companion reproducibility snapshot is **`v8-reproducibility.20260926`**.
Its versioned access and citation link is the
[GitHub release](https://github.com/shaikhamalkawi-ux/Decision-Stability-Certificates-for-Power-System-Operating-States-/releases/tag/v8-reproducibility.20260926).
The package contents are maintained in [`reproducibility/`](reproducibility/README.md).

**The snapshot is published on [Zenodo](https://zenodo.org/records/22976152)**
with DOI [10.5281/zenodo.22976152](https://doi.org/10.5281/zenodo.22976152).
The GitHub release and Zenodo record contain the same frozen ZIP package.

The package was prepared before DOI registration. Its internal pending-deposit
text reflects that earlier preparation state. The current root documentation
and release notes record the published status; the deposited package, manifest,
and checksums remain unchanged.

## Included in the companion package

| Material | Content and purpose |
|---|---|
| Generated RTS outputs | Eight monthly first-week dispatch matrices used to recalculate the archived mean and empirical transport quantities. |
| Generated PyPSA-GB outputs | January/July 2020 LP dispatch matrices and a minimal derived carrier classification, with original coordinate names retained. |
| Generated chronology/network outputs | Per-coordinate July repair means and the network witness's mean changes. |
| Generated AC outputs | Saved per-hour solver outcomes, restoration magnitudes, and diagnostics. |
| Derived Elexon results | Matched-day primary metrics, optimal-transport matching, and per-BMU mean changes. |
| Executable verification | A portable verifier for 26 saved-output arithmetic checks, a SHA-256 manifest verifier, and saved verification results/environment. |
| Research source code | Original author computation scripts for chronology, network repair, AC restoration, replication, and witness checks; these require the legacy research layout and inputs. |
| Acquisition and provenance | Elexon acquisition/analysis scripts, query details, source commits, scenario/environment records, and hashes of included or omitted inputs. |
| Citation and license information | `CITATION.cff`, separate MIT/CC-BY-4.0 scopes, and third-party source notices. |

Detailed schemas and units are in
[`DATA_DICTIONARY.md`](reproducibility/DATA_DICTIONARY.md).

## Excluded and how to obtain upstream inputs

The package excludes raw RTS-GMLC, PyPSA-GB external datasets, and raw Elexon
API responses. It also excludes the original full generator metadata, legacy
full-package archives, manuscript/supplement, internal reviews, correspondence,
and author-side submission drafts.

- **RTS-GMLC:** obtain the network/time-series inputs from
  [GridMod/RTS-GMLC](https://github.com/GridMod/RTS-GMLC) at commit
  `3ece0d3725c844056132393ee252b3083dd4eab4`.
- **PyPSA-GB:** obtain source models and external inputs from
  [andrewlyden/PyPSA-GB](https://github.com/andrewlyden/PyPSA-GB) at commit
  `8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`. Source-provided chronology
  parameters exist; their admissibility for the frozen experiment is still
  under review.
- **Elexon:** use the [Insights API documentation](https://developer.data.elexon.co.uk/),
  the included scripts, and the archived query register. The recorded original
  acquisition date is 2026-09-20. Fresh API responses may have changed; compare
  their hashes and record any new acquisition rather than silently replacing
  the historical inputs.

See [`ACQUISITION.md`](reproducibility/ACQUISITION.md) for commands, input paths,
and limitations. The original generator metadata hashes are preserved; the
portable verifier uses the included derived carrier classification and does
not recreate that classification from upstream metadata.

## Reproducibility limits and research status

The archived verifier passes 26 of 26 arithmetic checks using included generated
outputs. It does not rerun all optimizations, independently establish witness
feasibility, reproduce the entire Elexon analysis without raw inputs, or validate
all model assumptions and scientific claims. The original research scripts are
provided for inspection and reconstruction, with additional setup required.

V8 remains a pre-submission candidate with scientific and editorial corrections
pending. V7 remains the last independently accepted scientific baseline. The
reproducibility archive does not change that acceptance status.

## Rights and attribution

Author-owned code is MIT-licensed; author-owned text and generated data are
CC BY 4.0 only to the extent the authors own the relevant rights. This grant
does not override third-party source terms or confer rights to omitted inputs.
See [`LICENSE_SCOPE.md`](reproducibility/LICENSE_SCOPE.md) and
[`THIRD_PARTY_NOTICES.md`](reproducibility/THIRD_PARTY_NOTICES.md).
