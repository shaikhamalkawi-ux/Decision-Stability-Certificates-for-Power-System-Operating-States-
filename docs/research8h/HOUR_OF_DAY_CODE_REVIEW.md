# Hour-of-day arm: independent code/protocol review

Verdict: PASS for the reviewed model, construction and routing. Target optimization remains gated on independent prepared-archive PASS and root GO. Root had already authorized/launched preparation before this review was finalized; this is not a claim that the completed independent review preceded preparation. No optimizer was run by this reviewer.

Source `src/research8h_hour_of_day.py` SHA-256: `b617d41ab09d18d57c003147b52ae80f369225bc6029121109cee3d53e71d60e`.

Protocol `docs/research8h/HOUR_OF_DAY_PROTOCOL.md` SHA-256: `09b3a45af4224c65b03dd4d3972750ba417f0f26ccc153e51fa9ca3ae4d9829b`.

Both ordinary seeds use their own PCG64 generator and exactly one permutation of each three-position hour-of-day group, in hour order 0 through 23. The control uses the authoritative **lexicographic ordering of (hour, complete 24-bit U signature)**, increasing positions within each group, and retains identity draws. It is not a first-occurrence group order. Bijectivity, fixed 48-hour edges, hour modulo 24 and complete native-package inverse roundtrips are asserted. Startup/shutdown coordinates are reconstructed across all 168 hours, without artificial day-boundary resets.

Preparation rebuilds and compares the January identity's full sparse matrix, bounds, original mask, row labels and native nodal arrays. It fixes the native 23-unit fossil roster and 23,195 MWh cap, zero objective and no mean rows. The source separately proves the 24 native on/on ramp margins cover the actual constant thermal dispatch ranges. Identity/control acceptance conjoins native physics and exact original-binary expanded membership. Each ordinary copied point requires exact static membership after deleting only dwell rows; its full copied-schedule failure is not a model infeasibility claim.

The imported LP helper uses one configured simplex/presolve-off 30-second call and admits a negative only after exact robust ray recomputation; its certificate directory contains frozen matrix/bounds/row metadata copies. The output context is rebound to this new arm. The imported MIP helper uses the original physical model with an audited U-only mask, one 300-second call, no retry and canonical recovery. Accepted binary points require unchanged P/theta, original full-binary exact expanded membership and native physical checks. Numerical MIP infeasibility is retained as a diagnostic and classified UNKNOWN. All unresolved LPs precede MIPs; constructive positives and guard exclusions remain in the denominator.

Two reporting nuances are retained as review notes because preparation had already started; they require no redesign or rerun:

- `changed_adjacent_pair_count` is computed as the count of `diff(order) != 1`. It measures **breaks in consecutive source-hour continuity**, not the number of adjacent positions whose ordered pair differs from the identity pair. The complete permutation is saved, so the prepared review can report the literal changed-pair count separately. Interpret the producer's field using its actual definition.
- The protocol's “at most 1200 seconds” is a configured solve/check-phase allocation with a 305-second MIP-start guard, not a guaranteed hard deadline. The code starts this phase after manifest validation and native model loading. Solver limits are soft; actual phase elapsed time and LP/MIP times must be reported, with any overrun calculated explicitly. Preparation is excluded.

This family preserves hour-of-day package distributions but may change within-day order and weather continuity. It is an outcome-informed exploratory follow-up with new seeds fixed before their solves, not a blind replication, independent grid or demonstration of a novel principle. Final prepared review must verify frozen hashes, actual group/order records, model/bound mappings, exact controls and projected-mask provenance before root GO applies.
