# Independent exact energy-floor review — PASS

I read the complete diagnostic source and prospective protocol and performed one independent original-row replay without importing the producer or using an optimizer. Source reviewed: `dfb8069926c180edd266a5b8bc92a0154737627ab437a83d7f6fa80eb8bb53ee`; protocol: `b743544e02be563c750abf3f73ebcca13ee7c10b8cb9a3fea7d91774997e61ec`. The independent replay took 2.4992963999975473 seconds.

For each unchanged original world, the replay verified all 6,888 generation intervals against the boxes and all 8,064 eligible singleton-generation rows, the complete 12,096-bit fixed-state mapping, all 168 aggregate rows and the original 3,864-term fossil cap. Every archived lower/upper source actually attains its reported interval with the correct signed division and outward endpoint tolerance. Each hourly lower bound is the maximum of two valid necessary bounds; summing them is therefore valid even when different hours select different derivations. The tolerance is exactly `Fraction.from_float(1e-5)`.

Both worlds have the exact necessary fossil-electrical energy floor

`1741859908587528011403599 / 73786976294838206464 MWh`,

approximately 23,606.6037132 MWh. The original expanded cap is approximately 23,195.00001 MWh. Their strictly positive exact difference is

`242967941527088396181895 / 590295810358705651712 MWh`,

approximately 411.6037032 MWh. This rejects the one prescribed union schedule in each original expanded model and hence rejects that fixed-schedule common candidate. It does not reject any alternative commitment or either unrestricted individual problem. The unrestricted common question remains **UNKNOWN**. No empty generation interval or disjoint hourly aggregate interval was found; the retained rejection is the weekly cap implication. Unused network/multivariable rows need not be feasible for this necessary-bound argument.

All 15 reviewed input bindings and all four producer outputs were unchanged before and after replay. The review source and JSON contain the exact result and bindings. No new schedule, matrix, solver call or published-model modification occurred. Root's later cancellation of the unnecessary fixed-candidate LP is an administrative consequence of this result; the prospective protocol and earlier zero-call implementation failure remain preserved.
