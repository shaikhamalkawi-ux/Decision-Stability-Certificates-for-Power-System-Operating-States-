# Independent pre-solve review: uncapped January witnesses

Review date: 2026-09-26 UTC. No mathematical or implementation blocker was
identified in the reviewed source and protocol. This is a prospective source
review, supplemented by direct read-only inspection of the two source
archives; it is not an optimization result or an independent replay of a
future returned witness. No optimizer was called by this reviewer.

Reviewed files and SHA-256 values:

- `src/research8h_seasonal_uncapped.py`:
  `59b8f8f0d5446ef77e891df2a93bace8a664b5a846bd812cd2af266f2c41dc88`
- `docs/research8h/SEASONAL_UNCAPPED_PROTOCOL.md`:
  `90434553f65c8f97bf5b59f68966c97547f18b6f1b92ec317e30b0cbdef9479c`

The review also read `research8h_seasonal_reference.physical_check`, the
January source metadata and prior freeze, and the already-reviewed U-only
projection audit. No frozen runner, protocol, model, or result was edited.

## Model change and independent source checks

The preparation code selects exactly one row labelled fossil_energy_cap,
deletes that row from the matrix and both row-bound arrays, and copies all
column bounds unchanged. It rejects the presence of target_mean rows. The
same native inputs, unit identities, chronology, network, and initial/terminal
semantics are retained. The two fixed cases are seeds 26093100 and 26093101.

Direct ZIP/NPY inspection through Node, without importing either runner,
NumPy, or HiGHS, verified for both archived source cases:

- Matrix dimensions are 34,681 rows by 23,016 columns; every matrix coefficient
  is finite.
- All 23,016 column lower and upper bounds are finite and ordered.
- The unique fossil cap is row 24,264, with lower bound minus infinity and
  upper bound exactly 23,195 MWh.
- Its support consists of exactly 3,864 entries: each hour of each of the 23
  listed fossil units, all with coefficient exactly one.
- Row metadata contain no named-unit target_mean row.

The new objective has the same 3,864 fossil-hour coordinates with coefficient
one and zero elsewhere. Native Coal/Oil/NG classification is checked against
the archived unit list, with 121_NUCLEAR_1 excluded. Hard-coded dimensions
168/41/24/24 agree with both actual source metadata. These details establish
fossil MWh under one-hour intervals, not emissions or economic operating cost.
Finite dispatch bounds prevent an unbounded energy objective whenever the
model is feasible.

The auxiliary-integrality change uses the previously reviewed exact
projection argument. For binary U, canonical Y/Z preserve the physical
(P,U,theta) point. Since this objective involves P only, the recovery also
preserves its value. This statement concerns the strict model; it is not
being used to infer equivalence of arbitrary widened formulations. A
recovered point is checked directly against the full-binary widened model.

## Freeze, computational budget, and recovery

Preparation and execution are separate modes. Preparation checks the source
transfer manifest, runs the sparse projection audit, saves both new models
and objectives, preserves the original full-integrality masks, and freezes
source/protocol/input hashes. Execution validates the entire manifest before
constructing a solver. An exclusive execution marker prevents accidental
reruns. Successful preparation and matching frozen hashes remain required
before the root's authorized execution; the first attempt to inspect new
prepared artifacts during this review found them not yet present, so this
review does not misrepresent them as independently verified at that point.

The prescribed budget is one 600-second HiGHS call for each of the two cases,
in fixed order, with one thread, seed zero, presolve on, relative gap 1e-8,
and no warm start or retry. Actual runtime and solver options are saved.
Concurrency and soft-limit overshoot preclude treating these timings as a
controlled performance experiment.

The runner archives the raw vector and residuals whenever a vector is
returned. Recovery requires finite coordinates and U within 1e-5 of zero or
one. It rounds U, creates exact canonical binary Y/Z with initial zeros, and
leaves P and theta unchanged. Both raw and recovered matrix checks are
required for numerical admission. A timeout alone remains UNKNOWN; a
time-limited incumbent is not presumed optimal.

