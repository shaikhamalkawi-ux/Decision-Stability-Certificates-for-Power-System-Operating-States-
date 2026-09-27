# Clarification of signal, metadata and raw-input counts

27 September 2026. This is an additive wording correction; no experimental input, software output or scientific verdict is changed or rerun.

The frozen AUER_PROJECTION_PROTOCOL.md, supported-signal projection section, specifies the following distinct counts:

| Object | Count | Meaning |
|---|---:|---|
| Raw operational time-dependent input coordinates per hour |107|41 generator lower bounds +41 upper bounds +1 aggregate input +24 nodal inputs|
| Projected supplied signal-table series per hour |41|24 nodal demands +11 utility-scale PV/wind capacity factors +6 hydro inflows|
| Named signal generators in the author VRES metadata table |17|The11 PV/wind units plus6 hydro units; this is not the complete supplied signal-table count|
| Aggregate features actually used in the inspected clustering comparison |4|The author's declared aggregate feature extraction, distinct from the input tables and raw operational coordinates|

The shorthand17-signal projection/representation in RESIDUAL_ORDER_PROTOCOL.md, CYCLE05_WORKING_ASSESSMENT.md and CYCLE05_FINDINGS_AR.md can incorrectly suggest that all projected demand/availability/inflow inputs total17. Read it as referring only to the17 named signal generators; future summaries use the full explicit24+11+6 table breakdown. Those historical documents and their hashes are preserved. The earlier exact residual-vector result remains about four normalized clustering features, not full107-coordinate approximation error or all41 supplied series.

The current working-note draft was corrected before release. The arithmetic equality/inequality results, actual fixed arrays, 15+21 invocation denominator and5/3 whole-day collision counts are unchanged. This clarification neither enlarges the method's supported signal contract nor proves operational equivalence.
