# One numerical SCIP search on the original common-commitment model

Prospective distinct arm, 2026-09-27. Source drafting and one solver-free preparation are authorized. The one scientific optimize call still requires root source approval, an independent prepared-data gate and explicit execution GO. No synthetic solve or repeated capability probe belongs to this arm.

## Scientific question and fixed scope

Ask the same unresolved question as `COMMON_COMMITMENT_PROTOCOL.md`: can one shared complete168-hour U/Y/Z schedule serve both the first-January identity and existing `days_321`, with independent P/theta dispatches and unchanged23,195MWh fossil-unit electrical-generation caps? The pair is post hoc:321 was the unique first-week collision of the executed primary observer plus full Hindex. A verified common schedule would refute nonexistence of any common schedule for this pair; it would preserve the older failure of the particular original identity schedule.

The original HiGHS MIP supplied no incumbent under its fixed budget; its continuous relaxation has an exact expanded feasible point. The near-bit restricted-diving failure did not exclude an unrestricted common schedule. The distinct Gurobi attempt stopped at licensed model-size error10010 before returning a scientific search result. All these records remain immutable. This arm uses an independently installed numerical backend with different established search heuristics; it is neither a performance experiment nor an algorithmic novelty claim.

The only model is the unchanged frozen original common formulation:69,362rows,33,936columns,291,176coefficients,12,096shared U/Y/Z binary declarations. Both entire original world models are retained, including all native48-hour dwell/boundary conventions, theta/output boxes and each cap. Objective coefficients and constant remain zero, minimization sense. No mean target, additional case, changed cap, altered physical encoding, diving fixing, warm start, individual-world solve or approximate coefficient truncation is introduced.

## Backend and proof boundary

Use only `.work/scip_capability_env01/Scripts/python.exe`: CPython3.12.14, PySCIPOpt6.2.1, NumPy2.3.5 and SCIP10.0.2. The closed capability setup imported one empty Model, with zero optimize calls. Its parameter dictionary lacked `exact/enable` and `certificate/filename`. Consequently this arm is explicitly **numerical SCIP**, with no exact-SCIP or proof-log claim. No new package installation, build, license or capability probe is included. SciPy is unnecessary.

