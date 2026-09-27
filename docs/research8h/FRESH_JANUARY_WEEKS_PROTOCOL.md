# Frozen fresh-January-week experiment

Implement the approved FRESH_JANUARY_WEEKS_DESIGN_PROPOSAL.md. Root approved the
fixed windows and seeds at 23:49 UTC on September 26, 2026, before root had
received or inspected optimizer outcomes from the earlier same-week
hour-of-day arm. That arm's completion was subsequently reported as 23:48:22
UTC; this is not a claim that its outcomes did not yet exist. No
rule is adapted to that arm's eventual outcomes. This experiment uses the next
two chronological January windows in the same RTS Area 1 system: native
zero-based rows 168:336 (January 8--14) and 336:504 (January 15--21), 2020.
Neither window may be replaced. This is within-season fresh-window evidence,
not independent-network, learned-method, weather-realism or field validation.

Use a narrow native-row adapter. At each selected row validate identical
Year/Month/Day/Period fields in all five native Load/PV/Wind/Hydro/RTPV tables,
the expected 168 consecutive hourly timestamps, finite arrays, generator order,
fixed hydro and native thermal bounds. Call avail_at and rtpv_at, and calculate
net demand as Area 1 load minus total RTPV. Never call solve_hour, use processed
first-week dispatch as a new-week reference, or import its economic/shedding
objective. Feed actual native row numbers into the unchanged full native DC
assembler and independently reproduce nodal demand from source load shares.

Keep 41 generators, 24 thermal units, 24 buses and 38 lines; all native output,
renewable/hydro, DC nodal/line/angle and minimum-up/down constraints; no mean,
shedding, storage or slack rows. The native on/on ramp inequalities are
analytically redundant here and checked directly on witnesses. Use mature free
initial U, initial Y/Z zero, residence clipped at hour 167 and no cyclic or
post-horizon constraints. Do not carry a previous week's terminal status into
the next week's initial history. Fossil means the 23 native Coal/Oil/NG units;
121_NUCLEAR_1 is excluded from the objective and cap.

There are four separate modes and gates: prepare-references, run-references,
prepare-targets, run-targets. Prepare both uncapped reference models and freeze
all source/protocol/native data, objective, matrix/bounds, original full-binary
mask and audited U-only mask before either reference solve. Require root code
review and an independent prepared-archive PASS plus explicit GO before
run-references. Exclusive execution markers prevent accidental repeats.

Reference order is week 2 then week 3. Use one uncapped fossil-MWh-minimizing
U-only MIP600 per week, threads 1, seed 0, presolve on, gap 1e-8; no warm start,
retry or tuning. The reference execution/check phase is 1,800 seconds starting
on run-references entry before validation/loading. Do not start a call unless
both phase time remaining and time until 04:00 UTC on September 27, 2026 are
at least 605 seconds; equivalently use the minimum of those two remainders.
Unstarted calls retain NOT_RUN_BUDGET or NOT_RUN_CUTOFF. At most two reference
solves are configured. Preserve numerical objective, bound, gap, status and
actual soft-limit overrun without claiming incumbent optimality.

Save every returned raw point. Recover only finite U within 1e-5 of zero/one:
round U, recompute exact binary Y/Z from adjacent changes with initial zero,
and leave P/theta unchanged. An accepted reference requires raw/recovered
matrix checks, the original full-binary exact expanded check and the native
no-cap physical checker. The standard U-only projection is audited against
every actual auxiliary row; original U/Y/Z integrality remains the acceptance
mask. Numerical-only or failed points are not references. Retain failures.

Wait until both reference records and final input hashes close before target
preparation. Eligibility is exactly accepted references from this arm, with no
replacement incumbent or week. Every unaccepted week retains NO_REFERENCE for
both ordinary cases and its class control. For an eligible reference let E be
the exact rational sum of stored binary64 fossil dispatch. Set B=ceil(101 E/100)
whole MWh, using exact arithmetic. The same B is used for that week's identity,
two ordinary cases and control, with zero target objective. No cap adjustment
or unit-mean target is allowed. Record reference energy/status/gap/headroom.

