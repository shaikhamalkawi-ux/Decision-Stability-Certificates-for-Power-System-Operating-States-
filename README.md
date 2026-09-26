# DSC-Grid — Decision Stability Certificates for Power-System Operating States

DSC-Grid studies how a distributional power-system operating-state target changes
when static feasibility, clock-hour conditioning, commitment, chronology,
network constraints, and AC restoration are considered. These questions concern
different quantities and must be interpreted separately.

## Reproducibility snapshot

Version **`v8-reproducibility.20260926`** contains selected generated outputs,
a portable arithmetic verifier, original research computation scripts, Elexon
acquisition/analysis code, and source provenance. The package is in
[`reproducibility/`](reproducibility/README.md).

Release and deposit status:

- [GitHub release](https://github.com/shaikhamalkawi-ux/Decision-Stability-Certificates-for-Power-System-Operating-States-/releases/tag/v8-reproducibility.20260926)
- Published archive: [Zenodo record 22976152](https://zenodo.org/records/22976152).
- Archive DOI: [10.5281/zenodo.22976152](https://doi.org/10.5281/zenodo.22976152).

**The reproducibility snapshot is published on Zenodo.** The GitHub and Zenodo
releases contain the same frozen package. The package was prepared before DOI
registration, so its internal references to a reserved DOI and pending deposit
are historical. This root README and the release notes record the published
status; the frozen archive bytes have been retained unchanged.

## Research status

**V8 is a pre-submission candidate with scientific and editorial corrections
pending. V7 remains the last independently accepted scientific baseline.**
The reproducibility snapshot preserves inspectable V8 outputs; it does not
promote V8 to the accepted baseline or represent the manuscript as ready for
submission. The journal target is IEEE Transactions on Power Systems.

The independent review identified a necessary correction to the PyPSA-GB
chronology interpretation: the pinned upstream repository contains chronology
parameters. Inactive or absent attributes in the frozen solved LP extracts do
not establish that suitable parameters are absent upstream. The admissibility
of source-provided parameters for the specific experiment remains to be resolved.

The saved-output verifier passes **26 of 26 arithmetic checks**. This establishes
consistency of the selected archived calculations, not end-to-end regeneration,
feasibility of every solver witness, or validation of every scientific claim.
The July network-repair upper endpoint remains a witness bound, not an optimum;
Elexon results are observational, and AC restoration is separate from chronology.

## Run the portable verification

From this repository root, with Python 3.12 or later:

```bash
python -m pip install -r reproducibility/requirements.txt
python reproducibility/code/verify_manifest.py reproducibility
python reproducibility/code/verify_26_claims.py reproducibility verification/26_claims
```

The manifest checks the immutable package files. The arithmetic command reads
frozen generated outputs and writes its own report outside the package. It
recomputes RTS and PyPSA-GB mean/transport quantities, repair-output sums, and
AC-output counts/medians. The original research scripts under
[`reproducibility/code/research/`](reproducibility/code/research/README.md)
need upstream inputs, additional dependencies, and the legacy research layout;
they are outside this portable verification.

## Data, code, and reuse

[`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md) distinguishes included outputs
from omitted upstream inputs. Raw third-party datasets, original generator
metadata, manuscripts, author-side drafts, and internal reviews are excluded
from the versioned companion package. Upstream source commits, acquisition
instructions, and hashes are retained. Fresh Elexon responses may differ from
the original acquisition because the provider can revise public data.

Author-owned code is MIT-licensed. Author-owned documentation and generated
data are CC BY 4.0 only to the extent the authors own the relevant rights.
Third-party terms remain effective. See
[`LICENSE_SCOPE.md`](reproducibility/LICENSE_SCOPE.md) and
[`THIRD_PARTY_NOTICES.md`](reproducibility/THIRD_PARTY_NOTICES.md).
Use [`CITATION.cff`](CITATION.cff) to cite this snapshot.

## Repository layout

```text
reproducibility/      Versioned public companion package and portable verification
releases/             Package ZIP and checksum
src/                  Research development source
results/              Research result records
manuscript/           Manuscript development source
supplement/           Supplement development source
provenance/            Source, environment, and hash records
```

Development files outside `reproducibility/` are not all included in the
versioned companion archive. Numerical changes and scientific revisions must
be versioned, traceable to source evidence, and reviewed before baseline promotion.
