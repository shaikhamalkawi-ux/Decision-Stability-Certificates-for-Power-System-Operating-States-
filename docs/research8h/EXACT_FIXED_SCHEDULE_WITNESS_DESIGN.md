# Exact original-January fixed-schedule witness: design only

Status: a prospective design for review, not an executed protocol. No new LP, basis reconstruction, exact rank diagnostic, package installation or model repair has been run. The completed branch-path study remains a complete null result: its 1,344 nonseparating candidates do not establish strict feasibility. This proposal changes neither its records nor any existing model.

## Recommended bounded attempt

Use one numerical simplex basis proposal with the original fossil-electricity objective, then reconstruct that basis exactly, hour by hour, and check the resulting rational point against every original archived constraint at zero tolerance. This is substantially less implementation work than introducing an exact LP solver. It can return a rigorously checked positive point; a missing or unsuccessful reconstruction leaves the full unit-commitment question unresolved.

The original January reference is the fixed target. It has no aggregate fossil cap and no individual generator energy targets. Its objective minimizes the hourly dispatch sum of the 23 fossil generators, excluding `121_NUCLEAR_1`. Retain that objective in the numerical proposal. After a complete strict witness is obtained, compute its exact weekly fossil energy and compare it to the already published cap **23195 MWh**. Do not impose a new cap, choose a different cap, or change the objective after seeing the result. An energy at or below 23195 can support a strict positive for the existing capped identity only after an exact model-relation and capped-model point check. An energy above 23195 establishes only the uncapped positive. Neither outcome proves optimality.

## Fixed inputs and structural gates

The authoritative model is `results/research8h/seasonal_reference/month_01/`: its original sparse matrix, bounds, integrality, objective, metadata and native data. Known matrix SHA256 is `43eadfdf239a339757187fa4d52e786d1be7277bb93009d5ded1973523bf1386`; bounds SHA256 is `ea8158050cefbaa9c8bdf5fd387ead50cbd9b803d378fe706a1c2522f5552518`. Preparation must verify these against the existing provenance, then bind every actual input and the new source/protocol in a separate manifest.

Fix all 12,096 original U/Y/Z coordinates to the already canonical binary schedule in `results/research8h/seasonal_transfer/january_identity/constructive_vector.npz`, SHA256 `7c534f8691c761815224ac43773259da5a8e1d3eb2aa892dcb64dc46541672db`. Preparation must verify exact binary values, canonical transitions, identity to the original reference schedule, and the precise relationship of the identity archive to the uncapped original. Signed zero is numerically zero. Do not extract or round a new schedule from a fresh optimizer result.

The original archive has 34,680 rows and 23,016 columns. Its offsets are P=0, U=6888, Y=10920, Z=14952, theta=18984, with hour-major blocks. After substituting the fixed states, each hour has 41 P coordinates and 24 theta coordinates: at most 65 continuous coordinates. The expected continuous row families per hour are one aggregate balance, 48 thermal output inequalities, 24 nodal balances and 38 branch limits. The other 16,032 rows have no continuous coefficient after substitution. These counts and separability are prospective assertions to check from actual sparse rows, not permissions to discard unexpected entries.

For every original row, compute the exact fixed-state contribution and retain its row-ID mapping. Every row with no free coefficient must satisfy its original finite endpoints exactly. A failed constant row prevents a positive and identifies failure of this fixed schedule; it says nothing about other schedules. Verify that every remaining row belongs to exactly one hour, preserving every coefficient and endpoint. No temporal row can be omitted merely because its name suggests that it involves only states. Discover the zero-pinned reference angle from the original bounds; the previously inspected archive pins bus index 12, bus ID 113.

Retain all original dispatch and angle boxes, thermal output bounds, hydro dispatch, renewable availability, aggregate and nodal balances, and branch limits. The original model has no explicit ramp rows. Preserve its documented native on/on ramp convention and independently check it with exact rational dispatch and the existing native rates; do not introduce startup/shutdown ramps or a new physical convention.

## Exact balance replacement; numerical proposal only

Interpret every stored binary64 coefficient and endpoint as its exact rational value. After state substitution, let the aggregate equality be `a0 x = b0` and the 24 nodal equalities be `ai x = bi`. Replace only the aggregate row by

```text
lambda * (a0 - sum_i ai) x = lambda * (b0 - sum_i bi),
```