The independent native checker has no cap parameter and adds no substitute
large cap. It checks dispatch bounds, fixed hydro, aggregate and nodal
balance, both commitment-coupling calculations, transition identities,
canonical starts/stops, observed residence runs, native on/on ramps, branch
ratings, angles, and slack. It reconstructs the network from native row
indices and requires exact agreement of its native nodal-load array with the
archived one. This is the appropriate no-cap checker.

## Exact point membership and objective bounds

`exact_point_check` interprets every saved binary64 matrix, bound, and vector
coefficient as its exact rational value. It forms every sparse row dot
product with Fraction arithmetic, compares all finite column/row bounds,
and checks every coordinate in the original U/Y/Z integrality mask is
exactly zero or one. It records both strict membership and membership after
outward expansion of every finite bound by
tau = Fraction.from_float(1e-5). This is the same precisely stated numerical
convention used by the robust capped certificates.

The exact fossil-energy sum uses the authoritative recovered NPZ dispatch;
CSV exports are not substituted for it. A passing expanded-point audit
provides a rigorous finite feasible upper bound for the expanded full-binary
uncapped model. It provides such an upper bound for the strict model only
if strict membership also passes. Exact summation of energy alone would not
establish either bound without exact point membership.

Admission requires the raw matrix, recovered matrix, native physical, and
exact expanded-model checks. A tolerance-only candidate is explicitly
distinguished from a verified expanded-model witness. Solver objective,
solver-reported numerical lower bound, and gap are recorded separately and
do not become exact certificates. A solver infeasibility status is numerical
evidence; it cannot override a mathematically verified point, and any apparent
status/point discrepancy must remain visible in reporting.

## Scientific interpretation and remaining verification

A robust capped negative plus a verified uncapped witness can distinguish a
finite energy requirement from the earlier possibility that the entire
uncapped chronology was impossible. Both statements must refer to matching
coefficient, integrality, and bound-expansion conventions. In particular,
expanding the former cap upper bound also changes it from B to B + tau;
an exact converted energy lower bound should state which model it bounds.
An expanded witness alone does not prove strict uncapped feasibility.

Let [L,U] be independently justified bounds for the twin's minimum fossil
energy in a stated common model, and let E0 be the energy of a verified
original-order incumbent. Then [L-E0,U-E0] bounds the twin's optimum relative
to that particular incumbent. It is not automatically an interval for the
difference of both orders' true optima. Nevertheless L-E0 is a valid lower
bound on that optimal ordering penalty because the original optimum is at
most E0. An upper bound on the difference of optima needs a lower bound on
the original optimum as well. Neither incumbent should be described as an
optimum without the corresponding evidence.

The next required audit is independent replay of the prepared single-row
deletion, objective, source hashes, and any returned recovered witness. There
is no result from this arm in this review, no new formulation claim, and no
inference of April/October replication from the January pair.

## Completed prepared-artifact preflight

Preparation subsequently completed at 2026-09-26T21:36:19.496697+00:00.
Before an execution_started.json marker existed, this reviewer independently
verified all 55 files in the prepared manifest against both SHA-256 and file
length. The manifest hash is
`59ad33b7ef6c6854d9acb3bcca837a521b10dd695711124e204c5c6f4e3a5352`.
The frozen runner and protocol hashes match those reviewed above.

A direct Node ZIP/NPY comparison, independent of the Python preparation
functions, passed for each prepared case:

- CSR data, column indices, and row pointers exactly equal the original
  matrix with only row 24,264 deleted; the new row count is 34,680.
- Row bounds have exactly the matching deletion; all column bounds are
  unchanged.
- Every native input NPY payload is copied exactly.
- The objective is exactly one on the 3,864 fossil-hour coordinates and zero
  everywhere else.
- The original integrality mask is preserved exactly; the new mask is one
  on U coordinates 6,888 through 10,919 and zero elsewhere.
- Both saved structural audits pass, with 4,008 rows for each of transition,
  exclusive transition, minimum up, and minimum down, reducing declared
  integer columns from 12,096 to 4,032.

Final preflight verdict: no blocker. This completed independent prepared
review predates execution; future witness and post-run hash replay remain
separate obligations.
