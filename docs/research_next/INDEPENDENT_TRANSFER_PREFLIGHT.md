# Independent chronological-UC transfer preflight

Date: 2026-09-27. Status: **recommend a small model-fidelity pilot; HOLD scientific execution pending a separate source/model gate**. This is an additive source and schema assessment, not a replication result. Protected Git21, manuscripts, released archives and prior experiment ledgers were not modified.

## Decision

Use the official UnitCommitment.jl conversion **`or-lib/10_0_1_w`** as the first small independent-data UC/cost pilot. It has ten thermal units, 24 hourly periods, native finite ramp limits, nontrivial initial obligations, minimum up/down times, positive startup charges and piecewise-linear production costs. Selection is by smallest listed non-RTS native UC family and first fixed instance name, before optimization outcomes. The data are synthetic Pisa/OR-Library UC benchmarks, not historical system observations. One bus and zero lines mean this tests independent **UC data and formulation**, not an independent transmission network. [Official catalogue](https://anl-ceeesa.github.io/UnitCommitment.jl/0.4/guides/instances/)

A 24-hour sequence contains only one occurrence of each hour of day. Consequently, a nonidentity permutation preserving hour of day is impossible. This pilot is **Phi0/unrestricted order only**; it cannot directly confirm the six prior HOD results. Its purpose is to admit a faithfully encoded, inexpensive independent model before considering larger transfer cases. No scientific target permutation, model or optimization was generated during this preflight.

## Sources actually inspected and pinned

The official [individual OR-LIB file](https://axavier.org/UnitCommitment.jl/0.4/instances/or-lib/10_0_1_w.json.gz) was read in memory: 2,419 compressed bytes, SHA256 `6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe`; decompressed JSON SHA256 `3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308`. The JSON embeds an MIT license attributed to J. E. Beasley (2010), consistent with the [OR-Library licence](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/legal.html). Retain its licence and source attribution when redistributing it. It declares schema 0.3 although served in benchmark namespace 0.4. A versioned web directory is not assumed immutable: both compressed and decompressed hashes must be pinned.

Pin the software independently to UnitCommitment.jl **v0.4.0, commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`**, not mutable documentation or master. Its [software licence](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/LICENSE.md) is the Argonne modified BSD licence. The reader, default formulation, status, dwell, ramp and curtailment source paths were inspected; full conversion equivalence to the original Pisa generator has **not** been proved. Online docs may describe a later 0.4 state, so source code at this commit controls any adapter.

Small source files and two individual compressed instances were fetched normally with TLS; no bulk instance archive, environment installation, Julia execution, model import or solver run occurred. The author Tejada archive and its results archive were inspected only through metadata, not downloaded. Paper metadata/abstracts were used for provenance; this assessment does not claim a full paper reading or reproduce an original published optimum.

## Actual selected-case fields

All ten units have four production-cost segments (five MW/cost points), constant scalar physical parameters, and one startup-cost category. Each category's delay equals that unit's minimum downtime. Thus the case has positive startup charges but does **not** exercise multiple downtime-dependent startup prices. Spinning-reserve requirements are zero throughout. There are no transmission, storage, renewable or fuel-type data in this file.

| Unit | Initial signed age (h) | Initial MW | Minimum up/down (h) | RU/RD (MW per one-hour step) | Startup cost ($) |
|---|---:|---:|---:|---:|---:|
| g0 | -1 | 0 | 4 / 3 | 42.003808 / 32.599073 | 172.862432 |
| g1 | 4 | 74.666609 | 3 / 3 | 31.325072 / 36.390287 | 168.685601 |
| g2 | -4 | 0 | 4 / 3 | 20.632301 / 21.831385 | 162.202704 |
| g3 | 2 | 85.048019 | 3 / 4 | 27.869072 / 27.091832 | 160.219192 |
| g4 | -4 | 0 | 3 / 3 | 22.204262 / 27.417263 | 159.160047 |
| g5 | 1 | 68.169224 | 8 / 8 | 51.694535 / 61.702851 | 265.616960 |
| g6 | 1 | 120.163482 | 7 / 8 | 67.064482 / 49.715649 | 273.416626 |
| g7 | 6 | 72.655836 | 8 / 8 | 64.139573 / 69.178653 | 306.216230 |
| g8 | -8 | 0 | 13 / 14 | 89.618227 / 78.751405 | 445.842452 |
| g9 | 9 | 118.674849 | 14 / 12 | 101.140357 / 99.597226 | 466.424559 |

Positive age means already on; negative age means already off. The remaining initial dwell is material, especially g5/g6/g8/g9. Startup and shutdown **output** limits are absent, a different issue from the positive startup **costs**.

## Model assumptions that must survive transfer

- The pinned [reader](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/instance/read.jl) uses `1e6 MW` for missing RU/RD/SU/SD, while current format prose calls the default infinity. Do not replace the actual finite default silently. Schema migration supplies thermal type; any automatic repair and its actual effects require an explicit audit before model admission.
- The pinned [default formulation](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/formulations/base/structs.jl) combines Garver status/production variables, KnuOstWat2018 costs and MorLatRam2013 ramp/startup formulations. An independent adapter must specify this composition rather than say only “standard UC”.
- [Status linkage](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/formulations/Gar1962/status.jl) uses the supplied initial status and excludes simultaneous start/stop. [Dwell rows](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/formulations/base/unit.jl) enforce remaining initial obligations and trailing windows inside the horizon. No cyclic state or obligation to continue beyond the horizon is added.
- With constant minimum output, the pinned [ramp code](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/formulations/MorLatRam2013/ramp.jl) constrains output **above minimum**, with reserve terms, including startup/shutdown transitions. Its comments explicitly flag differences from alternative startup/shutdown ramp formulations. First-period rows depend on native initial status/power. This is not the old RTS online-to-online ramp rule, and U-only integrality recovery cannot be inherited.
- [Curtailment is an actual native variable](https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/4f04f0dd6641b071fd7556346c3d7190c2ffdfe5/src/model/formulations/base/bus.jl), bounded between zero and hourly load, with default penalty $1,000/MW per step. Reserve shortfall is forbidden by the default negative shortfall-penalty setting. Native penalized cost and a separately named **zero-curtailment hard-service restriction** answer different questions. Neither model may be silently substituted for the other.

Under hard balance with only thermal generation, total production MWh equals the sum of hourly demand. A demand permutation preserves that sum. Therefore, total thermal MWh is a mathematically constant objective here; there is no supported fossil subset or emissions roster. Use native production plus startup cost (and explicitly account for curtailment penalties in the native baseline), or study feasibility. A native-cost result is not an extension of the RTS fossil-electricity-energy quantity.

## Alternatives and reasons not selected first

| Candidate | Verified scale/provenance | Decision |
|---|---|---|
| OR-LIB `10_0_1_w` | 10 thermal, 24 h, synthetic native UC, one bus | Selected first for model-fidelity/cost pilot; no HOD/network claim. |
| Tejada19 `UC_168h_36g` | 36 thermal, 168 h, synthetic Pisa-derived native UC, one bus, nonzero reserves | Weekly alternative, but all 36 units omit ramps and startup cost/delay fields. Defaults yield nonbinding large ramp limits and zero startup charges; HOLD as a full ramp/startup transfer. |
| PGLib-UC `ca/2014-09-01_reserves_1.json` | 610 thermal, 48 h, CAISO-derived generator/load data, one bus | Stronger empirical origin and richer native physics, substantially larger. Valid fallback after a separate computational/fidelity design. |
| PGLib FERC | At least 934 thermal plus renewable profile, 48 h; generator data and PJM profiles combined by library authors | Larger again; no transmission model. No need to re-inspect all 44 cases. |
| UC.jl MATPOWER cases | Small independent topologies, but UC loads/costs/ramp/reserve assumptions synthesized by converters | Could be a disclosed hybrid benchmark, not an independently observed network-plus-UC record. Not selected as native transfer. |
| RTS Area2/Area3 | Same RTS system and related topology templates | Not independent provenance; old assessment remains unchanged. |

The [Tejada individual file](https://axavier.org/UnitCommitment.jl/0.4/instances/tejada19/UC_168h_36g.json.gz) is 5,914 compressed bytes, SHA256 `05d868f85ffae29a18a904fc594e34c462e0f94baec11e76cf6466d3b176adc6`; JSON SHA256 `936e76430bcd068aa0700030e39856a8569a922d5c8c96214c9b238b6eb3d6e3`. It embeds MIT attribution to Diego Alejandro Tejada Arango (2018). The [original author repository](https://github.com/datejada/UC-data/tree/1b417ece7ca61d41fca7302df6a0313f8236d611) also supplies MIT terms; `UC-Instances.zip` is 1,069,070 bytes (Git blob `7a2f0916d0628e66eb7cea5799ff0373f464a1a3`), not fetched in this preflight. Its conversion fidelity remains unadjudicated.

The PGLib fallback was independently re-fetched at commit `39a7f38cf4703de92f0291f0c873c2e98c789301`: [case](https://raw.githubusercontent.com/power-grid-lib/pglib-uc/39a7f38cf4703de92f0291f0c873c2e98c789301/ca/2014-09-01_reserves_1.json), 329,702 bytes, SHA256 `ae2c0bbf7be38a34e3167a2bb839c33b0f1b8bcced51a5b4c0f9ef46fd759831`. Counts: 610 initially-on units, 200 must-run, maximum minimum up/down six hours, 1,220 startup categories, 1,488 production-cost points. [Data are CC BY4.0 and software MIT](https://github.com/power-grid-lib/pglib-uc/blob/39a7f38cf4703de92f0291f0c873c2e98c789301/LICENSE). Its [model](https://github.com/power-grid-lib/pglib-uc/blob/39a7f38cf4703de92f0291f0c873c2e98c789301/MODEL.tex) has native reserve, startup-category, initial-ramp and shutdown assumptions; the executable Python runs a solver at import and was not imported. Existing SHA256s were confirmed: Python `ca340c71fe78627c3fab2a2f356b4b2ec3a650c8e9883d6ef645aa2ea1b534ea`, model TeX `e612d71922cf5b19a2f8e7903c8ac6b25a0953e5065c368c94571752f360b6aa`, licence `b5ececfa64eb67fd5b0e5c135624f0f9004b938d399150e644f9641b659e628c`.

## Bounded next-case plan and admission criteria

The next phase should first freeze one explicit source-faithful encoded model and an independent direct-checker feature map, then prepare a **reference + exactly two predeclared Phi0 demand-package permutations + an identity/exact-input positive control**. Fix untouched horizon, units, source values, initial ages/power, formulation, objective and service convention. Do not use a same-U class shuffle as a promised feasible control: finite ramps and startup production constraints may fail. Identical-input controls may legitimately be identity and must be reported as such. No clock, weather-adjacency or nontrivial-control claim is implied.

Freeze permutation seeds, protected edge indices, source-package definition, exact numerical encoding, solver limits and result routes before generating targets or solving. Long native dwell means protecting a few endpoint hours is not a claim that interior alterations cannot affect boundary obligations. A modest first pilot can cap each of three full-binary solves at 300 seconds and each of three corresponding LP bounds at 30 seconds, without retries or outcome-dependent case replacement; timing is a proposal, not an execution authorization. Do not select a cost cap after looking at target outcomes. Prefer uncapped native-cost brackets initially; any hard-service restriction and cap recipe need separate prospective names.

**GO to source-only admission work:** individual data/licensing access, rich native selected-case fields and manageable size are verified. **HOLD optimization until:** (1) source/schema/automatic-repair/formulation mapping is complete; (2) zero-curtailment versus native penalized semantics is explicit; (3) every binary variable is retained and independent initial/terminal/ramp/startup/PWL checks are specified; (4) matrix/objective and finite-box provenance are reviewable, with justified handling of any unbounded variable; (5) fixed case generation and bounds/cost claims pass source and prepared-input review. A numeric incumbent is not an exact upper witness; a numeric LP bound is not an exact lower proof. Preserve unknowns, infeasible hard-service cases, zero-cost gaps and all denominators.

**HOLD broader claims:** no native-model equivalence proof, verified feasible reference, optimum, new-network validation, real-system transfer or HOD replication exists from this preflight. This is a useful independent UC starting point, not evidence that the current manuscript's stronger claims generalize.