and retain all 24 nodal equalities unchanged. Here lambda is a positive exact power of two, selected deterministically so that the largest absolute nonzero coefficient of the difference lies in [1,2). Compute this choice with integer/rational comparisons, not a floating threshold. Record the original aggregate row, all nodal row IDs, the full exact difference (including every nonzero entry), its exact right side, and lambda. The inspected old audit found a nonzero difference on 15 angle columns, but preparation must derive and verify this again from the chosen original archive rather than trust the old count. A zero difference with nonzero right side is an exact fixed-system contradiction; a zero difference with zero right side is outside this fixed proposal and must stop preparation for review, not invoke an unplanned replacement.

This replaces 25 equations by 25 equations through an invertible rational row operation. In particular, the original aggregate equation is recovered by dividing the new equation by lambda and adding all retained nodal equations. The small aggregate-minus-nodal coefficient vector is a real constraint of this archived nominal representation; it must not be discarded as roundoff. Do not add an approximate extra row while retaining the original aggregate and describe that different system as equivalent.

The rescaled rational system supplies the authoritative reconstruction equations. Conversion to binary64 for HiGHS supplies only an approximate **basis proposal**. Archive the converted matrix/endpoints and the exact conversion differences. A numerical status, primal point or objective from this proposal is not a proof for either the exact transformed system or the original system. Exact reconstruction and original-row acceptance below are essential.

## One basis proposal, then deterministic hourly reconstruction

The mathematically separable hourly problem can be passed to HiGHS as one block-diagonal weekly LP. This uses one optimizer call rather than 168 calls while retaining one fossil objective equal to the sum of the hourly fossil objectives. Proposed fixed options are simplex, presolve off, one thread, random seed 0, a 60-second soft time limit and no supplied warm start. Freeze the precise simplex strategy, tolerances, conversion policy and all options before execution; a concrete recommendation is serial dual simplex with the installed default feasibility tolerances. No second objective, altered scaling, alternate basis or solver retry belongs to this attempt.

Archive the complete returned column and row basis statuses, numerical point, log, status, iterations, options and actual time, even if no useful basis is returned. A valid returned basis may be considered after a time limit; its feasibility still depends entirely on exact checks. Invalid or absent basis, nonfinite data or an unsupported status becomes an explicit unresolved result.

For each hour in fixed order 0 through 167, let B be its basic structural columns, N its nonbasic structural columns, and I its nonbasic row activities. Fix each N entry to its exact bound indicated by its basis status. Use the exact finite lower endpoint for `kLower`, the exact finite upper endpoint for `kUpper`, and zero for `kZero` only for a genuinely free variable. Fixed intervals have one exact value. An ambiguous `kNonbasic` or inconsistent/infinite indicated endpoint is unsupported; do not guess an endpoint from a rounded primal value. Apply the same declared endpoint interpretation to the row activities in I. Equality rows have a unique endpoint. Keep the row-status mapping explicit and review it against the installed interface before implementation.

After eliminating the basic row activities, the candidate structural basis solves

```text
A_exact[I,B] x_B = endpoint_exact[I] - A_exact[I,N] x_N.
```

For a valid block basis, `|I| = |B| <= 65`; check this independently for every hour. A valid numerical basis need not be nonsingular for the exact rational matrix. If it is singular, report that hour as unresolved. No second basis selection or active-set repair is allowed in this attempt.

Clear each equation's dyadic denominators by an exact positive power of two and solve the resulting integer augmented system with deterministic fraction-free elimination and exact back substitution. Use sorted original column/row IDs and the first available nonzero pivot in that fixed order; no magnitude cutoff. Check every division asserted exact. Bound intermediate integer growth prospectively, for example at 8192 bits, and retain an explicit resource-limit result if exceeded. Archive the active row IDs, selected endpoints, nonbasic values, pivot choices, exact recovered coordinates and reconstruction diagnostics. A separate focused synthetic validation should cover upper/lower/fixed bounds, a free variable, nonsingular nondyadic solutions, exact singularity, a near-dependent equation that must be retained, constant-row rejection and deliberate point corruption; these fixtures should use no optimizer.

Proposed arithmetic budget is 900 seconds, sampled between hours and elimination pivots. All 168 hours remain in the denominator, including `NOT_EVALUATED_PHASE_LIMIT`. Record preparation/validation, numerical solve, rational reconstruction and final replay times separately, including any soft overshoot. A partial set of exact hourly positives cannot establish a full-week witness. This is a proposed budget, not authorization to run it.

