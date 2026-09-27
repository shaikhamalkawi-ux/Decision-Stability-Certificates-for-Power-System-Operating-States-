# Design-only proposal: the next two January weeks

No model has been generated and no optimizer has been run for this proposal.
It implements the root's fixed choice of the lowest unused January weeks:
native zero-based hourly rows 168:336 and 336:504, using Python half-open
notation. These are January 8--14 and January 15--21, 2020. They remain two
related windows in the same RTS Area 1 system and season, not independent
networks, field trials or a learned method's generalization test.

Read-only calendar inspection confirms that Load, PV, Wind, Hydro and RTPV
DAY_AHEAD files have identical Year/Month/Day/Period fields through the first
504 rows. Row 168 is 2020-01-08 Period 1, row 335 is January 14 Period 24,
row 336 is January 15 Period 1, and row 503 is January 21 Period 24. No dispatch
optimization, reference-quality screening or target outcome was used to choose
these windows. This inspection read raw calendars only; it assembled no model.

## Native input adaptation

The existing v8r1_rts_seasonal.inputs helper cannot be used unchanged: it is
bound to each month's already processed first-week dispatch and hourly summary.
A new narrow input adapter should accept these two explicit native row arrays.
For each row, read the unchanged model.avail_at(row), the Area 1 load value,
and model.rtpv_at(row); form net demand as area load minus total fixed RTPV.
Validate the expected hourly calendar and all five time-series calendars at
every selected row, finite arrays, identical native roster, fixed hydro and
thermal nameplate bounds. Do not call the native solve_hour function: its
cost/shedding choices are unrelated to this experiment.

Pass these arrays and actual native row indices into the unchanged
research8h_service_network_mip.build assembly. Its nodal reconstruction already
uses the supplied native rows. Verify the 41-generator/24-thermal/24-bus/38-line
roster, 23-unit fossil objective/cap selection, all matrix/bound/label and native
array hashes, and native ramp redundancy. Keep the same mature free initial
status, initial Y/Z zero, truncated terminal dwell, angle/line bounds and no
mean targets or shedding. Do not carry a prior week's terminal state into a
new reference; that would change the declared boundary model.

## Fixed draws and controls

Proposed seed assignments are fixed now and were absent from the existing
source/protocol/result JSON ledger when checked:

| Native rows | Ordinary seeds | Hour/U-class control |
|---|---|---|
| 168:336 | 26093210, 26093211 | 26100210 |
| 336:504 | 26093220, 26093221 | 26100220 |

Use exactly the hour-of-day draw algorithm already declared in
HOUR_OF_DAY_PROTOCOL.md: for h=0,...,23, independently permute the three
positions [48+h,72+h,96+h] with one PCG64 generator per seed; fixed first/last
48 hours. Controls group by (hour modulo 24, full exact 24-bit U signature),
visit keys lexicographically and positions increasingly, and retain every
singleton/identity/duplicate draw. Recompute canonical Y/Z. Save generator
states, group inventories, permutations, inverse maps and changed adjacency.
This preserves hour of day, not within-day chronology or weather plausibility.

Keep both intended weeks, all four ordinary identifiers and both controls in
the ledger regardless of reference eligibility or outcomes. No substitutions,
additional draws, alternative weeks or April/October retries. Root should
freeze this design/seed choice before receiving the earlier same-week
hour-of-day outcomes; no rule should be adapted to those outcomes afterward.

## Two prospective stages

First freeze both uncapped reference models before either reference solve.
Use exactly one U-only fossil-minimizing MIP600 per week, thread 1, seed 0,
presolve on and relative gap 1e-8, no warm starts/retries. Keep the original
U/Y/Z mask for canonical recovery checks. Accept only a recovered point with
native no-cap checks and exact expanded full-binary membership; report strict
membership separately. A timeout with no accepted point leaves that week
NO_REFERENCE without replacement. Record numerical bounds/gaps separately;
an incumbent is not a proven optimum.

Then, for every eligible week, fix B = ceil(101 E / 100), using exact rational
fossil energy of its accepted canonical reference. Generate the fixed identity,
two ordinary orders and class control. Rebuild the identity and verify that
deleting only the cap row recovers its reference matrix/bounds. Every identity
and class control must pass complete native and exact expanded binary checks.
Ordinary transferred points must pass static native and exact expanded checks
after removing only minimum-up/down rows; their full dwell failures are not
negative labels. Freeze all eligible weeks' target models and all controls
before the first target solve, with an independent archive review and GO.

Use the existing frozen hour-of-day routing: constructive exact full positives
need no optimization; all remaining continuous LP30 calls occur before any
conditional U-only MIP300 calls. One call per eligible route, same options as
the current hour-of-day protocol, no retries. LP negatives require exact
outward-robust Farkas verification. Binary positives require canonical recovery,
original full-mask exact membership and native checks. Continuous feasibility,
numerical MIP infeasibility and timeouts do not become exact binary labels.

All exact statements use the existing binary64 model with every finite bound
expanded outward by Fraction.from_float(1e-5). No claim of strict nominal
feasibility follows from numerical tolerances. Include source/model/bound/
manifest hashes in every certificate/point audit, followed by independent
post-run replay before publication.

## Budget and ownership proposal

Maximum configured solver time is 2*600 + 4*30 + 4*300 = 2,520 seconds (42 min),
with controls requiring no optimization. A practical upper planning allowance
is 90 minutes including native preparation, two independent preflight gates,
exact checking and final review; this is not a guarantee under shared-host
delays. Suggested execution allocations are 1,800 seconds for reference
execution/checking with a 605-second call-start guard, then 2,100 seconds for
target execution/checking with a 305-second MIP guard (and a 35-second LP guard).
Retain soft-limit overrun and NOT_RUN_BUDGET/NO_REFERENCE separately. Root
should impose its overall cutoff, including no new solver call after 04:00 UTC,
and maintain at most two simultaneous long MIP threads across its research arms.

Proposed implementation ownership, if root approves: one new generic adapter/
runner at src/research8h_fresh_january_weeks.py, one frozen implementation
protocol, and results/research8h/fresh_january_weeks with separate reference and
target manifests/execution markers. Existing sources remain read-only. Reuse
the dynamic-budget native checker and exact point/ray helpers. Do not reuse
research8h_day_blocks.solve_mip unchanged: it hardcodes the old 23,195 MWh cap.
The seasonal-cap-continuation MIP checker instead reads each model's budget.

This proposal supplies no execution authority. Root's review, explicit source/
protocol ownership, independent prepared-model PASS and GO are still required.
Report fresh-week outcomes separately from earlier January and seasonal arms;
neither a positive nor a negative should retroactively repair an earlier gate.
