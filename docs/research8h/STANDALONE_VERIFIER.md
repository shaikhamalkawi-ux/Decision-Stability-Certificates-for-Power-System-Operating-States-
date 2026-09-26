# Standalone exact archive verifier

`src/research8h_standalone_verify.py` uses only Python's standard library. It reads existing NumPy ZIP archives without importing NumPy, SciPy, HiGHS, the optimization runner, or the native power-system model. It never solves an optimization problem. The current supported archive format is deliberately narrower than arbitrary NumPy/SciPy serialization.

This provides an independent, portable arithmetic check of saved evidence. It is not a new Farkas theorem, an independent validation of physical measurements, a reconstruction of native network data, or a proof of minimum information or certificate support.

## Existing tooling and scope

Before implementation, the source inventory showed that `check_temporal_core.py` and `research8h_kgram_check.py` were already stdlib-only. They check different discrete constructions. The existing full-matrix ray/point checkers import NumPy/SciPy or the model assembly. This tool therefore covers an additional dependency-independent route rather than replacing those checkers.

The mathematical input is a finite-column-box linear model

`row_lower <= A x <= row_upper`, `lower <= x <= upper`,

with an explicitly supplied original binary-coordinate mask for point checking. Every archived binary64 number is interpreted as its exact rational value. Infinite row endpoints are allowed; all column endpoints must be finite. The uniform expanded model moves each finite lower bound down by tau and each finite upper bound up by tau. The default tau is the exact rational value of the binary64 number `1e-5`, **not** the decimal rational `1/100000`. Binary coordinates remain exactly zero or one.

The tool validates the encoded matrix, not whether an archive correctly represents its intended physical model. It does not reconstruct nodal demand, fuel classifications, residence times or native source data. That provenance remains the responsibility of the separately preserved model/source audits.

## Ray proof

For each signed row multiplier d_i, select the lower row endpoint when d_i is positive and the upper endpoint when d_i is negative. The selected endpoint must be finite. Multiplication gives

`d^T A x >= beta = sum_i d_i selected_endpoint_i`.

Compute `c = A^T d` exactly. The finite box implies

`c^T x <= M = sum_j c_j (upper_j if c_j > 0 else lower_j)`.

Consequently, `beta - M > 0` proves infeasibility of the continuous model, hence also of any model adding integrality to those same rows and bounds. A zero or negative gap is a valid nonseparating ray, not an infeasibility proof. No orientation flipping, sign projection or coefficient repair is performed: the supplied sparse multipliers are checked as encoded. The historical certificate's orientation/candidate metadata is descriptive and is not applied again to its already exported multipliers.

The expanded gap is recomputed directly from widened selected row endpoints and widened box endpoints. Separately, it is computed as

`gap_expanded = gap - tau * (sum_i abs(d_i) + sum_j abs(c_j))`.

The two exact results must agree. The norm penalty includes canceled-column effects correctly: canceled c_j contribute zero, while their originating nonzero row multipliers still contribute to the row norm. A positive nominal gap alone does not certify the expanded model.

## Point proof

The original binary mask is a required explicit argument. Do not substitute a reduced U-only solver mask for the original U/Y/Z mask. The tool checks mask shape and values, exact zero/one membership of every declared binary coordinate, every finite column bound, and every row product using `fractions.Fraction`. It reports strict and expanded membership separately, with exact maximum positive residuals.

Certification is relative to the **supplied** matrix, bounds and mask. A well-formed mask is not automatically the intended UC mask: for example, a supplied all-zero mask declares a continuous model. Manifest coverage binds file contents but does not establish their semantic role. Claims about the original UC model therefore additionally require independently checked provenance of its full original U/Y/Z mask and model assembly. The reported binary-coordinate count and file hashes support that separate audit; this verifier does not replace it or claim access to raw information.

A point with a small nonzero nominal violation can be an exact witness for the specified expanded model. It is not a strict nominal witness. A fractional binary coordinate is rejected even if every linear inequality passes. No point rounding or feasibility repair is performed.

## CLI

Run from the repository root with Python 3.10 or later. The recorded validation used Python 3.12.14 with `-I -S`, which disables site initialization and isolates the interpreter environment.

```text
python -I -S src/research8h_standalone_verify.py self-test

python -I -S src/research8h_standalone_verify.py ray \
  --model-dir results/research8h/seasonal_transfer/seed_26093100/lp \
  --certificate results/research8h/seasonal_transfer/seed_26093100/lp/dual_certificate.json \
  --manifest results/research8h/seasonal_transfer/input_manifest.csv

python -I -S src/research8h_standalone_verify.py point \
  --model-dir results/research8h/day_blocks/days_312 \
  --vector results/research8h/day_blocks/days_312/constructive_vector.npz \
  --integrality results/research8h/day_blocks/days_312/integrality.npz
```

