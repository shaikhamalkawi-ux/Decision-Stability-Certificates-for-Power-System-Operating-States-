# Prepared execution timing interpretation

This reporting sidecar was added after the preparation freeze and changes no
frozen source, protocol, matrix, bound, objective, native input or case. The
prepared manifest remains
`44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a`.
No optimizer had started when this note was written.

The frozen guard checks remaining phase and UTC time after model construction,
then writes a small `launch_decisions.json` record before returning to the
immediately following `solver.run`. Filesystem latency can age the sampled
decision. The 605/65-second guard includes five seconds beyond the nominal
600/60-second solver limit, but this padding is not a hard latency guarantee.
The root accepted this explicitly as a soft-guard timing nuance after the
complementary source review; no reprepare, source change or extra call was
authorized. It is not a mathematical or model-admission defect.

Actual solver start/end timestamps, per-call elapsed times and all observed
soft-limit, phase or cutoff overruns remain authoritative. The completion
reporting audit must compare each actual start with its saved guard decision
and flag any observed admission/start discrepancy, rather than infer that a
saved decision alone proves an exact wall-clock launch guarantee. All skipped
calls and their zero-call records remain in the ledger. The separate independent
prepared PASS and explicit root execution GO remain necessary.
