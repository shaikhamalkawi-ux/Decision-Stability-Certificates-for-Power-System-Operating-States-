# Prospective April/October cap continuation

This is a later continuation using the separately frozen 600-second U-only
reference arm. Preserve the original January-only seasonal-transfer results,
its failed two-week gate, and its April/October NO_REFERENCE records. This arm
does not revise those historical outcomes. It asks whether the same synthetic
order-effect experiment replicates with the newly generated references.

Consider only April and October. Eligibility comes exclusively from the final
results of results/research8h/seasonal_reference_continuation, whose manifest
is cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b.
Wait until all three reference-continuation calls and final input checks finish
before freezing eligibility or target models. Require the selected reference
to have an accepted exact expanded-model witness, and recheck its canonical
recovered vector against its original full-binary matrix and native inputs.
An unaccepted month remains NO_REFERENCE in this arm; do not replace it, use
July, rerun references, or select an alternative incumbent. Reference energies
need not be optimal. Numerical solver bounds are not exact optimum bounds.

Use exactly the previously declared identifiers: April ordinary seeds
26093400 and 26093401 with class control 26100400; October ordinary seeds
26094000 and 26094001 with class control 26101000. Process months and ordinary
seeds in that order. For each eligible month, compute E as the exact rational
sum of canonical binary64 dispatch over the native 23 Coal/Oil/NG units,
excluding 121_NUCLEAR_1. Set the common cap B = ceil(101 E / 100) whole MWh.
Record E, B, headroom, source vector hash and original reference status/gap.
No mean targets, alternative cap, emissions coefficients or adaptive adjustment.

Use numpy Generator(PCG64(seed)), one draw per identifier. Ordinary orders
jointly permute source positions 48 through 119, leaving both 48-hour edges
fixed. Permute all hourly source packages, reference dispatch, exact binary
U and angles together; reconstruct Y/Z from the resulting U. For each class
control, traverse interior exact 24-bit U classes in first-occurrence order
and permute positions within each class using its one generator. Preserve
identity/duplicate draws. Check bijections, inverse roundtrips, complete native
nodal arrays/source rows, fixed edges and exact fossil-energy preservation.

Retain the same full 24-bus/38-branch/41-generator DC model, 24 thermal units,
availability, fixed hydro, rooftop PV, line/angle bounds, mature free initial
statuses, Y/Z initially zero, native residence through hour 167, no cyclic or
post-horizon closure, and the analytically redundant native on/on ramps.
There are zero individual means and one aggregate fossil-energy cap; the
target objective is zero. No shedding, storage, slack or network simplification.
For each identity, removing only its cap row must exactly recover the
reference's original physical matrix/bounds and original integer mask.

Before target execution, every identity and class control must pass the full
native capped checker, original full-binary matrix check, and exact expanded
point check. All original U/Y/Z coordinates must be exact zero or one. Each
ordinary permuted reference must pass hourly static network/cap checks,
including an exact point check after removing only minimum-up/down rows.
Record its full dwell check separately: a failed constructive schedule is
never an infeasibility label. Direct on/on ramps are still checked. A failed
identity, class or static audit stops preparation with records retained.

The exact convention is the same for both signs: archived binary64 values are
interpreted as rational numbers, and every finite row/column bound is expanded
uniformly outward by tau = Fraction.from_float(1e-5). Save strict membership
separately. A positive that passes only expanded membership is not an exact
unwidened physical-model witness. Static and complete binary checks have
different scopes and must be reported separately.

Freeze source/protocol, eligibility, both months' available cases, source
inputs, references, cap records, all orders/models/bounds/metadata, original
and U-only integrality, exact controls and hashes before any target solve.
Use separate prepare-only and run-prepared modes. Execution revalidates every
hash and an exclusive marker prevents an accidental repeat. Wait for root's
independent preflight and explicit GO; this protocol alone does not start a
solver. At most one optimizer in this arm is active; root coordinates other
arms and the limit of two simultaneous long MIPs.

Stage A runs one continuous LP for every eligible ordinary case, including any
already constructive positive: simplex, presolve off, one thread, seed zero,
30 seconds, zero objective. Finish all Stage A calls before Stage B. Archive
every returned point, numerical check, raw ray and candidate transformations.
For each returned infeasibility ray, try both signs and each raw/sign-admissible
projection. Recompute every full separation using exact Fraction arithmetic;
never assume omitted entries are negligible. A negative requires positive
separation even after uniform tau expansion of all finite bounds. Bind each
certificate to its exact archived matrix, bounds, row metadata, raw ray and
experiment manifest. No ray-recovery solve or retry is allowed. Describe global
cap/reference dependencies and distinguish support size from minimum memory.

Stage B traverses the same fixed order. Skip a case with a robust exact LP
negative or an already verified constructive binary witness. Otherwise run
one 300-second U-only MIP with the audited standard projection, presolve on,
one thread, seed zero and gap 1e-8; keep all original physical rows/bounds and
zero objective. No warm start, fixing, tuning or retry. Both stages are within
a 2,400-second execution-phase allocation, starting on entry to run-prepared
before validation/model loading. Do not start a MIP unless at least 305 seconds
remain. A guard-skipped case stays UNKNOWN. At most four LP30 and four MIP300
calls are possible (1,320 configured solver seconds). Record actual runtimes,
verification time and soft-limit/phase overrun; the start guard is not a hard
wall-clock guarantee. Controls use no optimization.

For a returned MIP candidate, retain raw data/checks. Recover only finite U
within 1e-5 of zero or one: round U, derive exact Y/Z changes with initial zero,
leave P/theta unchanged, and save the separate point. Require original
full-binary matrix/bounds, direct native capped physics (dwell/transitions,
ramps, output/hydro, independent DC reconstruction/line limits, exact fossil
sum) and exact expanded membership for a positive. Strict membership is a
separate flag. Numerical MIP infeasibility is not an exact certificate; a
timeout without a verified point is UNKNOWN. Continuous feasibility alone
does not establish binary feasibility. Retain all failures and statuses.

A robust exact capped rejection paired with the passing static control shows
a chronological obstruction in this encoded, tolerance-expanded DC model.
It does not by itself prove uncapped feasibility, an energy penalty or an
optimality gap. Report outcomes nested by month, not as independent new grids.
Keep all four intended ordinary cases and both controls in the design ledger,
including NO_REFERENCE cases. Report certified ordinary negatives by April
and October separately. Also report augmented evidence across the already
known January success and these later April/October continuation outcomes:
at least two held-out weeks with a verified ordinary negative and passing
controls strengthens cross-week replication, while explicitly including
January's previously known result. Recheck the existing January certificate
artifacts without optimization before recording that context. This is not a
requirement that both new weeks succeed, and the original initial-arm gate
remains NOT_MET because only January was eligible at that time.
This is a later, stronger-reference continuation within one RTS system, not
learned-method transfer, field validation, proof novelty or a retroactive pass
of the earlier replication gate.
