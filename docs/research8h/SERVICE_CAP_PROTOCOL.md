# Prospective aggregate fossil-energy cap sensitivity

This development sensitivity is fixed before its outcomes. It tests whether
the original four ordinary-twin LP rejections survive replacing all41 named
generator energy equalities by one shared upper budget. The five cases are
identity and seeds26092600--26092603, in that order; they were already selected
and rejected in the original pilot. This is not held-out validation.

Use the source-bound archived continuous models in
`results/temporal_information/lp_certificate/`. Remove every `target_mean` row
and retain all other rows and all variable bounds unchanged. Append one upper
bound on the sum of output across the23 fossil units: the archived24-unit
thermal list excluding121_NUCLEAR_1. This is a fossil-generation energy budget
in MWh, not an emissions measurement or cost calculation. No native verified
emissions factors are available for the present claim. Nuclear, hydro and
renewable energies are not individually constrained.

Fix the budget from the original verified July network dispatch: sum its
archived binary64 fossil outputs, rounding that exact sum upward to binary64,
then add1e-6 MWh solely to avoid an equality-edge conversion issue. Use this
same budget for every permutation. Do not tighten it after seeing outcomes.
The original identity P/U/Y/Z witness must pass the changed model before any
optimization. Save all input hashes, the exact rational reference energy,
budget and model artifacts before solving.

Run one LP per case with the existing independently assembled model and exact
certificate checker:45seconds, one thread, seed0, simplex, presolveoff. Preserve
all terminations and failed/fragile ray checks. A robust exact negative rejects
this relaxed service specification; a continuous witness only establishes LP
feasibility, not binary or network feasibility. A timeout without evidence is
unknown. No retry, threshold search or binary solve is part of this protocol.

The existing paired-order result concerns specified individual energies. A
positive outcome here would narrow its operational interpretation, not erase
the original result. This test is distinct from the theoretical k-gram example
with a dispatchable thermal unit and an emissions/energy cap.
