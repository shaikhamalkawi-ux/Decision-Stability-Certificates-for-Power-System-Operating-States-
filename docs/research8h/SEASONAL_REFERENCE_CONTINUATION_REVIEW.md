# Seasonal reference continuation: independent review

Final verdict at 2026-09-26T22:27:47.002Z: **PASS: source, protocol and all three prepared archives; no blocker found.** No optimization was run by the reviewer. The parent controls execution authorization and concurrency.

## Reviewed source identity

- Runner SHA-256: 8a5cff279e48569056f0217d003f8a43f1d7f026c541f8d9671e8d68e8897d4a.
- Protocol SHA-256: b0100c2cae77bb1c38c206a10107ad3c9488a3b466386c02118f371df317d505.
- Exact point helper remains the previously reviewed seasonal_uncapped source, SHA-256 59b8f8f0d5446ef77e891df2a93bace8a664b5a846bd812cd2af266f2c41dc88.

## Source and proof review

The prospective arm uses April, July and October in that fixed order, with one 600-second call per case, one thread, seed zero, presolve on, relative MIP gap 1e-8, no warm start or retry. Prepare and execution are separate. All three models and their manifest must freeze before any solve; execution verifies source/protocol/manifest digests and uses an exclusive marker. Concurrency gating is the parent's responsibility.

Preparation requires the previous recorded input manifest and unchanged timeout records, reconstructs the source models without optimization, and compares every CSR entry, bound, original integer mask, objective, label, native array and source-hour mapping. It copies original files and keeps original metadata/integrality/result separately. Only the U-only integer mask changes in the solver model. New outcomes do not revise the old UNKNOWN results or retroactively satisfy a prior replication gate.

The reviewer independently decoded and scanned all three original CSR archives in Node. Each has 34,680 rows, 23,016 columns and 141,724 nonzeros. Every auxiliary occurrence belongs to transition, exclusive_transition, minimum_up or minimum_down, with 4,008 rows per family and the required signs, unit/time indexing and bounds. Other rows contain no Y/Z. Original state masks/bounds and initial auxiliary zeros pass. The old integer mask covers exactly U/Y/Z (12,096), while the specified new mask covers exactly U (4,032). All column bounds and matrix coefficients are finite. Each objective is one on exactly 23 fossil dispatch coordinates per hour, zero elsewhere; no mean or energy-cap row occurs.

With exact binary U, canonical Y/Z satisfy transition and exclusivity and cannot increase nonnegative residence sums. The zero auxiliary objective preserves the projected optimization problem. This is an established formulation reduction, not a new algorithm; differing run limits and representations preclude a clean speed comparison.

## Candidate acceptance and claims

The raw vector is retained and numerically checked. Recovery is eligible only for finite vectors with U within 1e-5 of exact zero/one. Rounding U does not itself prove feasibility: the runner leaves P/theta unchanged, recomputes all adjacent Y/Z and initial zeros, then checks the recovered point against the unchanged original matrix and the independent native no-cap checker.

Exact arithmetic subsequently requires every coordinate marked in the original U/Y/Z integer mask to equal zero or one and recomputes every finite row/column violation using exact rational binary64 values. Strict membership is reported separately from membership in the uniformly tau=Fraction.from_float(1e-5) expanded model. Positive references require the raw/recovered numerical checks, native physical checks, objective cross-check and exact expanded membership. An expanded-only point supplies an energy upper bound only for that expanded model. Numerical MIP lower bounds are not independently exact certificates. A solver timeout, unverified candidate or numerical infeasible status is not upgraded to a certified result.

The rigorous upper is the exact rational fossil sum of the recovered dispatch. The solver's own objective and dual bound are stored as separate numerical diagnostics. There is no exact optimality claim.

## Historical preservation baseline

Before preparation completed, the reviewer independently saved hashes of the old summary JSON/CSV, completion and freeze files, plus all three original result.json files. The completed archive comparison below confirms that all eight historical files remain unchanged.


## Completed prepared-archive replay

The all-three freeze is timestamped 2026-09-26T22:21:49.365848+00:00, with solver_execution_started=false. Manifest SHA-256: cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b. The reviewer independently checked **105/105** bound file hashes and byte counts, zero mismatches. Source and protocol digests match the code review above. An additional independent replay of the original reference manifest passed **50/50** entries; its SHA-256 is a4cd70b40e26a9c5019df545364adb06124ce4e46e67c713caf4667ae19c02af.

For each of April, July and October, all nine original/copy pairs are byte-identical: matrix, bounds, objective, native inputs, row labels, source-hour mapping, original integrality, original metadata and original result. The new integer mask is exactly the intended 4,032 U coordinates; all other coordinates are continuous. The new metadata differs only in binary_columns, original_binary_columns, auxiliary_objective_coefficients_zero and continuation_month. Saved native reconstruction/projection audits report zero optimization calls and agree with the independently scanned original sparse matrices. No duplicate column entries occur within any sparse row. Native reconstruction is the preparer's computation; the reviewer independently verified its archived inputs/copies and the sparse projection structure, without reimporting the native model implementation.

All eight historical snapshot hashes still match: original summary JSON/CSV, completion, both freeze files and the three timeout result records. The reviewer last confirmed execution_started.json absent at 2026-09-26T22:26:58.438Z. Hence this completed archive review precedes the first solve.

One initial serial read-only hash scan exceeded its 60-second tool limit and produced no usable verification result; its kernel was reset. The reviewer reran verification in bounded batches, obtaining the completed counts above. This was a reviewer I/O timeout, not a model or solver result; no source/archive mutation or optimization occurred.