The fixed capability/completion/wheel/installed-payload records are pinned, together with installed `scip.pxi` SHA256 `e6abd57d0f19a30c30d0c1c603e2b69ec890af4b6b3c94aaf44d289bb43efb16` and `scip.pyi` `8d44bb57b11ffb5688433b9f32ba1450c0c35c2e8787822ed12a09f29a559aa4`. The runner validates each archived installed binary/metadata payload before execution. Installed source and the [official model API](https://pyscipopt.readthedocs.io/en/stable/api/model.html) ground addVar/addCons, linear coefficient/endpoints, original-variable bounds/types, emphasis and parameter access. The source inspection observed that binary addVar clips bounds to[0,1]; the original binary boxes already lie within[0,1], and full readback still requires exact equality.

## Frozen preparation and backend translation

Preparation reads each trusted historical byte buffer once, verifies size/hash and copies from that same buffer. Preserve byte-identical copies of the five joint model/map files, the eight files for each original world, and GEN.csv. Pin the original48-input manifest/freeze, prior common and diving outcomes, Gurobi failure and SCIP capability. Bind final source/protocol, copied native inputs/specifications, installed backend provenance and the fixed plan. Preparation imports only the pinned standard-library model loader, not SCIP, and performs no optimizer call.

Use the same exact finite-side encoding: an equality once; otherwise one inequality per finite lower/upper endpoint. This gives82,130 backend rows and introduces no auxiliary variables. Store original-row/side/sense and exact binary64 endpoint hex in the prepared map. Every original column is created once by a unique name `x{original_index}`. SCIP may internally order its variable array differently; retain created handles in original-coordinate order and archive the actual backend name order instead of assuming array order.

After constructing the pre-transform model and **before** its sole optimization call, separately read back every original variable's bounds/objective/type and every linear constraint's coefficient dictionary and left/right endpoint. `getVars(transformed=False)` and `getConss(transformed=False)` must contain exactly the unique declared names; every object must remain original and stage must remain PROBLEM. `getValsLinear` names are mapped through the explicit unique x-index naming rule. Every readback must match the archived sparse row and side map exactly, including zero objective/offset, all12,096 binaries and all33,936 column boxes. Missing infinite inequality endpoints use SCIP's infinity sentinel; finite endpoints must match exactly. Save full readback arrays/hash, coordinate name lists and counts. Any mismatch stops before optimization, without repair.

## Fixed search settings, first-solution policy and timing

On a fresh model, capture the complete default parameter dictionary. Apply the supported installed `SCIP_PARAMEMPHASIS.FEASIBILITY` preset once, then these explicit settings in fixed order:

| Parameter | Value |
|---|---:|
| limits/time |1800.0seconds|
| limits/solutions |1|
| parallel/maxnthreads |1|
| lp/threads |1|
| randomization/randomseedshift |0|
| randomization/permutationseed |0|
| randomization/lpseed |0|
| numerics/feastol |1e-8|

The emphasis is an installed classical solver preset, not a learned method. The explicit thread/seed/limit/tolerance settings override any preset values. Save both complete parameter dictionaries and **every changed value** after setters; require the same parameter registry, all explicit values, and no further parameter change during model construction or immediately before the call. Unsupported setters stop before search; no silent fallback. Also retain post-call parameters to expose solver-side changes. Private output/log controls do not change scientific constraints.

Use exactly one `optimize()` call, no external LP/ray/IIS, separate polish, solution-pool enumeration, restart invocation, retry, alternate backend or supplied start. SCIP's internal LPs/heuristics/presolve are part of that sole MIP call. limits/solutions=1 asks for first-solution termination; do not read another candidate if the returned best point fails exact admission. No time/parameter tuning after outcomes.

The soft phase starts before prepared-input verification and lasts2,400seconds. Require1,805seconds remaining before the1800-second call and recheck after both call-ready writes immediately before invoking it. A skipped call remains NOT_RUN/UNKNOWN. Readiness markers explicitly are not actual-call markers. Caller-owned attempted/returned counters survive exceptions; attempted increments immediately before optimize. Actual invocation seconds, solver time, nodes/LP iterations and any time-limit overrun are retained. The final elapsed sample includes checks/input rehash/result writing; completion writing, disposal and private-log receipt are outside the sample and must be reported as closeout overhead.

## Exact returned-point admission

The numerical proposal uses the original nominal model. If there is a returned solution, save only the best raw point from that sole call, ordered by the original created-variable handles. Require finite full coordinates. A binary value may be snapped only if its exact binary64 value is within `tau=Fraction.from_float(1e-5)` of exactly one of0 or1; otherwise reject the candidate. Every continuous dispatch/angle byte is retained. No redispatch, clipping, canonical transition repair or further solver call is permitted.

Reuse the unchanged full admission procedure: pinned standard-library kernel `research8h_standalone_verify.py` SHA256 `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f` checks the complete joint and both projected original models, with full original masks and every finite bound uniformly widened by exact tau. Require all12,096 projected bits identical and binary. The pinned prior `researchnext_common_commitment.py` SHA256 `039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284` supplies only its unchanged native-check function with explicit frozen world paths. It checks availability/output/aggregate balance, transition/dwell conventions, native on/on ramps and fossil electrical caps; original-matrix membership covers nodal DC, branches and theta boxes. Keep the inherited binary64 hourly ramp conversion semantics.

Accept `VERIFIED_EXPANDED_COMMON_COMMITMENT` only if all full matrix/mask and both native checks pass. This is a tolerance-expanded archived-model claim, with supplementary native consistency, not nominal tau=0 or physically exact-data feasibility. A numerical status alone—including INFEASIBLE—never supplies a negative proof. No point, rejected point, timeout, admission failure or execution error leaves the unrestricted common-binary question UNKNOWN. No objective optimum/cost/individual-world feasibility inference follows.

## Closure and independence

Freeze and revalidate all input hashes at entry and close; require an external trusted prepared-freeze digest and fresh run/private-log directories. Save all failures/UNKNOWN outcomes, raw and recovered candidate vectors if any, full backend readback, settings, ledger and exact admission records. Keep raw startup/solver logs private until a separate disclosure review; publish only selected numeric status and log hashes. Independent prepared review precedes explicit execution GO; independent post-run replay/ledger review precedes scientific claims. No closed common, diving, Gurobi or capability artifact is changed.

Source drafting reused the reviewed candidate-check implementation as text without executing it. Only syntax/source inspection belongs to this stage; old fixtures and capability probes are not repeated.
