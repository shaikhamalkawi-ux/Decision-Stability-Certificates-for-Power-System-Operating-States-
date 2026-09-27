# One necessary-master candidate; common question remains UNKNOWN

The single authorized run closed with exit0. Exactly one master MIP and one conditional fixed-schedule LP were attempted and returned. There were no retries, warm starts, new cuts or additional candidates. This is the **producer readout, pending independent post-run review**.

SCIP returned exactly one solution to the necessary master after46.8863171999692s, with11 nodes and73,329 internal LP iterations. Its numerical status was `optimal` for a zero feasibility objective; this is not an operational-cost optimum. The sole returned state block passed the producer's exact rational necessary-master admission, including all original binary state rows/boxes, both inherited affine cuts, integer capacity necessities and the deterministic minimum fossil-total auxiliaries. This establishes only the prepared necessary conditions, not a network dispatch witness.

The corresponding unchanged original joint model, with all12,096 states fixed to that sole block, was passed to HiGHS once. Every original row/coefficient/endpoint/continuous box and zero objective was read back before the call. HiGHS returned `kInfeasible` with no valid solution in0.6656821999931708s. No ray, IIS, exact negative proof or returned physical dispatch point was requested or obtained. This numerical restricted LP outcome does not establish an exact rejection of the schedule or an unrestricted common-commitment negative.

The authoritative `run01/completion.json.final_admission` is `accepted_common=false`, `common_verdict=UNKNOWN`, with the phase deadline met. Total phase61.233897899976s; master/LP/phase soft overruns are all zero. The worker returned normally without timeout. Both producer processes revalidated frozen inputs. No old result was relabeled; the previously verified separate individual positives and prior candidate exclusions retain their original scope.

The exact necessary master remains17,212 rows /12,432 columns /12,096 binary states. The recourse LP retained the original69,362 rows /33,936 columns. The original pre-control source/preparation is preserved; the bounded successor inherited its master byte-for-byte and changed execution controls only.

Key bindings:

- Source `62a2755aa289dc353893d3bf23ccf46ff839dffdf1937d5cdbc4320ce9526c18`.
- Protocol `ff502793f1fa52c6a10a228e2fe5f0d8a5caba5ff77380006c897c3f3e243553`.
-239-binding freeze `75e9e276c356290129c85fefa9fdc5fb36f175174efb5b2e131bb96fdbef80d5`.
- Root GO `317abf9467b7a464139ab576f8ae00e9c59c4da1ad54ae31d4c73d6a9b4a0135`.
- Parent completion `3488a998b8d01cf279cddb20c9f6e22f04afd1ff3fdaf2d98260909c2d395883`.
- Exact master admission `983c62c4aaec8969ecc02ee774a55aa1fe2b95edf74d884dbae6f69e28b5a87a`.
- LP completion `ab79c29693e901d5b61c50f0083c21b3cde702391f61e877b42b54a9b44022f4`.

`PROCESS_CLOSURE.json` records the exact invocation/session and observed owned processes. Windows used a venv launcher plus actual Python child for the master. The brief normal LP worker completed before its descendant chain was sampled; no descendant PID is invented. Its parent worker returned0 without timeout, and all observed owned PIDs were absent at the final check. No external termination occurred. Raw startup/solver logs remain private; public receipts contain their paths/sizes/hashes only. The frozen direct-child timeout implementation was not exercised by this successful normal process return and is not evidence of tested Windows descendant termination.

`producer_output_inventory.csv` binds this readout, process receipt and all23 producer run files. It excludes private raw logs and itself. No further mutation of these producer files is planned before independent review.
