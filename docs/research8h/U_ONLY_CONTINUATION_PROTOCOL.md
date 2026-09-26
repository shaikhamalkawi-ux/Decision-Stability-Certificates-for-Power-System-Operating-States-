# Equivalent projected model: computational continuation

This is a separately frozen computational continuation of the four unresolved
July full-network service cases, seeds26092600--26092603 in that order. Their
original 120-second configured MIP calls, all UNKNOWN without incumbents, remain
unaltered. The all-on and fixed-original-schedule restrictions also remain
separate failed restrictions. No completed unrestricted binary label is known
for these four cases when this protocol is written.

Reuse each exact archived matrix and all row/column bounds in
`results/research8h/service_network_mip`. Keep the same zero objective, the
180555.9189139999MWh cap on23fossil units, native DC network, generator identities,
input permutation, free mature initial state and clipped terminal residence
conventions. There are no named-generator mean constraints. Change only the
declared integrality mask: the4032U coordinates are integer, while the8064Y/Z
coordinates retain their continuous [0,1] bounds. This is an equivalent
projection onto physical dispatch, commitment and angle variables, not a new
unit-commitment formulation or a changed physical experiment.

## Exact projection argument and applicability audit

For integer U and a feasible continuous pair Y,Z, the transition equation is
Y_t-Z_t=U_t-U_(t-1). If the right side is1 or-1, the [0,1] bounds force the
usual (1,0) or (0,1) pair. If it is0, Y_t=Z_t>=0. Replace that equal pair by
(0,0). Equivalently define Y*=max(deltaU,0), Z*=max(-deltaU,0), with both initial
values0. This decreases Y and Z componentwise. It preserves transition and
exclusive-transition rows, and weakens every minimum-up or minimum-down row,
whose auxiliary coefficients are positive. All other rows are unchanged.
The recovered Y*,Z* are binary. Conversely every original binary feasible
point is feasible with the relaxed auxiliary integrality. Thus the projected
feasible sets agree exactly over real arithmetic.

Before solving, inspect the actual sparse matrix and bounds: only transition,
exclusive_transition, minimum_up and minimum_down rows may contain Y/Z; their
coefficient patterns and row senses must match the above argument. Check
Y/Z bounds0..1, initial bounds0, U bounds0..1, objective zero and the exact
old versus new integer intervals. Any mismatch stops the arm for diagnosis.
No stronger claim applies to models with other startup/shutdown constraints,
costs of unrestricted sign, history conventions or auxiliary-row couplings.

## Frozen computation and recovery

Write all case bindings, integrality arrays, source/protocol/input hashes and
structural audits before the first solve. Run one HiGHS MIP per case with
time_limit600seconds, presolveon, threads1, random_seed0, mip_rel_gap1e-8 and no
warm start. No retries, cap changes, seed substitution or adaptive options.
Archive full logs and actual elapsed times, including overshoot. Longer effort
and fewer declared integers both change from the original run, so this arm is
not a controlled speed comparison and cannot attribute any gain to one change.

For every returned vector, preserve the raw vector and its matrix residuals.
Only when finite rawU coordinates lie within1e-5 of0or1, round U to those binary
values and derive exact binary Y*/Z* from adjacent rounded U. Keep P and theta
unchanged. Save this recovered vector separately. Test it against the complete
original matrix/bounds and the native physical checker: dispatch availability,
fixed hydro, raw and rounded thermal coupling, transitions, observed residence
runs, native on/on ramps, nodal balance, branch ratings, angle/slack bounds and
the unchanged fossil cap. Admission requires both original-matrix and native
checks at1e-5, exact recovered binary coordinates, and a passing raw relaxed
matrix check. Numerical rounding is never justified solely by solver status.

A verified recovered point is a binary DC-network service admission at the
stated tolerance. It is not an exact-rational feasible point, economic optimum,
AC solution, field result or proof about all reorderings. A numerical MIP
infeasible status is numerical evidence only, not an exact binary certificate.
A timeout without a passing recovered witness remains UNKNOWN. Preserve failed
raw/recovered candidates and all prior outcomes. Post-run source/model hash
checks and independent witness replay are required before publication.
