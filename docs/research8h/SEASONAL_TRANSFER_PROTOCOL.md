# Frozen January service-order replication

Implement `SEASONAL_TRANSFER_DESIGN.md` with the eligible reference set already
observed before target generation: January is the sole verified held-out
reference. April and October remain NO_REFERENCE, with all six intended target
and control identifiers retained as not run. Do not substitute weeks or rerun
references. July uses the existing positive network-repair witness only as an
identity implementation check, outside the held-out sample. The design's gate
of replication in at least two held-out weeks cannot be met with this eligible
set; this arm can only supply a single-week case study.

The canonical January dispatch is the binary64 vector in the frozen seasonal
reference `month_01/returned_vector.npz`. Verify its archived source/model hashes,
native inputs, matrix and physical checks first. Let E be its exact rational
fossil-energy sum over units whose native Fuel is Coal, Oil or NG, excluding
121_NUCLEAR_1. Fix B = ceil(101 E / 100) whole MWh using exact arithmetic. Record
reference status, bound, gap, E, B and headroom. This is a reference-based
fossil-energy benchmark, not an external policy or carbon cap, and the reference
need not be optimal. Apply the same formula to the old July witness solely for
its implementation check.

Freeze ordinary January seeds 26093100 and 26093101 and constructive control
26100100. Each uses numpy Generator(PCG64(seed)), one draw, no replacement.
Ordinary twins jointly permute source positions 48..119; both 48-hour edge
blocks are fixed. Preserve complete nodal loads, RTPV, availability, fixed hydro
and reference dispatch/status/angles by the same source mapping. Round the
already verified reference statuses to their exact 24-bit binary vectors before
forming commitment classes and checks; retain raw reference data as provenance.
For the control, traverse interior commitment classes in first-occurrence
order, permute source indices within each class with its single generator, and
recompute Y/Z from the resulting U sequence. No old transition indicator is
permuted. Retain identity or duplicate draws.

Before solving, verify identity and control binary-network witnesses, and verify
each ordinary permuted reference as a static hourly network witness under the
same cap. The latter may fail dwell; that is recorded but is never a negative
label. Check inverse permutations, source rows, native nodal input reproduction,
the unchanged package multiset, exact energy preservation, native fuel roster,
integer columns, objective and absence of individual mean rows. A failed
identity/static/control audit stops target execution with records retained.

Use the full native 24-bus/38-branch/41-generator DC model with 24 thermal
U/Y/Z structures. It has free mature initial status, zero initial Y/Z, truncated
within-horizon dwell, no cyclic closure, native availability/fixed hydro,
angles in [-pi,pi], the source slack and branch limits. Verify native on/on ramp
redundancy from hourly ramp versus output range and directly check witness ramps.
No named-unit mean, load shedding, storage or target/network slack is introduced.
The zero objective expresses feasibility only.

Freeze source, protocol, native/reference inputs, all generated orders, matrices,
bounds, integrality, metadata and control checks before the first target solve.
Run Stage A for both ordinary twins in seed order: continuous full-network LP,
simplex, presolve off, one thread, seed zero, 30 seconds. Use the existing exact
binary64 Farkas verifier, checking both ray orientations and any explicitly
sign-projected candidate from the one returned ray. Every candidate separation
is recomputed exactly. A negative requires positive separation after outward
1e-5 relaxation of every finite row and column bound. Bind the certificate to
its archived model and metadata. No ray-recovery optimization is allowed.

After both LPs, run Stage B in the same order for each case without a robust
exact negative: same matrix and bounds with all archived U/Y/Z integrality
restored, zero objective, presolve on, one thread, seed zero, gap 1e-8 and one
120-second call. No warm start, fixing, retry, adaptive cap or time extension.
The maximum allocation is two LP30 calls and two MIP120 calls. Record actual
times and any solver overrun. A 20-minute phase limit starts at the first LP;
do not begin a scheduled MIP with less than 125 seconds remaining. An unstarted
case is NOT_RUN_BUDGET, not a negative. Source generation and verification times
are reported separately. No control optimization is needed.

A passing exact outward-robust LP certificate is CERTIFIED_INFEASIBLE for the
encoded binary64 model. A directly verified binary-network witness is
VERIFIED_FEASIBLE. Continuous feasibility alone is LP_FEASIBLE/BINARY_UNKNOWN.
MIP Infeasible without an exact proof is a separate NUMERICAL_MIP_NEGATIVE.
Timeouts or failed checks without a valid witness are UNKNOWN. Preserve all
failed candidates and logs. Positive checks use native dispatch/binary/dwell/
transitions/ramps, independent DC reconstruction, provided-angle rows and exact
fossil sums; no comparison of a schedule's means with themselves is admissible.

A capped rejection plus a passing hourly-network control is evidence of a
chronological obstruction under this cap. It does not establish that the cap
is indispensable or quantify an energy penalty without a separately authorized
uncapped binary witness. This is synthetic order-effect replication within one
RTS system, not learned-method transfer, new-network validation, a Markov-model
refutation, proof novelty, or field evidence.
