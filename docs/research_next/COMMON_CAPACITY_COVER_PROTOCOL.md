# Universal common-commitment capacity-cover floor

Prospective protocol, 27 September 2026. This is a classical 0/1 covering-knapsack implication for the two fixed original identity/day321 worlds, not a new method or a further optimizer run. Source: `src/researchnext_common_capacity_cover.py`. The design memo SHA256 is `1292887f44b46eae60093620c4b062c4b9842d01c1852bb0d8f86c4aba9f6993`.

## Frozen denominator and target

Use the original common archive with freeze `4f21891d7d1f1793dd92e5b830edf5b5cf62474e5521d788c9aec17929ea9a59` and manifest `8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c`. Both unchanged 34,681-row, 23,016-column world models retain their original full 12,096-bit masks and original 23,195 MWh caps. Their U/Y/Z coordinates are shared through the verified original joint maps. No frozen-union state bounds are used.

The target is the same uniform finite-bound expansion `tau=Fraction.from_float(1e-5)`, not a decimal replacement. Integer coordinates remain exact integers. The original common assembly is inherited through its existing independent transport review and immutable bindings, rather than regenerated. All 48 inherited inputs are checked before and after preparation/execution. The pinned standalone stdlib NPZ/CSR decoder is reused explicitly; this is not an independent parser implementation.

## Preparation and admission

One `--prepare-only` is authorized separately from scientific calculation. Capture immutable input bytes and new source/protocol hashes before admission; copy the selected two original matrices, bounds, masks, row metadata and model metadata plus joint maps/mask/native roster. At close rehash all inherited/source inputs and every prepared payload. Freeze admission, payloads, input manifest and transport hashes. No scientific DP table, threshold or cap verdict is computed during preparation.

Check exact sparse coefficients and endpoints, not row labels alone: all 24x168 thermal upper and lower rows in each world, all 168 aggregate equalities, both complete 23x168 fossil-cap rows, original U boxes and all original integer masks. The actual fossil unit roster must equal the native Coal/NG/Oil roster, excluding the one nuclear unit. The upper and lower thermal coefficients must be nonnegative integers, with minimum not above maximum, and equal their native CSV nameplates exactly. Every hour's ordered fossil capacity/minimum pair must be identical across the two worlds. Nonfinite, noninteger, differing or malformed premises are UNSUPPORTED; there is no ceil/floor coefficient fallback, replacement case, envelope substitution or repair.

Hard declared admission guards: capacity-grid sum at most 100,000 and at most 168 distinct common ordered coefficient tuples. Group identical tuples and reuse one complete table per tuple. Sum-capacity calculation and tuple grouping are resource/admission checks, not scientific threshold queries. A future source/protocol revision would be needed to broaden this supported input class.

## Exact bound and calculation

For each world/hour, let L be the actual aggregate lower endpoint minus tau. Let nonfossil U be the original finite column upper endpoint plus tau. Define d as the maximum of (i) L minus the sum of the 18 nonfossil upper bounds and (ii) the sum of the 23 fossil original lower boxes minus tau each. Fossil generation is at least d. Using nuclear's unconditional upper box is an explicit safe relaxation of its shared commitment; it does not claim that upper dispatch is attainable. Keep any small negative fossil floor allowed by expansion.

The 23 thermal upper rows require shared integer capacity at least H=max(d_identity,d_day321)-23*tau. The exact integer threshold is max(0,ceil(H)), using rational ceiling. For each distinct coefficient tuple, a complete 23-item exact-capacity dynamic program finds minimum committed fossil PMin cost M among all binary subsets whose total capacity reaches that threshold. The recurrence starts at D0[0]=0, other states unreachable, and uses a separate previous layer for each unit. Preserve all 24 full layers, including unreachable states, and the full terminal exact-capacity and suffix-minimum frontiers. A minimizing feasible subset alone would not certify the minimum; the complete recurrence is the evidence.

Each world's necessary hourly fossil floor is max(d,M-23*tau). Sum the 168 hourly floors and compare with that world's original cap plus one tau. Strict excess for either world, or an empty capacity-cover set, gives a universal common-binary rejection pending independent proof review. Exact equality is a null. Otherwise report NO_REJECTION_FROM_THIS_BOUND and keep the original binary question UNKNOWN. This bound ignores network/dwell and cannot attribute a rejection to chronology-specific residence constraints. It is unrelated to a proof that the single old union schedule is feasible or infeasible.

The known expanded joint continuous point need not satisfy this integer-specific floor. No LP-point replay/comparison is part of this arm. No fractional-cover baseline, state search, cap change, optimizer, alternative rounding or further scientific case is included.

## Tests, execution and evidence

Before admission, tiny invented fixtures exhaustively enumerate all subsets and prefixes for several small integer rosters, compare every exact DP state and rational threshold query, test negative/positive rational ceiling, a strict integer-vs-fractional cover jump, a cap equality boundary, and rejection of mismatched world tuples, wrong roster/grid guards and malformed actual thermal coordinates. They read no scientific model and import no scientific decoder/optimizer.

One future `--run-prepared --expected-freeze-sha256 <trusted hash>` requires separate root authorization. One 120-second soft calculation phase begins at entry, includes input validation, DP, serialization and final rehash, and is sampled after all substantive result files are saved. The final completion-record write is explicitly outside that sample. Check the budget during each layer/state sweep, each hour and after writes. A slow filesystem operation can return after the limit; then retain partial files and report INCOMPLETE, never a complete scientific verdict. Do not restart or resume automatically. Preserve unsupported/partial/error evidence.

Execution produces exactly one table per admitted distinct tuple and 168 common threshold queries with two world derivations each. Recheck source/protocol/prepared payloads and the manifest/freeze transport at close. Independent verification of the actual selected row premises, full DP recurrence and exact endpoint comparisons is required before using a rejection scientifically. No interpreter install, external network action or optimizer call is authorized by this protocol.
