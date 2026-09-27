# Flow-conserving DC encoding: separate model-variant design

Status: design only. No new model archive, coefficient-difference diagnostic, solver call or rational reconstruction has been run for this variant. The original fixed-schedule attempt is closed with 168 unresolved candidate points. It remains unchanged. This proposal cannot repair, relabel or retroactively validate that original encoding.

## Purpose and fixed cases

Test whether the first January hour-of-day comparison survives a different, explicitly conserving representation of the DC equations. Use exactly the existing January identity, positive control 26100200, and ordinary cases 26093200 and 26093201, with their archived source-hour maps and native packages from `results/research8h/hour_of_day/`. Retain both ordinary cases regardless of result; no new seed, redraw, week or replacement. Preserve the existing fossil cap **23195 MWh** in all four target models. This is a sensitivity analysis on known cases, not unseen replication or a novel network formulation.

The representation change is substantive at the level of exact binary64 rational models. Integer flow incidence will impose exact conservation, while the old angle-only nodal coefficients were formed with separate floating additions, and the old aggregate net load was also formed separately. The two exact feasible sets are not presumed equal or nested. Negative and positive claims must identify the new variant. The old exact certificates remain statements about their old models.

## New model and exact differences from the old model

Retain the original 23,016 coordinates P/U/Y/Z/theta and append 38 flow coordinates for each of 168 hours. The full variant therefore has 29,400 coordinates and the same 12,096 binary U/Y/Z coordinates. Keep the original P and theta boxes, including the discovered zero reference pin; keep all state boxes, transition, exclusivity and dwell rows, initial/terminal conventions, thermal output rows, native availability/hydro and the single fossil cap. No new ramp or boundary convention is introduced.

For each archived branch row, verify exactly two opposite nonzero angle coefficients, one common-hour pair and finite symmetric original limits. Let the positive coefficient be b_e > 0 at bus u and the negative coefficient be -b_e at bus v. Define outward flow orientation u to v and add the equality

```text
f_e - b_e theta_u + b_e theta_v = 0.
```

Use the original branch row limits as the lower/upper box for f_e. This exactly represents that old branch-flow restriction in the extended variables. It introduces no new reactance, branch limit, tap approximation or floating summation of branch coefficients.

Let D have +1 at the outgoing bus u and -1 at the incoming bus v for each branch. Replace each old nodal angle row by

```text
generator injection - D f = native nodal net load.
```

All incidence entries are the exact integers -1, 0 and 1. Keep the same generator-to-bus map and archived native nodal RHS. Omit the independently assembled aggregate-balance row. Summing these new nodal equations cancels every flow exactly and gives `sum(P) = sum(native nodal net load)` for that hour. The old archived aggregate `net` array is retained unchanged as provenance and for the difference report; it is no longer a second, independently rounded balance equation.

All four full capped variants are expected to have 34,513 rows: the old 34,681 less the 168 aggregate rows, with the 6,384 old branch rows replaced one-for-one by flow definitions and the 4,032 nodal rows replaced one-for-one by incidence equations. Actual row/column maps, counts and all retained coefficient/endpoint equality must be checked from the matrices before freeze. No row may be deleted by a heuristic near-zero test.

Preparation must report, as reduced exact rationals, every changed nodal angle coefficient after eliminating the new flow variables. If C_old is the old angle coefficient block, then the new eliminated block is `C_new = -D diag(b) D^T`; archive `C_new - C_old` with bus/row/branch mapping. Also record, for every original source-hour package, `sum(native nodal loads) - old aggregate net`. Validate the common branch block across every hour and case before storing a common difference table plus exact package maps. Count changed coefficients and report exact maximum magnitudes with optional display approximations. These are representation differences, not tolerances used to erase constraints. No value has yet been computed for this proposal.

## One identity basis proposal without coupling the hourly reconstruction

There is one design issue requiring an explicit choice: the weekly cap couples all hours. Keeping it inside the numerical identity proposal does not support independent 103-coordinate hourly basis reconstruction without a more complicated bordered linear system.

Recommended choice: assemble and freeze the full **capped** identity variant first; make its fixed-U/Y/Z numerical basis proposal by deleting only that cap row and using the original 23-fossil electricity objective. This is a declared proposal relaxation, not a change to the target model. Minimize the sum of hourly fossil electricity, solve once for a numerical basis, reconstruct its independent hourly blocks, then require the recovered exact point to pass every row of the full capped variant, including cap 23195. The same acceptance rule applies even if the numerical solve reports Optimal. Exact objective minimization is not claimed without a separate dual proof, which this arm does not propose.

The fixed identity schedule is the already canonical original January U/Y/Z schedule. No new integer solve, rounding of a new U or alternative commitment is permitted. After substitution, check every original constant-state row exactly. The proposal has 168 blocks of 103 continuous coordinates: 41 P, 24 theta and 38 flows; each has 110 continuous rows: 48 thermal inequalities, 24 nodal balances and 38 flow definitions. Check these counts and separability from actual coefficient supports. A previously verified original schedule is not automatically a verified point of the new variant.

Use one 60-second serial simplex call, presolve off, thread 1, seed 0, no warm start or retry. Extract one returned basis and reconstruct using the same reviewed exact endpoint logic and fraction-free arithmetic, now with blocks of at most 103 coordinates. Retain the 8192-bit arithmetic guard, fixed row/column order and a 900-second arithmetic limit; all 168 hours remain in the denominator. A singular basis, resource limit, unsupported status, violating point, or energy above the fixed cap gives no strict capped positive. Do not change the cap, basis, solver options or objective after failure.

