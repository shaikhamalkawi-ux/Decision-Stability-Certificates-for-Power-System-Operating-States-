# All-four seasonal uncapped energy follow-up — closed

Independent post-run replay passed. Three of the four prescribed April/October targets have verified binary upper witnesses and finite, strictly positive optimum-difference enclosures. The fourth remains **UNKNOWN / NO_UPPER**. All four cases are retained.

These are retrospective Phi0 unrestricted interior-package permutations in the original angle model with uniform finite-bound expansion by the exact binary64 value of `1e-5`. They are not the January hour-of-day-preserving cases, nor the separate strict flow model. All positive witnesses satisfy the original 12096-coordinate binary mask and native checks; strict nominal membership remains false.

| Target | Month | Difference of target and identity optimal fossil electricity, MWh | Relative optimum difference | Uncapped outcome |
|---|---|---:|---:|---|
| 26093400 | April | [422.215678, 1460.098124] | [0.988706%, 3.461710%] | Verified binary upper |
| 26093401 | April | [273.680850, 1596.186199] | [0.640881%, 3.784357%] | Verified binary upper |
| 26094000 | October | [689.463677, 904.158184] | [0.556323%, 0.729564%] | Verified binary upper |
| 26094001 | October | Not established: no finite binary upper | Not reported | UNKNOWN / NO_UPPER |

Displayed endpoints are rounded outward; exact rational records in `energy_brackets.json` are authoritative. Each finite difference interval is [LT-UI, UT-LI], and its percent interval is 100 times [LT/UI-1, UT/LI-1]. The lower bounds come from exact signed-dual/finite-box residual evaluation of the continuous relaxations; the uppers come from accepted original-mask binary points. Neither numerical solver bounds nor incumbents are assumed optimal.

For 26094001, the exact target lower bound is approximately 124698.1560853128 MWh, above its reference upper of approximately 123932.13982439978 MWh. This gives a necessary positive energy separation **if the target is nonempty**. No accepted binary target point was returned, so finite uncapped feasibility, a finite optimum-difference interval and a relative interval are not claimed.

Exactly two identity LP60, four target MIP300 and four target LP60 calls ran, with no retries or new identity MIPs. All four MIPs reached their time limits; three supplied accepted witnesses. Actual MIP time was 1212.9905777 seconds and LP time 73.2779043 seconds. The total phase was 1397.5052624 seconds within the 2100-second allocation, ending at 03:52:42 UTC before the 04:00 cutoff. Aggregate solver soft-limit overrun was 12.9905777 seconds and is retained. All ten actual starts respected the cutoff guards; the largest recorded admission-to-start delay was 0.008003 seconds. These shared-host timings are accounting, not performance comparisons.

The independent reviewer rechecked all 397 frozen bindings and 164 closed producer files, all six objective-bound calculations, both unchanged reference uppers, all three new original-mask/native points, both finite/conditional reporting branches, intervals and the ten-call ledger, without optimization. Source matrices delete only the original cap row; original masks, calendars, complete native package transport and every other physical bound remain fixed.

A separately labeled post-hoc check tested **all three** accepted new points against their actual old capped parent matrices. Both April points fail their old 43131 MWh cap, which does not prove those capped models infeasible. The new 26094000 point passes every expanded original parent row, box and binary constraint, as well as direct native checks: its energy is approximately 124835.46367319977 MWh below the old 125172 MWh cap. This is a new capped-admission proof from the later uncapped arm. The old capped run's four UNKNOWN records are preserved, not rewritten. Case 26094001 has no new upper point. No target lower bound exceeds its old cap plus tau, so no new cap-negative conclusion follows.

The original failed replication gate, failed augmented cap criterion and earlier conditional follow-up's zero eligible cases remain unchanged. Three seasonal positive energy gaps are within-system evidence from two additional seasons; they do not augment the six January HOD cases or constitute independent-network validation. Fossil electricity is not fuel, money or emissions. The numerical expansion has mixed units and is not a physical uncertainty guarantee.

Independent report: `results/research8h/seasonal_all_four_energy_independent_review/postrun_review.json`, SHA256 `da0264aeba0ade3a27140acd91d51d4dba4335e26c9f7c3704470de6de642ec8`. Its separate `new_historical_cap_points.json` has SHA256 `65c9c6f2d8392b19a10c7433753954238a9e6f219e0e143299b5f0c66573127e`. The original producer summary's PENDING review label is retained as a historical snapshot; this readout and the independent reports supply the final review status. `FINAL_ARTIFACT_INVENTORY.csv` binds the full input/output/review closure and this readout, excluding its own self-reference. No reviewed evidence file was edited for closure.