The backslashes above denote shell line continuations on POSIX systems; use a single line in Windows Command Prompt. `--tau` accepts decimal or hexadecimal binary64 notation. `--output path.json` optionally saves the report and refuses to overwrite an existing file. Without it, the report is printed only.

Every report records its own source SHA-256, Python version, input hashes and zero optimization calls. Ray certificates must bind `matrix.npz` and `bounds.npz` by SHA-256. Declared row-metadata and raw-solver-ray hashes are also verified against adjacent files. A supplied `--manifest` is checked in full, including SHA-256 and byte counts; for a ray, it must match the certificate's declared experiment-manifest digest. Its checked digests must cover the matrix/bounds for a ray, or matrix/bounds/vector/original mask for a point; byte-identical copies are permitted. Thus an unrelated valid manifest cannot stand in for input provenance. Omitting the full manifest leaves an explicit unverified-manifest field: mathematical model verification remains possible, but full experiment provenance has not been replayed by that invocation.

Archived manifests contain paths from the original host. On a different checkout, use explicit repeated mappings, for example:

```text
--path-map "C:/old/repository=/new/repository"
--path-map "C:/old/native-inputs=/new/native-inputs"
```

Mappings replace an exact path prefix on a separator boundary; they do not change expected file hashes. Relative manifest paths resolve against the manifest's directory. If external native files were not copied, omit the optional full-manifest replay and retain the resulting provenance limitation explicitly. The smaller model/certificate archive must still contain every file for which the ray certificate declares a local hash.

## Distinct outcomes

| Status | Meaning |
|---|---|
| `CERTIFIED_EXPANDED_INFEASIBLE` | Exact strict and expanded ray gaps are positive. |
| `CERTIFIED_STRICT_INFEASIBLE_ONLY` | Strict gap positive; expanded gap not positive. |
| `VALID_NONSEPARATING_RAY` | Well-formed, admissible ray that does not separate. |
| `CERTIFIED_STRICT_POINT` | Exact binary point satisfies every nominal bound. |
| `CERTIFIED_EXPANDED_ONLY_POINT` | Exact binary point satisfies only the specified expanded model. |
| `POINT_NOT_FEASIBLE` | Point fails binary membership or at least one expanded bound. |
| `INVALID_INPUT` | Malformed data, hash mismatch, invalid mask/CSR, nonfinite data, or inadmissible multiplier endpoint. |
| `UNSUPPORTED_FORMAT` | Unsupported dtype, ordering, NPY version, or compression. |

Exit status is 0 for a certified outcome or passing self-tests, 1 for a well-formed noncertificate/rejected point, and 2 for invalid or unsupported input. A strict-only certificate is deliberately a certified outcome with explicit limited scope. Archive-claimed gap fractions are compared with recomputed fractions and reported separately; their claimed pass flags do not determine mathematical acceptance.

A mismatch with an archived claimed gap is reported rather than automatically invalidating a newly recomputed proof. In particular, requesting a different tau can legitimately change the expanded gap. Such an output must not be described as reproducing the archived claimed fraction; the computed gap, requested tau and comparison flags determine what was actually verified.

## Parser and safety boundaries

Only CSR archives with expected members are accepted. The parser uses `zipfile`, `struct` and `ast.literal_eval`, never pickle or general evaluation. It supports C-order little-endian float64, signed int32/int64, uint8 masks and the scalar three-byte CSR format marker. It rejects object/structured dtypes, Fortran layout, unsafe/unexpected/duplicate ZIP members, malformed payload sizes, invalid dimensions and pointers, out-of-range or duplicate row indices, nonfinite coefficients/points, invalid bounds and duplicate sparse multiplier rows. Archive sizes and header sizes are bounded. Files are read without extracting ZIP members to the filesystem.

## Fixed validation set

The selected fixtures are the two January full-network service-cap negatives (`seed_26093100`, `seed_26093101`) and two positive witnesses (`january_identity`, `days_312`). These choices were fixed before running this verifier. They exercise two different archived support patterns plus a source and day-reordered positive. No optimization or additional corpus search is part of validation.

The built-in 35 tests use hand-derived small inequalities and deliberate malformed inputs: upper/lower sign errors, infinite selected endpoints, exact cancellation, a zero expanded gap, one-binary64-step tau boundaries, fractional binary points, invalid masks, corrupt/duplicate CSR entries, object/Fortran NPY files, unsafe/duplicate NPZ members, altered hashes and a valid but unrelated manifest. They do not compare a solver with itself. Saved outputs and the fixture-comparison readout are under `results/research8h/standalone_verifier/`.

Successful comparison validates this finite selected evidence and parser scope. It is not a proof that arbitrary future inputs are bug-free. The root performs a separate code/results review before publication.
