# Conditional uncapped follow-up for the seasonal cap continuation

Design recorded before the April/October target outcomes were available to the
root. This is a recommendation requiring separate implementation, source/model
freeze, independent preflight and execution approval. It starts no solver.

The fixed population is all four already frozen targets: April seeds26093400
and26093401, October seeds26094000 and26094001. Keep every case in the ledger.
Do not replace references, targets, weeks, seeds or cap formulas. The question
is whether any proven capped chronology obstruction has a feasible uncapped
operation, and what rigorously bounded fossil-electricity penalty follows.

Route each certified expanded-model full-LP negative to one uncapped energy
minimization MIP, obtained by deleting only its single fossil-energy cap row
and associated bounds. Keep every other coefficient and bound, original
binary mask, native input and horizon convention unchanged. Set the objective
to the same168by23 fossil-dispatch sum. Use the established U-only projection
with canonical exact U/Y/Z recovery and unchanged P/theta. Each routed case
receives exactly one600second call, one thread, seed0, presolve on and gap1e-8,
without warm start, retry or extra time. All routed archives must freeze before
the first such solve. Unrouted capped positives retain their already verified
binary witnesses as uncapped witnesses; capped UNKNOWN cases remain UNKNOWN
and are not quietly dropped from the population.

Acceptance requires the same original full-binary exact expanded-point check
and independently reconstructed native no-cap physical checks. Preserve raw
points and failed recovery. A timeout with a passing witness establishes an
upper bound, not optimality. A timeout without a passing witness gives no
finite upper bound. Report strict nominal membership separately.

For a certified negative that obtains an uncapped binary witness, an optional
separately frozen precision phase runs one60second continuous fossil-minimizing
LP for that target and one for its identity reference, sharing the identity LP
across both targets of a week. Simplex, presolve off, one thread and seed0;
no retries. Reuse a valid existing bound when available, retaining the larger
certified lower bound. Compute exact signed-dual plus finite-box residual
bounds for the uniformly expanded model, with no clipping at zero. The older
cap-ray lower bound and reference witness remain preserved.

If target optimum T and identity optimum I have certified positive enclosures
[L_T,U_T] and [L_I,U_I], report the outward-rounded intervals
[L_T-U_I,U_T-L_I] for T-I and [L_T/U_I-1,U_T/L_I-1] for T/I-1. No finite target
upper bound means no finite energy-penalty interval. Report a nonpositive lower
endpoint as such, rather than describing a proven increase. Fossil MWh means
electrical output, not fuel input, operating cost or emissions.

At most four600second MIPs and six60second LPs can be scheduled by this design.
Shared-host actual times and soft-limit overruns must be retained. Set a fixed
4200second execution-phase allocation before implementation, with no new MIP
started when fewer than605seconds remain and no LP when fewer than65seconds
remain. A skipped call is NOT_RUN_BUDGET. Stop initiating this arm after04:00UTC
on27September2026 to leave time for independent audits and final reporting.

This is a conditional continuation of a fixed sample within the same RTS area,
not independent-network validation. It does not revise the initial failed
replication gate or make safe bounding, Farkas proofs, or UC projection new.
