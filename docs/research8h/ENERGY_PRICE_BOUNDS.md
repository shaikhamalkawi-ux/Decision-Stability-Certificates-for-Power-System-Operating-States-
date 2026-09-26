# Solver-free exact bounds on the January order penalty

This audit introduces no optimization, target selection, cap change or witness editing. It independently checks each completed uncapped January recovered point (seeds26093100 and26093101), preserving a pending status if the second result is unfinished. All statements concern the finite binary64 model with every finite row/column bound expanded outward by the exact rational tau=Fraction.from_float(1e-5), retaining the original binary U/Y/Z coordinates. No exact nominal-model feasibility or optimality is claimed.

First bind each uncapped matrix to its capped parent with exactly the one fossil_energy_cap row removed, every other row/bound and native input unchanged. Check the fossil objective has coefficient one only on every hour's 23 native Coal/Oil/NG dispatch coordinates (excluding nuclear), using the pinned source roster. Independently evaluate the recovered vector, all matrix rows and finite bounds as Fractions, and verify every original binary coordinate is exactly zero or one. Its exact objective U_target is then a rigorous expanded-model upper bound. Time-limited solver bounds and gaps remain descriptive numerical outputs and are not used as rigorous bounds.

The identity reference uses the archived constructive_vector.npz, not the raw near-binary solver vector. Verify its exact expanded full capped model membership and exact binary coordinates again. Removing the cap preserves that point, so its exact fossil energy E_reference is an upper bound on the uncapped identity optimum.

For each identity hour t, validate that its actual aggregate-balance row contains exactly coefficient +1 on the 41 dispatch columns at that hour, no other coordinates, and equal lower/upper bounds. Let F be the 23 fossil columns and N the remaining 18. If l_t is that row's actual lower bound and L_j,U_j are the original variable bounds, expanded-model feasibility implies

    sum_F P_tj >= sum_F (L_tj - tau)
    sum_F P_tj >= (l_t - tau) - sum_N (U_tj + tau).

Therefore L_identity is the sum over all168hours of the maximum of those two exact rational quantities. This lower bound drops network, chronology and most hourly restrictions; it need not be tight. The proof uses verified matrix support and actual archived bounds, not a presumed load convention. A native net-array equality check supplies additional input grounding.

For each target, use its existing capped Farkas certificate, whose cap multiplier is -gamma<0. Remove the cap row and set s=d_noncap/gamma. For objective c equal to the fossil row and q=c-A_noncap^T s, the exact arbitrary-multiplier lower bound is

    LB = sum_i s_i * (row_lower_i if s_i>0 else row_upper_i)
         + sum_j q_j * (column_lower_j if q_j>=0 else column_upper_j).

Use exact ratios of the saved hexadecimal binary64 multipliers and exact Fractions for all coefficients/bounds. All selected row bounds must be finite. Widen only the remaining noncap rows and all column bounds: L_target=LB-tau*(sum|s|+sum|q|). Independently verify LB=B+exact_gap/gamma and L_target=B+exact_robust_full_gap/gamma+tau; the final +tau is required because the cap row is removed. This bound applies to the uncapped LP and hence to its original-binary subset.

For finite feasible identity and target binary models, with optima E*_identity and E*_target, exact interval arithmetic gives

    L_target - E_reference <= E*_target - E*_identity
                            <= U_target - L_identity.

Separately, [L_target-E_reference, U_target-E_reference] brackets the target optimum's excess over this chosen reference incumbent; it does not bracket optimum-to-optimum difference. Save rational endpoints without inward rounding. Displayed decimals are approximate; outward rounded display endpoints may be provided separately. Negative bounds are not silently clipped. No interval is asserted for a target lacking a verified exact expanded feasible point.

The parent reviewed and approved this proof before numerical classification. The runner and protocol are hashed before audit execution. This is a solver-free follow-up to already observed outcomes, not a prospective optimization experiment. The two cases share one January week and one RTS network; this does not satisfy a multiweek or multiseason replication gate. Fossil MWh is an energy objective, not an emissions or cost claim.
