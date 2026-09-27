# Uncapped continuation of the two January hour-of-day cases

This separate exploratory continuation follows the independently verified capped negatives for seeds 26093200 and 26093201. It asks whether those same two hour-of-day-preserving orders admit full binary/network dispatch without the fossil-electricity cap, and, if so, what rigorous bounds can be placed on their optimal fossil-electricity increase. It is not new data, a new network, a new replication, an emissions calculation or an exact-optimum claim. All completed capped results remain unchanged.

Preparation is separate from execution. Freeze source, protocol, both matrices/objectives/masks/native inputs, inherited identity evidence and transitive source hashes before any new solve. Root code/protocol review, independent prepared PASS and explicit root GO are all required. No additional seeds, replacement permutations, retries, warm starts, cap changes or target-derived tuning are allowed.

For each existing target, delete **only** its sole fossil_energy_cap row. Preserve every other matrix coefficient, row bound, finite column bound, original U/Y/Z binary coordinate and hourly native input. Preserve the same initial/terminal conventions, full 24-bus/38-line DC network, 168-hour week, no shedding and no named-unit means. Reindex row labels while retaining their original row IDs. Do not remove any dwell, transition or network row. The objective has coefficient one on all 168×23 native Coal/Oil/NG P coordinates and zero elsewhere; nuclear and renewable outputs and all state/angle variables have zero objective coefficient. The target is total fossil electrical MWh, not fuel use, emissions or money.

Recheck the actual-matrix U-only integrality projection. Original U/Y/Z integrality remains the acceptance checker. Solve the two targets in fixed seed order with one 600-second MIP each: presolve on, one thread, random seed zero, relative gap target 1e-8, no warm start. Preserve status, elapsed time, objective, numerical lower bound, numerical gap, node count and all returned vectors. A valid-incumbent flag alone is not feasibility.

Eligible U coordinates must be finite, within 1e-5 of exact 0 or 1. Recover exact U and canonical startup/shutdown indicators across the entire week, without modifying raw P or theta bytes. A target upper bound requires the recovered point to pass the original full uncapped matrix with exact rational arithmetic and the original U/Y/Z binary mask, plus the separate native no-cap physical checker. Report both strict nominal and uniformly expanded membership. The expanded model widens every finite row/column bound by exactly Fraction.from_float(1e-5); it is not measurement uncertainty. An accepted point's fossil energy is summed as exact Fractions of its stored binary64 P values. Failed or merely numerical candidates are retained, not called rigorous upper bounds.

After both scheduled MIP decisions, run one 60-second continuous energy LP for each of the same targets in the same seed order, even if a target lacks a verified binary incumbent, provided the declared time guards permit it. Use simplex, presolve off, one thread and seed zero. No new identity LP is run. Archive every returned primal, row/column dual, solver status and exact lower-bound calculation. A numerical LP optimum and a fractional LP point are not proofs of an exact optimum or binary upper bound.

The lower-bound proof is the previously reviewed signed row-dual plus finite-box correction. For arbitrary archived finite raw row multipliers, zero entries whose signs select infinite row endpoints. Call the projected vector d, beta the exact sum of d times its selected finite row endpoint, and q=c−A^T d. Then

`LB_nominal = beta + sum_j q_j * (column_lower_j if q_j >= 0 else column_upper_j)`.

Every coefficient, multiply, sum and sign decision uses its exact binary64 rational value. For uniform outward tolerance tau,

`LB_expanded = LB_nominal - tau * (sum_i |d_i| + sum_j |q_j|)`.

This does not require exact dual stationarity or solver optimality. Preserve raw and projected duals separately. Do not clip an expanded lower bound at zero, because its power boxes also expand. A zero-row-dual finite-box bound is frozen during preparation as the fallback; the final target lower bound is the maximum of this valid baseline and any valid returned-dual bound. Invalid/unavailable duals are recorded without another solve.

Reuse the already verified uncapped January identity bounds from `energy_lp_refinement`: its exact lower bound and the exact binary reference upper Eref. Verify identity model/objective equality to the capped HOD identity after deleting only the cap, replay the archived identity dual formula and original-binary upper point, and bind the existing independent review. Do not optimize the identity again.

Only when a target has a verified exact expanded binary upper Utarget and a valid exact expanded lower Ltarget, form the uncapped original-binary optimum-difference interval

`[Ltarget − Eref, Utarget − Lidentity]`.

Keep the different interval `[Ltarget − Eref, Utarget − Eref]` explicitly labeled as target optimum excess over the chosen reference incumbent. If the verified identity and target lower bounds are positive, the optimal relative penalty lies in

`[Ltarget / Eref − 1, Utarget / Lidentity − 1]`.

This ratio is not an absolute gap divided by the incumbent. Exact rational endpoints are authoritative and all displayed interval endpoints are rounded outward. A lower bound alone does not establish finite uncapped feasibility or a finite cost penalty. If a lower bound exceeds an accepted upper, stop with a fatal contradiction rather than repairing a witness or changing a bound.

Execution has a 2100-second soft solve/check allocation and an absolute launch cutoff at 2026-09-27 04:00:00 UTC. The phase clock starts after entry manifest validation/native loading; record invocation, allocation and completion UTC times directly in this new runner. Initiate a MIP only if both phase and cutoff time remaining are at least 605 seconds; initiate an LP only if both are at least 65 seconds. Limits are admission guards, not forcible wall-time deadlines. Record actual overruns and do not relaunch skipped cases. Skipped or unverified MIP outcomes remain UNKNOWN, with two cases in the denominator. At most two 600-second MIPs and two 60-second LPs are configured (1320 solver seconds). The runner executes sequentially; root coordinates the separate host-wide limit of at most two concurrent long solvers.

Evaluate each launch guard after loading that case and constructing/passing its solver model, immediately before the actual solver.run call. A failed guard preserves a NOT_RUN result with zero optimization calls and zero solver elapsed time; it does not trigger a shorter solve or a retry. Model setup time therefore cannot silently bypass the remaining-time check.

Preserve all strict flags, residuals, raw/recovered vectors, diagnostics, omitted calls and time-limit statuses. Independent post-run replay of accepted points, lower-bound arithmetic and final intervals is required before publication. These are bounds on two particular uncapped expanded binary64 models for the same January week and the frozen synthetic perturbations.
