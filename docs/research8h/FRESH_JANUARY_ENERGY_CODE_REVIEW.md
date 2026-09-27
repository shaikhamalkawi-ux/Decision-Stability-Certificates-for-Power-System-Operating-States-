# Fresh January energy: independent code and protocol preflight

Reviewed 2026-09-27, before this arm preparation/optimization. Verdict: **PASS for preparation; no mathematical or implementation blocker found in the reviewed source.** This is not the prepared-archive or execution gate. No producer file was changed and no model or optimizer was run.

Source: `src/research8h_fresh_january_energy.py`, SHA256 `0ad4536f7b9be7d681a4e164eb8546cc1755ddccb2b49e90887e92d4f08b250d`. Protocol: `docs/research8h/FRESH_JANUARY_ENERGY_PROTOCOL.md`, SHA256 `56ad8786aedeabab42374bb91d923c6453c4f468414a19bea54d352a3e9e8bca`. The protocol path is under `docs/research8h/`. Both complete files and the imported exact-bound arithmetic were inspected.

## Model and provenance

All four fixed targets enter in seed order, including the capped UNKNOWN. The two identity matrices remain the original uncapped references. Each target removes one and only one row whose family, finite upper endpoint, negative-infinite lower endpoint and complete coefficient vector are checked against the fossil objective and its own weekly cap. No mean row is introduced. Preparation compares the identity after equivalent cap removal, all retained bounds, native inputs and full masks. The exact energy-derived caps are checked separately for the two weeks; no first-week constant is reused. Target package and calendar mappings retain complete arrays, hour of day and the fixed outer 48-hour blocks. Actual native fossil/thermal rosters and the 3,864-coordinate objective are checked; nuclear is excluded.

Existing review output bindings and both closed input manifests are checked before creating the output tree. Preparation binds parent artifacts and transitive local sources, freezes all six cases, checks both reference witnesses, and audits the actual U-only projection. The original 12,096-column integrality mask remains the acceptance mask; the 4,032-column U-only mask is a solving device. An independent archive replay is still required.

## Arithmetic and acceptance

For signed d selecting finite row endpoints, every feasible x obeys c*x >= beta + min_box (c-A^T*d)*x. The inspected helper computes products, sums, residual signs and the box minimum using exact Fractions of binary64 values. Widening every finite row and column endpoint by tau subtracts tau times the sum of the two L1 norms. Projection of inadmissible row signs is explicit and preserved; the result does not require numerical dual optimality. The zero-row-dual fallback is valid and is not clamped to zero. The strongest available bound is compared against accepted uppers to fail closed on a contradiction.

The target upper requires raw/recovered matrix checks, exact expanded membership under the full original binary mask, and the native no-cap check. P and theta bytes are retained; only eligible near-binary U is rounded and canonical Y/Z recovered. A continuous point or solver bound cannot become a binary upper. Absence of an accepted upper remains NO_UPPER. Strict membership is separate from the uniform 1e-5 finite-endpoint expanded model; neither is a field-measurement uncertainty claim.

The optimum-difference enclosure [L_T-U_I,U_T-L_I] and, when both lower bounds are positive, ratio enclosure [L_T/U_I-1,U_T/L_I-1] are valid. The unchanged reference incumbent is only an upper witness. Six-decimal floor/ceiling fields use integer arithmetic and preserve negative endpoints. Exact rational endpoints remain authoritative; the approximate float field alone is not an outward enclosure.

## Calls and limits

The phase clock starts before validation and native loading. The schedule is two identity LP60 calls, four target MIP600 calls, then four target LP60 calls. After model construction, each actual solver.run has the 65/605-second minimum-remaining guard for both phase and UTC cutoff. Explicit default arguments bind the correct case in each lambda. Exclusive execution marker, distinct LP/MIP directories, fixed options and complete denominator prevent a silent retry or label-based skip. The protocol correctly describes 3,600 seconds and solver time limits as soft allocations/start guards; actual overruns and skipped calls are recorded. No warm start, adaptive target, new identity MIP or extra solve was found.

## Remaining gates

Independently verify the prepared manifest, exact matrix/cap deletion and identity equivalence, package mappings, masks, objective, both reference points and zero-dual bounds. Root must separately authorize execution after that PASS. Any eventual upper/dual/interval and accounting claims need a post-run independent replay. Existing capped labels and artifacts are unchanged.
