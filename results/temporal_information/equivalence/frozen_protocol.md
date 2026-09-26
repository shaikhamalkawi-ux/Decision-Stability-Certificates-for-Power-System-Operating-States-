# Fixed identical-unit weekly-energy pooling audit

Protocol frozen before the grouped feasibility runs, 2026-09-26. This is a bounded diagnostic within the approved temporal-information pivot. It preserves every previous source file and result.

## Question and fixed sample

Test whether eight previously rejected individual-unit mean targets become feasible when weekly energy is pooled only within strictly source-matched, co-located modeled-equivalence groups. Use all eight previously selected first weeks: January, February, March, April, May, June, July and October 2020, 168 hourly snapshots each. The existing published individual-mean min-up/down verdict is the comparator; do not rerun or replace that record. No dates, generators, groups or budgets will be selected after observing grouped outcomes.

## Group construction

Retain exact equality of all 55 non-identity columns in the native 57-column `gen.csv`, including Bus ID, source Unit Group, Unit Type, Category, Fuel, initial source injections, P/Q bounds, dwell/ramp/start parameters, outage/maintenance fields, fuel prices, all heat-rate/output curve fields, VOM, every sulfur/emissions field, electrical/dynamic fields and storage fields. Additionally require equal source-derived base marginal cost and equal full-year time-varying minimum/maximum availability profiles as used by the admitted model. Units with different hourly profiles stay separate.

The only source-column exclusions are **GEN UID** and **Gen ID**, both unit identifiers. The author model's `1e-7*index` cost tie breaker is also excluded: it encodes ordering, not a physical cost difference. Its value will be retained in the inventory. No source cost-curve field or base cost is discarded.

This establishes equality of represented model attributes, not verified empirical identity. In particular, some emissions entries are the string `Unit-specific`. Matching that placeholder does not establish equal actual emissions. Flag those groups explicitly; do not claim that pooling preserves emissions. Emissions are not constrained in this feasibility experiment, but their source fields are retained and audited. All missing/placeholder source values are disclosed.

## Exactly one change to the tested feasible set

For a group G, replace individual equalities `mean_t p[t,g]=mu[g]` with the single equality `mean_t sum(g in G) p[t,g]=sum(g in G) mu[g]`. Singleton constraints stay unchanged. This pools **weekly target energies only**. Each generator keeps its own hourly output variable, binary commitment, transition variables, availability, conditional minimum/maximum output and native minimum up/down times. There are no hourly identity swaps, aggregated commitment units, representative dispatch curves, or reassigned chronology traces.

Retain the previous aggregate-balance, no-network, no-shedding formulation and fixed-hydro/rooftop-PV conventions. Initial status is free, `startup[0]=shutdown[0]=0`, and only observed in-horizon transitions induce residence; the final horizon is not extended. Match the previous min-up/down family. The source on/on hourly ramps are redundant as established in V8R1; retain the rate fields in grouping and verify their bounds on any witness, without adding a different startup/shutdown model. No generation-cost optimization or emissions constraint is introduced.

## Budget and evidence rules

Run one zero-objective HiGHS feasibility MILP per month: maximum 60 seconds, one thread, random seed zero. All eight outcomes must be reported. Explicit Infeasible status is solver-certified rejection within numeric tolerances. A feasible incumbent is admitted only after separate witness checks; time limits or other statuses without a verified incumbent remain unresolved. Never turn a timeout into rejection. Do not extend case budgets after seeing an outcome.

The independent witness checker validates finite values; dispatch and binary domains; rounded-status output coupling; aggregate hourly balance; fixed hydro; group means; transition identities and mutually exclusive startup/shutdown; free-start/terminal boundary conventions; residence via direct inspection of every rounded status change; and native on/on ramps. Acceptance tolerance is `1e-5` for MW/dimensionless residuals and `1e-5 MW` for each group mean (`0.00168 MWh` per weekly group energy). Individual-mean drift is reported diagnostically and is not an acceptance criterion in the grouped model.

Save the complete group/member inventories, retained/excluded columns, shared values, profile hashes, all monthly pooled targets, source/code/protocol hashes, solver logs/statuses, and complete per-unit witnesses for admitted cases. Verify saved CSV witnesses by rereading them. The portable input directory is read-only; the audit writes only its new output directory.

## Interpretation fixed in advance

Grouped admission following individual rejection shows sensitivity to preserving labeled unit energy within the tested modeled-equivalence classes. It does not prove that the original labeled target was feasible, that label swaps are physically valid, or that emissions were preserved. Grouped rejection shows that this narrowly defined pooling does not remove the obstruction in that case. Unresolved runs support neither conclusion. Either result remains conditional on the chosen hourly, no-network, weak-boundary model and these eight archived weeks.
