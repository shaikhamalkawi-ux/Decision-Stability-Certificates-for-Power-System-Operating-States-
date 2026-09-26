# Standalone exact verifier: selected validation readout

Status: PASS for the fixed validation set; ready for the parent's independent code/results review. No optimization was run. No original result, source model, certificate, point or experiment protocol was changed.

Final verifier SHA-256: 708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f.

The final source was executed using Python 3.12.14 with -I -S. An AST import audit confirms that every imported module belongs to the Python standard library. Results are in final/ and the independent comparison is selected_fixture_comparison.json; compare_selected_fixtures.py reproduces that comparison without rerunning the mathematical checks or a solver (its output uses exclusive creation).

| Fixed fixture | Independent outcome | Agreement with existing exact archive |
|---|---|---|
| January seed 26093100 | Expanded model infeasible | Strict and expanded ray fractions, support counts match exactly |
| January seed 26093101 | Expanded model infeasible | Strict and expanded ray fractions, support counts match exactly |
| January identity | Expanded-only binary point | Exact row/column maximum residuals and locations match |
| Day order 312 | Expanded-only binary point | Exact row/column maximum residuals and locations match |

The two expanded algebraic separation gaps are approximately 46526.78957194592 and 194355.96483466134. These raw ray-normalization gaps are **not MWh**. Both positives retain exactly 12,096 declared original binary U/Y/Z coordinates. Their largest nominal row violation is 8080919107015283899 / 316912650057057350374175801344 (about 2.5498884647111388e-11), so neither is a strict nominal point. The uniformly expanded model uses tau = 5902958103587057 / 590295810358705651712.

All 35 hand-derived/adversarial tests pass. They distinguish unsupported/invalid data, a valid nonseparating ray, strict-only versus expanded ray separation, strict versus expanded-only points, fractional binary values, exact tau boundaries, bad signs/infinite endpoints, canceled columns, invalid masks/CSR, unsafe NPZ/NPY formats and unrelated manifests. They do not use an optimizer as the expected-answer oracle.

The seed26093100 invocation verified all 136 entries of the original seasonal manifest and required it to bind its matrix/bounds. The day312 invocation verified all 148 entries of the day-block manifest and required coverage of its matrix/bounds/vector/mask. The second negative and identity invocations intentionally omit repeated full-manifest scans: their individual reports retain that limitation explicitly, while still recording input SHA bindings and, for the ray, checking its declared model/label/raw-ray hashes. No claim is made that those two individual invocations separately revalidated a complete manifest.

Initial development outputs in this directory (outside final/) retain the earlier source hash 8dca5e1c3c4fa920ff5b3a2f1c8335696b9fbe39c350eb99eb6903da32edebf9 and 34 tests. All four fixtures passed then. Before finalization, the manifest API was strengthened to reject a valid but unrelated manifest, and a 35th adversarial test was added. The final four-fixture rerun is preserved separately. Shared-host startup/I/O delays occurred; reported timings are not computational benchmarks.

The checks establish arithmetic consistency of the supplied linear models, masks and selected witnesses. They do not reconstruct the native physical model, prove the semantic correctness of a supplied mask, validate field measurements, establish minimum certificate support, or introduce a new Farkas method. An original UC claim additionally relies on the separately checked provenance of the original full mask/model. Archived claimed-gap mismatches are comparison flags rather than proof-invalidating conditions; a different requested tau can legitimately change the expanded gap.
