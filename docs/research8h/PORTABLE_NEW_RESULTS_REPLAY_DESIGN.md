# Portable replay of the newly closed results: design only

Status: PROPOSED, not implemented or executed. Prepared on 27 September 2026 after read-only inspection of the existing portable wrapper, the fresh-energy prepared/post-run review sources and schemas, and the four HOD subset-point archives. No optimization, mathematical replay, old-source edit or manuscript edit was performed for this assessment. Metadata inventories and hashes were read to ground this design.

## Recommendation and fixed scope

Add one new wrapper, provisionally `reproducibility/replay_new_closed_results.py`, with its own protocol and reports. Keep `reproducibility/replay_closed_research.py` and `src/research8h_standalone_verify.py` unchanged. The extension is technically feasible using Python `-I -S`, the standard library and the already reviewed NPZ/CSR exact-verification kernel. It is a reproduction extension, not new scientific evidence or a new optimization method.

The fixed new denominator is:

- Six uncapped fresh-energy models: `week_2_identity`, `week_3_identity`, `seed_26093210`, `seed_26093211`, `seed_26093220`, `seed_26093221`.
- Six exact objective lower-bound replays, two reference upper points and four target upper points, all accepted upper points using the original 12,096-coordinate U/Y/Z mask.
- Four target interval records, each including optimum-to-optimum difference, excess over the chosen reference incumbent, relative optimum penalty and percentage penalty.
- Four expanded continuous subset points: seeds 26093200 and 26093201 crossed with `two_cc` and `locality48`. These are not binary witnesses.

This does not repeat the old wrapper's selected five negative rays, ten positive points or its two first-week HOD energy intervals. Running the old and new wrappers as separately named replays would cover their union. The two unrestricted first-week energy intervals are not silently added to the new numerical replay: they retain their existing independent audit and are outside this minimal extension. The new wrapper must not describe itself as a full replay of every historical experiment or every figure row.

## Reuse without changing frozen code

The current old wrapper has SHA256 `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85`; the kernel has SHA256 `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`.

The new wrapper can verify those hashes and import the kernel by explicit file location with `sys.dont_write_bytecode=True`. Pure old-wrapper helpers such as safe relative path resolution, strict JSON decoding, `objective_lower`, rational conversion and interval arithmetic may be imported through the same pinned-file mechanism. Do not instantiate the old `Replay` class, call its `main`, or reuse its hardcoded 23195-MWh cap and old case roster. A small new archive resolver should make all new dependencies explicit.

Do not invoke the existing review scripts as portable programs. Although the fresh and subset post-run reviewers use standard-library arithmetic, their helper imports and manifest traversal retain host assumptions. In addition, the prepared reviewers intentionally assert that execution markers do not yet exist; rerunning those entire programs on closed archives is wrong. Transfer their reviewed checks into the new wrapper's declared closed-archive workflow, keeping the old scripts as hash-bound provenance only.

The kernel already supports the needed little-endian float64 and integer NPY arrays inside stored/deflated NPZ, exact CSR rows, finite column boxes, infinite permitted row endpoints, and exact point evaluation. No NumPy, SciPy, pandas, solver, network client, author home directory or native-model import is needed. Unsupported dtype, layout or NPZ members must remain a failure rather than trigger an alternate parser or a package installation.

## Package and manifest closure

Use a newly prepared delivery package with a complete relative `FILE_MANIFEST.csv`. A separate frozen replay descriptor or protocol must bind the new wrapper, protocol, kernel/helper hashes, reviewed evidence commit, prescribed case order and expected historical manifest digests. Supply the expected outer-manifest digest from the reviewed delivery descriptor or as a required CLI argument; a self-consistent edited manifest alone is not an independent authenticity claim.

The concrete additional manifest schemas are:

| Manifest | Digest | Entries | Path base |
|---|---|---:|---|
| `fresh_january_energy/input_manifest.csv` | `44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a` | 378 | Historical absolute paths: 369 research, 9 native |
| `hod_reoptimized_subsets/input_manifest.json` | `1d3c54426828dcca5684ca21d6f1af95f2c05cfc87631423ae939a354c867119` | 155 | Historical absolute research paths |
| `fresh_january_energy/producer_artifact_manifest.csv` | `f48d012ff996f86e1981afe3b2d79165b0c80ae47f0cfdde43922fc17cbd4b90` | 169 | Relative to the fresh-energy arm directory |
| `hod_reoptimized_subsets/artifact_manifest.csv` | `ba2c7a894fc7a2aa1984f05b9246233e73eb278a2c5abf93b99c5951add1c025` | 71 | Relative to the repository/package root |