## Complete strict acceptance and lossless artifact

Serialize all 23,016 coordinates as canonical reduced numerator/denominator strings with positive denominator; include an original-column index and bind the original model hashes. Reconstructed coordinates may have nondyadic denominators, so a float NPZ alone is not a lossless witness. Optional approximate CSVs are display artifacts only. The existing float-point checker and closed archives must remain unchanged; add a separately reviewed rational-point replay entry point if this attempt is authorized.

Success requires all of the following against the **original**, unmodified archived model:

1. All coordinates are finite rationals in their original finite column bounds with no expansion.
2. Every original integer coordinate is exactly 0 or 1 and equals the fixed canonical U/Y/Z schedule.
3. Every original sparse row activity satisfies its original lower and upper endpoint exactly; original equalities are exact equalities. Check all 34,680 rows, including every substituted constant row, the original aggregate rows, original nodal rows and original branch rows. There is no residual tolerance, near-zero deletion or rounded equality.
4. Native temporal/output/availability/on-on-ramp checks are consistent with the original stated semantics, using the rational point and bound native inputs; native checks supplement rather than replace original-row replay.
5. An independent implementation replays the complete original matrix and rational vector without importing the reconstruction routine, and verifies unchanged input bindings.

Compute fossil energy from the original exact objective coefficients and recovered P values, retaining a lossless rational total. If its total is at most 23195, also verify the original capped January identity's exact matrix/bounds relation and directly replay this same rational point against that existing full capped model. This post-check introduces no new optimizer call or altered cap. A strict uncapped or capped point is a feasible witness and an exact objective upper bound for that same exact model; it is not a global or fixed-schedule optimum certificate. The numerical objective and any numerical dual bound remain separately labeled numerical.

## Alternative and implementation risks

A fully exact rational LP could instead solve each of the 168 small fixed-schedule hourly programs, including the near-dependent original equality. It would avoid reliance on a numerical basis proposal. However, no ready exact LP engine was found in the checked scientific environment or PATH: the read-only inventory found NumPy, SciPy and highspy 1.12.0, while Python import specifications for SymPy, gmpy2, PPL, pycddlib, swiglpk and CVXOPT were absent; `soplex`, `qsoptex`, `esolver`, `sage` and `cddexec` were not on the inspected PATH. This is an environment-specific inventory, not a host-wide absence claim. Python's standard-library `Fraction` is available. No package was installed and no solver instance was created for this inventory.

Implementing a new exact phase-I/simplex engine brings additional pivot, degeneracy, anti-cycling and rational-growth verification work. Installing and validating an established exact solver would also be a distinct task. Neither should be introduced as an unplanned fallback after this candidate basis fails. The one-basis route is therefore the smaller first attempt. Its anticipated systems are at most 65 by 65, but no reconstruction runtime has been measured; the phase/bit limits are necessary because integer growth and degeneracy may dominate.

The installed highspy type stubs expose `getBasis`, `HighsBasis.valid`, `col_status` and `row_status`. Official [HiGHS basis-status documentation](https://ergo-code.github.io/HiGHS/dev/structures/enums/#HighsBasisStatus) describes bound/basic/free statuses, and the official [Python example](https://ergo-code.github.io/HiGHS/stable/interfaces/python/example-py/) retrieves a solution basis. These API facts support using a basis as a proposal; they do not certify exact reconstruction or this model. Installed-version behavior and row activity endpoint conventions need a source-level check in the implementation review.

The decisive missing evidence is whether one numerically proposed basis of the rationally equivalent rescaled system reconstructs to a point satisfying **all** original inequalities, not merely the troublesome equalities. Exact rank, active-bound degeneracy, the final weekly energy and the cost of rational elimination are not yet known. Strict all-null path certificates give no assurance of a positive outcome. A numerical infeasible status, exact singular basis, bound violation, time limit or failed reconstruction must not be reported as full unit-commitment infeasibility. Even an exact contradiction restricted to the fixed states would exclude only that schedule. Reassembling the network matrix to enforce a different conservation identity would change the target model and is outside this proposal.

## Required gates before any execution

Root should review this design first. If approved, the next step is a separately owned source/protocol draft and solver-free preparation with all exact transformations, input hashes, schedule/constant-row/separability checks and focused checker tests specified prospectively. Independent source and prepared-archive review must precede a separate explicit execution GO. No existing published result, cap, reference schedule or archived model needs modification.
