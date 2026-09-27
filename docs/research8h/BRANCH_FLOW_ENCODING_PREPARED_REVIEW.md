# Independent prepared flow-conserving model review

PASS before any optimizer call or basis reconstruction. The four full models each have 34,513 rows, 29,400 columns and 12,096 original binary coordinates. Independent read-only source imports were confined to the frozen standalone NPZ kernel. All 103 frozen bindings remained unchanged; no execution marker existed.

The reviewer derives graph edges and exact branch coefficients from every old branch row, verifies native generator incidence and fuel classification against the attributed native CSV, and checks all retained rows, replaced nodal and branch rows, masks, boxes, objectives, source-hour maps, exact package permutations and control commitment equality. It verifies both native ramp conversion and residence parameters. Only the 168 separately rounded aggregate rows are omitted. Metadata dimensions, nonzero counts and column orders match the actual exported arrays.

All four cases share 15 changed nodal coefficients after exact flow elimination. Their maximum absolute difference is 3/2199023255552. The maximum absolute difference between the exact nodal-load sum and the old aggregate RHS is 37/281474976710656. These are exact representation differences, not neglected tolerances or a proof of feasible-set equivalence.

The identity proposal deletes only the fossil cap and substitutes the fixed original states. Its 18,480 rows and 17,304 columns form 168 independently verified blocks of 110 rows and 103 columns; all 16,032 constant-state rows hold exactly. Every coefficient, endpoint, box and objective is checked against the full variant, with no endpoint-conversion differences. The full target cap remains 23195 MWh.

The first reviewer attempt stopped on an incorrect expected-member schema when reading the control native NPZ. The strict decoder correctly rejected requesting one key from a six-key file. The attempt source and error record are preserved; the reviewer alone was corrected to read the complete schema. Producer files and mathematical inputs were unchanged. The corrected review passed in 11.3648723 seconds with zero optimizer calls.

Input manifest: 0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4. Final reviewer source: 54fd65020f351203d4ae43c8a8e71af4c82e27511446865798879d4c1f0aec1b. Result: 19d5a9ca7cf293c8390a5a998aecabda769b5eff496b51d6ffb512fc4ad9660e.

No outcome is established by preparation. Execution requires a separate root GO, and any strict witnesses or rays require independent post-run replay. The old exact-model failure and expanded-model findings retain their original scope.