The two relative bases are different and must not be inferred from the filename. All row schemas are exactly `path`, `sha256`, `bytes`, irrespective of CSV field order. The kernel's current manifest helper supports CSV; the subset JSON array needs a small strict adapter. Preserve the original manifest bytes and expected digest, and remap paths only in memory.

Use exactly the existing two prefix maps, with separator normalization and component-boundary matching:

1. `C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3` to the selected package root.
2. `C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs` to `reproducibility/native_sources/rts_inputs` inside that package.

Resolve every mapped path inside the package; reject unmapped absolute paths, drive substitutions, traversal, duplicate normalized names and conflicting hashes for one resolved file. Require every resolved historical input and every replayed output to belong to the outer manifest. Verify size and SHA256, not existence alone. Collect the transitive manifest file closure at preparation time; do not describe the sum of manifest row counts as a count of unique files.

The nine native bindings are `code/dscgrid_model.py`, `bus.csv`, `branch.csv`, `gen.csv` and the Hydro/Load/PV/RTPV/WIND hourly CSVs. The existing native addendum already provides the appropriate path map and an independently bound 17-file native inventory within its 24 payloads. Verify the relevant addendum inventory, notices and bytes; import none of its model code. `gen.csv` is needed for the objective roster check, while the other native files provide preserved provenance. This replay does not regenerate network matrices from those raw files.

Also bind the fresh and subset independent prepared/post-run review JSONs, their review sources, parent reference/target freezes, cap JSONs, native input archives and all vectors/duals used below. Inspect review PASS statuses and their bindings, but calculate the mathematical checks anew rather than accepting those statuses as the proof. Record the actual scientific commit represented by the final package; do not label a later package as unchanged Checkpoint04.

The subset independent post-run review binds the 61 producer files that existed at its closure. Check that historical dictionary exactly by its listed paths; separately bind later readouts/reviews through the final package manifest and the 71-entry arm artifact manifest. Additional documented files are not evidence that the earlier 61 files changed, and the historical dictionary must not be silently redefined as a current-directory enumeration.

## Fresh model and objective checks

For each of the six models, decode all arrays from the package. Require 34,680 rows, 23,016 columns, the declared hour-major layout, unchanged finite column boxes and the exact original mask `0*6888 + 1*12096 + 0*4032`. Separately verify the archived solver mask `0*6888 + 1*4032 + 0*12096`; it is provenance and must never replace the upper-point acceptance mask.

Compare each model with its corresponding capped fresh target archive: delete exactly its single `fossil_energy_cap` row, keep every other row/coefficient/bound and row label in order, and keep the column boxes unchanged. The caps are 26532 for week 2 and 48319 for week 3, derived from the exact respective reference energies by `ceil(101*Eref/100)`. There must be no remaining cap or individual-mean row. Validate the cap row is the same objective support, not merely a row with a convenient label.

The identity archive has a deliberate bookkeeping distinction: its source reference model was already uncapped, so its saved `retained_parent_rows.npz` is the identity map, whereas target archives store the original capped-row selection. For identities, verify both equality to the native-reference model and cap-only deletion relative to the capped identity target. Do not reject that documented identity map or misinterpret it as a missing cap deletion.

Require exactly 41 source-matched unit names and 23 Coal/Oil/NG generators, excluding the nuclear unit. Compare the objective with the deleted cap coefficients and with the native fuel roster: coefficient one for each of those 23 dispatch columns in every one-hour interval, zero elsewhere. No startup cost or emissions coefficient enters this objective.

Replay native-input archive equality and package transport using the kernel's array decoder: pmin/pmax/net/nodal values and source rows must match the parent reference under the saved source-hour permutation; first/last 48 positions and hour-of-day labels remain unchanged. Use binary64 byte comparison where exact encoding, including signed zero, is the claim. Bind each target permutation CSV to its own source-hour and native-row arrays. This establishes transport of archived physical inputs and model inheritance; it is not a fresh raw-data calendar/network assembly or a new native engineering-equation evaluation.

## Six exact objective lower bounds

For each model, read the raw row/column dual NPZ and the projected row-dual NPZ. Independently reproduce the admissibility projection: a positive multiplier selecting an infinite lower bound or a negative multiplier selecting an infinite upper bound becomes zero; nonfinite dual values are rejected. Check the projected values and projection count against the archived record. The raw vector and projected vector must remain distinguishable.

With all archived binary64 values interpreted as exact fractions, evaluate

`beta = sum_i d_i*(lower_i if d_i>0 else upper_i)`,

`eta = c - A^T d`,

