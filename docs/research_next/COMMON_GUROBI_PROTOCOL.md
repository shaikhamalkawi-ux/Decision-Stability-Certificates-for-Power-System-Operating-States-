# One alternate-backend search for a common commitment

Prospective source-only protocol, 2026-09-27. No preparation, Gurobi import, model construction, license-capacity probe, or optimizer call is authorized by this document itself. Preparation follows source review; execution additionally requires an independent prepared-data gate and a separate explicit execution authorization.

## Question and rationale

For the original first January week, does one common schedule of **all 12,096 U/Y/Z binary coordinates** admit separate dispatch and voltage angles for the identity chronology and the existing `days_321` chronology, under each original 23,195 MWh fossil-unit electrical-generation cap? This pair was selected post hoc because it is the unique first-week collision of the executed author-grounded observation together with its complete Hindex. The pair-selection history remains unchanged.

The closed original HiGHS run exhausted its fixed 600-second MIP allocation without an incumbent (actual call 606.6583649000095 s). Its continuous relaxation has an independently checked feasible point in the uniformly expanded model, so that relaxation cannot supply a valid expanded Farkas rejection. A separate fixed near-bit neighborhood was numerically infeasible; that restricted result left the original common-binary question UNKNOWN. This arm uses one different established solver and its documented feasibility-search emphasis on the **unrestricted original joint model**. It is a bounded search for a witness, not an algorithmic novelty or a comparative speed claim.

## Frozen model and provenance

The only scientific model is the archived common model in `results/research_next/common_commitment/prepared`: 69,362 rows, 33,936 columns, 291,176 stored coefficients, and all 12,096 original binary declarations. There are separate continuous P/theta columns in each world and shared U/Y/Z. The nominal coefficient matrix, row intervals, column boxes, coordinate maps, native arrays, generation roster and cap constraints are copied byte for byte; the objective is zero feasibility, as before. No diving bounds, warm start, cap change, mean target, additional chronology, alternative schedule, or physical-model change is introduced.

The runner pins the old prepared freeze `4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59`, the 48-entry input manifest `8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c`, prior outcome/review records, and three existing backend-readiness records. Historical payload bytes are captured once, checked against their trusted size/hash, and copied from that capture. The new manifest binds the new source/protocol, all inherited inputs, every copied model/native payload, the backend-row map, environment inventory, and fixed plan. Final preparation and pre-execution validation require unchanged inputs.

The standard-library exact kernel remains `src/research8h_standalone_verify.py`, SHA256 `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`. The unchanged native checker is the `native_check` function in `src/researchnext_common_commitment.py`, SHA256 `039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284`, invoked with the new frozen copies and explicit native specification. No old entry point is executed or modified.

## Existing backend and readiness limit

Use the already installed `.work/auer_projection_env/Scripts/python.exe`: Python 3.12.14, gurobipy/Gurobi 13.0.0, NumPy 2.5.3, SciPy 1.18.1. Preparation checks installed distribution metadata only, without importing Gurobi or opening a licensed environment. Execution additionally checks `gurobi.version()` against 13.0.0.

Existing evidence comprises `isolated_environment.json` (SHA256 `431af4e6f9a8a8e10a30f3f690551084b43d84b18b56b761594e9be1123e5366`), `synthetic_license_probe.json` (`5ef5d25e22f8117a9b7ac5c3508b18b8960b142efacdc72f67749b596715e009`), and `probe_completion.json` (`78356593844606bf71d9deaf9d6163c0e1fc820816d1737488eda2f8a974a00d`) under `results/research_next/auer_projection_preflight`. These establish only a successful tiny synthetic call and the recorded environment. Completed clustering calls were also small. **Entitlement/capacity for this 33,936-column model remains UNKNOWN.** A license, environment, or capacity error stops this arm without installation, credential inspection, license modification, purchase, backend substitution or retry. It is an execution-readiness failure, not evidence of mathematical incompatibility or infeasibility.

The installed 13.0 API stub documents the used `addVar`, `LinExpr`, `addLConstr`, `getRow`, attribute, parameter and `optimize` interfaces. It was inspected without importing it (stub SHA256 `e7a605f39a1d30bb0933dcfb2771a7db59bc44ddac63d1af7c859ee104d6d7f7`). The official [Gurobi parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html) documents MIPFocus=1 as feasibility emphasis and SolutionLimit=1 as first-solution termination; the explicit feasibility tolerances below are inside the documented ranges. No claim of a reproduced published algorithm is made.

## Lossless backend translation before the sole call

All original columns keep their order and lower/upper endpoints, with binary type exactly where the original mask is one. Each finite equality row becomes one equality. Each non-equality row becomes one constraint for each finite lower/upper endpoint. This splitting uses identical coefficients and endpoints and introduces no auxiliary variable. Fully unbounded rows are unexpected and cause a preparation failure. Endpoints are stored as exact binary64 hexadecimal strings in the prospective backend-row map.

