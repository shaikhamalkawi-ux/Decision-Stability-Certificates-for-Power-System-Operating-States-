# Portable replay of newly closed results

This protocol specifies the new `reproducibility/replay_new_closed_results.py` wrapper. It complements the unchanged Checkpoint04-scope wrapper. Source implementation alone is not permission to prepare a candidate package or execute the replay: those steps require the parent's separate review gates. The implementation and this protocol must be frozen before preparation.

## Fixed denominator and mathematical meaning

The wrapper covers six fresh uncapped models: week 2 identity, week 3 identity and targets 26093210, 26093211, 26093220, 26093221. It replays six exact objective lower bounds, two original-mask reference uppers, four original-mask target uppers and the four targets' interval records. Targets 10/11 use week 2; targets 20/21 use week 3. None is selected by outcome or sign.

It also checks the four HOD continuous subset points: targets 26093200/01 crossed with `two_cc` and `locality48`. Two full HOD identity/class-control binary points establish four row-subset inheritances. These auxiliary controls are not new energy targets.

All exact membership and objective claims use archived binary64 coefficients interpreted as rational numbers and every finite row/column bound widened by exactly `Fraction.from_float(1e-5)`. Upper witnesses retain the complete original U/Y/Z mask with 12,096 binary entries. Strict membership is reported separately. The continuous subset checks explicitly use a zero mask and report their nonbinary original-state counts; their positive zero-mask Boolean is not binary acceptance.

The old wrapper's prior rays and energy intervals are not rerun by this extension. The new run is solver-free reproduction of archived mathematics and provenance, not native physical-model reconstruction, exact optimization, a new experiment, a second-machine test or an external-network result.

## Source and package binding

The old wrapper remains pinned at SHA256 `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85`. Only its pure helpers are imported. Its hardcoded `Replay`/`main` is not called. The unchanged NPZ/CSR exact kernel is pinned at `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`. Imports use explicit package file paths with bytecode writes disabled. There is no NumPy, SciPy, solver, installer, producer-model import or network call.

The proposed candidate derives from the parent's reviewed Checkpoint05 base plus only the new wrapper and this protocol, with a newly generated outer manifest. Preserve every base payload byte. Actual base commit, ZIP digest, payload count and candidate-manifest digest must be recorded during later separately authorized preparation, not invented here.

Invocation after that gate:

```text
python -I -S reproducibility/replay_new_closed_results.py --package-root EXTRACTED_ROOT --report-dir NEW_EXTERNAL_DIRECTORY --expected-package-manifest-sha256 REVIEWED_DIGEST --package-evidence-commit REVIEWED_BASE_COMMIT
```

The manifest digest is supplied from the independently reviewed delivery record. The commit argument records that delivery identifier and is not authenticated through a remote Git request. The executed wrapper must match the package-bound wrapper. Every accessed payload must be in the verified outer manifest; the package's complete file inventory must match the manifest plus the manifest file itself.

Historical manifest bytes remain unchanged. The wrapper checks their pinned hashes and adapts paths only in memory. Exactly two component-boundary prefix maps are permitted: the original research worktree to the package root, and the original portable native-input root to `reproducibility/native_sources/rts_inputs`. Slash normalization does not authorize searching by basename or another root. Escapes, duplicate normalized names, conflicting resolved bindings and unbound inputs fail.

Fresh prepared closure contains 378 entries; subset prepared closure contains 155. The 169-entry fresh producer manifest is relative to its arm directory, while the 71-entry subset artifact manifest is relative to the repository/package root. The JSON subset manifest is parsed with the same strict row schema as CSV. Historical parent manifests and the native addendum are verified too. The independent subset review's earlier 61-file dictionary is checked as its historical closure, separately from later artifacts. Manifest entry totals are not unique-file counts.

The native addendum supplies 17 source bindings within 24 payloads. Its raw data and author-model bytes are verified; only the native generator CSV is read for the fuel roster. No native model code executes. Independent PASS review records and their bound files are checked as provenance, but new mathematical replay does not treat PASS text as proof.

## Fresh model, point and bound replay

For each fresh model, compare the actual full rows and finite boxes with the capped parent after deleting exactly its single fossil cap. Week caps remain 26532 and 48319, derived from the exact reference energies by `ceil(101 Eref/100)`. No other row, coefficient, endpoint, column or mean constraint changes. Identities additionally match their already uncapped reference archive; their saved retained-row array is consequently the identity map, whereas target arrays retain capped-parent row numbers.

Verify the 23-unit Coal/Oil/NG dispatch objective against native generator names/fuels and the removed cap row, excluding nuclear. Validate the original and projected masks separately. Check the archived 107-coordinate package transport with exact binary64 encoding, including the separate aggregate demand, nodal demand and generator bounds. Source row/permutation arrays, fixed edges, clock labels and native week ranges must match. This is archived-input transport, not raw CSV reassembly.

