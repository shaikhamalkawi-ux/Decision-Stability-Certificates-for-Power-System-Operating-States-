# Frozen strict-balance branch-path diagnostic

This is a new representation-level diagnostic of the unchanged four original reference matrices. It follows the completed nominal-balance audit, whose 672 aggregate-minus-nodal combinations all failed to separate using original angle boxes. It is not a positive-witness repair, physical infeasibility experiment, change to the existing models, or replacement for expanded-model results.

Source: `src/research8h_strict_balance_paths.py`. New output only: `results/research8h/strict_balance_paths/`. Use the Python standard library and the hash-pinned existing NPZ/model decoder. No solver or producer module is imported. Exact arithmetic uses `Fraction` on the archived binary64 coefficients, endpoints and exact rational path multipliers. All scientific rational outputs use numerator/denominator strings; there is no float/hex conversion of rational multipliers.

## Separate preparation and execution gates

Root and an independent reviewer inspect the complete source/protocol before preparation. `--prepare-only` verifies the old audit freeze and all its input hashes, reads all four complete archived matrices/boxes/row labels and metadata, and checks the structure described below. It writes a new fixed input manifest and preparation freeze. It does not compute shortest paths, new balance residuals, support bounds, separating candidates or synthetic diagnostic tests. It must preserve the earlier read-only inspection's rejected index-zero assumption and correction in a separate provenance note.

After all inputs are frozen, independent prepared-archive review and a separate explicit root GO are required before `--run-prepared`. All source/protocol/input bytes then remain unchanged. Existing output/execution markers block duplicate preparation or execution. Old arms are read-only. No result authorizes another tree, metric, box choice, solver, repair or retry.

## Fixed denominator and unchanged inputs

Use the original `seasonal_reference/month_01`, `month_04`, `month_07` and `month_10` archives, in that order. Use hours 0 through 167 in order and orientations +1 then -1. This gives 672 hour/week cases and exactly 1,344 intended orientations. The already archived aggregate-minus-nodal coefficients and right-hand sides are bound and must match the newly reconstructed original-row combinations exactly.

Validate every original CSR matrix and column/row bound before use. There must be 24 buses, 38 branch rows per hour, 23,016 columns and 34,680 rows. Every branch row must have two exactly opposite, nonzero angle coefficients within one hour, symmetric positive finite endpoints, and its recorded semantic label. Each hour must have exactly one angle column pinned to zero. Discover this pin from actual bounds; the present archives pin bus index 12 / ID 113. It is a column bound, not an invented matrix row. The graph must be connected to that pin. Check exact hour-normalized coefficient, endpoint, bus-order and reference equality for all four weeks before reusing a common path structure.

Each original balance combination contains one aggregate equality with multiplier +1 and all 24 nodal equalities with multiplier -1; reverse all signs for orientation -1. Its multiplier L1 norm is exactly 25. Reconstruct all touched coefficients without tolerance dropping and require every nonzero coefficient to lie on that hour's angle columns. This is not a new selection of balance rows.

## One fixed all-path construction

Use the strict exact edge metric `R_e / |b_e|`, with positive edge costs. Run Dijkstra from the discovered reference once on the first month's hour-zero block. Compare candidate labels by exact total cost, then the full tuple of archived base-hour branch-row IDs in traversal order. Use bus index only as a final heap tie break. Sort adjacency by base-hour row ID and neighboring bus index. Preserve parallel branches as distinct edges. No alternative tree is selected after any diagnostic result.

All non-reference coordinates use their chosen path, including coordinates with zero residual coefficient. Do not use `min(original box, path)`, another path metric, a changed reference, alternative balance combination, or adaptive coordinate subset. Reuse the one tree only after the complete structural identity checks. Record every edge, chosen ordered path, direction, exact distance, and rational multiplier `p_je`. Independently reconstruct each path against its actual branch rows to obtain exactly `theta_j - theta_ref` and exactly the stored path distance.

