# Fixed identity commitment under January day reordering

All five predeclared redispatch LPs reject the **fixed unpermuted identity U/Y/Z schedule**. Each rejection has an independently replayed exact rational certificate that also rejects the uniformly outward-expanded finite row and column bounds, with tau equal to the exact binary64 value of 1e-5. There are five fixed-schedule rejections, zero accepted witnesses and zero unresolved fixed-schedule cases.

| Day order | Solver status | Exact expanded certificate gap (approximate, raw ray units) | Nonzero certificate rows | Cap-row multiplier nonzero |
|---|---|---:|---:|---|
| 132 | Infeasible | 594.24908410 | 91 | Yes |
| 213 | Infeasible | 370.56937910 | 91 | Yes |
| 231 | Infeasible | 594.24908410 | 91 | Yes |
| 312 | Infeasible | 370.56937910 | 91 | Yes |
| 321 | Infeasible | 110.46898000 | 23 | No |

These are **restrictions**, not relaxations, of the original unfixed binary models. They do not establish that any of the five original models is infeasible. In particular, order 312 retains its previously verified full-model positive with a different commitment schedule. Its fixed-identity rejection is consistent with that positive. Previous day-block LP/MIP outcomes are unchanged; no unresolved parent case is promoted to a rejection here.

All global static constraints, full 24-bus/38-line DC network, native chronology, 23-fossil-unit energy cap of 23195 MWh, source inputs and bounds were inherited unchanged. There are no named-unit mean constraints. Only the 12096 U/Y/Z coordinates are fixed to exact identity bits; 12048 bound pairs actually change because 48 initial transition coordinates were already fixed. P and theta remain free within their inherited boxes. The same 23-unit fossil-electricity objective is used, with no emissions-factor or economic-cost interpretation. The identity control passes exact expanded fixed-model and original-binary checks without a control optimization.

Exactly five LP calls were made once, in the frozen order, with a 60-second limit, simplex, presolve off, one thread and seed zero. All completed as Infeasible in approximately 1.7 to 3.9 seconds on a shared host; these times are not a performance benchmark. The frozen source, protocol and all 200 input hashes remain unchanged.

The solver returned value-valid vectors for all five infeasible runs. This flag does not assert feasibility. Raw vectors and anchored diagnostics are retained: only U/Y/Z were replaced by the exact identity anchor, while P/theta bytes stayed unchanged. Every such diagnostic fails the exact expanded fixed and unfixed checks and the independent native checks. None is an accepted witness or an upper bound.

Certificate gaps are in arbitrary raw-ray scale, not MWh. Full rational quantities, raw/projected rays and hash bindings are authoritative in each case's `fixed_schedule_certificate.json`. The displayed cap support is descriptive; it does not identify a unique cause. The copied `model_metadata.json` files remain unchanged parent snapshots: their old zero-objective text and binary-column counts do not describe the executed continuous LP. Actual objective arrays, bounds, protocol and `PREPARED_MODEL_INTERPRETATION.md` specify this arm.

Independent replay covers exact parent-row identity and state-only bound changes, the native fossil roster/objective, the exact identity anchor/control, every raw/projected certificate multiplier and rational nominal/expanded gap, every retained diagnostic vector, and all 200 frozen bindings. See `INDEPENDENT_REVIEW.md` and `independent_review.json`. This is a same-January-week fixed-schedule sensitivity result, not an additional network, replication, or general necessity claim.
