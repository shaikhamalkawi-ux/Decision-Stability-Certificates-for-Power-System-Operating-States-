# Read-only assessment of an additional RTS area

Decision: **HOLD new-area optimization in the current research window.** Area 2 has a different generation roster and different hourly profiles, but its isolated transmission network is an exact copy of Area 1's template after canonical relabeling. More importantly, Area 2 contains concentrating solar power (CSP) with source-defined storage and natural inflow, which the existing model does not implement. Area 3 is not a clean fallback: it retains the same network template with one additional branch and includes a battery whose energy dynamics are also absent. No new-area model, matrices, dispatch, optimization, or feasibility verdict was produced by this assessment.

The selection was fixed before inspecting any new optimization outcome: Area 2, source rows 0–167 (2020-01-01 Period 1 through 2020-01-07 Period 24), as the lowest-index unused area and the same January week. Area 3 was inspected only for structural compatibility, not selected after a solver failure. The pinned source supports both areas; the limitation is the currently admitted model and adapter, **not missing upstream data**. A future valid Area 2 experiment would be a held-out area/roster/profile test within RTS, not independent new-network validation. Its broader roster coverage could add more than another Area 1 week, but the implementation and independent verification required do not justify a rushed additional arm before approximately 04:00 UTC.

## Evidence and comparison procedure

All eight existing native CSVs were read directly from `C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs/raw/RTS-GMLC_v0.2.3`. The source revision is `GridMod/RTS-GMLC@3ece0d3725c844056132393ee252b3083dd4eab4`. Existing hashes match the acquisition lock in `src/v8r1_prepare_rts_inputs.py`. Additional pinned source metadata were fetched read-only over normal certificate-verified HTTPS and examined in memory; they were not added to the admitted input archive.

The branch comparison preserved parallel circuits as a multiset. Each endpoint was replaced by its integer bus ID modulo 100, the branch UID was removed, and **every remaining source column** was compared as its exact CSV string. Thus the result is stronger than matching connectivity or just the coefficients used by the DC model. Generator UID comparison similarly removed only the area prefix while retaining the within-area bus number and complete unit suffix. No physical/cost field was normalized away. Exact hourly comparisons used binary64 `.hex()` values without rounding, interpolation, or quantization. Only source tables, schemas, counts and code were inspected; no new network matrix was assembled.

| Source-derived inventory | Area 1 | Area 2 | Area 3 |
|---|---:|---:|---:|
| Buses | 24 | 24 | 25 |
| Internal AC branch rows, including parallel circuits | 38 | 38 | 39 |
| Generator rows | 52 | 37 | 69 |
| Decision rows under the existing positive-PMax/non-RTPV filter | 41 | 35 | 48 |
| Positive-PMin rows excluding Hydro/PV/Wind | 24 | 24 | 26 |
| Coal/Oil/NG decision units | 23 | 23 | 26 |
| Nuclear units | 1 | 0 | 0 |
| Hydro / utility PV / wind / RTPV rows | 6 / 10 / 1 / 10 | 10 / 1 / 0 / 1 | 4 / 14 / 3 / 20 |
| Additional technology requiring adjudication | None in the existing selected model | CSP, 1 | Battery storage, 1 |
| Local source bus marked Ref | 113 | None | None |

The count of 24 positive-PMin units in Area 2 includes `212_CSP_1`; it must not be called 24 fossil units. Its fossil roster is 4 Oil, 7 Coal and 12 NG units. Area 1 has 6 Oil, 8 Coal, 9 NG and one nuclear conventional unit. Of the canonical conventional UIDs, 15 match between areas. All 15 have equal PMax, PMin, minimum up/down time and ramp-rate strings, but only 2 match across the tested cost/startup/heat-rate fields. Nine Area 1 conventional UIDs have no counterpart and eight Area 2 conventional UIDs have no counterpart. This is a roster change, not a claim that every individual physical parameter differs. The cost comparison included fuel price, VOM, average/incremental heat rates, output breakpoints, startup/shutdown costs and hot/warm/cold startup heat; emissions equivalence was not assumed.

