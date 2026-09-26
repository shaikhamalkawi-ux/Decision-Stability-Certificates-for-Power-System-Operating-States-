# Exact no-dwell permutation symmetry audit

This is an exploratory, solver-free structural audit designed after the January service-cap results. It adds no cases, feasibility labels, optimizer calls or priority claim. Existing matrices, witnesses and frozen experiments remain unchanged.

The archived optimization objectives in these feasibility models are zero and are explicitly loaded, checked and hash-bound. The fossil-energy functional below is separately defined by the audited 168x23 cap coefficients, not claimed to be the stored objective. No optimization is performed with either functional.

## Proposition and scope

Consider the archived January binary DC service model with every finite row and column bound expanded by the same rational tau, where 0 <= tau < 1. Delete only the minimum_up and minimum_down rows. Every U, Y and Z coordinate is still required to be an integer. Their nominal column bounds are [0,1], except Y[0] and Z[0], whose upper bounds are zero. The transition equalities have integral coefficients and zero right-hand side; exclusivity is Y+Z <= 1. No other remaining row uses Y or Z. The objective and fossil cap use only dispatch, with the same time-independent fossil roster.

The projection of this no-dwell model onto P,U,theta is exactly the model obtained by deleting the transition/exclusivity rows and Y/Z columns. To lift any projected feasible point, set Y[0]=Z[0]=0 and Y[t]=max(U[t]-U[t-1],0), Z[t]=max(U[t-1]-U[t],0). Expanded integer U bounds imply U is exactly binary. The lifted variables satisfy every removed transition and exclusivity row exactly and their bounds. Conversely, projection of a no-dwell feasible point trivially satisfies the retained rows. The argument covers strict tau=0 and the declared expanded tau=Fraction.from_float(1e-5); it does not infer that either strict model is nonempty.

If joint hourly packages are permuted and every retained hourly row and column bound is carried with its package, permuting P,U,theta is a bijection between these projected feasible sets. The fossil-energy objective and common cap are invariant under that permutation. Thus the attainable fossil-energy sets, and their infima (including empty-set +infinity), are identical in the no-dwell binary models. Combining with projection/lifting gives the same statement for the original no-dwell formulations. This is a statement about attainable values and projected feasible sets; it does not assert a one-to-one correspondence between arbitrary auxiliary-variable representations.

This elementary separability argument is an explanatory proposition, not a new general unit-commitment theorem. It fails without additional proof when there are effective ramp constraints, storage states, startup costs, reserves with inter-hour coupling, initial dwell obligations, or other remaining temporal constraints. The current finite-horizon formulation has no pre-horizon residence obligation; it fixes only initial transition variables. Source/model assumptions are part of the result.

## Fixed audit

Read the published January identity, its two ordinary twins and commitment-class control, and all five published day-block permutations. No new candidate selection is permitted. For each archive:

- Check the full declared binary mask and the exact U/Y/Z column bounds; check every transition and exclusive-transition row against the canonical integral template, including all168x24 state positions and fixed initial Y/Z columns.
- Check that deleting dwell/transition/exclusivity rows removes every Y/Z occurrence; every remaining noncap row is confined to its labelled hour and P/U/theta coordinates. Reject unknown row families, duplicate row keys or unexpected global couplings.
- Match target rows to identity rows by family, source hour and unit/bus/branch identifier. Compare the mapped sparse coefficients, both row bounds, reduced column bounds and original integer masks exactly as binary64 values, with no numerical tolerance. Check inverse/bijection conditions and unchanged fossil cap and time-independent objective.
- Reject noncanonical CSR matrices with unsorted or duplicate column entries, nonfinite coefficients, NaN bounds, or nonfinite column boxes before any sparse-row dictionary comparison. Check the stored zero objectives separately from the cap-defined fossil-energy functional.
- Freeze all accessed artifact/source/protocol SHA-256 values and byte sizes before arithmetic; rehash after. Record explicit failures rather than converting them into a feasibility verdict.

The audit proves equivalence of the supplied matrices subject to the independently checked templates; native data assembly remains covered by the prior experiment reviews. It performs zero optimization and does not claim minimum temporal information or a physically realistic shuffled trajectory.

The existing January static witnesses already show that the no-dwell cap models are nonempty in the expanded arithmetic semantics. Exact full-model rejection therefore attributes the cap incompatibility to reinstating dwell constraints in this declared formulation. The stronger objective-set symmetry is useful for interpretation; it is not an additional empirical replication or a real-grid causal estimate.