Before optimization, independently read back through the Gurobi API **every** constructed variable's index, bounds, objective coefficient and type, and every constructed row's coefficients, sense and right-hand endpoint. Require equality to the archived model plus the fixed row-splitting map. Require zero objective constant, minimization sense, no quadratic/general/SOS constraints, no extra columns, and NumStart=0. Save the readback arrays and a count/hash report. A readback mismatch stops before optimization; there is no silent coefficient normalization or repair.

## One fixed call and timing

Use exactly one original full MIP call with these prospectively fixed settings:

| Parameter | Value |
|---|---:|
| TimeLimit | 1800 seconds |
| Threads | 1 |
| Seed | 0 |
| MIPFocus | 1 |
| SolutionLimit | 1 |
| MIPGap | 1e-8 |
| Presolve | -1 (automatic) |
| FeasibilityTol | 1e-8 |
| IntFeasTol | 1e-9 |

All other mathematical search settings remain installed-version defaults. No MIP start or hint is supplied. The tighter numerical tolerances are chosen before any outcome to reduce subsequent exact-admission failures; they do not change the exact acceptance tolerance.

The soft phase budget is 2400 seconds, beginning before prepared-input validation. Require at least 1805 seconds remaining before the call; check again immediately after the call-ready record is written. Failure of either guard produces NOT_RUN, not a scientific result. Actual wall time, solver-reported time and any 1800-second soft overrun are retained. The phase includes preparation revalidation, model assembly/readback, the call, candidate checks, final input rehashing and result serialization up to the elapsed sample. Final completion serialization, console summary, disposal and the private-log receipt are outside that sampled phase and must be described as closeout overhead, not hidden within a hard deadline guarantee.

The call ledger distinguishes **optimize invocation attempted** from **optimize returned**. An invocation that raises a license/capacity error may have attempted=1 and returned=0 without any established scientific search. Public reporting must say so; the `optimizer_calls` count records attempts, not proof that search occurred. Exceptions preserve stage, error type, numeric backend code, call ledger and partial artifacts, without raw exception text. There is no retry, second incumbent, solution-pool search, LP, IIS, ray request, alternate basis or individual-world solve.

## Candidate admission and interpretation

If the sole returned call has a solution, archive its raw vector. All coordinates must be finite. A binary coordinate may be rounded only when its exact binary64 value is within the unchanged `tau = Fraction.from_float(1e-5)` of exactly one of 0 and 1. Preserve every continuous coordinate byte. This is the only allowed recovery. SolutionLimit=1 means a first numerical incumbent rejected by exact admission is retained as a rejection; this arm does not continue for another candidate.

Require all of the following for `VERIFIED_EXPANDED_COMMON_COMMITMENT`:

1. Exact rational membership of the rounded point in the unchanged joint model, with its full 12,096-bit mask and every finite row/column bound widened uniformly by tau.
2. Exact rational membership of both coordinate projections in the two unchanged original full models, using each complete original binary mask.
3. Exact equality and binary membership of all 12,096 projected U/Y/Z states across the two worlds.
4. The unchanged supplementary native checker passes for both worlds: hourly availability/output, aggregate balance, all native dwell and transition conditions under the same mature initial/free terminal convention, native on/on ramps, and the fossil electrical-output cap. Nodal DC, branch limits and theta boxes are checked in the unchanged full original matrices in step 2. The native checker's binary64-derived coefficients and tolerance convention are inherited explicitly.

The exact archived-model membership is a statement about the uniformly expanded stored numerical model, not nominal tau=0 membership or arbitrarily precise physical data. The native check supplements it without replacing that distinction. A verified common commitment would disprove, for this pair and this convention, the claim that no one commitment can serve both; it would not erase the failure of the old particular fixed commitment.

No incumbent, a rejected point, timeout, numerical infeasibility, environment/capacity failure or a phase guard leaves the unrestricted binary question UNKNOWN. Numerical INFEASIBLE alone is not an exact negative. Even a joint negative, if some future arm established it, would not by itself establish either world's individual binary feasibility. This arm does not attempt any negative proof.

## Privacy, closure and review

Raw Gurobi/startup logs remain under private `.work/researchnext_common_gurobi/run01`. Startup logging is disabled before environment start and Python output is redirected there; solver console output is disabled and solver logs use the same private location. A public receipt may bind only raw-log path, size and SHA256 with privacy review explicitly NOT_PERFORMED. Do not publish raw logs or startup exception strings without a separate content review for license identifiers or credentials. No license file, environment secret or credential value is read by this runner. Selected numeric status/timing fields are public.

Preserve the one execution marker, actual attempted/returned ledger, readback, raw/candidate vectors if present, exact check reports, all null/error outcomes, and before/after input bindings. A separate independent post-run review is required before a scientific positive claim. Producer readout/inventory are appended only after stable closure; old common/diving/observer evidence remains immutable.

Only invented row-encoding fixtures and syntax checks are allowed during source drafting. Their receipt binds the source/protocol and explicitly records zero scientific reads, preparations, Gurobi imports and optimizer calls. They do not establish scientific-model translation or license capacity.
