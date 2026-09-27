# Independent Auer execution source review

**SOURCE REVIEW PASS**,27September2026, for final runner SHA256`a18058186dde3dfe0dbd6717c27636e76ef59debbbcfbd36f7bb887c7a232d9c` (`src/researchnext_auer_execution.py`) and protocol SHA256`86313ffced10a4e384da01c60a50b7bd8bb62a46c544b96ef4e5653b29c8daf2` (`docs/research_next/AUER_EXECUTION_PROTOCOL.md`). This is read-only source/contract review. I did not import or execute the harness, adapter, author code or TSAM; no tests, clustering, scientific-array calculation or optimizer call was run by this reviewer. It is not a replication or an execution result.

## Finding resolved before preparation

The initially reviewed runner`d974627b8b9a6e9f41de330d3af51e115e777251fffd89ba893cf5db0fd4b049` checked proximity to integers and assignment constraints, but did not explicitly require rounded solver values to lie in{0,1}. Declaring Pyomo variables binary does not by itself validate their returned values. I reported this gap promptly. The author added `all(v in (0, 1) for row in rounded for v in row)` immediately after the near-integer check; I read and verified that final delta and SHA. No source was edited by this reviewer. The earlier five invented fixtures remain attributed to their actual older runner hash42acdd61…, and were not rerun or relabeled.

## Contract and primary source inspection

Read the complete execution runner/protocol, the relevant frozen projection adapter and protocol, and `READINESS_AND_TSAM_SOURCE_AUDIT.md`. Directly inspected the pinned primary author sources, rather than treating the audit memo as a substitute: `InOutModule/Utilities.py` extraction, aggregated preparation, clustering call, selected-table/weight/Hindex construction and apply route; `InOutModule/CaseStudy.py` transition computation at lines845–883. The latter sorts RP identities, initializes matching row/column labels and counts a circular last-to-first edge before row/column normalization.

Also read the actual TSAM2.3.9 source-inspection copy: all of `utils/k_medoids_exact.py`, the k-medoids routing in `periodAggregation.py`, medoid representation, and the constructor/defaults, normalization, day unstacking, preprocessing and ordinary `createTypicalPeriods` path. These confirm feature-wise MinMax scaling, seven contiguous24-hour/96-coordinate vectors, Euclidean distances, the49-binary/57-constraint model and the unmodified solver call intercepted by the harness. TSAM recomputes each cluster's medoid via within-cluster distance sums/first argmin; the harness does not replace that behavior with solver facility IDs.

The frozen adapter projection deliberately omits the independent aggregate-net equation and hydro must-dispatch constraint and records capacity-factor roundtrip differences. The harness's output cannot establish equivalence with the107-coordinate UC model. The unusual author demand-merge multiplicities are preserved, exposed and checked. Common static signal metadata, unit/bus identities and unchanged native dwell/ratings are compared before execution. No-storage temporal preprocessing is the stated boundary, not equivalence of an activated downstream UC/storage model.

## Canonical observation and transition correctness

The declared observation includes all selected bus-demand, named VRES-profile and hydro-inflow rows, RP/K weights and N/P_to/P_from. Source-day indices and Hindex chronology are excluded only from this explicitly limited observation and retained as provenance. Their omission is not justified for long-duration storage or schedule-reconstruction claims, which are expressly excluded.

Canonicalization simultaneously maps every table RP label and both matrix axes under all six permutations, sorts table records without removing multiplicities, and compares canonical strings directly. Numeric values are finite binary64 hex with only signed-zero normalization. The primary author path produces rp01,rp02,rp03 and sorted matrix axes in that order; its table and matrix coordinates therefore match the permutation mapping. A smallest nonzero numeric difference is retained. Hashes are indexes rather than the equality test.

The adapter calls the author's unbound transition method on the newly generated Hindex and assigns all three fresh matrices. This avoids the known isolated table helper's stale/unset transition cache. The circular7-edge and3×3 conditions are checked. There is no substitution of the earlier unclustered noncyclic hour-transition baseline.

## Calls, termination, repeat and hash gates

The fixed schedule is identity,target1,target2,class-control,identity-repeat for each of three weeks: fifteen invocations, six primary targets including the historical UNKNOWN, three controls and three repeats. Each invocation builds a fresh projected carrier. Repeated original canonical disagreement or failure makes every comparison in that week UNKNOWN, without an adaptive retry, R choice, tie rule or feature change. Controls are not assumed to have equal observations.

The wrapper preserves the author/TSAM model and intercepts only its actual Gurobi factory/solve to set the disclosed30-second,one-thread,seed0,zero-relative-MIP-gap options. It rejects an unexpected backend, signature, model size or second solve. Numerical optimal status plus finite near-integer values, explicit binary-domain membership and every rounded assignment/facility condition are required. No exact combinatorial optimality proof is claimed. Other statuses/errors remain UNKNOWN. Caller-owned attempted-call state survives an exception after the call; actual durations and soft overruns are retained.

The900-second phase starts before validation/imports. A35-second remaining-time guard is checked both before the invocation and immediately before the actual solve after input serialization. This is a soft budget, not a process-kill guarantee. Both global patches are restored in `finally`. The exclusive execution marker prevents a silent second run.

Preparation and execution pin the adapter, projection bytes, selected native bindings, author import closure, actual TSAM source against its official wheel, schedule and runner/protocol. Complete installed distribution inventory and interpreter identity are checked, with declared Python/transitive-version deviations from the author's environment. No full environment/bitwise paper-run reproduction or relocated-package claim follows. Frozen dependencies are rehashed at close. A prepared-archive check and explicit parent execution GO remain separate gates.

No remaining source-level correctness blocker was identified for this fixed projection/configuration. This verdict authorizes neither scientific interpretation before execution nor broader operational or methodological claims.
