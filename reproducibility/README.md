# DSC-Grid reproducibility snapshot

Version: **v8-reproducibility.20260926**  
Status: **Pre-submission; scientific and editorial corrections pending.**

Companion research outputs for *Static Feasibility Can Overstate Chronological
Admissibility in Distributional Power-System Operating States* by Ghassan
Malkawi and Ahmed Abdelaziz Elsayed.

This snapshot preserves selected generated numerical outputs and executable
arithmetic checks from the V8 research baseline. It is not a journal-ready
manuscript or a statement that all scientific claims have passed review. The
manuscript, internal reviews, author correspondence, and upstream raw datasets
are excluded.

## Archive identifiers

GitHub release: https://github.com/shaikhamalkawi-ux/Decision-Stability-Certificates-for-Power-System-Operating-States-/releases/tag/v8-reproducibility.20260926

Planned Zenodo record: https://zenodo.org/records/22976152  
Reserved DOI: **10.5281/zenodo.22976152**.

**Zenodo file deposit and record publication are pending.** The reserved DOI
is not yet registered as a published archive. Use the GitHub release URL above
for access and citation until the Zenodo deposit is completed.

## Reproduce the archived arithmetic

With Python 3.12 or later and the dependencies installed:

```bash
python -m pip install -r requirements.txt
python code/verify_26_claims.py . verification/26_claims
```

The 26 checks recompute 14 RTS mean/transport quantities, 6 PyPSA-GB
static/conditional quantities, 2 repair-output sums, and 4 AC-output
counts/medians. They use frozen author-generated dispatch and result tables.
They do not rerun the original optimizations or prove the validity of the
models, theoretical claims, chronology parameters, or upstream data selection.
The GB carrier classification is a derived extract from the frozen metadata;
this verification does not rebuild that metadata from upstream inputs.

## Scientific status

Static transport, chronology, and AC restoration are different quantities.
The July network repair output is an upper-bound witness, not a certified
optimum. Elexon quantities are observational summaries, not causal estimates.
The PyPSA-GB outputs were generated using LP dispatch. The claim that the pinned
upstream PyPSA-GB repository lacks chronology parameters requires correction:
those parameters exist upstream. This snapshot therefore makes no validated
GB chronology result or blanket parameter-absence claim.

## Files and access

- `data/processed/`: frozen generated dispatch, repair, AC, and Elexon summaries.
- `code/`: adapted 26-claim arithmetic verifier and Elexon acquisition/analysis.
- `code/research/`: original optimization and research scripts; these require
  upstream inputs, additional dependencies, and the legacy research layout.
  They are outside the portable arithmetic verification; see the local README.
- `provenance/`: source commits, scenario/environment records, and SHA-256 hashes.
- `verification/26_claims/`: the arithmetic verification run for this snapshot.
- `DATA_DICTIONARY.md`: schema, units, and limits of each included table.
- `ACQUISITION.md`: access instructions for upstream inputs not redistributed.
- `THIRD_PARTY_NOTICES.md`: source attribution and separate upstream terms.

The code and derived data do not replace the third-party sources. Original
upstream raw data, the old full-package ZIP, and third-party generator metadata
are not included. Mutable API responses may differ when acquired again; compare
against the frozen hashes and record differences rather than silently treating
new responses as the frozen baseline.

## Licensing

Author-owned code is licensed under MIT (`LICENSE-CODE.txt`). Author-owned
text and generated research data are licensed under CC BY 4.0
(`LICENSE-DATA.md`), only to the extent the authors hold the relevant rights.
Third-party material and rights remain governed by their original terms; see
`THIRD_PARTY_NOTICES.md` and `LICENSE_SCOPE.md`. No manuscript, internal review, or author-side draft
is included in this archive.
