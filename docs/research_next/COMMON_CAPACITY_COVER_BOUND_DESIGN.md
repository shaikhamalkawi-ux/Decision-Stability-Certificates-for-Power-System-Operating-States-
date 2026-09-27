# Universal common-schedule capacity-cover bound: design only

27 September 2026. This is a source/theory assessment, not a calculation of the proposed bound. No scientific arrays were evaluated, no candidate was generated, and no optimizer was invoked. It is separate from the fixed-union energy-floor result and from the original interrupted UNION execution. The full common-binary question remains UNKNOWN.

## Decision and scope

**Proceed to a bounded implementation/preparation proposal, subject to independent gates.** A binary capacity-cover bound can reject every common schedule, whereas the closed union-floor diagnostic rejects only its particular frozen schedule. It can be stronger than the continuous joint model even though that model has an exactly checked expanded feasible point. This is classical 0/1 covering-knapsack dynamic programming, not a new optimization or certification method.

Its scientific discriminator is narrow: can instantaneous shared binary decisions, the two hourly demand profiles and their fossil-energy caps already rule out common operation after network and all residence constraints have been relaxed? A positive rejection would NOT isolate minimum-up/down or missing interday transitions. A null result gives neither a common binary witness nor evidence that dwell is the cause of the difficulty.

## Exact statement

Let worlds `i=0,1` be the unchanged original identity/day321 matrices, hours `t=0,...,167`, and `F` the actual 23 fossil generators. Let `tau = Fraction.from_float(1e-5)`. All comparisons below are rational comparisons of the archived binary64 coefficients/endpoints, not decimal reconstructions. Keep the original integer declarations: the expanded original `[0,1]` commitment boxes still admit only the integers 0 and 1 because `0 < tau < 1`.

Require the actual rows, with no additional coefficients, to imply for every fossil generator:

`a_j u_tj - tau <= p_itj <= b_j u_tj + tau`.

Here the *same* nonnegative integer capacity vector `b` and the same nonnegative minimum-output vector `a` must occur in both worlds. The simplest supported implementation also requires integer `a`. Check these properties against every actual thermal lower/upper row at every hour; a nameplate CSV or row label alone is insufficient. A group of hours with another verified common integer pair `(b,a)` may share its own DP table, but a world-to-world mismatch is UNSUPPORTED under this design.

At each hour verify an aggregate row with coefficient 1 on exactly the 41 generation columns and no others. Write its expanded lower endpoint as `L_it`. For each nonfossil generation variable take its finite original column upper bound plus `tau`, denoted `U_itj`. Define

`d_it = max(L_it - sum_(j not in F) U_itj, sum_(j in F)(original_column_lower_itj - tau))`.

Thus actual fossil generation `f_it = sum_(j in F) p_itj` satisfies `f_it >= d_it`. This definition retains small negative lower bounds allowed by uniform expansion; silently clamping dispatch or the fossil floor to zero would change the target model.

Summing the 23 thermal upper rows gives

`sum_j b_j u_tj >= max_i d_it - 23*tau = H_t`.

Since `sum_j b_j u_tj` is an integer, the necessary cover threshold is `h_t = max(0, ceil(H_t))`, with exact rational ceiling. Define

`M_t = min {sum_j a_j u_j : u in {0,1}^23, sum_j b_j u_j >= h_t}`.

If there is no cover, no common binary schedule exists. Otherwise, summing the 23 thermal lower rows establishes the universal hourly and weekly bounds

`f_it >= max(d_it, M_t - 23*tau)`;

`E_i >= B_i^cover := sum_t max(d_it, M_t - 23*tau)`.

Verify the actual fossil cap row contains exactly all `23*168` fossil generation coordinates, each with coefficient 1 and no others. If `B_i^cover` is strictly greater than that row's original upper endpoint plus `tau` for either world, the original common binary system is infeasible in the uniformly expanded model. Equality is not a rejection. This conclusion quantifies all shared schedules; it does not depend on the union schedule or any earlier optimizer status.

Proof: every feasible original point satisfies the selected boxes/rows and exact binary commitments; its commitment therefore belongs to the cover set, whose minimum minimum-output cost is `M_t`. Summing valid hourly lower bounds and comparing one required cap yields a contradiction. Dropping the remaining rows only enlarges the possible set and cannot invalidate this negative implication.

## Nuclear, variable coefficients and tolerance caveats

