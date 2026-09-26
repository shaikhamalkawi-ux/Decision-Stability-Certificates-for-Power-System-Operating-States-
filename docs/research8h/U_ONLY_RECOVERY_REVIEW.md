# Independent review of U-only integrality and auxiliary recovery

Review date: 2026-09-26 UTC. This review concerns the prospective continuation
in `src/research8h_u_only_continuation.py` and
`docs/research8h/U_ONLY_CONTINUATION_PROTOCOL.md`. It does not report a solve or
an empirical outcome. The reviewer did not call an optimizer or change the
runner, protocol, archived models, or previous results.

## Exact claim and proof

For the particular archived models, relaxing integrality of startup Y and
shutdown Z leaves the feasible projection onto (P,U,theta) unchanged, provided
U remains binary. This is an equivalence observation about this formulation,
not a new unit-commitment formulation or an approximation guarantee.

For each unit and t >= 1, write delta = U[t] - U[t-1]. The transition row gives
Y[t] - Z[t] = delta, with 0 <= Y[t],Z[t] <= 1. Since U is binary, delta is -1,
0, or 1. For delta = 1 the bounds force (Y,Z) = (1,0); for delta = -1 they
force (0,1). For delta = 0, Y = Z >= 0 and replacing both by zero decreases
each auxiliary coordinate. Define the canonical recovery by

    Y*[0] = Z*[0] = 0
    Y*[t] = max(U[t] - U[t-1], 0)
    Z*[t] = max(U[t-1] - U[t], 0).

The initial values already have fixed-zero bounds. The recovered auxiliaries
are binary, remain within their bounds, satisfy each transition equation and
Y* + Z* <= 1, and are componentwise no larger than the original auxiliaries.
Every minimum-up row has the form sum(Y in a window) - U[t] <= 0; every
minimum-down row has the form sum(Z in a window) + U[t] <= 1. Reducing Y/Z
therefore preserves these rows. All other rows are free of Y/Z, so the same P,
U, and theta still satisfy them. Conversely, every original binary feasible
point belongs to the formulation with continuous Y/Z. This proves equality
of the projected feasible sets over exact real arithmetic.

When both actual residence windows include their current auxiliary (as in
the positive-duration native construction), an even stronger observation
holds: U[t] = 0 forces Y[t] = 0 by the minimum-up row, and U[t] = 1 forces
Z[t] = 0 by the minimum-down row. Together with transition, Y/Z are already
canonical in an exact feasible point with binary U. The recovery argument
above is sufficient without relying on this stronger property.

The proof requires neither an optimal solution nor a dual argument. The
objective here is identically zero, so feasibility is the entire task. An
objective or additional constraint involving auxiliary variables would need
its own analysis. In particular, arbitrary startup costs, startup-dependent
ramps, auxiliary lower bounds, logical coupling, terminal conventions, or
initial-history equations are not automatically covered. The existing free,
mature initial state and clipped finite-horizon residence convention are
preserved; no cyclic or alternative-boundary invariance is claimed.

## Implementation review

The runner reuses each of the four original sparse matrices, row and column
bounds, zero objective, native input arrays, and metadata. It changes only the
integrality mask from the 12,096 U/Y/Z coordinates to the 4,032 U coordinates.
Its sparse audit checks the transition and exclusive-transition patterns,
the signs and row senses of residence sums, fixed initial auxiliaries, and
the absence of Y/Z from every other row. Checking exact residence-window
lengths is unnecessary for this projection proof: componentwise monotonicity
holds for any of the audited positive-coefficient sums. Native duration
semantics are separately checked when admitting a recovered witness.

All four cases are prepared and their bindings, integrality masks, audits,
and input manifest are written before the first optimization call. The
declared calls are one per case, in seeds 26092600 through 26092603 order,
with 600 seconds, one thread, presolve on, random seed zero, zero objective,
and no warm start or retry. The runner preserves the original results and
checks source/input hashes again after the continuation. The separate longer
time allowance and altered integrality mask prevent attributing any solver
improvement specifically to the reduced integer count.

The admission path is appropriately conservative:

- It archives and checks the raw returned vector, without trusting solver
  status as a feasibility certificate.
- It permits recovery only for finite vectors whose U entries lie within
  1e-5 of a member of {0,1}.
- It saves a separate vector with exactly rounded binary U and canonical
  binary Y/Z, leaving P and theta unchanged.
- It checks that recovered vector against the complete original archived
  matrix and bounds, then against native availability, commitment coupling,
  actual residence runs, on/on ramps, nodal balance, branch limits, angles,
  and the unchanged aggregate fossil-energy cap.
- It requires the raw matrix check, recovered matrix check, and native
  physical check all to pass. The original raw commitment coupling is
  checked through the raw matrix; the native checker receives the recovered
  commitment and checks that recovered coupling independently.

The native checker calculates the fossil-energy sum and its cap excess using
exact rational interpretations of the binary64 dispatch and budget before
applying the declared 1e-5 MWh acceptance tolerance. No named-unit mean target
is added. Numerical MIP infeasibility is explicitly labelled numerical and
not an exact certificate; an unresolved call without a passing recovered
witness remains UNKNOWN. An inconsistency between an infeasible status and
an admitted witness raises an assertion instead of silently choosing a label.

## Numerical limits and publication interpretation

The exact theorem assumes exact binary U and exact feasibility. It does not
justify rounding an approximate point by itself. Rounding U can change
capacity-coupling residuals by a generator's scale, and reconstructing Y/Z
can expose residence violations. The complete recovered checks are therefore
essential, even when all raw U entries meet the integrality tolerance.

A passing witness is a numerical binary DC-network service admission at the
stated tolerance. It is not an exact-rational feasible point, a minimum-cost
or minimum-energy solution, an AC or field validation, or a guarantee about
other permutations. In particular, any positive exact cap excess within the
stated tolerance must remain visible in the saved physical audit.

Any passing result should receive an independent replay of both the original
archived matrix and the native physical rules, with manifest hashes verified,
before publication. The old 120-second outcomes remain UNKNOWN regardless of
what this separate continuation finds. There is no identified mathematical
or implementation blocker in the reviewed source/protocol.

## Independent archive scan

An additional read-only scan checks the four archived matrices directly,
without importing the continuation runner or HiGHS. The proof and code
review above was completed before the root authorized launch. The extra
archive scan remained running when the root proceeded, relying also on the
runner's fail-closed sparse audit before its first solve. The additional
scan subsequently exited with shell status 1 and no captured output after
prolonged host delay. It supplies no passed independent archive audit. This
extra scan is therefore not represented as a completed pre-launch gate.
Any successful read-only rerun will be recorded separately; none is claimed
at this checkpoint.
