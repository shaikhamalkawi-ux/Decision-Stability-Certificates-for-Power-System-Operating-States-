# Closed result: finite strictly positive energy penalties in the flow-conserving model

Independent post-run replay passes. Both fixed ordinary HOD targets have strict rational uncapped binary witnesses and exact objective lower bounds. Their optimal fossil-electricity penalties relative to the January identity lie in finite intervals with strictly positive lower endpoints. Every point and bound here uses **tau=0 in the separately specified flow-conserving DC model**. The old independently rounded angle-model results remain unchanged.

The following decimal intervals are rounded outward to six decimal places; archived rational fractions are authoritative.

|Case|Exact enclosure of minimum fossil electricity, MWh|Optimal penalty versus identity, MWh|Relative optimal penalty|
|---|---:|---:|---:|
|January identity|[22616.830716,22964.941240]|Reference|Reference|
|Ordinary26093200|[23532.980654,23952.175431]|[568.039414,1335.344714]|[2.473506%,5.904208%]|
|Ordinary26093201|[23824.881499,24024.798984]|[859.940259,1407.968267]|[3.744578%,6.225312%]|

The denominator is two ordinary targets; both are retained and have finite strict intervals. A feasible upper point is not a proof of the global binary optimum. The lower bounds come from exact certificates for full continuous relaxations with unfixed U/Y/Z; the upper bounds come from exact feasible binary points. The optimal penalty enclosure is `[L_target-U_identity,U_target-L_identity]`. Percent bounds use the verified positive identity lower bound and nonnegative target lower bound.

## Model and witness scope

Each new full model deletes only the fossil-cap row from its closed branch-flow parent:34512 rows,29400 columns and the complete12096-coordinate binary mask remain. Every other coefficient, row/column bound, native package, source-hour permutation, graph, dwell/boundary rule and23-fossil objective is unchanged. Nuclear121_NUCLEAR_1 remains excluded from fossil energy. The closed capped models retain their23195 MWh cap and strict positive/negative results; this follow-up does not edit them.

The January upper reuses and rebinds the already verified strict identity point. Each target fixes only the U/Y/Z schedule from its predetermined old accepted uncapped point and proposes a new dispatch in the distinct flow model. No alternative schedule or MIP was searched. All336 target-hour exact reconstructions pass, followed by complete uncapped matrix/box/binary and direct native checks. Each target point passes all34512 rows,29400 coordinates and12096 binary states at tau=0. Native checks include incidence conservation, flow equations/limits, availability/hydro/committed output, transitions, mature initial/clipped residence and the existing rationalized binary64-hourly on/on ramp convention. The separate uncapped checker removes only the cap rule and explicitly verifies cap absence; it does not ignore any failed physical check.

All five predetermined lower candidates were retained for each of the three full models. The positive sign-projected candidate gives the selected largest bound each time. Raw positive and negative candidates are rejected for selecting an infinite row endpoint; zero and negative sign-projected candidates remain valid, weaker alternatives. Every valid bound recomputes all coefficients of `c-A^T y` and the exact finite-box correction. No stationarity tolerance, numerical solver bound or old-model energy certificate is trusted or transferred.

## Execution, provenance and review

Preparation ran once,39.754522500006715s, with zero optimization or target-basis reconstruction. It bound355 inputs, all three full cap-deleted models and both fixed proposals before execution. The single execution marker is03:34:49.685962UTC, before the unchanged prospective03:35 start gate. The absolute04UTC and phase guards were retained.

Exactly five LP calls ran in the declared order: full identity2.0324453999928664s; full ordinary00 2.824913699994795s; full ordinary01 3.0430321999883745s; fixed ordinary00 0.8935600999975577s; fixed ordinary01 0.9209716000186745s. Each had a60-second soft limit. Total optimizer time was9.714922999992268s; arithmetic388.1135927000141s within900s; execution phase404.7295330000052s within1800s. All numerical calls reported Optimal, but the scientific conclusions rely on the rational checks. There were no retries, MIPs, warm starts, alternate bases/schedules, cap changes, skipped hours, unresolved cases or time overruns.

Independent prepared review checked all355 bindings, exact cap-only model relations, every proposal/constant row and schedule, native byte copies, the inherited identity point and the cap-only difference in the native checker. Independent post-run replay took53.3024002s with zero optimizer calls. It checked all355 input bindings and453 snapshotted producer files, three full strict/native points, all15 dual candidates, all336 hourly memberships, both finite positive intervals and the five-call ledger. It also verified the native specification against the pinned original generator CSV. No producer artifact was changed during review.

This result supplies finite strict-model energy-cost evidence on the two already known January HOD cases. It establishes neither a new out-of-sample replication nor formulation novelty, and it is not a field experiment, physical-measurement exactness claim, AC/security result or operating recommendation. The flow-conserving representation and its documented small coefficient/RHS differences from the old encoding remain explicit. The old nominal exact-witness attempt stays unresolved.

## Closed replay artifacts

- `input_manifest.json`: SHA256 `7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7`.
- `outcomes.json`: SHA256 `ec069eaf704bb60536fbca167ec799722ffc34092f8a2a2a9c405fb543ef4a13`; stores exact bounds, penalties and ratios.
- `completion.json`: SHA256 `6adde0c24ddd34ce2e37dd9964aa8c7065825a37593268029eb8c35084915488`.
- Each full case contains its cap-deletion map, native provenance, complete model, objective/full mask, rational point, strict check and all lower-bound candidate/residual records. Each target proposal retains its basis, all168 exact-hour records and solver log.
- Independent review: `../branch_flow_energy_prepared_review.py/.json` and `../branch_flow_energy_independent_review/postrun_review.py/.json`; memo `docs/research8h/BRANCH_FLOW_STRICT_ENERGY_POSTRUN_REVIEW.md`.
- The appended artifact inventory binds the closed evidence and this readout. Portable strict-flow replay design or implementation is a separate delivery task, not an additional result in this arm.
