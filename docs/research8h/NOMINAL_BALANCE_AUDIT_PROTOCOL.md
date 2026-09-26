# Exact nominal balance-consistency audit

This is a read-only arithmetic audit of all four original seasonal reference
archives (January, April, July, October), with no optimization or model change.
The archived positive vectors so far establish membership in the uniformly
expanded binary64 model, not the strict nominal model. This audit asks whether
nominal aggregate and nodal equalities have exactly the intended redundancy.

For every one of the 168 hours in each week, form the exact rational difference
between its aggregate-balance row and the sum of its 24 nodal-balance rows.
Verify that all selected rows are equalities. Archive every nonzero coefficient
and the right-hand-side difference. Test whether the resulting equality can be
satisfied within the original column box by computing its exact minimum and
maximum. Check both corresponding signed row multipliers with the independent
standalone Farkas checker at tau zero and at the existing binary64 1e-5.

A strict separation would identify a floating-point encoding obstruction,
not a physical temporal obstruction. A nonseparating difference does not prove
the strict model feasible. An expanded separation contradicting an already
verified expanded point would require stopping for diagnosis. No coefficient,
bound, archived model, or previous result is repaired or replaced. Findings are
reported for all four weeks and all hours, including null results. This audit
does not prove arbitrary numerical stability or justify a different tolerance.
