# Independent all-four seasonal energy post-run review

Verdict: PASS. One stdlib-only replay completed in 40.96791969999322 seconds with zero optimizers or producer imports. All 397 frozen input bindings and 164 closed producer files matched before and after review.

Recomputed all six signed-dual/residual/finite-box lower bounds and all fixed zero-dual comparisons. Replayed the two reference points and three accepted target uppers against every actual row, finite box and all 12,096 original U/Y/Z binary coordinates. Direct native checks independently cover GEN roster, availability/hydro, canonical transitions, clipped dwell, on-on ramps, native hourly balances, branch limits and supplied-angle nodal membership. The rounded nodal operator is the frozen original angle encoding, already audited for provenance; no new numerical native assembler or angle solve was used. All five accepted points are uniformly expanded members at the exact binary64 tau=1e-5 and are not strict nominal members.

All four cases are retained. The exact optimum-difference formula [LT-UI,UT-LI] and positive-denominator ratios agree with every reported finite interval. Negative and missing-evidence branches were not clamped or dropped.

| Target | Difference of expanded binary optimum energies, MWh | Relative difference, % |
| --- | ---: | ---: |
| seed_26093400 | [422.215678, 1460.098124] | [0.988706, 3.461710] |
| seed_26093401 | [273.680850, 1596.186199] | [0.640881, 3.784357] |
| seed_26094000 | [689.463677, 904.158184] | [0.556323, 0.729564] |
| seed_26094001 | NO_UPPER | Not reported |

Displayed finite endpoints are rounded outward to six decimal places; exact rational records are authoritative. For seed_26094001, the positive lower difference is at least 766.016260 MWh if its binary feasible set is nonempty. This does not establish finite feasibility, a finite optimum interval or a percentage interval.

## Separate later proof against the old caps

Checked every accepted new target point against its actual old capped parent matrix, its full original binary mask and native inputs in a separate sidecar. The October seed_26094000 point passes the expanded old capped model and native checks, with an unexpanded cap margin of at least 336.536326 MWh. Its nominal strict membership remains false. This is a new post hoc capped binary witness derived from the later uncapped study.

The April seed_26093400/01 points fail their old caps; that failure of these particular points proves no capped infeasibility. October seed_26094001 has no accepted upper to transfer. None of the four new objective lower bounds exceeds its old cap plus tau, so this arm supplies no new cap-negative certificate.

All four historical capped-run UNKNOWN labels remain immutable. Current mathematical knowledge is more specific: seed_26094000 now has expanded cap admission; the other three old capped instances are unresolved by this follow-up. The earlier failed negative-replication gate remains failed. These are retrospective within-system April/October Phi0 energy cases, not HOD-preserving PhiH tests, external-network transfer, strict witnesses or exact optima.

## Execution and stable evidence

All ten calls occurred in the fixed order. MIPs took 1212.990577699995 seconds in total, LPs 73.27790429999004 seconds, and the entire phase 1397.5052623999945 seconds. The 12.990577699994901 seconds of cumulative MIP soft-limit excess is retained; the 2100-second phase and UTC cutoff were not exceeded. The saved actual-call admission diagnostics are consistent. One target retains NO_UPPER.

- Reviewer source: results/research8h/seasonal_all_four_energy_independent_review/postrun_review.py; SHA256 34494cb749d882ecdd17e34cc7692fa142d153f1bd30b2857eebe3e40b4e01ba.
- Main report: results/research8h/seasonal_all_four_energy_independent_review/postrun_review.json; SHA256 da0264aeba0ade3a27140acd91d51d4dba4335e26c9f7c3704470de6de642ec8.
- Separate capped-point report: results/research8h/seasonal_all_four_energy_independent_review/new_historical_cap_points.json; SHA256 65c9c6f2d8392b19a10c7433753954238a9e6f219e0e143299b5f0c66573127e.
- Frozen manifest: 7a5a4cde36105325bcf5fd70e19a06d2997ce39240678ddbb82186f9ead4b078.

No producer file or historical outcome was modified.
