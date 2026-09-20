# Workstream C - July network chronology repair

## Gate decision

**Retain the V7 certified bracket.** A new 600-second HiGHS 1.12.0 solve used
the verified 11.9262964643-MW schedule as an explicit MIP start and added the
known independent relaxation lower bound as an objective cut.

The warm start was accepted as feasible. At the time limit, the solver returned:

| Quantity | Result |
|---|---:|
| Primal objective | 11.926296464290 MW |
| Dual bound | 8.020508464288 MW |
| Relative gap | 32.7494% |
| Maximum primal infeasibility | 7.951e-12 |
| Sum of primal infeasibilities | 9.724e-10 |

The run neither improved the incumbent nor raised the lower bound beyond the
independent exact no-network minimum-up/down repair. Therefore the strongest
evidence remains

`8.020508464286 <= A_network+minUD+ramp <= 11.9262964643 MW`.

The upper endpoint remains a feasible-witness bound and is not relabelled as an
optimum. The lower endpoint transfers from the exact no-network relaxation.
The only legitimately available MIP engine was HiGHS 1.12.0; SCIP, Gurobi,
CBC, and GLPK command-line solvers were not available in the execution
environment. The solver log, result JSON, warm-start schedule, and input
witnesses are frozen in `results/network_milp_v8`.