For original residual q, add branch multiplier `-sum_j q_j p_je` on edge e, summing all non-reference path contributions before selecting the signed row endpoints. Path multipliers already include division by the actual branch coefficient. Keep the original balance multipliers unchanged and verify that branch and balance row sets are disjoint. On direct reconstruction against the complete original sparse rows, all touched coefficients must cancel exactly except the reference coefficient `sum_j q_j`, including the original `q_ref`. Retain zero-valued touched coefficients in the record so generation/state cancellations are explicit.

## Strict and uniformly expanded checks

Evaluate the complete merged original-row combination directly: selected finite row endpoints, finite-column box maximum, multiplier/coefficient L1 norms, strict gap and exact expanded endpoints at `tau = Fraction.from_float(1e-5)`. Require equality with the norm formula. No modified model or inferred box is used in this direct certificate calculation.

Also compute the conservative independent per-variable path bound, unmerged edge supports, merged edge supports, shared-edge gain and reference gain, for both zero expansion and tau. Require the exact identity

```text
assembled_gap = independent_path_box_gap
  + sum_e (R_e + tau) [sum_j |q_j p_je| - |sum_j q_j p_je|]
  + tau [sum_j |q_j| - |sum_j q_j|].
```

The edge sums run over non-reference path coordinates. The final reference sums include the original reference coefficient. For strict checks set tau to zero. Both gains must be nonnegative. Archive merged and unmerged rational coefficients and supports, not only a Boolean identity claim.

Verify for every orientation the independent predicted upper bound

```text
expanded_gap <= abs(beta) - 25*tau < 0.
```

The zero-centered branch intervals and reference pin make the remaining support costs nonnegative. An expanded separator, failed exact cancellation/identity, changed hash, or contradiction of that upper bound is a hard review stop with preserved partial outputs; it is not a publishable expanded-negative finding. The same archived models already have exact expanded positive reference evidence.

Classify evaluated outcomes as `CERTIFIED_STRICT_REPRESENTATION_INFEASIBLE` only when the direct strict gap is positive, otherwise `VALID_NONSEPARATING_RATIONAL_CANDIDATE`. Record expanded gaps and flags separately. A strict positive gap certifies infeasibility only for the exact archived representation. A nonseparating candidate does not certify feasibility. No physical infeasibility, numerical stability, new temporal-memory result, or strict positive witness is inferred.

## Finite arithmetic budget and records

Execution first verifies the frozen manifest and loads/validates/caches all four complete model archives and mappings. Record this validation time separately. After writing the execution marker, start a 600-second soft arithmetic phase, including the fixed synthetic new-logic checks, common-path computation, diagnostics and record writing. Check phase elapsed immediately before each orientation. Once it reaches 600 seconds, retain each remaining orientation as `NOT_EVALUATED_PHASE_LIMIT`, with no arithmetic evaluation or replacement. A single in-progress orientation may overrun the soft limit; record actual elapsed time and overrun. Do not silently drop the intended denominator.

Fixed synthetic checks cover exact equal-distance tie breaking, non-dyadic path coefficients, complete path reconstruction, nonzero shared-edge gains in both regimes, and nonzero expanded reference gain with zero strict reference gain. They are not scientific target cases or optimizers. They run only under the separately authorized execution mode.

Save one common path table and all 1,344 intended records, in four ordered compressed JSONL files. Every evaluated record binds its original matrix/bounds/labels, frozen input manifest and common path table. Save the complete outcome ledger and timing/count completion record only after successful processing and a final frozen-input hash replay. The final phase sample occurs after outcome-ledger serialization and before completion-record serialization; the latter final write is outside the reported phase sample. Hard stops produce a separate failure record with intended/completed counts and preserve partial files. No automatic retry is allowed. Independent post-run reconstruction, arithmetic/denominator/hash review and root review are required before publication.
