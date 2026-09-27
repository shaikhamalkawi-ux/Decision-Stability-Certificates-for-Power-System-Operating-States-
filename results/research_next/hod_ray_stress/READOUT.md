# Closed fixed-ray HOD stress experiment

The single authorized run completed all twelve contextual margins and all six extremizer roles. It found one new first-week chronology certified infeasible in the uniformly expanded encoded model. The same unchanged trained ray failed to separate every chronology in the two other declared January families: their exact maximum margins are negative. This is a null transfer result for this particular ray, not evidence that either family is feasible.

All producer applicability, package, assignment/full-model margin and final hash checks passed. No errors, phase skips, solver calls, ray refits, alternative projections or positive-witness searches occurred. Independent post-run review is a separate gate; this readout records the producer's closed results.

## Six fixed extremizer outcomes

The ray was trained on the already known negative first-week seed26093200. It was reused without changing a multiplier, orientation or scaling. The table's margins are certificate-margin units under this fixed scaling, **not MWh or operating-cost differences**. Caps are the unchanged fossil-energy budgets in MWh. Decimal margins are display approximations; signs and decisions use exact rational arithmetic.

| January week | Existing cap MWh | Minimum expanded margin | Maximum expanded margin | Maximum result |
|---|---:|---:|---:|---|
|1|23195|−823781.153960281|+17651.75749732912|certified expanded infeasible|
|2|26532|−1578152.2924085485|−958310.6033940823|nonseparating over the whole declared family|
|3|48319|−1858581.4415148974|−936589.4576603328|nonseparating over the whole declared family|

The three minima and the latter two maxima also failed to separate the strict encoded model. There is no positive-feasibility inference from any of these five nonseparating points. The first-week maximum improves this particular margin over its trained source context, whose expanded margin is17111.125630528997. It does not maximize true UC cost, physical severity, or the number of infeasible family members.

All six exact expanded margins share denominator

`D = 748288838313422294120286634350736906063837462003712`.

| Week/role | Exact numerator (margin = numerator / D) |
|---|---|
|1minimum|`-616426242721429168570644409407521423680238519992789624237`|
|1maximum|`13208613111866649912228518373674133679809458718987393619`|
|2minimum|`-1180913745568057075450126711018991203800786347158603163053`|
|2maximum|`-717093128157192585850877842743531671262617016499182626221`|
|3minimum|`-1390755747782068381132300508293912209957207972809204950445`|
|3maximum|`-700839437249248662946414761309235633846207901295589582253`|

## Finite family, proof and context checks

Each week fixes its first/last48hours and independently permutes three interior packages at each clock hour. The complete107-coordinate package is retained. All three packages in each of the24groups were distinct, so each declared family has exactly6^24=4738381338321616896different physical input sequences. The kernel evaluated144group assignments per week; it did not enumerate that entire Cartesian product or solve a dispatch problem. Exact lexicographic local source-order tie breaking selected each extremizer. Every selected extremizer differs from all four retained old orders in its week; no duplicate was omitted or replaced.

Each week retained6743selected endpoint terms:1442nonzero row multipliers plus5301nonzero combined-column support coefficients. Of these,1421were assigned to interior destination/source tables; all remaining terms, the actual weekly fossil cap and the complete row-plus-column tau penalty entered the fixed contribution. Full selected-endpoint catalogues, rational coefficients, q, norms, constants, group tables, all ties and deterministic choices are preserved in `run01/week_1_family.json`, `week_2_family.json` and `week_3_family.json`. Support counts are not minimum raw-information or memory requirements.

Native thermal constants, binary64 hourly ramp redundancy, every unit/dwell/transition row, all normalized network blocks, full12096binary masks and exact CSR/coordinate equality across the three identities passed. The source-level coefficient-invariance argument was checked against pinned builders. The complete new bounds were assembled from reordered native package values, archived, reloaded and checked by the existing general exact ray verifier. Each of the six full-model gaps matched its assignment optimum exactly, including tau=Fraction.from_float(1e-5), all finite boxes and the original independently rounded aggregate/nodal balances.

All twelve old contextual margins lay between their respective extrema and matched direct full-endpoint evaluation. The trained context reproduced its previously archived exact strict/expanded fractions. All six identity/class-positive contexts had negative margins, as required. Among the six old ordinary contexts, only the trained seed26093200 separated under this particular ray; other previously certified negative cases need not be detected by it. Their historical labels were not changed, and seed26093211 remains binary UNKNOWN. No old primal witness was replayed.

## Exact files and accounting

Preparation ran once and admitted132bindings. The reviewed source then ran once under cached CPython with `-I -S`, session23860,exit0. Scientific phase time was26.67203430001973seconds against its600-second soft limit. Initial byte validation/import took0.3828277999709826seconds. Elapsed time through final rehash, before completion-file closeout, was28.16957659999025seconds. All132bindings matched again at close. Zero optimization, clustering, ray-fitting and binary-witness replay calls occurred.

| Artifact | SHA256 |
|---|---|
|`src/researchnext_hod_ray_stress.py`|`f89dd091519bf6d6ce43c5f4d33366cdb809d49637bb83d0574e4e8ff090be95`|
|`docs/research_next/HOD_RAY_STRESS_PROTOCOL.md`|`d118a47250b8d4945a63e97210b2bc1150f482b8e874758a2d7475de23eb23a2`|
|`prepared/input_freeze.json`|`38c358e51b42df6ad8ff7766b00d92a995c218f621b34cc0e896ccbbdc9dda76`|
|`run01/completion.json`|`ac6b1da871bed6d24c229c6855acc447f37fbdfe0836a0ba1b3f75ad992be64b`|
|`run01/all_outcomes.json`|`87bc7a037522d56cbaaf42ea2caae10b5364400961651f068f87de05d926139f`|

The six `run01/week_*_minimum/` and `run01/week_*_maximum/` directories contain the complete native/model/bound/mask/label/permutation archives and rebound unchanged-ray certificates. Twelve `context_*.json` records retain all contextual outcomes. `fixed_ray_and_q.json` records the single trained source and exact combined coefficients. `SOURCE_READINESS.md` remains the historical pre-execution checkpoint; it was not rewritten after execution. No frozen old file was edited.

This is a same-system, post-label, fixed-certificate stress test using classical assignment arithmetic. The new chronology has no newly verified feasible uncapped upper schedule, so no finite operating-energy penalty is claimed. It is not an executed representative-period method, weather-plausibility result, independent-network result, field trial, general novelty claim or proof of minimum information. The original binary64 network encoding and its established strict-versus-expanded interpretation are preserved.
