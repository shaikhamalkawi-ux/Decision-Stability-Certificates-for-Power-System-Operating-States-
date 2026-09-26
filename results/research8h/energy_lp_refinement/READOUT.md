# Three LPs refine the January fossil-energy difference bounds

All three fixed LPs returned numerical Optimal status and improved their exact certified expanded-model lower bounds. Combining those lower bounds with the **unchanged, independently verified binary upper witnesses** narrows the optimum-to-optimum energy-difference intervals to:

| January target order | Refined optimum difference from identity, MWh | Prior interval, MWh |
|---|---:|---:|
| seed26093100 | **[1542.835730, 2546.796204]** | [681.629680, 3048.533304] |
| seed26093101 | **[2139.151137, 3077.464141]** | [782.406864, 3579.201241] |

These intervals concern the **uncapped original-binary DC-network/native-UC models with every finite row and column bound expanded outward by exactly Fraction.from_float(1e-5)**. They do not claim exact feasibility for the nominal unexpanded models, exact physical measurements, a proved optimum, emissions or monetary cost. Displayed lower endpoints are rounded downward and upper endpoints upward to six decimal places; the archived rational numerators and denominators are authoritative.

| Model | Prior certified lower bound, MWh | New certified lower bound, MWh | Unchanged binary upper bound, MWh | LP solver seconds |
|---|---:|---:|---:|---:|
| January identity | 22114.085669 | 22615.822769 | 22964.941240 | 5.225 |
| seed26093100 | 23646.570920 | 24507.776969 | 25162.618973 | 6.990 |
| seed26093101 | 23747.348104 | 25104.092377 | 25693.286910 | 16.247 |

The LPs are sources of lower bounds only. Their continuous primal vectors are not binary feasible upper points. No new binary optimization or witness editing occurred. The original cap-ray target bounds, identity balance/box bound and binary upper witnesses remain preserved in `energy_price_bounds`; the best lower bound in each case is explicitly max(previous bound, new bound), so a failed or weaker refinement would not discard valid prior evidence.

The frozen design used exactly three calls in the declared order, one thread, seed0, simplex, presolve off and60seconds per LP, with no retry, warm start, limit extension, alternate target or objective. There were no unknown cases in this arm. Solver times total approximately28.46seconds; import and filesystem delays on the shared host are separate, and these timings are not a performance benchmark.

For identity, the single cap row was deleted with its associated bounds. The two target matrices are exact copies of their already uncapped parents. Every model has34680rows and23016columns, zero cap rows, zero named-mean rows, and exactly3864 cost coefficients equal to1 on the168×23 native Coal/Oil/NG dispatch coordinates. The nuclear unit is excluded; all state and angle objective coefficients are zero. The variables are continuous for these LP calls. Independent preflight checked exact matrix/row-map/bound/objective equality, unchanged binary upper-point bindings, all59 frozen files, and ten independent signed-dual/finite-box examples.

The numerical Optimal labels are not the proof of the lower bounds. Each saved finite signed row dual is projected only where its sign would select an infinite row bound. With q=c−A^T d and beta the selected row-bound sum, the exact calculation is

    LB_nominal = beta + min_(L<=x<=U) q^T x
    LB_expanded = LB_nominal − tau*(||d||_1 + ||q||_1).

Every coefficient, multiplier, residual, sign decision and product is interpreted as an exact Fraction of its saved binary64 value. The finite-box residual term makes the bound valid without exact dual stationarity. No expanded bound is clipped at zero. Raw/projected duals, primal vectors, exact stationarity residuals, logs and statuses are retained. A saved-dual replay reproduces the exact bounds, and each bound is checked against its established exact expanded binary upper witness.

Let L_I be the best identity lower bound, E_ref the exact reference-point energy, and L_T,U_T the target bounds. The refined optimum-difference interval is

    [L_T − E_ref, U_T − L_I].

For comparison, the different quantity “target optimum minus the chosen identity incumbent's energy” has intervals **[1542.835730,2197.677734]** and **[2139.151137,2728.345671]** MWh. Those smaller upper endpoints must not be called optimum-to-optimum upper bounds. Both types are stored separately in `refined_brackets.json`.

All59 frozen preparation hashes still match after the three solves. The freeze binds sourceSHA256 `f91472fee2b0cc170a94e1cfb58d6ed997ec94a967a09f484af9ff85b7fa5b3c`, protocolSHA256 `083ac02d802f955f5598b44cab73994db6461a988c5ef07fe23008d53c352dc9`, and input-manifestSHA256 `b85b1260ded4d4f0a2576c921a4d84581360bfe7adddac361d5ad8826fd6e32d`. Final independent replay is recorded in `INDEPENDENT_REVIEW.md` and `independent_review.json`.

This is a precision refinement of two orders of the same January week and RTS network. It adds no data, seasonal replication, network replication or new method. The original horizon-boundary and fixed-source modeling conventions remain unchanged. The multiseason replication gate remains outstanding.

An arithmetic-only addendum gives a relative optimum penalty. Both identity and target optima have strictly positive exact lower bounds, so monotonic division yields

    L_T / E_ref - 1 <= E*_target / E*_identity - 1
                   <= U_T / L_I - 1.

The resulting rigorous outward-rounded percentage ranges are **[6.718221%,11.261126%]** for seed26093100 and **[9.314855%,13.607571%]** for seed26093101. These are ratios of the two model optima; they are not the absolute-difference interval divided by the chosen reference incumbent. `relative_penalty_bounds.json` stores exact rational ratio and percentage endpoints and copies the unchanged absolute brackets; its companion CSV uses exact outward-decimal strings. The separate standard-library addendum script reads only the existing bounds, performs no optimization, and leaves the frozen LP source/protocol and all absolute bounds unchanged. The same expanded-model, fossil-electricity and single-week limits apply.
