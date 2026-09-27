# Closed result: strict witnesses and negatives in a distinct flow-conserving DC model

Independent post-run replay passes. The January identity and the fixed HOD/U-class control both have exact rational binary feasible points at **tau=0**, under the unchanged 23195 MWh fossil-electricity cap. Both ordinary HOD targets have exact infeasibility certificates for their full continuous relaxations, so their binary models are infeasible as well. These statements concern the separately declared flow-conserving DC variant. They do not change any result for the old independently rounded angle model.

| Fixed case | Verified result | Exact-check summary |
|---|---|---|
|January identity|Strict capped binary positive|34513 rows,29400 boxes/coordinates and12096 binary states; native checks pass|
|Control26100200|Strict capped binary positive|Direct full-model/native check;14 source-hour positions change; exact energy preserved|
|Ordinary26093200|Strict continuous negative, hence binary negative|Strict gap177.6127556277553; expanded gap176.60074849462814|
|Ordinary26093201|Strict continuous negative, hence binary negative|Strict gap345.6330934751227; expanded gap344.47516106401184|

The ordinary denominator is two. Identity and class control remain separately reported controls. The decimal gaps above summarize archived exact rational fractions; they depend on multiplier scaling and are not energy penalties. Expanded gaps use exactly `Fraction.from_float(1e-5)` on this variant's finite row and column endpoints.

The two positive points have identical exact fossil energy, approximately **22964.941239556698 MWh**, with approximately230.0587604433019 MWh of slack below the cap. The lossless energy fraction and all29400 rational coordinates are archived. This is a feasible energy upper bound, not a proof of the globally optimal binary objective. The identity proposal deleted the cap and fixed the inherited canonical schedule; its recovered point then passed the full capped model. All168 hourly reconstructions passed, followed by complete matrix, original binary-mask and direct native checks. The mapped control was independently checked, including native on/on ramps.

## Representation and preserved scope

The variant retains the old physical packages, unit/state/dwell rows, mature free initial boundary, clipped final residence, original P/theta/state boxes, topology, branch limits, fossil roster and cap. It introduces38 line flows/hour, exact existing paired branch coefficients in flow definitions, and integer nodal incidence. It omits the separately rounded aggregate equation; exact summation of native nodal loads supplies aggregate conservation. Each full capped model has34513 rows,29400 columns and142396 nonzeros.

Eliminating flows changes15 entries in the common24-by-24 nodal angle operator compared with the old independently rounded operator. The largest absolute coefficient difference is1.3642420526593924e-12. In160of168 hourly packages, exact summation of native nodal RHS values differs from the old rounded aggregate RHS; the largest absolute difference is1.3145040611561853e-13. Every nonzero coefficient and RHS difference is archived as a rational number and retained, without rounding away small differences. No feasible-set nesting or exact equivalence between the encodings is claimed.

The old nominal exact-witness attempt remains168 unresolved candidates. These new strict points do not repair or relabel that attempt. The new result supplies strict mathematical evidence within a separately specified flow-conserving DC representation on these already known January cases; it establishes no unseen-week replication, physical measurement exactness, AC/security feasibility, field experiment, dispatch instruction or formulation novelty.

## Complete execution and certificate accounting

One prepared execution made exactly three continuous LP calls: identity proposal0.9297020999947563s, ordinary00 1.7394686999905389s, ordinary01 1.6502518999914173s. Total optimizer time was4.3194226999767125s, under the fixed60/30/30s limits. There were no MIPs, retries, alternate bases, additional schedules, cap changes or warm starts.

All four predetermined ray candidates were retained for each ordinary case. Both raw orientations were rejected for selecting an infinite row endpoint. In both cases the positive sign-projected candidate passed strict and expanded separation; the negative sign-projected candidate was valid to evaluate but nonseparating. Projection removed only sign-inadmissible row multipliers, and each complete candidate was rechecked exactly against the actual full new matrix and every finite box.

Preparation took18.94975080000586s and bound103 inputs. The execution marker records03:10:52.363023UTC and4.538820200017653s of initial validation. The execution phase took141.45142009999836s, including128.7444198000012s of shared arithmetic, against1800/900s budgets. There were no arithmetic or phase overruns and no skipped hours or targets. Final closeout reporting/inventory is separate from these execution timings.

The independent post-run replay took24.78498260001652s with zero optimizer calls and no producer-source imports. It checked both full rational points, all original binary states, native rules, exact control mapping/energy, both targets' complete four-candidate ray sets, the103 frozen bindings and unchanged producer outputs, plus all three call and168-hour ledgers. The independent preparation review separately verified every source-to-variant row, native package, graph, cap, mask, all16032 constant-state rows and all18480 proposal rows. Its first reviewer-only NPZ-key subset assertion failure was preserved and corrected without changing producer files.

## Replay artifacts

- Frozen input manifest: `input_manifest.json`, SHA256 `0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4`.
- Strict points: `january_identity/rational_point.json` and `seed_26100200/rational_point.json`, with corresponding `strict_point_check.json` files.
- Selected separators: each ordinary directory's `ray_+1_projected.json`; all raw rays, rejected candidates, solver logs, exact checks and full models are retained.
- Native and encoding provenance: each full case's `native_inputs.npz`, `permutation.csv`, `graph.json`, `native_spec.json` and `representation_differences.json`.
- Independent prepared review: `../branch_flow_prepared_review.py` and `.json`, including the preserved `attempt01` pair.
- Independent post-run replay: `../branch_flow_independent_review/postrun_review.py` and `.json`.
- The appended `artifact_manifest.csv` binds this readout and the closed producer/review artifacts. The prospective strict-energy follow-up design is outside this closed arm and is not a result here.
