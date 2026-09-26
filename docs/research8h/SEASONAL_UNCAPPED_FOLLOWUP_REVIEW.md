# Review of the conditional uncapped follow-up design

Reviewed the root-authored SEASONAL_UNCAPPED_FOLLOWUP_DESIGN.md and the existing
exact_bound implementation in research8h_energy_lp_refinement.py. This review
starts no optimization and supplies no new target outcome. The design was
recorded before target outcomes were available to its author; this review was
performed while the separately frozen cap-continuation experiment ran.

The scientific question and conditional routing are sound. A certified capped
negative by itself does not show that uncapped operation is feasible. A checked
uncapped binary point supplies that missing finite upper bound, without making
the incumbent optimal. Deleting only the cap row preserves every other physical
constraint and the declared tolerance convention. Retaining every case in the
fixed ledger prevents unresolved cases from disappearing from the analysis.

For the precision phase, any sign-admissible signed row multiplier d gives

    c'x >= selected_row_bound_sum(d) + min_box (c - A'd)'x.

Under uniform outward expansion of all finite bounds by tau, subtract
tau times the sum of the absolute row multipliers and the absolute residual
coefficients. Exact stationarity or solver optimality is unnecessary. The
reviewed helper computes this bound with exact rational arithmetic, projects
only inadmissible multiplier signs, and recomputes the complete residual. It
retains negative lower bounds. In particular, the expanded dispatch box can
allow small negative coordinates, so clipping an energy lower bound to zero
would be unjustified without an additional valid argument.

The proposed difference enclosure [L_T-U_I, U_T-L_I] is valid when the four
endpoints bound the two optima in the same expanded model. The proposed ratio
formula also needs the stated positive enclosures, particularly L_I > 0.
Without that certified denominator condition, do not report a finite ratio
interval using the formula. A solver's numerical lower bound is not a
replacement for the exact residual bound. Native numerical physical checks
and exact expanded membership remain separate requirements for each upper
point; strict nominal membership must remain a separate flag.

The 04:00 UTC cutoff should be checked before each new solver call, together
with the 605/65-second remaining-phase guards. Actual soft-limit and checker
overruns must remain visible. Before the optional precision phase, freeze all
of its selected target/identity models and the shared-identity routing; no
outcome-dependent setting adjustment or retries are justified by this design.

Observed routing update: all four fixed April/October Stage A LPs returned
numerically continuous-feasible points, and none produced an exact capped
negative. Therefore no case meets this design's trigger for a new uncapped
MIP or its subsequent precision LPs. The still-pending binary Stage B can
provide capped positive witnesses for solver-free uncapped inheritance, or
leave cases unresolved; numerical MIP infeasibility alone does not satisfy
the exact-LP-negative trigger. No follow-up runner or optimization phase has
been implemented or executed. This is a null routing outcome, not a claim
that chronology has no effect in April or October.
