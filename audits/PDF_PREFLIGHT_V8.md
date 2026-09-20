# V8 PDF preflight

Date: 2026-09-20

| Check | Main | Anonymous | Supplement |
|---|---:|---:|---:|
| Pages | 8 | 8 | 6 |
| Undefined citations/references | 0 | 0 | 0 |
| Overfull boxes | 0 | 0 | 0 |
| Main/supplement bibliography entries | 35 | 35 | 12 |
| Type 3 fonts | 0 | 0 | 0 |
| Visual page inspection | PASS | same layout as main | PASS |

All fonts reported by `pdffonts` are embedded Type 1 fonts. The latest rendered
PNGs show no clipped text, overlap, broken tables, black boxes, or missing
glyphs. The manuscript remains below the 10-page TPWRS first-submission limit.

MiKTeX `pdflatex` was run twice for each target. `latexmk` was unavailable
because Perl was not installed; this did not affect the direct build.
