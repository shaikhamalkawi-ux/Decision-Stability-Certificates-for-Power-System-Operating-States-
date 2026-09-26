# Seasonal cap continuation: independent code preflight

Verdict: PASS for preparation. Execution remains gated on independent review of the completed prepared archive. No target output directory existed when this source review finished; no solver was called by the reviewer.

Reviewed source `src/research8h_seasonal_cap_continuation.py` SHA-256: `fe7253d9d6217a26ad3162422e91cc90dba83350526faed1443d54c8500b29ab`.

Reviewed protocol `docs/research8h/SEASONAL_CAP_CONTINUATION_PROTOCOL.md` SHA-256: `14349e3ea185f0cd4089ab5d2745afbbd4c7d5240064893b5f3ffe0065b6bbb2`.

The code waits for all three reference-continuation calls and final input checks. It considers only the fixed April/October schedule and keeps ineligible cases in the ledger. It does not replace an unavailable reference with July or rewrite original NO_REFERENCE/UNKNOWN outcomes. Eligible references must pass an original full-binary exact expanded point check and native no-cap physics. The cap is the exact integer ceiling of 1.01 times the recovered reference's exact binary64 fossil-energy sum over 23 native fossil units, not a solver optimum or a tunable target. The common cap is fixed before target solves.

Removing the one cap row from each identity must recover its reference's entire physical matrix, bounds and original integrality mask exactly. Joint order construction covers all hourly packages and the reference P/U/theta arrays, preserves both 48-hour edges, and checks bijections, inverse roundtrips, native nodal reconstruction and exact total fossil energy. Class controls preserve the exact 24-unit U sequence. Identities and class controls require full exact expanded membership and native physics. Ordinary constructive points must pass exact static membership after removing only `minimum_up` and `minimum_down`; their full dwell failures cannot become infeasibility claims.

All prepared models, original and projected masks, controls and imported source dependencies are manifested before the freeze record. LP directories receive their bound/matrix/metadata copies before hashing. The execution mode rechecks the frozen manifest and exclusive execution marker. The U-only mask is audited against actual sparse rows; recovered MIP candidates preserve P/theta, round only eligible U and reconstruct canonical Y/Z, then face the original full-binary model, direct physical checks and exact expanded membership. Numerical/strict/expanded outcomes stay separate.

The fixed schedule runs every eligible ordinary LP once before conditional MIP calls. LP ray sign candidates and sign-cone projections are fully recomputed in exact arithmetic, and only a uniformly expanded positive separation certifies rejection. A robust negative conflicting with a constructive expanded positive stops execution. All remaining MIPs have one configured 300-second call, no tuning/retry/warm start, with a 305-second remaining-phase start guard. The guard does not make soft solver limits a hard wall-clock bound; actual times and phase overruns are recorded.

The augmented January-plus-continuation indicator is explicitly later evidence, retaining January's already known success and the original failed initial-arm replication gate. It cannot be described as two new independently discovered grids, proof novelty, field validation, or a prospective pass of the earlier arm. A capped exact rejection alone does not prove an uncapped energy penalty. Reference incumbents are accepted feasible baselines without optimality claims.

Prepared-archive review still must independently verify manifest contents/hashes, actual orders/native arrays, cap arithmetic, sparse projection, original-mask provenance and exact positive/static controls before the standing execution GO can apply.
