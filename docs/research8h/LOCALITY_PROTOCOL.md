# Frozen phase-one dwell-row locality experiment

This is a bounded post-pilot development experiment on existing seed 26092600, not a new held-out case. The protocol is written before any locality solves. First phase: at most 15 minutes wall time after the first LP starts; every LP receives at most 30 seconds. No original data, target, permutation, source function or historical result is changed.

## Fixed cases and windows

Use the existing repaired-July full 41-unit weekly mean and seed 26092600 hourly permutation from the baseline `7300129`. Use the original unpermuted repaired network dispatch/commitment as a positive witness. The only solved cases are the permuted case with the following nested, fixed windows, in this order (all hours are zero-based, inclusive):

| Width | Window |
|---:|---|
| 0 | Empty |
| 8 | [80, 87] |
| 16 | [76, 91] |
| 24 | [72, 95] |
| 48 | [60, 107] |
| 72 | [48, 119] |
| 96 | [36, 131] |
| 120 | [24, 143] |
| 168 | [0, 167] |

The common center is 83.5, the midpoint of the horizon and of the 72-hour permuted interior. No window is centered on a subsequently observed dual support. Run all nine candidates within the total budget, even if an early candidate rejects. No adaptive search or extra solves belong to this first phase. The shortest rejecting width means the shortest of these examined centered windows, not a globally shortest interval.

## Exact relaxation definition

Use `src/temporal_lp_certificate.py:assemble` at the bound source version. Keep every column and bound; all static hourly aggregate balances, availability/fixed hydro, conditional thermal output bounds; and all 41 complete weekly-mean equalities. U, Y and Z remain continuous in [0,1], with initial transitions zero. Keep transition identities and startup/shutdown exclusivity at every hour in the full horizon.

Only rolling minimum-up and minimum-down rows are eligible for removal. Keep such a row if and only if **all hour-indexed variables in its nonzero coefficients lie inside the candidate window**. Inspect sparse-matrix column indices, not merely the row's endpoint. A rolling minimum-up row at t touches U[t] and Y[max(1,t-UT+1)..t]; minimum-down analogously touches U[t] and Z[max(1,t-DT+1)..t]. No shortened/rebased rolling sum is substituted. Empty-window models have no dwell rows; the full-window model recovers the baseline exactly. Windows are nested, so retained dwell sets are nested. Every model is a row-subset and continuous/no-network relaxation of the original UC formulation.

The phrase localized dwell constraints refers only to these retained minimum-residence rows. Full-horizon transition linkage, static information and all-week means remain. In particular, a retained startup Y[s] at the left edge is globally linked to U[s-1], which may be outside the window. This is not an isolated-window chronology test or a claim that all required raw data lie in the window. Weekly means alone may depend on every hour.

## Controls and certification

Before the first LP, check the original repaired identity P/U and derived Y/Z against the complete independently assembled identity model, then against every corresponding row-subset identity relaxation. These checks must pass at 1e-5; the original witness is not expected to satisfy reordered demand. Also verify the empty-window twin using jointly permuted P/U and freshly derived Y/Z (never merely permuted transition flags). Compare reconstructed full seed matrix/bounds with the archived baseline numerical arrays, and bind source code, model, native inputs, witness, permutation and protocol by SHA256.

Use the existing bound `solve_case` with simplex, presolve off, one thread, seed zero and maximum 30 seconds. Retain every model matrix/bound, row map, raw dual ray, certificate candidate and exact check. A robust rejection requires `exact_ray_check` to establish exact rational separation for the archived binary64 model and survival of outward 1e-5 perturbations of every finite row and column bound. Save and replay the chosen certificate without optimization. A solver infeasibility status without a verified ray is reported separately. Feasible continuous relaxations are independently checked and mean **unknown for full UC**, never feasible UC. Timeouts remain unresolved.

Record which dwell families/units/hours were retained and which occur in a successful certificate, alongside global row support. A readable explanation may state that the globally fixed energies and static balances cannot coexist with these local dwell rows; do not attribute the contradiction to a single unit or a local raw-data subset without further proof. Phase one does not optimize sparsity or duplicate the separate multiplier-extraction workstream.
