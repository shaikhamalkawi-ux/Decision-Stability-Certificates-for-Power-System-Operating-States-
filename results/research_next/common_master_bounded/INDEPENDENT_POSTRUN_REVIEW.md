# Independent closed-run review — bounded common master

Verdict: **PASS of the archived execution and its stated scope; the common-commitment question remains UNKNOWN.** The independent review ran once in 8.1871398 seconds, with no optimizer, model rebuild, producer import, new candidate, or private-log access.

The reviewer checked all 239 frozen bindings and 25 public producer outputs before and after review. It reconstructed both saved backend readbacks against their pinned inputs: all master coefficients, endpoints, boxes, binary types and objective; and all 69,362 rows, 33,936 columns and 291,176 coefficient values of the fixed original joint LP. The joint matrix and continuous bounds are unchanged; exactly the 12,096 original state coordinates are fixed to the sole nominated schedule. The pinned standard-library NPZ decoder was reused explicitly; this is independent review logic, not an independently implemented decoder.

Exactly one master solution was returned. All 12,096 state values were already exact bits, so restoration changed none. Independently reconstructed values for the 336 auxiliary lower envelopes satisfy every one of the 17,212 exact rational master rows and all 12,432 boxes. This certifies membership in the **necessary master only**, not operational feasibility or cost optimality.

The single SCIP call used 46.8863172 seconds and 11 nodes. The single fixed joint LP used 0.6656822 seconds and reported numerical infeasibility with no valid continuous point. There is no accepted network witness or exact negative certificate. Neither this numerical status nor master membership settles existence of another common binary schedule. The authoritative completion verdict is UNKNOWN. The 61.2338979-second recorded phase had no configured overruns; documented final completion/cleanup overhead is outside that phase sample. Prescribed solver options agree; SCIP's internal `propagating/genvbounds/timingmask` changed from 15 to 0 and is recorded rather than treated as a user-option change.

Normal process closure records the observed launcher/worker processes as absent. The fast LP call's actual descendant PID was not observed, and Windows timeout/descendant termination was not exercised or established by this run.

Stable evidence:

- Reviewer source `INDEPENDENT_POSTRUN_REVIEW.py`: `bc289db42fcd761941bff15fbe0ebbdc977f5a21b718fc2d3738155ce330ac8e`.
- Review report `INDEPENDENT_POSTRUN_REVIEW.json`: `d5b2c4baac6605ef98f6cc025757c5f36c372166931ba7afe870d5509fdc9ad2`.
- Producer inventory: `a7201af2fc77e7a556c5b0fc2ee0634f812808f0e4f092b64656baf24d668428`.
- Producer completion: `3488a998b8d01cf279cddb20c9f6e22f04afd1ff3fdaf2d98260909c2d395883`.
- Prepared freeze: `75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5`.

All producer files remain unchanged. No additional solve, alternative nomination or negative-certification attempt was made.
