# Common numerical expansion range for fixed closed evidence: design only

Status: PROPOSED; no sensitivity calculation, implementation, preparation or replay has been performed. This design was requested after the corresponding capped and energy results closed. It is a retrospective assessment of fixed evidence, not a prospective scientific replication, a new robustness theorem, physical uncertainty analysis or information-minimality result. The portable-wrapper review remains a separate gate and takes priority before any implementation phase here.

## Question and frozen cases

For what common numerical expansion values tau do the already archived binary witnesses and fixed row multipliers jointly certify the same claims? Only tau varies. Matrices, nominal row/column bounds, finite/infinite endpoints, objectives, original binary masks, cap values, packages, input orders, witnesses and multipliers remain unchanged. In particular, the nominal cap B is fixed; its effective expanded row endpoint is B+tau.

Use every prescribed member of these two declared groups:

| Claim group | Fixed targets | Identity/control context |
|---|---|---|
| First-week HOD capped negatives | 26093200, 26093201 | Original January week 1 and control 26100200; nominal cap 23195 |
| Fresh-week HOD capped negatives | 26093210, 26093220, 26093221 | Week 2 original/control 26100210 and week 3 original/control 26100220; caps 26532 and 48319 |
| First-week HOD positive optimal-energy differences | 26093200, 26093201 | Same uncapped week 1 identity |
| Fresh-week HOD positive optimal-energy differences | 26093210, 26093211, 26093220, 26093221 | Same uncapped week 2 or week 3 identity |

The capped certificate denominator is five, comprising every closed HOD cap-negative case. The underlying six-target capped ledger must also be displayed, with 26093211 explicitly UNKNOWN and without a negative-certificate sensitivity range. Its inclusion in the six-target energy group does not resolve its separate capped question. The two earlier unrestricted first-week targets, whole-day permutations, seasonal unknowns and subset-template points are outside this bounded calculation.

For the capped group include all three identity witnesses and all three preselected class controls as additional fixed positive evidence. Report them separately from the five ordinary negatives. For energy, include all three original identity witnesses and all six target upper witnesses against the corresponding uncapped models. Repeated vectors may share bytes, but their capped and uncapped model-point relations are distinct and must not be confused.

## Existing robustness information

This is not the first ray-wise tolerance diagnostic. Existing `dual_certificate.json` records already contain `verification.maximum_uniform_bound_relaxation` as a floating diagnostic, in addition to nominal and outward-expanded gap records. The proposed addition is exact endpoint arithmetic plus simultaneous positive-witness, negative-ray and energy-increase conditions across the fixed declared cases. Recompute the relevant quantities from the archived coefficients and multipliers rather than treating that floating threshold as an exact endpoint.

## Point threshold: lower endpoint is included

Let `l <= A x <= r` and `a <= x <= b` be a fixed archived model. Every column endpoint is finite; infinite row endpoints are omitted from violation calculations. Let J be the original 12,096 U/Y/Z coordinates, and require each `x_j` in J to be exactly 0 or 1. All vector coordinates and matrix coefficients must be finite. Increasing tau cannot repair failure of the exact binary-mask requirement.

For a fixed accepted vector x define

`p(x) = max(0, max_i(l_i-(A x)_i), max_i((A x)_i-r_i), max_j(a_j-x_j), max_j(x_j-b_j))`,

using only finite row endpoints. Every operation is on exact rational interpretations of the archived binary64 values. Then this fixed point belongs to the uniformly expanded model exactly when `tau >= p(x)`. Its lower endpoint is closed. At tau below that threshold this point fails; no statement about other feasible points follows.

Archive the exact threshold, maximum row and column violation, original binary-mask check, model/vector hashes and the constraining row/column side. If the maximum is zero, report that fact rather than inventing a positive violation. Capped identity and class-control points must be checked against their capped model, including its cap row. An uncapped point check alone is insufficient for a capped positive claim.

The future runner can compute each distinct model/vector/mask combination once, then reuse its exact threshold. A safe cache key includes matrix, bounds, original mask and vector digests, not a matrix digest alone. No search for a better witness or rescaling/editing of the saved vector is allowed.

## Fixed capped ray: strict upper endpoint

For each saved admissible signed row multiplier d, use the exact archived projected multiplier values. Independently verify any archived raw-to-projected sign operation and finite selected row endpoints; do not silently change the supplied multiplier or choose a different certificate.

Set

`q = A^T d`,

`beta = sum_i d_i*(l_i if d_i>0 else r_i)`,

`M(q) = sum_j q_j*(b_j if q_j>=0 else a_j)`,

`Delta0 = beta - M(q)`,

`S_ray = sum_i |d_i| + sum_j |q_j|`.

The exact expanded gap is `Delta(tau)=Delta0-tau*S_ray`. For `S_ray>0`, the fixed certificate separates strictly when `0 <= tau < Delta0/S_ray`. Its upper endpoint is open: equality gives zero gap and does not certify infeasibility.

