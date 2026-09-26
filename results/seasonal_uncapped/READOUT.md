# Uncapped January witnesses with exact tolerance-qualified bounds

Both predeclared January twins have accepted uncapped binary DC-network
witnesses. Each recovered vector passes the full original binary-model matrix
and native no-cap physical checks, and an exact rational check against that
model with every finite row/column bound expanded outward by
tau = Fraction.from_float(1e-5). Neither stored numerical vector satisfies all
strict unwidened equalities/bounds exactly. Consequently the energy values below
are rigorous feasible upper bounds for the **expanded binary64 model only**.

| Seed | Exact-sum feasible upper bound, displayed MWh | Solver-reported numerical lower bound, MWh | Reported MIP gap | Actual solver seconds |
|---|---:|---:|---:|---:|
| 26093100 | 25,162.61897255671 | 24,509.560575070558 | 2.59535145% | 600.2440444 |
| 26093101 | 25,693.286909556562 | 25,110.049372068534 | 2.26999971% | 602.0467944 |

Both statuses were Time limit reached. Neither incumbent is established optimal,
and the displayed solver lower bounds are numerical reports, not independent
exact lower-bound certificates. The exact feasible objective fractions are:

- Seed 26093100: 906578891427777312835 / 36028797018963968 MWh.
- Seed 26093101: 1017815955397983932811197640867839 /
  39614081257132168796771975168 MWh.

For seed 26093100 the maximum exact row/column violations of strict bounds are
1.1550227441148309e-10 and 9.350742402602918e-12. For seed 26093101 they are
3.980460405728081e-11 and 3.205080645329872e-11. All are below the exact archived
tau. Every original U/Y/Z coordinate is exactly binary after recovery. The
canonical evidence is `recovered_vector.npz` plus `exact_point_check.json`;
raw vectors, readable CSV copies, native residuals and failed strict checks are
also preserved. No dispatch or angle coordinate was altered during recovery.

The only physical-model change from each capped twin is removal of its single
fossil-energy-cap row. All other rows, bounds and native inputs are unchanged;
there are no named-generator mean rows. The objective sums the 23 Coal/Oil/NG
units with unit weights and excludes nuclear. U-only integrality reduced the
declared integer count from 12,096 to 4,032, with the exact applicability audit
passing in both cases. Recovered binary Y/Z are checked against the original
full binary model; this is not a claim about a different relaxed physical model.

The separately archived capped certificates reject even the full continuous
models after the same outward tau expansion, including the cap upper bound.
Thus these uncapped witnesses and capped negatives give a coherent pair in a
common tolerance convention: each order has a finite feasible fossil-energy
level, while the benchmark 23,195 MWh cap cannot be met. The old January
reference and commitment-class control remain the corresponding positive
controls; their exact expanded-model audits are separate evidence.

If an independently certified target energy lower bound L is paired with the
upper bound U here, [L-E_ref, U-E_ref] describes target-optimum excess over the
chosen archived reference energy. Because reference optimality is unproved,
the upper endpoint is not an upper bound on the difference between the two
unknown optima. The lower endpoint does bound that optimum-to-optimum difference
from below. All such comparisons must use the same expanded-model convention.

Exactly two MIP calls ran, without warm starts, retries or adaptive changes.
Configured solver time was 1,200 seconds; actual solver time was
1,202.2908388 seconds. Execution and checks after model loading took
1,287.0382653 seconds, excluding earlier import/startup and preparation. Source
and all 55 frozen input/model files passed final hash/size checks. Nine
solver-free exact-checker boundary tests also passed, including strict versus
expanded membership, exact tau versus the next float, row scaling and rejection
of fractional binary coordinates.

This remains a two-case study within one January week of the same RTS system.
It supplies no new field, AC, security or cross-network validation and does not
erase the earlier April/October NO_REFERENCE results or satisfy the two-week
replication gate. The U-only projection and longer solver budget are standard
computational choices, not method-novelty or speedup claims.
