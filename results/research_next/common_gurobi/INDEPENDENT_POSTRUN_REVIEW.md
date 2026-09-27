# Independent closed Gurobi failure/readback review

PASS, 27 September 2026, completed 09:44:10 UTC. The completed corrected audit took 3.132832 seconds. No optimizer or producer import, no old joint reassembly, and no access to raw private startup/solver logs.

All 86 frozen input bindings and all 42 producer-inventory entries were rehashed unchanged. The independent prepared review is inherited by its trusted hash. The NEW saved Gurobi API readback was checked fully against the pinned original CSR and reviewed endpoint-splitting map: all 82,130 rows, 316,712 coefficient uses, finite right-hand sides and senses match; all 33,936 column boxes and zero objective coefficients match; all 12,096 original binary declarations remain intact. This establishes faithful archived backend translation. It establishes neither feasibility nor infeasibility.

The original failure ledger and separate closure agree: one optimize invocation attempted, zero returned, 0.002757799986284226 seconds, error10010. Its meaning was independently confirmed by reading only the installed public error-constant source: SIZE_LIMIT_EXCEEDED, exceeded licensed model size limit. Both pre-call guards were satisfied. No numerical solver status, incumbent, accepted point or exact negative certificate exists. The unrestricted common-commitment question remains UNKNOWN; scientific search was not established. The 10.552318-second execution-marker-to-error timestamp span is not claimed as a complete perf-counter phase. No repeat, fallback or license change occurred in this producer arm.

Exactly the eight expected public run files exist, with no raw/candidate solution or returned-solver-result file. The private-log receipt was checked only as public metadata; private log contents were neither read nor copied.

## Reviewer development record

The initial reviewer stopped because the pinned stdlib kernel does not support the saved row-sense NPY dtype |S1. Its source and failure receipt are retained as INDEPENDENT_POSTRUN_REVIEW.initial.py and .initial_failure.json. Only the reviewer was corrected: an explicit NPY-v1, shape82,130, one-byte-sense decoder accepts the three permitted signs and rejects other schema/content; every other array still uses the pinned kernel. The first corrected launch was interrupted by the Node tool's default30-second execution wrapper; after confirming no report and no live reviewer process, its receipt was retained as INDEPENDENT_POSTRUN_REVIEW.infrastructure_interruption.json. The SAME corrected source was then run through the session-capable shell and completed PASS, session59191 exit0. These are reviewer-only failed/interrupted attempts, not additional optimization or changed producer evidence.

Corrected reviewer source SHA256: 077054ff4a0808c930d21ff9e0b0c2099d660d97b88c540c91d46e374eb2f18b.
Report SHA256: 63c5ad47a29733d0ba8deb19dc63ad4650524dea037cd9a487adc81642685dff.
Producer inventory SHA256: a604995726f1ca5ae4928bdc65c60e51034fae52add32fca98018876cd4dc767.
Failure closure SHA256: 22401b45326159af3aec4821f9b970ec90ad65db326be35c5661b62108443209.

No scientific positive or negative claim is added. The successful row transport remains useful even though the available license blocked this call.