## Strict point and positive-control acceptance

The new point artifact must include all P/U/Y/Z/theta/f coordinates as lossless indexed rationals and bind the new matrices, bounds, masks and native inputs. Verify all 34,513 full-model rows and all 29,400 boxes at tau=0, exact original binary states, flow definitions, native nodal equations, branch-flow boxes and the unchanged fossil cap. Supplementary native output/dwell/on-on-ramp checks keep the existing numeric-input conversion convention. For aggregate conservation, the new supplementary checker must use the **exact sum of native nodal loads**; reusing the old check `sum(P)==old net` would silently reimpose the very equation this variant intentionally omits. Keep the old `net` discrepancy report visible. Do not edit the closed old checker to accommodate this model.

If the identity is accepted, transfer P/theta/f rows with the already frozen control permutation. Its complete U sequence is preserved by construction; retain that chronological U and canonical Y/Z, rather than permuting transitions. The joint native packages and homogeneous fossil weights imply that static constraints and the exact energy sum transfer, but still check the actual control matrix, original binary mask, native dwell/ramp rules and cap directly. An accepted identity does not allow an unchecked control claim. If identity acceptance fails, retain the control as unestablished; do not replace it or run a control optimization.

No ordinary permutation is presumed positive from a transferred schedule. The new ordinary models leave all U/Y/Z choices free, with the same original unit constraints and bounds. The identity's fixed schedule is confined to its separate proposal.

## Two capped-target continuous calls and exact rays

For each of the two ordinary cases, solve exactly one continuous relaxation of its complete capped variant, retaining every original unit row but relaxing the original binary mask. Keep the new flow definitions, incidence equations, all boxes and cap 23195. Use 30 seconds per call, serial simplex, presolve off, thread 1, seed 0, no retry; use the same 23-fossil objective for a consistent new-variant ledger. The old HOD feasibility model had a zero objective; changing the objective in this separate variant does not alter its feasibility set and must not be described as a byte-identical objective inheritance from that archive.

If HiGHS reports infeasibility and supplies a ray, archive its raw multipliers and apply one prospectively fixed sign-admissible projection/orientation recipe from the already reviewed certificate machinery. Check every candidate against the actual new matrix/endpoints using exact rational row sums and finite column-box support, including every flow coordinate. Keep rejected candidates. No guessed deletion, coefficient threshold or sparse-support search is part of this design.

A strictly positive tau=0 separation is an exact negative for the new continuous relaxation and therefore its binary subset. Also report the exact separation after uniform finite-bound expansion by the historical `Fraction.from_float(1e-5)`, as a separate robustness flag. The latter expansion now also touches flow boxes and flow-definition rows; it is a declared formal convention for this new encoding, not an equivalence to the old expanded model. Freeze these two readouts before execution. Numerical infeasibility without a verified ray is UNKNOWN; an LP point is continuous evidence only, never a binary positive. No MIP call, cap sweep, alternative ray search or extra case is proposed.

## Call order, time feasibility and independence

Freeze all four full capped models, the derived cap-deleted fixed-state proposal, complete provenance/difference maps and call/routing plan **before any solve**. Recommended fixed optimizer order is: identity proposal (60 seconds), target 26093200 (30 seconds), target 26093201 (30 seconds). Running all three calls before the bounded reconstruction prevents the identity arithmetic from selecting which ordinary cases receive a call. There are at most three LP calls and zero MIPs. Process the two saved ray candidates in fixed case order, then the identity hourly basis and conditional mapped control, all under a separately frozen arithmetic limit and total phase budget.

A prospective total phase budget of 1800 seconds comfortably contains the configured 120 solver seconds, 900 identity-arithmetic seconds and bounded ray/replay/serialization allowance. At each actual optimizer call, check both remaining phase time and remaining time until **2026-09-27 04:00 UTC**, with start guards of 65/35/35 seconds and rechecks after launch-decision I/O. Arithmetic also stops at its fixed limit or the absolute cutoff, with explicit unevaluated cases/hours. Preserve actual soft overshoots and all nulls; no call starts after the cutoff. At design time (approximately 02:40 UTC) this appears feasible if implementation/review/preparation gates complete promptly, but runtime has not been measured for the 103-coordinate reconstruction and no execution is authorized by that estimate.

The next authorized stage, if root accepts this choice, would be separate source/protocol drafting only. Reuse reviewed pure arithmetic/NPZ helpers through frozen hashes where appropriate; add a separate variant-native checker rather than modify old sources. Independent preparation must verify all original-to-new retained rows, exact graph equations/incidence, difference reports, oldcap arithmetic, source-hour maps, original masks, and the cap-deletion/fixed-state proposal relation. Separate execution GO is required after that gate. Post-run independent ray and rational-point replay must precede any scientific claim.

The decisive result would be strict capped identity and control positives together with exact capped negatives for the two known order perturbations in this separately documented conserving representation. Any missing component limits that statement. Conflicting results narrow representation robustness; they do not invalidate correctly checked historical proofs about different models. Even a complete success remains DC unit-commitment evidence on synthetic known-case reorderings, with no AC/security, weather-plausibility, field-operation or novelty claim.
