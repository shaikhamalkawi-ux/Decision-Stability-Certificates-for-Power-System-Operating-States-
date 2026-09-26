# Pooled-energy chronology twins: separate post-pilot extension

The repaired July identity witness passes the same strict 26-group mean constraints, native per-unit dwell rules and weak horizon boundaries. All four preselected jointly permuted twins remain Infeasible after individual weekly energies are relaxed to those group totals.

| Case | Prior individual-target status | Grouped-target status | Solve time (s) |
|---|---|---|---:|
| Identity | Verified network witness | Verified grouped witness | No solve |
| Seed 26092600 | Infeasible | Infeasible | 1.953 |
| Seed 26092601 | Infeasible | Infeasible | 3.031 |
| Seed 26092602 | Infeasible | Infeasible | 2.484 |
| Seed 26092603 | Infeasible | Infeasible | 1.797 |

These are four fixed 60-second cases, single-thread HiGHS 1.12.0, seed zero; none timed out. The target is the complete mean of the repaired July network witness, not the original static July target. Existing permutation CSVs define the orders, preserving the first and final 48 hours. Demand and native availability are permuted together, and saved native row indices are checked against the source mapping. The grouping inventory is byte-identical to the archived-week audit: 41 dispatch units, 24 distinct thermal chronology variables, 26 weekly energy groups. Per-hour identity reassignment is never used.

The unpermuted positive witness was checked before solving and again after saving/reloading its dispatch, commitment, startup and shutdown CSVs. Both checks pass. Maximum group-mean residual is exactly zero; maximum balance residual is `6.821210263296962e-12 MW`; binary, transition, output-coupling and residence residuals are zero. The complete control is in `identity/`. Its source dispatch SHA256 is `a58ffcaa470cdc01d574ebd34fd2ab4953cb9a73087e1103407bf7b945be65da`; source commitment SHA256 is `d0baca56221f249076e11dbf26d49c8418ff189b27e44ef4fe5a5ad805cfa449`.

The extension was declared after the archived-week pooling outcomes and the parent's individual-target twin outcomes were known. It is a separately labeled robustness check, not an initial preregistered or held-out test. Its protocol/code/group/permutation/target hashes were frozen at `2026-09-26T19:16:35.128325+00:00` before these four grouped solves. No case or time budget changed after a grouped outcome.

Within the tested model, the identity/permutation feasibility contrast survives pooling weekly energy within exact represented-equivalence groups. Consequently these four paired counterexamples do not require fixing separate unit energies within those groups. This is conditional on the particular four permutations, same-week data, hourly native dwell model and free-start/truncated-end boundaries. It does not prove that a proposed cheap certificate detects them, that arbitrary technology aggregation is valid, or that actual emissions match. Numerical solver rejection is retained as such; there is no independent analytic rejection certificate in this directory. The parent's no-network infeasibility also applies to a stricter network-constrained formulation if its remaining physical assumptions match, but this extension itself solves only the no-network relaxation.
