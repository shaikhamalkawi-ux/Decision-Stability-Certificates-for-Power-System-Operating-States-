# Fixed reference commitment under the aggregate service budget

Prospective protocol, 2026-09-26. This arm is separate from the four frozen
unrestricted binary-network MIP calls. Their settings, timeouts and results
remain unchanged. The LP service-budget arm admitted all four continuous
relaxations; the first two unrestricted MIP calls timed out without incumbents
before this arm was defined. No fixed-reference-dispatch result has been seen.

For exactly seeds 26092600--26092603, reuse the already frozen full DC-network
service matrices and the unchanged 180555.9189139999 MWh fossil-energy cap.
Fix all U/Y/Z variables to the original verified July chronological reference
schedule, without permuting that schedule. Reoptimize only dispatch and angles
against each jointly permuted demand/availability package. There are no named
generator mean constraints. Min-up/down constraints and boundary conventions
are inherited unchanged. This is a restriction of each service feasibility
model, never a relaxation.

Freeze all four matrices, fixed bounds, source/protocol/input hashes before
the first solve. Use one continuous HiGHS feasibility LP per case, zero
objective, presolve on, one thread, random seed zero, configured 30 seconds.
No retries, schedule changes, cap changes or alternative seeds are part of
this arm. Record actual elapsed time even if it exceeds the configured limit.

A returned point is a binary-network admission only if the archived matrix
and the independent native physical checker both pass at 1e-5 tolerance,
including the rounded binary states, residence times, nodal balances, line
limits, native on/on ramps and aggregate fossil cap. Archive full numerical
witnesses. LP infeasibility excludes only this fixed schedule; it says nothing
about the unrestricted binary problem. Any timeout without a verified witness
is UNKNOWN. Do not describe either negative outcome as operational rejection.

The point of the arm is to test whether the original negative named-unit-mean
examples can instead operate under the same aggregate service budget through
redispatch alone, without changing the valid chronological commitments. It is
a feasibility sensitivity check, not a new optimization algorithm. Any change
in generator means is descriptive and is not a minimum repair calculation.