`L_nominal = beta + sum_j min(eta_j*a_j, eta_j*b_j)`,

`L_expanded = L_nominal - tau*(sum_i |d_i| + sum_j |eta_j|)`.

Use `tau = Fraction.from_float(1e-5)` and independently compare the norm expression with direct minimization over widened row/box endpoints. Recompute the complete sparse exact residual and compare all nonzero coordinates with `exact_stationarity_residual.json`. Check all saved lower-bound terms, not only a displayed decimal.

Also recompute each zero-dual bound. Select the same archived maximum of the projected-dual bound and zero-dual bound. Never clip the expanded bound to zero: expanded fossil dispatch boxes permit the exact zero-dual baseline of approximately -0.03864 MWh. A numerical optimal status or numerical dual objective is not used as an exact proof. The completed dataset has six available lower-bound records; a missing required record is a replay failure, not permission to rerun an LP.

## Six original-mask energy upper witnesses

For each identity, verify its `reference_upper_vector.npz` is byte-identical to that week's archived accepted reference vector. Check exact expanded membership with the full original mask and compute `sum c_j*v_j` as a fraction. Compare with its reference binding, identity-energy JSON and independently reviewed reference record.

For each of the four targets, load the recovered and raw MIP vectors. Check P and theta bytes are unchanged by recovery, every recovered U/Y/Z is exactly zero or one, U is within the recorded numerical recovery tolerance of raw U, and all Y/Z coordinates equal the canonical changes of U with initial Y/Z zero. Evaluate the recovered point against every uncapped row and column bound using the full original mask. Preserve strict nominal pass/fail separately. The raw point may also be checked with a zero mask as a continuous diagnostic, never as an upper witness.

Compute each target energy by exact objective summation, compare it with the MIP result and bracket record, and require expanded membership before assigning a finite upper bound. Inspect/hash-bind the saved native no-cap checks without claiming that the portable wrapper re-executed the native physical assembler. A missing upper must not be replaced by a fractional LP point, numerical solver objective or inherited reference point.

## All four fresh interval records and old UNKNOWN label

Keep the order and week mapping fixed: 26093210/11 use week 2; 26093220/21 use week 3. Recompute each identity's and target's selected lower/upper bounds and all four interval families:

- Optimum difference: `[L_T-U_I, U_T-L_I]`.
- Target optimum excess over the chosen reference incumbent: `[L_T-U_I, U_T-U_I]`.
- Relative optimum penalty: `[L_T/U_I-1, U_T/L_I-1]` when both lower bounds are positive.
- Percentage penalty: 100 times those relative endpoints.

Compare exact numerator/denominator pairs and outward six-decimal display values. Preserve a crossing-zero interval, nonpositive bound or absent upper if present; no sign or success filtering is allowed. For this fixed closed dataset all four uppers exist and all four difference lower bounds are positive. Failure to reproduce that archived fact is a diagnostic failure, not a reason to omit a case.

Retain the original capped denominator and classification separately. Recompute the exact cap-implication comparison `L_T > B+tau` without editing its historical ledger. In particular, 26093211's positive optimal-energy gap still does not resolve its original cap 26532. The new summary must not replace UNKNOWN with infeasible merely because the optimal-energy difference is positive.

## Four continuous subset points and template scope

The two `two_cc` models have 19,985 rows and the two `locality48` models 28,689 rows; all have 23,016 columns. Reconstruct the fixed row masks from their full HOD parent models:

- `two_cc`: retain the transition, exclusivity, minimum-up and minimum-down rows only for 107_CC_1 and 118_CC_1; retain the entire static/network/cap background.
- `locality48`: retain all transition and exclusivity rows and only dwell rows whose every U/Y/Z support hour is within 60 through 107 inclusive; retain the same static/network/cap background.

Compare the exact ordered retained-row list, every coefficient/row bound, all column bounds and the unchanged 23195 cap. Do not trust a family-count summary or UID label alone; the locality support must come from the actual state-coordinate indices. Compare copied subset archives with their already reviewed fixed-template source model, then verify that source's restriction against the full parent. Include the row metadata and retained-row files in the package closure.

Read and validate each archive's original integrality mask, but evaluate its returned continuous point using an explicit all-zero mask passed to the kernel API. Save `binary_coordinates=0` and count nonbinary entries against the original mask separately. Current expected counts in case order 26093200/two_cc, 26093200/locality48, 26093201/two_cc, 26093201/locality48 are 245, 273, 255 and 382. The kernel's `original_binary_coordinates_exact=true` under a zero mask is vacuous; never present that field by itself as binary acceptance. All four strict nominal checks fail and all four expanded continuous checks pass in the closed archive.

