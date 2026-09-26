# Exact January energy-difference bounds without another optimization

Both uncapped January orders now have independently verified binary feasible points in the explicitly expanded encoded models. Together with the existing exact capped certificates, they give finite rigorous intervals for the increase in the optimum fossil-energy objective. This audit ran **zero optimizations**.

All optima below refer to **uncapped** DC-network/native-UC models with every finite row and column bound widened outward by exactly `Fraction.from_float(1e-5)`, while preserving original binary U/Y/Z. This matches the earlier exact robust certificate convention. It is not a claim of exact nominal-model feasibility, exact physical measurements, emissions, monetary cost or solver optimality.

The identity optimum is at least 22114.0856691 MWh by a verified balance/box lower bound, and at most the exact energy of its constructive reference point, approximately 22964.941239556443 MWh. The reference point is an incumbent, not a proved optimum.

| January order | Target optimum interval, MWh | Target optimum minus identity optimum, MWh | Target optimum minus chosen reference energy, MWh |
|---|---:|---:|---:|
| seed26093100 | [23646.570920, 25162.618973] | **[681.629680, 3048.533304]** | [681.629680, 2197.677734] |
| seed26093101 | [23747.348104, 25693.286910] | **[782.406864, 3579.201241]** | [782.406864, 2728.345671] |

Each displayed lower endpoint is rounded downward and each upper endpoint upward to six decimal places. The exact numerator/denominator records in `results.json` and the per-case JSON files are authoritative. The last two columns answer different questions; the smaller upper endpoint in the last column must not be reported as an optimum-to-optimum upper bound.

The identity lower bound uses only restrictions that survive deletion of the cap. For each of the 168 hours, the actual aggregate-balance row was verified to have coefficient +1 on exactly that hour's 41 dispatch columns and zero support elsewhere; its bounds equal the archived native net array. Fossil membership was checked against the pinned native source: 23 Coal/Oil/NG units, excluding nuclear. If F denotes fossil units, N the other 18 units, and l_t the actual balance-row lower bound, every expanded feasible point satisfies

    E_fossil,t >= max(sum_F(L_tj - tau),
                     l_t - tau - sum_N(U_tj + tau)).

Summing these exact rational hourly bounds gives `L_identity`. It deliberately drops network and chronological restrictions and need not be tight. The identity constructive point was separately replayed against every row and column using exact Fractions; U/Y/Z are exactly binary. Its expanded capped-model membership supplies an uncapped feasible upper bound after removing the cap.

For each target, the audit verified that its uncapped matrix removes exactly the one capped-parent fossil-energy row, while all other rows, bounds, original integrality and native inputs are unchanged. Every recovered-vector row and column was independently evaluated with exact Fraction arithmetic; the original binary coordinates are exactly 0/1. The objective equals one times each of the 168×23 fossil dispatch coordinates and zero elsewhere. The exact sum at that recovered point is `U_target`.

The target lower bound uses the existing saved cap ray. With cap multiplier −gamma, normalize all other multipliers by gamma, set q=c−A_noncap^T s, and evaluate the row-plus-box objective bound exactly. Only the noncap rows and column bounds are widened. The audit independently verifies both identities

    LB_nominal = B + nominal_Farkas_gap/gamma
    L_target = B + robust_full_Farkas_gap/gamma + tau.

The extra `+tau` in the second line accounts for removing the cap row before widening. Raw Farkas separation values are arbitrary ray-scale quantities; normalized energy lower bounds have units of MWh.

For the two uncapped expanded binary optima, the rigorous interval follows from

    L_target - E_reference <= E*_target - E*_identity
                            <= U_target - L_identity.

The upper points were returned by time-limited MIPs and do not establish an optimum. Solver numerical bounds, gaps and displayed objective rounding were not used as exact proof. The upper-bound audit checks the recovered points against original binary U/Y/Z, so it does not rely on a solver's near-integer coordinates being exact integers. Both completed results were present at this audit's single availability freeze; no rerun was used to add a later result. The unchanged horizon-boundary conventions of the seasonal-transfer and uncapped protocols apply.

All 49 bound audit inputs and all 55 entries of the uncapped preparation manifest passed their hash checks. Frozen runners, models, protocols, witnesses and prior certificates were not edited. The new runner is `src/research8h_energy_price_bounds.py`; the reviewed proof is `docs/research8h/ENERGY_PRICE_BOUNDS.md`. `identity_bound.json` contains all 168 hourly calculations. `audit_freeze.json` records source bindings; `completion.json` records the zero-optimization completion. Independent review is supplied separately.

These are two orders of one January week on one RTS network. They demonstrate a finite positive fossil-energy penalty within this stated model and tolerance convention. They do not complete the outstanding multiseason replication gate or justify a general seasonal/network claim.
