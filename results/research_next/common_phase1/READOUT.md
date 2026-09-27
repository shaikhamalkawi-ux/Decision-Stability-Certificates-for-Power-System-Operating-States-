# Phase-I producer result: exact nominee rejection, common question UNKNOWN

The sole authorized phase-I run closed normally, session63821 exit0. **This is producer evidence pending independent exact post-run review.** One60s-bounded LP was attempted and returned in3.635906200041063s. The whole phase took20.919138900004327s, with no solver or phase overrun, retry, alternative multiplier, dual-ray retrieval or next master call.

HiGHS returned numerical optimality, valid primal/dual flags,19,325 simplex iterations and objective5.300026405336286. Those numerical facts are not the proof. The frozen sign-projection recipe reconstructed one original-row multiplier vector and complete q=A^T*d. The producer's exact checker admitted the necessary state inequality with RHS

`450876382487823762278891047947239219241 / 85070591730234615865843651857942052864`.

The archived nominee's exact state-side value is0, so the exact positive separation margin equals that RHS (approximately5.300026405336258, displayed from the saved fraction). The saved unrounded continuous control's state-side value is

`24219835069594288446557719279817175 / 1298074214633706907132624082305024`,

approximately18.6582822434607, and satisfies the cut. Its old full-point membership proof was not rerun and the control is not called binary. The reconstructed candidate has24 nonzero original-row multipliers,21 nonzero state terms and19 nonzero continuous residual terms. Every original-coordinate coefficient, continuous support endpoint and tau term is retained. Both canonical endpoint-cancellation gains happen to be zero for this returned multiplier; the exact identities nevertheless passed.

The final authoritative `run01/completion.json.final_admission` is `EXACT_CUT_REJECTS_FIXED_NOMINEE`, with `accepted_nominee_rejection=true`, deadline met and **common_verdict=UNKNOWN**. Subject to independent review, this excludes only the already nominated fixed schedule under the original expanded joint model and supplies a globally valid necessary state inequality. It does not prove that all common binary schedules fail, reject either individual world, give an operating-cost bound or establish a physical slack in MW/MWh. The certificate scale comes from a weighted mixture of original rows; no minimum-support or normalization-invariant quantitative-distance claim is made.

All292 frozen bindings remain unchanged. The original source model,23,195MWh caps, chronology, full12,096 nominated bits and existing master results were preserved. The98,546-row /33,937-column numerical phase-I model adds only the predeclared uniform artificial s formulation. Complete backend readback, all raw returned vectors, exact rational d/q/support/cancellation terms and provenance are archived. Raw solver logs remain private.

Key hashes:

- Source `8af88d286e85f5807ab0bc11cc2450d10596f667e62f4b45c5279c8ebbc2eacb`.
- Protocol `6617c67b1c93339487a41c306217c8770142665b9e35e33f23a09225f1e00583`.
- Freeze `9d2a0768eb785277d9b8ddf04483e0e83ed97ba628fff23e2a32b146649e1496`.
- Root GO `c6d26869297aaecb3a05bca5936019ba78a7bc7ae65380826d5d7150dd9bf44b`.
- Completion `c5920a87bf20cfdf226b53d4aa89c5998301d27a097caf21275272410c944547`.
- Exact candidate `427dba0e4a75fd7bce5dff278c958fb73dafa2fbf41cf0a1cdc3c08f391a178b`.
- Raw solution/duals `5d10000e4f667b58aeb82af6e7939aa75cd0be4ea79934d4eabfc725bfde87af`.

`PROCESS_CLOSURE.json` records the actual Python PID/parent from the runner and normal completion. Both recorded PIDs were absent at the final check; no termination or descendant-timeout claim is made. `producer_output_inventory.csv` binds all10 run artifacts plus this readout and the process receipt, excluding itself and private raw logs. These12 producer artifacts are stable for independent review.
