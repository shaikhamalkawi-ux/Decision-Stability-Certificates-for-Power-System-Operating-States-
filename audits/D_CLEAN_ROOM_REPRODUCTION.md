# Workstream D - Clean-room numerical reproduction

## Result

**PASS: 26 of 26 audited numerical claims reproduced within declared
tolerances.**

The clean-room script imports no DSC-Grid analysis module. It reads released
CSV/ZIP artifacts, independently reconstructs empirical L1 transport with a
Hungarian assignment, repeats the GB coordinate filtering and clock-hour
grouping, and recomputes repair sums and AC witness summaries.

The audit covers:

- all seven RTS mean movements and full empirical W1 values;
- the full-precision January-July RTS lock;
- six principal PyPSA-GB counts and transport quantities;
- the July 8.020508-MW relaxation-repair artifact sum;
- the July 11.926296-MW network-witness artifact sum; and
- both AC successful-witness counts and restoration medians.

Rounded main-table values use a 0.0005-MW tolerance; full-precision locks use
1e-7 MW or tighter. The claim-by-claim CSV and JSON summary are in
`results/clean_room_audit`, and the independent script is in
`code/clean_room_audit.py`.

This arithmetic reproduction is deliberately distinct from solver claims. It
confirms that the released raw/tabular artifacts imply the reported numbers;
solver optimality or infeasibility is supported only by the separate exact,
relaxation, or feasible-witness records identified in the claim ledger.