Fixed identifiers are week 2 ordinary 26093210 and 26093211, control 26100210;
week 3 ordinary 26093220 and 26093221, control 26100220. For each ordinary seed
use one numpy Generator(PCG64(seed)); for h=0,...,23, permute [48+h,72+h,96+h]
once and assign the source positions to those same destination positions.
For each control, group interior hours by (hour modulo 24, exact complete
24-bit reference U), visit keys lexicographically and positions increasingly,
calling permutation once even for singletons. Treat +0.0 and -0.0 as the same
exact binary status for U-control invariance, while retaining bitwise payload
roundtrip checks and reporting bitwise U equality separately. Retain duplicate/identity draws.
Both 48-hour edge blocks stay fixed. Save RNG states, group inventories and
maps. Jointly permute every native hourly package and reference P/U/theta;
recompute Y/Z. Verify inverse/bitwise package roundtrips, source rows, hour of
day, native nodal reproduction and exact energy preservation. Report source
continuity breaks (successive source indices do not differ by +1) separately
from literal changes of a destination's ordered adjacent source-index pair.

Rebuild each capped identity and check that removing only its cap row recovers
the uncapped reference matrix/bounds and original mask. Verify the cap's exact
23*168 dispatch coordinates and unit coefficients; do not hardcode 23195 or
reuse a helper with that cap literal. Every identity/control must pass full
native and exact expanded original-binary checks. Every ordinary transferred
point must pass static native and exact checks after deleting only minimum-up
and minimum-down rows. Record full constructive checks separately; a failed
copied schedule is not infeasibility. A failed required control stops target
preparation with evidence retained.

Freeze both weeks' eligible target models and all controls before any target
solve. Root review, independent prepared PASS and a separate explicit target
GO are required; reference GO does not authorize targets. All four intended
ordinary cases and both controls stay in the design ledger including missing
references. Target order is week 2 seeds then week 3 seeds. Exact constructive
full positives need no optimizer. For every other eligible target run one
LP30, simplex/presolve off, thread 1, seed 0, zero objective, provided the minimum
of phase and UTC-cutoff time remaining is at least 35 seconds. All such LPs precede MIPs.
No retries or ray-recovery solves. A negative requires exact Farkas separation
remaining positive after the same uniform finite-bound expansion; bind every
ray to model, bounds, labels and manifest, retaining raw/sign-projected checks.

After the LP phase, each unresolved case with a completed LP may receive one
U-only MIP300, presolve on, thread 1, seed 0, gap 1e-8, no warm start or retry.
Require the minimum of phase and UTC-cutoff time remaining to be at least
305 seconds. Its
recovery/native/exact acceptance matches the reference rule but uses the
actual case cap. The target execution/check phase is 2,100 seconds from entry
to run-targets before validation/loading. At most four LP30 and four MIP300
calls are configured. Guard-skipped cases remain UNKNOWN with explicit reasons.
No new optimizer call in this arm may begin at/after the cutoff.

Every exact statement concerns archived binary64 coefficients and expansion
of every finite row/column bound outward by Fraction.from_float(1e-5), with
original U/Y/Z still exact binary. Strict nominal membership is reported
separately. Continuous admission, numerical MIP infeasibility and timeouts
without accepted points remain UNKNOWN for exact binary classification. Never
turn a numerical bound or an incumbent into exact optimality. Exact point and
ray checking remains separate from native numerical checks.

The maximum configured total is 2,520 solver seconds: two references600 plus
four LP30 plus four MIP300. Controls use no optimization. Run at most one
optimizer from this arm; root coordinates a maximum of two long MIP threads.
Record phase allocation, actual solver/check times and soft-limit overruns;
start guards are not hard wall limits. All earlier reference, cap, gate and
UNKNOWN records remain unchanged. Report both new weeks separately and any
augmented context explicitly. No additional uncapped follow-up, precision LP,
cap sweep or dataset is authorized by this protocol. Independent post-run
replay is required before publication.