For all six lower bounds independently reproduce raw-row-dual sign projection at infinite row endpoints. Recompute `eta=c-A^T d`, signed row term `beta`, finite-box minimum and exact sparse stationarity residual. Evaluate

`L = beta + sum_j min(eta_j a_j, eta_j b_j) - tau (sum_i |d_i| + sum_j |eta_j|)`.

The unchanged helper also verifies direct widened-endpoint arithmetic. Compare every saved bound component and nonzero residual coordinate. Replay the zero-dual baseline and the archived maximum selection. Never clamp an expanded lower bound to zero and never use a solver's numerical bound as the proof.

Verify the two reference upper vectors match their source reference bytes and pass the full original binary mask. For the four targets verify raw/recovered P and theta bytes, recovered exact U, canonical Y/Z with initial zeros, raw continuous membership, and recovered original-mask membership. Compute all six upper energies by exact summation. Preserve strict flags and inspect the stored native-check flags without claiming native engineering equations were rerun.

Recompute all four interval families for each target: optimum difference `[L_T-U_I,U_T-L_I]`, target optimum excess over the selected incumbent `[L_T-U_I,U_T-U_I]`, relative penalty `[L_T/U_I-1,U_T/L_I-1]` when lower bounds are positive, and percent penalty. Compare exact fractions and six-decimal outward display fields. Generic helper logic retains zero crossings and returns no finite interval without an upper. This fixed closed archive is expected to reproduce all four accepted uppers; a missing required upper fails the replay rather than triggers computation or case omission.

Preserve the earlier capped UNKNOWN for 26093211. Separately calculate whether the new uncapped lower bound exceeds `B+tau`; that comparison does not relabel the historical ledger. A positive optimal-energy difference alone does not prove cap infeasibility.

## Subset points and controls

Require byte equality to the previously frozen fixed-template model files, then independently reconstruct each ordered row selection from its actual full HOD parent. `two_cc` retains all four temporal families only for 107_CC_1 and 118_CC_1. `locality48` retains all transition/exclusivity rows and only dwell rows whose entire nonzero U/Y/Z support lies within hours 60–107 inclusive. All static/network/cap rows and column boxes remain. Dimensions are 19,985 or 28,689 rows by 23,016 columns. Row labels alone do not determine locality support.

Compare every CSR row, endpoint, retained index, native column metadata and the 23195 cap. Evaluate returned vectors with a zero mask, while separately validating the archive's original full mask. Expected exact nonbinary state counts are 245, 273, 255, 382. All four expanded continuous checks pass and strict checks fail. This excludes linear separators only inside these expanded fixed row/box templates; it does not establish binary feasibility or exclude integrality-based proofs.

Replay both HOD full original-mask constructive controls against their own matrices, bounds and vectors. Compare the four saved rule-mapping CSVs. Checked full membership plus exact row deletion/unchanged boxes establishes inheritance; shared matrix hashes are insufficient to substitute one control's bounds for another's.

## Focused synthetic checks

The wrapper contains small new-logic checks for positive/negative row signs, imperfect duals requiring a finite-box correction, a negative zero-dual expanded bound, infinite-endpoint projection, nonfinite-dual rejection, full/projected/zero mask distinctions, different optimum/incumbent denominators, zero-crossing intervals, no upper, both rounding directions, actual dwell support crossing 59/60 and 107/108, and dropping other-unit transitions under the two-unit rule. It also checks normalized duplicate manifests, unmapped/prefix-lookalike/escaping paths, missing historical UNKNOWN, duplicate JSON keys and nonfinite JSON.

These fixtures use tiny synthetic objects and a temporary external directory; no frozen payload is modified. They complement the unchanged kernel's existing fixtures. They have not been executed at source handoff and must run only at the authorized replay gate. The source review should inspect all production mismatch guards in addition to these selected fixtures; the fixture list is not a claim of exhaustive parser or wrapper verification.

## Output, failure and closure

The output directory must be new and outside the resolved package, including symlink resolution. Reports are exclusive-create JSON files. They contain exact fractions, preserved strict/expanded flags, mask roles, model/manifest hashes and actual elapsed time. No report writes into the package. Pre-existing manifest-bound bytecode is allowed, while the final file inventory must remain unchanged.

Final PASS requires all six lower bounds, six original-mask uppers, four interval records, four continuous subset points, two auxiliary full controls and four inheritances, followed by full package and historical-manifest rehashing. Record zero optimizer/network/native-assembler calls. On any error write a failure report outside the package, retain completed external reports, exit nonzero and do not retry automatically. A later source correction or rerun requires its own explicit review record; no frozen evidence is repaired in place.
