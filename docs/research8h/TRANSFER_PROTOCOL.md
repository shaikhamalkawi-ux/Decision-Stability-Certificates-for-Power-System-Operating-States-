# Prospective same-week transfer of fixed temporal rules

This protocol is frozen before generating the new case outcomes or running any transfer LP. The rules are learned from earlier development cases; the present test uses new seeds but the same repaired July week, same source model and same 41-unit complete mean target. It is prospective rule transfer within one week, not external validation or a new network sample. Preserve every generated case, failure and duplicate without replacement.

## Frozen sample generation

Generate exactly eight ordinary twins with seeds **26092700–26092707**, using `numpy.random.Generator(numpy.random.PCG64(seed))` to permute source indices 48..119. Keep the first and last 48 source indices fixed. Permute complete hourly packages jointly: native demand/nodal load, generator availability, seed dispatch and all 24 thermal commitments. The complete individual weekly means stay unchanged.

Generate exactly eight positive controls with seeds **26092800–26092807**. Partition the same interior source indices by the exact full 24-bit thermal commitment row of the verified repaired witness. Iterate classes in first-occurrence order. For each class, assign a random permutation of its source indices to its original positions, using one seeded generator per case. No resampling, rejection sampling or replacement is allowed. Because every destination has the same complete commitment vector as its assigned source, the entire U sequence stays pointwise unchanged. Compute Y/Z anew from adjacent U values; never permute old transition indicators.

Every case keeps a complete row permutation. Check the inverse restoration of complete packages and means, unchanged edges, exact class membership for positive controls, uniqueness/duplicates and changed-hour counts. Duplicates (including identity or previous development orders) stay in the sample and are reported. Save all 16 generated orders, witness/control checks, source hashes and a sample-freeze timestamp **before the first LP**. Do not choose seeds or rules after seeing any transfer outcome.

Independently check every positive-control P/U schedule against native minimum-up/down, rounded output coupling, native on/on ramps, aggregate and nodal balances, and branch limits. Require all checks to pass before solving. The original repaired witness also passes the complete identity LP matrix. Ordinary permuted seed schedules need only pass static/network checks; a failed seed chronology replay is not an infeasibility proof.

## Three fixed LP models for every case

All three models use the unchanged bound `temporal_lp_certificate.assemble` function, continuous P/U/Y/Z, the same column bounds, free initial state with zero initial transitions, clipped terminal dwell, static hourly aggregate balances and per-unit availability/output coupling, fixed hydro and **all 41 complete weekly means**. Network constraints and integrality remain relaxed.

1. **Full LP:** all original temporal rows.
2. **Two-CC rule:** keep transition, startup/shutdown exclusivity, minimum-up and minimum-down rows only for `107_CC_1` and `118_CC_1`. Remove those four row families for every other thermal unit. Keep all other rows and all column bounds, including the now partially unused other-unit Y/Z variables. Do not retune units per case.
3. **Fixed 48-hour locality rule:** keep global transition and exclusivity rows for every unit. Keep a minimum-up/down row only if every nonzero U/Y/Z variable in it has an hour in **[60,107]**, inclusive. This is the previously frozen direct-support definition; do not truncate rolling sums, change window placement, or infer isolated-window information sufficiency.

These are row-subset relaxations of the full continuous model, which itself relaxes the original UC model. All original positive witnesses must satisfy all three corresponding restricted matrices. A verified relaxed LP solution establishes only continuous feasibility; it does not establish full UC feasibility. Full-UC feasibility of positive controls comes separately from the original network/chronology witness checks.

## Fixed budgets and proof requirements

Use all 16 cases in listed order: eight ordinary twins followed by eight positive controls; run full, two-CC, and locality in that fixed order for each case. Maximum 30 seconds per LP, single thread, seed zero, simplex with presolve off. Phase wall budget is 20 minutes from the first LP; if fewer than 35 seconds remain, record the remaining scheduled runs as not run for budget and stop. No reruns or time extensions. Unknown/incomplete results remain unknown.

Every claimed negative needs the existing exact-rational check of saved binary64 matrix/bounds/multipliers and a positive separation after relaxing all finite bounds outward by `1e-5` in their own units. Archive and replay each certificate or continuous witness without optimization. Save raw solver statuses even when no robust certificate is obtained. Any positive-control solver infeasibility or negative certificate is a fatal contradiction: preserve the evidence and stop for diagnosis rather than silently excluding that case.

Report all 48 scheduled outcomes, duplicates, failed seed-replay counts, runtimes and input bindings. For each restricted rule, coverage is the number of ordinary twins rejected with robust exact certificates divided by the number of those twins rejected by the full LP with robust exact certificates. If the denominator is zero, coverage is undefined. Report separately any full-LP admission or unknown; never treat unknown as feasible UC. Report positive-control false rejections against the independently verified network witnesses. Do not infer coverage on new weeks, networks, targets or arbitrary permutations from this small same-week sample.
