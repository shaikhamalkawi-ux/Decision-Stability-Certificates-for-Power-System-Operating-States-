# Post-pilot continuous relaxation and independently checked dual certificate

This protocol was written before running this strengthening experiment. It is
post-pilot development motivated by the first four paired-order MILP rejections
and the single-unit checker's inconclusive results. These five cases are not a
new held-out sample, and the existing paired-order protocol/results are unchanged.

The fixed cases are the verified July identity and the already archived hour
orders for seeds 26092600, 26092601, 26092602 and 26092603. Native inputs, the
repaired network dispatch, unit commitments and the original complete 41-unit
target means remain fixed. Each solve has a 60-second limit and one thread.

An independently assembled, continuous model retains aggregate hourly balance,
individual availability, fixed hydro, thermal minimum/maximum output linked to
commitment, transition identities, mutually exclusive startup/shutdown, rolling
minimum-up/down inequalities and all 41 mean equalities. P, U, Y and Z are all
continuous. Startup and shutdown at hour zero are fixed to zero, initial history
is mature and free, and the last dwell is clipped at the horizon. Removing network
constraints and integrality only relaxes the original operational problem. Native
on/on ramp constraints are omitted as in the pilot minimum-up/down formulation;
the separate archived audit establishes their redundancy for binary native units.

Before any solves, the identity's archived P/U witness and derived Y/Z are checked
against every row and variable bound of the assembled identity model at 1e-5.
The model matrix and every bound are archived per case, with input hashes and
row metadata, so subsequent certificate checking does not require an optimizer.

If an LP is feasible, its continuous vector is saved and independently checked
against all assembled rows/bounds. This only establishes LP feasibility and is
not a full operational witness. A time limit or other inconclusive status remains
unresolved. If HiGHS declares infeasibility, both orientations of its row dual ray
are examined. A status alone is not called an independently verified certificate.

For a multiplier vector y, let b be the sum of y_i times the lower row bound when
y_i is positive and the upper row bound when y_i is negative. Compute c = y^T A.
Let m be the maximum of c x over the box of column bounds. The exact inequality
b > m is a Farkas separation certificate. Nonzero multipliers on an infinite
selected row bound are invalid. All arithmetic for b, c and m uses Python rational
numbers obtained from the exact archived binary64 coefficients and multipliers.
No assumption that a numerically near-zero coefficient is zero is made.

In addition, require the separation to survive relaxing every finite row bound
and both bounds of every variable outward by 1e-5 in that bound's own units:
b - m - 1e-5 * (sum(abs(y)) + sum(abs(c))) > 0. This is an explicit numerical
robustness check, not a physical uncertainty model. Exact verification applies to
the archived floating-coefficient mathematical model, not exact original physical
measurements or unknown decimal source values. The certificate may retain many
hours and constraints; sparse multipliers alone do not prove minimum temporal
memory or raw-data compression.

Executable: `src/temporal_lp_certificate.py`. Results, archived models, multipliers,
and verification outputs belong exclusively to
`results/temporal_information/lp_certificate/`.