For each of the five capped pairs, report the pairwise range `[p(x_identity_capped), Delta0/S_ray)`, if nonempty. The additional week-matched class-control requirement may also be displayed as `[max(p(identity),p(control)), Delta0/S_ray)`. Both comparisons use the same original package observation, nominal cap and numerical tau; the class control is additional positive evidence, not another ordinary negative case.

The ray scale is arbitrary. Delta0 and the expanded gap are not MWh costs. The ratio threshold is unchanged under exact positive rescaling, but the implementation must use the fixed archived multiplier rather than construct a numerically rescaled replacement.

## Fixed energy dual: strict optimal-difference upper threshold

For each of the six target uncapped models, use its one saved projected LP row-dual vector. Do not tune multipliers or select among alternative bounds as tau changes. Define

`eta = c - A^T d`,

`L0 = beta + sum_j min(eta_j*a_j, eta_j*b_j)`,

`S_energy = sum_i |d_i| + sum_j |eta_j|`,

`L_T(tau) = L0 - tau*S_energy`.

All quantities are recomputed exactly, including the finite-box stationarity-residual correction. No exact dual stationarity or numerical optimal status is assumed. The already archived zero-dual baseline may be reported as provenance but is not substituted or maximized against this fixed-dual function after inspecting sensitivity results. At the recorded tau0, reconcile the saved selected bound and this fixed projected-dual bound explicitly.

Let `U_I=c^T x_identity` be the exact energy of that week's fixed accepted binary identity witness, and let `x_target` be the fixed accepted binary target upper witness. U_I is constant as tau changes. Both points must belong to their respective uncapped expanded models at the tested tau. Their existence plus finite boxes establishes finite attained binary optima.

For `S_energy>0`, the fixed evidence proves a strictly positive optimum difference whenever

`max(p(x_identity_uncapped),p(x_target_uncapped)) <= tau < (L0-U_I)/S_energy`.

The proof is `E*_target(tau)-E*_identity(tau) >= L_T(tau)-U_I > 0`. It does not assert that either saved witness is optimal. It needs neither an identity lower bound nor a target-optimum ratio, so those are outside this bounded sensitivity arm. In particular, do not infer a varying percentage bound from this calculation without the additional denominator evidence that such a statement would require.

## Common ranges and degenerate cases

Report all individual witness thresholds, all five ray ranges and all six energy ranges before the aggregates. Then produce three explicitly named intersections:

1. Capped evidence: all five ray inequalities and all three capped identities plus all three capped class controls.
2. Energy evidence: all six positive-energy inequalities and all three uncapped identities plus all six uncapped target uppers.
3. Joint evidence: the intersection of the first two, using exactly the same tau.

For a nonempty finite intersection the result is `[max required point thresholds, min strict proof thresholds)`. Equality of endpoints means the common range is empty. Save every active limiting case/point, including exact ties; do not drop a restrictive case. Keep individual ranges even if a common intersection is empty.

Handle zero slopes prospectively. For `S=0`, a strictly positive numerator imposes no finite upper limit; a zero or negative numerator gives no nonnegative tau satisfying the strict proof. For `S>0`, a nonpositive numerator likewise gives no valid nonnegative strict-proof range. Represent an unbounded upper endpoint with an explicit type/null field rather than JSON Infinity. A negative slope, nonfinite multiplier or inadmissible endpoint is an input/proof error, not a reason to take an absolute value or clamp a threshold. The archived nonzero rays and nonzero fossil objective are expected to give positive slopes, but the runner should verify this rather than rely on it silently.

There is no imposed `tau<1` restriction in this arm. The exact full-{0,1}-mask point and continuous-certificate/dual algebra hold with the original binary condition explicit; this calculation does not rely on the no-dwell canonical-lift theorem. No physical interpretation is attached to large or small numerical tau.

The exact recorded reference value is `tau0=Fraction.from_float(1e-5)`, namely `5902958103587057/590295810358705651712`. Each claimed interval must contain tau0, with a non-strict lower and strict upper comparison. Failure is a discrepancy with the closed evidence that must be reported and investigated; do not choose another ray, change tolerance or retry an optimizer to conceal it. Whether the common range extends strictly below and above tau0 is an outcome to be computed later, not asserted in this design.

## Display rules: validity intervals round inward

Exact fractions are authoritative. These are certified validity ranges, unlike the previously reported enclosures of unknown optimal-energy differences.

A safely displayed decimal subset must round its lower endpoint UP and its strict upper endpoint DOWN, retaining the open upper endpoint. Outward rounding would include uncertified tau values and is forbidden for a displayed valid band. Separately labelled outward enclosures of an endpoint may be reported, but must not be presented as a validity interval. If the rounded decimal subset collapses, retain the exact nonempty interval and report that the chosen decimal precision cannot display a nonempty safe subset; do not call the exact range empty.

Use a fixed display precision before execution, proposed 18 digits after the decimal for the safe subset, plus exact numerator/denominator and optional scientific-notation approximations clearly labelled as descriptive only. Report exact comparisons to tau0 and exact endpoint/tau0 ratios if useful, without rounding those ratios into stronger claims.