Area 2's complete 38-branch canonical multiset is exactly equal to Area 1's, including resistance, reactance, charging, all ratings, outage fields, tap ratios and length. Corresponding buses have equal MW load proportions and equal compared BaseKV/load/shunt fields; canonical bus 13 changes from Ref to PV. Regional load values differ in all 168 selected hours (maximum absolute difference 221.094918 MW). All six canonically matched hydro series differ in all 168 hours (maximum absolute difference approximately 16.6 MW). PV and RTPV do not have matching canonical UIDs across these two rosters, so there is no invented one-to-one profile comparison.

Area 3 contains all 38 canonical Area 1 branch rows unchanged, plus the 23–25 branch (X=0.009, tap=1, continuous rating 722 MW). This small extension of the same template is not an independent network family. Its 50 MW `313_STORAGE_1` would be incorrectly treated as an unconstrained nonthermal generator by the old availability logic.

## Isolation and source coverage

The existing area selection drops every branch with an endpoint outside the selected area. For Area 2 the removed AC ties are `AB1` (107–203), `AB2` (113–215), `AB3` (123–217), and `CB-1` (318–223). For Area 3 they are `CA-1` (325–121) and `CB-1` (318–223). Area 1 also drops its four incident ties. A future result must identify an **isolated area**, not the connected three-area RTS system. The source also contains a separate DC-branch schema; the present AC DC-power-flow model does not silently import HVDC facilities.

The five admitted hourly tables each have 8784 rows. Their first 168 Year/Month/Day/Period tuples agree. Every selected Hydro/PV/Wind/RTPV UID in Areas 1, 2 and 3 exists in its appropriate admitted table; Area 2 has no wind units. Regional load columns 1, 2 and 3 exist. This proves ordinary profile coverage, not full technology-model eligibility.