Nuclear is outside `F` but has a shared commitment in the full model. Using its unconditional expanded output upper box in `d_it` deliberately relaxes both that commitment dependence and nuclear minimum output. This is safe for a lower bound, possibly weak; it does not assert that the nuclear upper is simultaneously attainable or that nuclear is unshared in the original model. Renewables/hydro are similarly bounded by their actual finite boxes. The archived aggregate row already represents the model's specified net signal; do not subtract any renewable quantity a second time beyond the explicit nonfossil generation columns.

The scalar threshold `max_i d_it - 23*tau` with one capacity vector is invalid in general if the worlds have different fossil capacity coefficients. Likewise minimizing one common `a` does not yield the asserted cost in a world with a different minimum-output vector. General multidimensional covers or coefficient-wise envelope relaxations would require another declared design. This one must fail closed as UNSUPPORTED, without ceil/floor rounding of nameplates, fallback envelopes or outcome-adaptive replacements.

The `23*tau` terms apply to the 23 selected thermal row endpoints. They do not represent 23 column tolerances added again. The aggregate row contributes its own `tau` through `L_it`; each nonfossil upper box contributes its own `tau`; the final cap contributes one `tau`. Exact coefficients multiply exact binary states; no multiplication by an approximate/rounded state is allowed. Verifying original binary boxes and full original masks is essential.

## One bounded no-optimizer experiment

1. Freeze source/protocol, both original world matrices/bounds/masks/metadata, joint column maps, source roster and prior independent model-transport reviews. Read the immutable original common archive, not `common_union/fixed_bounds.npz`. Require the current original 12,096-bit mask and the exact shared-U mapping. Check all selected actual coefficient patterns, both full fossil cap rows and finite generation boxes. Preserve all original files.
2. Before scientific arithmetic, run tiny invented exhaustive controls: enumerate every subset of a small roster and compare the complete DP table and threshold minima; include a nonintegral threshold requiring exact ceiling, an integer jump that exceeds a fractional cover optimum, an impossible capacity request, and a tau/cap equality case. Include negative schema controls for differing world coefficients and wrong fossil/thermal row rosters. These are implementation checks, not additional empirical cases.
3. For each distinct verified common `(b,a)` tuple, compute one complete exact 0/1 DP table. With `D_0[0]=0` and all other states infinite, the recurrence is `D_j[c]=min(D_(j-1)[c], D_(j-1)[c-b_j]+a_j)` when the second state exists. Use separate previous/next arrays or decreasing capacity updates to prevent using a generator twice. A suffix minimum over capacities supplies all 168 threshold queries. Do not run an identical table separately at every hour. The method is pseudopolynomial in total integer capacity, not polynomial in binary input length.
4. Fix a source-level state/time guard before execution; exceeding it is INCOMPLETE, not a bound. Archive the verified roster, table/finite-state denominator and exact threshold/selected-cost/hourly-floor records. A feasible cover subset only gives an upper bound on `M_t`; certification of the lower bound requires checking the full recurrence/exhaustiveness, not just one minimizing-looking subset. Preserve every null, unsupported premise and incomplete case. No solver, schedule search, alternative rounding or follow-on arm is included.
5. Independently verify the scalar premises, DP recurrence and final exact cap comparisons. Existing exact continuous joint membership is a control for the **linear premises only**. It need not satisfy the binary-cover floor: such a violation is the intended possibility of an integer-specific strengthening, not a reason to discard the result. It would be an error only if that continuous point violated a purported universally linear inequality derived from rows/boxes alone.

There are exactly two fixed worlds and one predeclared bound family. Report the integer-cover strengthening over the same formula with the cover restriction relaxed only if that extra comparison is explicitly included before execution; it is not necessary for the primary negative/null test. No broader scientific claim should be inferred from the closed LP witness, fixed union obstruction, or numerical MIP timeouts.

## Source reading and current uncertainty

Read-only inspection covered `src/temporal_lp_certificate.py`'s actual thermal/aggregate assembly definitions, `src/researchnext_common_union.py`'s original-world/mask bindings, `src/researchnext_union_energy_floor.py` and its protocol, the archived original identity model metadata/native-spec text, and relevant original `gen.csv` lines. The visible source nameplates are integer-valued, and earlier source checks assert static thermal nameplates, which makes the exact-integer path plausible. **This memo did not verify the current scientific CSR coefficients or compute a DP threshold, table, floor or cap verdict.** Actual-matrix confirmation belongs to the prospective gated experiment.