Outside a stated range say only that this fixed evidence no longer certifies the paired claim. A failed point below its threshold does not prove model infeasibility. A zero/nonpositive certificate gap above its threshold does not prove feasibility. A nonpositive energy bound does not prove that the optimum difference vanishes or reverses. These limits also apply at strict upper endpoints.

## Authoritative input map

All paths below are relative to the shared repository. Later preparation must freeze exact hashes for every listed artifact, its transitive provenance and the future runner/protocol before calculations begin.

| Evidence | Model / mask / vector or multiplier source |
|---|---|
| First-week two negative rays | `results/research8h/hour_of_day/seed_26093200/lp/` and `seed_26093201/lp/`: `matrix.npz`, `bounds.npz`, `dual_certificate.json`, `raw_solver_ray.npz`, `row_metadata.csv.gz`; compare matrices/bounds to the corresponding original-mask parent directory |
| Fresh three negative rays | `results/research8h/fresh_january_weeks/targets/{seed_26093210,seed_26093220,seed_26093221}/lp/`, same artifacts and parent-original-mask equality |
| Three capped identity positives | `hour_of_day/january_identity/`, `fresh_january_weeks/targets/week_2_identity/`, `fresh_january_weeks/targets/week_3_identity/`: full capped `matrix.npz`, `bounds.npz`, `integrality.npz`, `constructive_vector.npz` |
| Three capped class controls | `hour_of_day/seed_26100200/`, `fresh_january_weeks/targets/seed_26100210/`, `fresh_january_weeks/targets/seed_26100220/`: full capped model, original mask and `constructive_vector.npz` |
| First-week uncapped identity | `results/research8h/energy_lp_refinement/january_identity/` model, `objective.npz` and `original_integrality.npz`; vector `hour_of_day/january_identity/constructive_vector.npz`; confirm inherited identity relation against `hour_of_day_uncapped/reused_identity_bounds.json` |
| First-week two target energy proofs | `results/research8h/hour_of_day_uncapped/{seed_26093200,seed_26093201}/`: uncapped model, `objective.npz`, `original_integrality.npz`, `lp/projected_row_dual.npz`, `lp/raw_duals.npz`, `lp/exact_lower_bound.json`, `lp/exact_stationarity_residual.json`, `mip/recovered_vector.npz`, exact point and MIP result records |
| Two fresh uncapped identities | `results/research8h/fresh_january_energy/{week_2_identity,week_3_identity}/`: uncapped model, objective, original mask, `reference_upper_vector.npz`, `reference_binding.json` |
| Four fresh target energy proofs | `results/research8h/fresh_january_energy/{seed_26093210,seed_26093211,seed_26093220,seed_26093221}/`: uncapped model, objective, original mask, projected/raw LP duals, exact bound/residual records and recovered MIP vector/point records |

The first two table rows use their exact sparse multipliers encoded in the certificate JSON, not a floating diagnostic field. The six energy rows use each saved projected row dual with its matching matrix, finite box and objective. No vector may be moved between weeks or capped/uncapped bound sets because a matrix hash happens to match.

Use the existing prepared manifests, independently closed post-run reviews and exact bracket JSONs to bind the results. Relevant manifest anchors already include HOD `078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc`, fresh targets `56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd`, first-week HOD uncapped `b0ffca41db74d7278c001c776ae3b8656272994d083c8fc215ecbbf665020f8a`, and fresh energy `44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a`. Preserve their bytes and explicit path remapping; a future prepared manifest is still required for this new calculation. The capped UNKNOWN ledger and all six energy target IDs must be separately bound.

## Proposed implementation and review gates

If the parent later authorizes implementation, use a new source/protocol/output directory, provisionally `src/research8h_tau_fixed_evidence.py`, `docs/research8h/TAU_FIXED_EVIDENCE_PROTOCOL.md`, and `results/research8h/tau_fixed_evidence/`. Keep every previous wrapper, model, result, certificate and manuscript unchanged. Prefer standard-library exact fractions and the pinned existing NPZ/CSR kernel, without a solver or native model import.

Prepare a fixed case descriptor, all hashes, model/mask equivalences, source week/cap/objective identities and an output directory that does not overwrite historical evidence. Independent source/protocol and prepared-input gates precede one explicitly authorized arithmetic execution. The current design does not authorize any of those steps.

Focused synthetic checks should cover: a positive point accepted exactly at its maximum violation; a fractional original-state coordinate rejected regardless of tau; a cap row affecting the capped point threshold; exact zero certificate gap at the open endpoint; an energy inequality strict only below its endpoint; zero slope with positive/zero/negative numerator; nonpositive numerator with positive slope; tied limiting cases; empty common intersection; inward versus outward decimal rounding; exact tau0 at a lower or upper endpoint; and a numerically displayed collapsed subset of a nonempty rational interval. No synthetic check needs an optimizer or edits to frozen files.

The future readout should make the common range and its limiting evidence clear, retain every case and degenerate result, and explicitly acknowledge the pre-existing per-ray robustness diagnostics. A wider common numerical interval would strengthen the documented stability of these fixed certificates and witnesses under this particular mixed-unit convention; it would not establish physical uncertainty robustness, field validity, a new independent network or a minimal sufficient temporal summary.