The pinned [time-series documentation](https://github.com/GridMod/RTS-GMLC/blob/3ece0d3725c844056132393ee252b3083dd4eab4/RTS_Data/timeseries_data_files/README.md) describes the CSP table as hourly solar potential. The separate [CSP inflow file](https://github.com/GridMod/RTS-GMLC/blob/3ece0d3725c844056132393ee252b3083dd4eab4/RTS_Data/timeseries_data_files/CSP/DAY_AHEAD_Natural_Inflow.csv) has 8784 records and column `212_CSP_1`. The pinned [time-series pointers](https://github.com/GridMod/RTS-GMLC/blob/3ece0d3725c844056132393ee252b3083dd4eab4/RTS_Data/SourceData/timeseries_pointers.csv) associate it with `212_CSP_HEAD_STORAGE`, parameter `Natural_Inflow`, scaling factor 200. These are inflow data, not permission to equate inflow to electrical PMax or to let the plant dispatch at 200 MW every hour.

The pinned [storage table](https://github.com/GridMod/RTS-GMLC/blob/3ece0d3725c844056132393ee252b3083dd4eab4/RTS_Data/SourceData/storage.csv) records CSP maximum storage 1.2 GWh, initial volume 0, start energy 0.04 and inflow limit 0.1 GWh. Its generator row has PMax 200 MW, PMin 30 MW and one-hour minimum up/down times. Area 3's battery has 50 MW charging power, 85% round-trip efficiency, and head/tail storage rows each with maximum 0.15 GWh and initial 0.075 GWh. The detailed conversion, efficiency, startup-energy and terminal conventions require an admitted implementation and review. The present assessment does not invent them. Existing fixed-output Hydro follows the already selected benchmark-output convention; it is not a claim to implement the upstream reservoir dispatch model.

## Code admission and boundary conventions

The generic sparse kernels mostly derive dimensions from their arrays, but the complete pipeline is Area 1-specific:

- `src/rts_native_model.py:9` selects `AREA=1` and builds filtered tables/network at import. Changing the variable afterward leaves stale objects. `src/v8r1_rts_seasonal.py:24–29` actually imports the portable `code/dscgrid_model.py`, and its input helper reads existing Area 1 target archives. A separate native timestamp extractor is needed; no Area 1 mean target should migrate into this arm.
- `src/research8h_service_network.py:34–36,64–65` excludes only `121_NUCLEAR_1`, asserts 23 fossil units, and requires that nuclear UID to exist. A future objective must derive the Coal/Oil/NG roster directly and verify every fossil unit, including any zero-PMin units. Area 2 has no nuclear UID to look up.
- `src/research8h_service_network_mip.py:30` assumes 41 removed mean rows. Seasonal drivers hard-code 168/41/24/24 unpacking and 34680-by-23016 metadata in continuations. Labels such as “23 fossil units” and “24 thermal units” must derive from the admitted roster instead of persisting by accident.
- The existing availability routine recognizes Hydro/PV/Wind and rooftop PV only. CSP and battery state variables/equations are absent. Excluding those units or holding them off would define a different restricted model requiring explicit prospective justification; neither is an automatic fix.
- Only Area 1 has a source Ref bus. An isolated connected area can use an explicitly chosen angle gauge, but the current lookup fails. Choosing canonical bus 13 (213 for Area 2) would be a new declared gauge, not a native Ref label. Connectivity and finite positive line X/rating were inspected as metadata; a future adapter still needs matrix/rank and direct-flow verification before admission. Because finite angle boxes are used, preserving the declared gauge is part of the model specification.
- The current chronology has free mature initial commitment, Y0=Z0=0, ceiling-rounded native dwell durations, no prehistory, and obligations truncated at the last horizon hour. It does not impose cyclic or post-horizon closure. These are **the existing model's conventions**, not an upstream initial-history claim. Storage requires additional initial/terminal conventions beyond them.
- Temporal assembly contains no explicit ramp rows. Existing on/on ramp omission was justified for the admitted source/range, so any new adapter must recheck source rate times 60 against the actual thermal hourly range and preserve the same startup/shutdown scope. Passing a nameplate metadata comparison alone does not validate CSP/storage chronology.
- `solve_hour` in the native file permits shedding and does not impose dwell; it is not a valid reference generator for this proposed no-shedding UC test. Independent checks need dynamic dimensions, safe empty-category reductions and full technology coverage.

These findings were independently checked by a second agent against the unchanged source. Frozen sources and completed evidence were not edited.

The metadata-only graph traversal found each retained area connected, with positive finite branch X and continuous ratings. All selected positive-PMin rows have positive dwell durations. For those rows, the minimum of `60 * Ramp Rate MW/Min - (PMax MW - PMin MW)` is 30 MW in Areas 1 and 2 and 53 MW in Area 3, with no negative margins. Every Coal/Oil/NG decision unit has positive PMin in all three areas. These checks remove certain schema hazards but do not supply the missing energy-state model or validate a new matrix.

## Minimum future design, conditional on a reviewed adapter

This is a design recommendation, not authorization or a prepared runnable experiment. Freeze one Area 2 January week, the complete roster, separate input archive, CSP/storage semantics, isolated topology, angle gauge and all boundaries before solving. Do not switch to Area 3 because a result is inconvenient. Preserve all 35 decision units with admitted source-grounded technology models; if that cannot be done, retain HOLD rather than silently deleting CSP.

1. Obtain one independently verified no-shedding full-DC/native-UC reference, with objective total Coal/Oil/NG electrical MWh and no named-unit means. Use one declared reference solve budget and retain any gap/status. Failure to find a verified incumbent is UNKNOWN and stops dependent tests. A numerical optimum is not required or presumed.
2. Freeze two ordinary complete-hour package permutations of the 72 interior hours (hours 48–119), keeping the first/last 48 hours unchanged, before either outcome. Set the cap by a predeclared exact rule such as ceiling(1.01 times the verified reference fossil energy). Keep the same cap, source data, network and physical model for both cases. These are two cases, not two independent networks.
3. Retain the identity as a full positive. For one additional shuffled positive control, a U-class permutation alone is **insufficient** when storage is present: it can break energy balance even if the commitment string is unchanged. Either construct a predeclared permutation that provably preserves every storage state transition and verify it, or run one predeclared fixed-commitment full-physics redispatch and accept the control only after complete independent verification. Failure is retained as a failed control construction, with no search over replacements. No negative experiment proceeds with an unverified assumed positive control.
4. Compare each ordinary case with a full continuous relaxation, retaining static/network/energy constraints and all admitted technology couplings. An exact robust certificate rejects that relaxation; a feasible LP only admits the relaxation. Binary/network/storage positives require archived vectors, source checks and exact expanded-model membership. Retain every UNKNOWN and every failed control. Report the denominator and do not call this a blind external-network validation.

Before any such solve, the adapter needs source/hash freeze, dimension/roster/input coverage checks, an Area 1 replay demonstrating that genericization preserves the existing model where technologies coincide, and an independent proof/code review of the additional energy-state equations. Those dependencies make it a separate research task rather than a safe late-window replication. This assessment recommends completing and reporting the already verified evidence instead.

## Source bindings

The official pinned tree response was untruncated and identified the requested commit; response SHA256 was `3c74771ddd87fb47335319d9146cdfa0efcf134303175c0e5c44235a31445928`. Fetches of the additional files succeeded; no TLS verification was disabled.

| Native source file | SHA256 |
|---|---|
| bus.csv | cec3f776222812d43eaeaf7ac85b577719dc565f354a04e120c12a647ddb710e |
| branch.csv | e92d16d13b1c5d2899f7871c0c99c3eb94605528beef157bf9e1ccbcffe5ef4e |
| gen.csv | 988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068 |
| Hydro/DAY_AHEAD_hydro.csv | 4030660920df850138472c5561322c71e5037813c8e3232d3f9bde512a40606d |
| Load/DAY_AHEAD_regional_Load.csv | 7a9470d32d49068a91334cb36db54cceb2feb5cb1f702b0fa0847af8bac6cf21 |
| PV/DAY_AHEAD_pv.csv | bfede6e558df5ea0f244b6326940a4ee0b95138643aa8a062897c67134c9c185 |
| RTPV/DAY_AHEAD_rtpv.csv | 13a6933c2e0a513e1a453143876dadef6977e6add7701a21f56fe6a753afce42 |
| WIND/DAY_AHEAD_wind.csv | 6a1a8dc7d10a518523b3b319902ecc1ca1c400223832b26c6edb3a6e69d01dbc |
| SourceData/README.md | f0d8963335862faf6608144bf81aa8027241d669dd52aba0960501f374ef9ae3 |
| timeseries_data_files/README.md | 9a8abae13396b0c1d3bf037152f5c5ab1a08aa0ef45367199ea592effcc26021 |
| SourceData/storage.csv | cc55c4b02f7595ab77399075c721e31da748f29482c7d78319c4f1530bf4b82c |
| SourceData/timeseries_pointers.csv | 0854ba0c63d4973e8818c91c2328869e379bb0140520d4586f4ffddf387aca0d |
| CSP/DAY_AHEAD_Natural_Inflow.csv | 0c54ae19d17dfb63edaa81df2cf006c0d1b1df759a4ab6aca692bfeffa0490ac |

| Inspected author source | SHA256 |
|---|---|
| src/rts_native_model.py | 8c31b40047fe60ceefa34b3c5b2e21301d252dd11b80698827ab47a1f084cc3a |
| src/temporal_lp_certificate.py | 6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4 |
| src/research8h_service_network.py | 1cdfa891e4b83e685bb38021709b99066aae6daa994e3c4500e815357f156a41 |
| src/research8h_service_network_mip.py | a8c9c73b9f85b10afbb7aa93672ca595ccff6f30a1584faefeea5599a775c760 |
| src/research8h_seasonal_reference.py | 6844c70fdfe298d85cb2e247ca828cd3b0a1046f3bfc70f306743f74ac0e7805 |
