# OR-LIB10 independent UC cost pilot — source and preparation protocol

Status on 2026-09-27: **SOURCE/HARNESS ONLY; scientific preparation and optimization not executed**. This protocol follows the independent-data preflight and root's approval of the case contract. Source review, a separately authorized preparation, independent prepared-model review, and a separate execution decision precede any scientific solve. The current Python source has no optimizer, network access or environment setup code. Existing RTS evidence, manuscripts and delivered artifacts remain untouched.

## Question, source and scope

The intended question is whether two fixed reorderings of an independent synthetic UC benchmark's unchanged hourly demand alter native encoded operating cost or hard-service feasibility. This is a Phi0/unrestricted-order pilot on a single-bus system. It is not a HOD-preserving, weather-preserving, network, fuel, emissions, or field-data replication of the earlier RTS results. A 24-hour horizon cannot admit a nonidentity hour-of-day-preserving permutation.

Use exactly `or-lib/10_0_1_w` from the [official individual benchmark](https://axavier.org/UnitCommitment.jl/0.4/instances/or-lib/10_0_1_w.json.gz): compressed SHA256 `6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe`, 2,419 bytes; decompressed SHA256 `3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308`, 6,811 bytes. Preserve the embedded MIT attribution. The horizon is 24 one-hour periods, ten thermal units, one bus, one spinning-reserve product with zero hourly requirements, no storage or transmission. No case substitution follows unfavorable results.

The declared source target is the **converted file interpreted by UnitCommitment.jl v0.4.0**, commit `4f04f0dd6641b071fd7556346c3d7190c2ffdfe5`, with its default Gar1962 production/status, KnuOstWat2018 PWL and MorLatRam2013 ramp/startup components. It is not a proven reconstruction of the original Pisa quadratic-generator input. The adapter binds 14 inspected upstream files, including the software licence, by SHA256 and copies them during a later authorized preparation. It never executes or imports those upstream files.

The selected file's schema0.3 migration adds thermal type. All40 segment widths are positive and all ten four-segment slope sequences strictly increase. One startup category per unit means the source repair routine makes no numerical changes; its delay equals minimum downtime, and its positive charge is fixed whenever the unit starts. **Multiple downtime-dependent startup-price categories and positive reserve requirements are not exercised.** The adapter rejects unsupported fields, nonconvex slopes requiring repair, alternate service products, partial must-run cases and nonzero startup/shutdown segment corrections rather than silently generalizing.

## Fixed cases and service variants

Indices are zero-based destination hours. The source order is 0 through23.

| Name | Fixed operation | Role |
|---|---|---|
| `identity` | Unchanged sequence | Reference and exact-input positive control once a witness is accepted |
| `reverse_4_19` | Reverse the source indices4 through19, inclusive | Target1 |
| `rotate_left1_4_19` | Move source index4 behind indices5 through19 | Target2 |

The first and last four hours remain unchanged. This does **not** preserve within-day adjacency, clock position, ramp feasibility or remaining initial obligations. Native dwell can extend14 hours; every source initial-age constraint remains active after the reorder. These two operations were selected before target generation or optimization. There is no RNG, severity tuning, cap selection or substitute seed. The complete time-dependent package is moved jointly: load, reserve requirement and curtailment penalty; generator inputs and costs are constant in this specific file and remain fixed. Every original scalar value and multiplicity is preserved.

Prepare two named variants of each of the three cases, six models total:

1. **`native_penalized`** preserves bounded load curtailment and the native $1,000/MW-per-step penalty. Reserve shortfall remains fixed to zero.
2. **`hard_service`** changes only the upper bounds of the curtailment variables to zero. This is an explicitly imposed common restriction, not the unmodified native baseline. Every matrix row, objective coefficient, other column bound and binary coordinate is identical for a given case.

Do not promise a feasible nonidentity control based only on unchanged U classes: finite ramp limits invalidate that shortcut. The identity control is deliberately a duplicate input, checked without another optimization. Denominators are always two targets per service variant. Duplicate control inputs are not independent replications.

## Explicit model and source feature map

For generator i and hour t, retain binary `U` (on), `Y` (start), `Z` (stop), and `D` (the single startup category). Continuous variables are `Q` (output above minimum), `R` (spinning reserve), four segment quantities `S_k`, system curtailment `C`, reserve shortfall `F`, and net injection `N`. All **960 declared native binary coordinates** are retained; `D=Y` is not used to remove a binary variable. Let m and M denote native minimum/maximum output, w_k the segment widths, a_k their slopes, c0 minimum-output cost, sc startup cost, and d_t the selected load. Let U_-1 be determined by the signed initial age.

The adapter has these rows, with their native duplicate/redundant rows retained:

- `U_t-U_(t-1)=Y_t-Z_t`, including supplied U_-1; `Y_t+Z_t<=1`; `D_t=Y_t`.
- Sum of starts in the trailing minimum-up window is at most U_t; sum of stops in the trailing minimum-down window is at most1-U_t. Windows are truncated only at the beginning of the encoded horizon. Initial residual dwell is a separate zero-sum row over forbidden initial starts/stops. There is no cyclic or post-horizon continuation obligation.
- `Q_t+R_t <= (M-m)U_t`; `0<=S_kt<=w_k U_t`; `Q_t=sum_k S_kt`. The last equality is emitted four times because the native source inserts it inside the segment loop. The native startup-limit row duplicates the headroom row here; its coefficient correction is zero because default SU=1e6 exceeds M. The native shutdown-limit row `Q_t<=(M-m)U_t` remains for t<T-1; its correction is likewise zero.
- For t>0, `Q_t+R_t-Q_(t-1)<=RU` and `Q_(t-1)+R_(t-1)-Q_t<=RD`. These are the pinned model's **above-minimum** ramp equations; no online-to-online exemption is inserted.
- Initially-on units retain native first-period expressions `m+Q_0+R_0<=P0+RU` and `P0-(m+Q_0)<=RD`, even if U_0=0. Initially-off units do not receive these two first-period rows. The normalization of the corresponding binary64 upper bounds is explicit in source; generic physical total-output ramp checks are not a substitute.
- `sum_i(m_i U_it+Q_it)+C_t-N_t=d_t`, `N_t=0`, and `sum_i R_it+F_t>=reserve_t`. Native `F_t=0`; native `0<=C_t<=d_t`, changed to `C_t=0` only in `hard_service`.

The native encoded objective is sum over units/hours of `c0_i U_it + sc_i D_it + sum_k a_ik S_ikt`, plus hourly curtailment penalty times C_t. All terms use the source-derived binary64 values; no currency/year calibration is inferred. Total thermal MWh is constant under hard balance and preserved demand sum, so it is **not** the pilot objective.

| Source file at the fixed commit | Mapped responsibility |
|---|---|
| `src/instance/read.jl`, `migrate.jl`; `src/validation/repair.jl` | Schema, derived slopes/widths, defaults, explicit no-repair eligibility |
| `base/structs.jl` | Default formulation composition |
| `Gar1962/status.jl` | Three status binaries, linkage, exclusion, minimum-output cost |
| `base/unit.jl` | Startup-category binaries, dwell, initial history, reserve variables, startup/shutdown limits, injection terms |
| `Gar1962/prod.jl` | Continuous production variables and generation/reserve headroom |
| `KnuOstWat2018/pwlcosts.jl` | Segment limits, repeated production equality, slope objective and native segment upper bounds |
| `MorLatRam2013/ramp.jl`, `scosts.jl` | Exact above-minimum ramp/startup-category semantics |
| `base/bus.jl`, `system.jl` | Curtailment, balance, net injection, reserves |
| `src/validation/validate.jl` | Reviewed limitations; not used as acceptance code |

All model-path basenames in this table are under `src/model/formulations/` unless an explicit full path is shown. Source links follow `https://github.com/ANL-CEEESA/UnitCommitment.jl/blob/` plus the fixed commit and path. The adapter's `SOURCE_SHA` dictionary is the machine-readable binding list.

## Finite boxes, harmless projection and numerical scope

Native source allocates continuous nonnegative `mfg_it` even with no flexiramp product. Inspection of this selected default composition found no objective coefficient or constraint reference to those columns. The adapter omits exactly these240 unused columns. Any retained feasible vector lifts by setting every omitted mfg to zero; any native vector projects onto the retained coordinates with identical cost. If a future source or feature adds an mfg reference, this reduction is invalid and admission must stop.

Native segment bounds are retained. Additional explicit boxes `0<=Q,R<=M-m` follow from nonnegativity, `Q+R<=(M-m)U` and0<=U<=1. In a one-bus model, the retained balance equality implies `N=0`, so its box is fixed at zero. F is natively fixed at zero; C already has finite native bounds. Thus the export has **finite bounds on every retained column**, with no invented big-M parameter. Binary coordinates are unchanged.

These added boxes are implied at **nominal** rows and preserve the nominal projection and objective. Uniformly expanding finite row and column bounds is a new convention applied to this explicit encoding; redundant added bounds and different row normalizations can change its expanded feasible set. No equivalence to an expanded upstream JuMP model is claimed. The huge default1e6 output limits are source values, not a new artificial bound.

Model JSON uses round-trip binary64 decimal coefficients, finite column bounds, and null only for absent row bounds. The explicit first-period bound arithmetic, segment differences and slope divisions are part of the contract. Runtime JuMP coefficient/export equality has not been tested and is labelled `NOT_TESTED`, rather than implied by source reading. Source-derived mathematical fidelity and bit-for-bit runtime export identity are distinct claims.

## Independent acceptance route and focused checks

`exact_matrix_check` evaluates every saved row, column and objective as `Fraction.from_float` arithmetic. All binary values must be exactly0 or1, regardless of numerical expansion. It reports nominal maximum violation and any chosen exact binary64 tau; no rounding or witness repair occurs.

`direct_check` consumes the case and named vector and independently loops over source equations without reading the exported sparse row coefficients. It checks initial history, all status variables, ramp/startup/dwell, segments, balance, reserves, curtailment and native cost. It detects a deleted matrix row or changed objective coefficient. The CLI also requires the supplied model to equal a fresh declared source-derived encoding from the hash-verified input.

At a feasible nonoptimal point, arbitrary segment allocations can cost more than the canonical greedy PWL cost at that dispatch. The checker separately reports saved segment objective and canonical cost diagnostic; it never silently substitutes one for the other or requires equality. If a tau-expanded candidate falls outside the nominal PWL domain, the diagnostic is null with explicit affected unit-hours: no clipping or extrapolation occurs. This does not alter acceptance or the saved encoded objective. An accepted saved objective is a valid candidate upper cost only for the precisely declared model/expansion and binary mask, with feasibility established separately.

The upstream validator is not the acceptance oracle: it rounds binary status at0.5, uses looser tolerances, and its transition-ramp rules differ from the model; curtailment-key and reserve-error-accounting issues were also found. These observations justify the independent source-equation checker and are not an upstream solver result.

Allowed source-stage tests use a handwritten four-hour, one-unit fixture only. They check valid noncanonical segments, fractional startup rejection, native-versus-hard-service curtailment, initial ramp shutdown behavior, residual initial dwell, objective tampering, an intentionally deleted ramp row, and a null canonical-cost diagnostic outside its nominal domain. They do not load OR-LIB10, call target-generation code or invoke optimization. Scientific model counts remain zero.

## Commands and future gates

Source-stage synthetic check (Python standard library only):

```text
python -I -S src/researchnext_orlib_uc.py self-test --report results/research_next/orlib_preflight/synthetic_checks01.json
```

After source review and explicit preparation authorization only, with locally acquired exact upstream files and the exact selected gzip:

```text
python -I -S src/researchnext_orlib_uc.py prepare --case-gzip INPUT/10_0_1_w.json.gz --source-root INPUT/UnitCommitment.jl --protocol docs/research_next/ORLIB_TRANSFER_PROTOCOL.md --output NEW_PREPARED_DIRECTORY
```

The preparation refuses an existing output directory or any source/data hash mismatch. It captures input bytes once, derives normalization from that same case snapshot, and copies those exact case/source/protocol/adapter snapshots into the archive. Before closure it rereads every original input and requires byte equality with the captured snapshot; any change fails and preserves partial outputs. It preserves raw inputs, source, protocol, normalized case, six models, descriptor and manifest. An independent prepared review must establish input transport, the two service variants' exact row/objective equality with only C upper bounds changed, all960 binary coordinates, initial/ramp/cost semantics, row normalization and every bound/projection justification. No optimizer backend exists in this harness.

A later separately reviewed execution extension may allocate one full-binary MIP300 seconds and one LP30 seconds to each of the six fixed models (native and hard-service identity plus two targets), thread1/seed0, with all outcomes retained and no retries. This is a prospective bound, not permission to execute now. No cap or target-dependent model alteration is proposed. Exact lower proofs should use signed row multipliers plus finite-box residual correction, preserving raw rational bounds; incumbent upper witnesses must pass both exact checkers. For each service variant retain all signed target-minus-identity brackets `[L_target-U_identity, U_target-L_identity]`; absent uppers, nonpositive bounds, infeasibility and unknown outcomes remain explicit. Native and hard-service brackets must never be pooled.

Current unresolved gates are source/adaptor review, native case preparation, independent prepared replay and a later solver implementation/execution review. No new scientific finding is asserted by this protocol.
