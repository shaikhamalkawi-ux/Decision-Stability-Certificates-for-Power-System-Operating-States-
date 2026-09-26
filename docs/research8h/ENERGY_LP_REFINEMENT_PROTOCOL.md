# Three fixed LPs to refine the existing January energy bounds

This is a precision refinement after the initial energy-price audit, not new data, seasonal replication, target selection or a new method. Preserve all existing cap-ray bounds, identity balance/box bounds, exact binary upper witnesses and their audits. Prepare all three models before any solve; obtain parent review and explicit GO before `--run-prepared`.

The fixed order is January identity, seed26093100, seed26093101. For identity remove exactly its single fossil_energy_cap row and associated row bounds from the archived seasonal-transfer model. The two target models are the already prepared seasonal_uncapped models. Retain all remaining coefficients, row bounds and variable bounds. Each model has34680rows and23016columns, with no cap and no named-unit means. Make every variable continuous for these three LP relaxations; do not alter their bounds. Minimize the identical sum of168×23 native Coal/Oil/NG dispatch coordinates, excluding nuclear; all U/Y/Z and angle costs are zero.

Bind each model and existing binary upper witness to the completed exact energy-price audit. Exact row deletion or equality with unchanged bounds inherits the already established positive expanded-model witness. These controls require no new optimization. Archive source/protocol hashes, all three matrices/bounds/objectives/row maps, original integrality and upper-point bindings, and the prior exact bounds before launch. All models and bindings must freeze before the first call.

Run exactly one HiGHS simplex LP per case with60seconds, presolve off, one thread and random seed0. No retry, warm start, limit extension, alternate objective or case selection. Save complete logs, status, timing, primal and row/column dual arrays when returned, and numerical primal checks. LP primal vectors are continuous and cannot supply binary upper bounds. A solver optimum or numerical dual bound alone is not an exact bound or an exact optimum. Shared-host timings are not benchmarks.

Use the reviewed mean-repair arbitrary signed-row-dual plus finite-box formula, adapted without epsilon-specific terminology or any nonnegativity clipping. For every finite raw dual d, project entries selecting infinite row bounds to zero and archive raw/projected vectors separately. Define beta=sum d_i*(l_i if d_i>0 else u_i), q=c−A^T d, and

    LB_nominal = beta + sum_j q_j*(L_j if q_j>=0 else U_j).
    LB_expanded = LB_nominal − tau*(sum_i |d_i| + sum_j |q_j|),

where tau=Fraction.from_float(1e-5). Every product, sum, residual sign and bound correction uses exact Fraction arithmetic on saved binary64 values. All column bounds are finite. This produces a valid objective lower bound for arbitrary admissible multipliers, regardless of numerical stationarity or solver status. A missing/nonfinite returned dual is not invented: record its absence and retain only the preexisting bound in the combined bracket. No clipping at zero is allowed for the expanded model.

Run solver-free synthetic checks of both multiplier signs, an imperfect residual with each box sign, zero dual and sign projection before freezing. Replay each saved projected dual and exact residual without a further optimization. Save exact rational lower bounds and a rational stationarity-residual archive. If an expanded bound exceeds the already verified exact binary upper point, stop with a fatal contradiction; do not continue interpreting outcomes.

For each case choose the maximum of the new valid expanded lower bound, if available, and its preexisting independently verified bound. Preserve both components and which is active. Keep existing exact binary upper energies unchanged. If L*_identity and L*_target denote these best certified lower bounds, report

    [L*_target − E_reference, U_target − L*_identity]

for target optimum minus identity optimum, and separately

    [L*_target − E_reference, U_target − E_reference]

for target optimum excess over the chosen identity incumbent. Both optima refer to uncapped uniformly expanded original-binary models; the LP is only a source of lower bounds. Preserve exact rational endpoints and round displayed lower endpoints down and upper endpoints up. Retain all solver outcomes, non-improvements and unavailable duals. Check all preparation hashes again afterward. No new data, network, season, replication or novelty claim is licensed.