For the identity and class control, replay their own original-mask constructive points on their full parent models, then establish inheritance by exact row selection and unchanged boxes. Bind each control's bounds, mask and vector individually: sharing a matrix hash does not make their bounds or points interchangeable. No control optimizer is needed.

The correct consequence is that no valid linear Farkas separator exists for these four expanded continuous row/box templates. It is not full UC feasibility, strict nominal feasibility, an objective lower bound, a proof against other supports, or a proof against integrality-based arguments.

## Output discipline and completion gate

Proposed invocation, only after implementation review and execution authorization:

`python -I -S reproducibility/replay_new_closed_results.py --package-root EXTRACTED_ROOT --report-dir NEW_EXTERNAL_DIRECTORY --expected-package-manifest-sha256 REVIEWED_DIGEST`

Resolve paths first. The report directory must not exist, must be outside the package even after symlink resolution, and must not be an ancestor from which package writes could be confused with reports. Create report files exclusively. Set no-bytecode mode before dynamic imports. The wrapper must not write into the extracted package, download dependencies, invoke a shell/optimizer, or rebuild any model.

Suggested reports: package/provenance closure; focused new-logic checks; six model relations; six exact bounds/upper-point records; four fresh interval records; four continuous subset records; control-inheritance evidence; historical capped-label check; and final summary. These are report categories, not additional experimental cases. Record hashes, exact rationals, strict/expanded flags, original and check-mask roles, actual Python version, elapsed time and zero optimizer/network calls.

Only write `NEW_CLOSED_RESULTS_PORTABLE_REPLAY_PASS` after every required case, binding and arithmetic check succeeds, with exactly six lower bounds, two reference uppers, four target uppers, four interval records and four continuous subset admissions. Report the two auxiliary full HOD control-point checks and their four subset inheritances separately; they are not extra energy targets. Rehash the entire outer manifest closure and historical manifests at the end; verify the final package file set is unchanged, permitting only pre-existing manifest-bound bytecode rather than assuming none existed. On failure preserve partial external reports and a failure record, exit nonzero and do not retry automatically.

## Meaningful focused checks for the new logic

Keep the unchanged kernel's existing fixture suite separate. Add focused synthetic checks only for the new routing and arithmetic:

1. Wrong week-to-reference mapping, swapped source cap, deleted noncap row, changed box or missing nonzero cap coefficient must fail.
2. Replacing the original 12,096-state acceptance mask with the projected 4,032-state mask must fail. A fractional point that passes a zero-mask check must remain continuous-only.
3. Raw/projected dual mismatch, inadmissible infinite endpoint, omitted exact residual coordinate, duplicate residual index and nonfinite dual must fail. Include positive and negative row signs and a deliberately nonstationary dual so the finite-box correction is necessary.
4. A zero dual on an expanded nonnegative nominal dispatch box must produce a negative baseline, without clipping. Compare direct widened endpoints with the norm correction exactly.
5. Distinct identity lower and upper bounds must expose the mistake `U_T-U_I` in place of the optimum-difference upper `U_T-L_I`; similarly test both ratio denominators. Test negative/zero-crossing endpoints and outward rounding in both directions.
6. A missing target upper must not become a finite interval. Removing or relabeling 26093211 from the fixed four-case roster must fail.
7. A dwell row whose actual state support crosses hour 59/60 or 107/108 must exercise the locality boundary. A retained row from another unit, changed cap/background row or swapped control bounds must fail.
8. Relative producer manifests with the wrong base, a JSON-manifest duplicate after slash normalization, an unmapped root, `..` escape, prefix lookalike and conflicting binding must fail before mathematical work.
9. A report directory inside the package or already existing must fail before output. A changed package payload during a staged test must prevent final PASS while preserving external partial reports.

These checks can run on tiny synthetic arrays and temporary external directories. They should not edit or corrupt frozen evidence. No new solver outcome is needed to test the wrapper.

## Limits and next gate

The design removes host-only dependencies from the proposed replay by replacing absolute-path access with verified in-package remapping. It establishes exact mathematics of archived models, original-mask energy upper witnesses, exact lower bounds, interval arithmetic and fixed-template continuous admission. It does not newly validate the physical formulation, reconstruct all native arrays from CSV, prove strict nominal positive membership, establish exact optima, rerun every earlier arm, or demonstrate second-machine portability before a second-machine execution actually occurs.

Next step, if authorized, is implementation plus independent source/protocol and prepared-package review, followed by one relocated solver-free execution. This document itself authorizes no implementation or execution and contains no claim that the proposed extension has already passed.
