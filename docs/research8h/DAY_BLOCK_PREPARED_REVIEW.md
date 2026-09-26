# Independent review of the prepared day-block archive

Verdict: **PASS for the frozen prospective execution route; no blocker found.** This review was completed after preparation and before execution. At the final pre-execution check (2026-09-26T22:08:22Z), execution_started.json was absent. The reviewer ran no optimization and did not modify any runner, protocol, input, or result archive.

## Frozen identity and hashes

Prepared at 2026-09-26T22:03:45.012792+00:00 with optimizations_started=0.

- Source SHA-256: 43441ca2da48c6d8acc2574461502f6f74a4f0f4a3b32ad653c5fd794a5f6a8b.
- Protocol SHA-256: b557ac53749616f13c600ddf2b02712e3fbd307083659dea05e65c108a659933.
- Prepared manifest SHA-256: 5f15b13ce9b15abb1ff6256a4e10fc568ab5384e01a324160b0e522b31c8927d.
- Independently read and hashed all **148** manifest entries: every SHA-256 and byte count matches. Source/protocol match the prior code review and prepared freeze.
- Independently replayed the inherited seasonal manifest: **136** entries, zero mismatches; SHA-256 9362c181d3aad078f9ff21fc35b3043ca923b70d8484e72565a4b39d7967eb87.

## Independent replay method

The reviewer decoded the archived NumPy/CSR files directly in Node, without importing the runner or its checker. A separate BigInt dyadic implementation interpreted every binary64 coefficient, bound and point coordinate exactly, recomputed every matrix row and column residual, and compared it with the exact binary64 value of tau=1e-5. This is an independent arithmetic replay, not reliance on a saved pass flag. Binary coordinates were checked for exact membership in {0,1}.

All five full and static point checks exactly reproduce the saved maximum row/column violations, as do the two source positive controls. Static here removes only minimum_up and minimum_down rows; it retains transitions, the global fossil cap and the full DC network. Direct native physical checks were inspected from the saved reports; the independent replay checks their encoded matrix counterpart and verifies copied native data, rather than independently reimplementing the full native checker.

| Case | Exact expanded static point | Exact expanded full point | Violated full matrix rows | Native residence events |
|---|---|---|---:|---:|
| days_132 | pass | fail | 7 | 2 |
| days_213 | pass | fail | 5 | 1 |
| days_231 | pass | fail | 5 | 1 |
| days_312 | pass | pass | 0 | 0 |
| days_321 | pass | fail | 7 | 2 |

Every failure above is confined to residence rows. The maximum violated row is 1 for each failing copied witness. The source january_identity and seed_26100100 controls both pass the full expanded model with exact binary coordinates. Their largest exact nominal row violation, also the largest for days_312, is approximately 2.5498884647111388e-11; the maximum column violation is approximately 2.155253753244324e-11. **None of these points is strictly feasible for every unexpanded binary64 bound.** The positive claims therefore remain explicitly for the uniformly expanded model.

The saved days_312 native physical check and binary_network_pass are both true; all five saved static_network_cap_pass flags are true. Four copied-witness failures do not establish infeasibility of their corresponding optimization problems.

## Mappings and model contents

Independently reconstructed exactly the five lexicographic nonidentity day orders: 132, 213, 231, 312, 321. Every permutation.csv row, native source-row identifier, native pmin/pmax/net/nodal array and source_hour mapping matches the intended whole-day permutation. Hours 0–47 and 120–167 remain fixed; hour of day and each day’s internal order are preserved. All permuted P, U and theta coordinates match the corresponding original witness coordinates exactly. Y/Z equal canonical transitions recomputed over the entire 168-hour sequence, with first-hour Y/Z zero.

The exact rational fossil energy is unchanged in every copied point: 1654798412944827657145 / 72057594037927936 MWh. Each frozen model has exactly one fossil_energy_cap row, upper bound 23195 MWh, with coefficient 1 on precisely 23 fossil-unit P coordinates at each of 168 hours. There are no individual-mean rows. Column bounds are finite and objectives are zero. Nuclear is absent from the verified 23-unit cap support.

The reported changed_adjacent_pairs_after_hours counts source-continuity breaks; it should not be described as every positional adjacent-pair difference. This does not affect the permutation or feasibility checks.

## Projection and certificate preparation

Independently scanned all five sparse matrices. Original integrality covers exactly U/Y/Z (12096 columns); projected integrality covers exactly U (4032). State bounds and initial auxiliary zeros match the recovery proof. Each model has 4008 rows in each of transition, exclusive_transition, minimum_up and minimum_down. Their coefficient signs, unit/time indexing, bounds, and auxiliary support satisfy the projection proof. Every other row is free of Y/Z. Saved projection audits agree.

In each case, lp/matrix.npz, bounds.npz, integrality.npz and row_metadata.csv.gz are byte-identical to the corresponding prepared parent files and are included in the validated manifest. Thus the exact-ray helper has the bound matrix/context files it requires.

## Execution interpretation

The frozen route may skip both LP and MIP for days_312 because its constructive full expanded point and native check already pass. All five cases remain in the denominator. The other four remain unresolved at preparation and should follow the fixed LP-then-conditional-MIP route. A failed copied witness, fractional LP feasibility, solver timeout, or unvalidated solver infeasibility must not be promoted to a certified binary result. The previously reviewed uniform tau convention, original-model recovery checks and exact-ray requirements remain necessary.

This review establishes consistency and replayability of the prepared experiment. It does not establish a novel method, strict nominal feasibility, general sufficiency of typical days, or the outcome of the four pending cases.
