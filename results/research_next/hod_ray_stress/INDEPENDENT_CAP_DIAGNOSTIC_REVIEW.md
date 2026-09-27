# Independent cap-diagnostic source and mathematics review

**PASS**,27September2026. Read the complete diagnostic source, root interpretation and closed JSON. No source execution, scientific recalculation, model generation, assignment optimization or old-checker replay was performed by this reviewer. This is an independent algebra/claim review of already recorded quantities, not a second proof execution.

Reviewed bytes:

- `src/researchnext_hod_cap_diagnostic.py`: `1ca6e7bca9cc5bc92bc08c8d10a251d2fa8cccd7bcde7288fac9d8f09923739e`.
- `ROOT_REVIEW_AND_CAP_INTERPRETATION.md`: `a25ef1114db20fb3943de4c4ac8c3d70bb56b188ea02d8bd2f909b1f9c605c2b`.
- `POSTHOC_CAP_DIAGNOSTIC.json`: `42490dd090a660338eb0e5d8f15f20181356103501f32f830a00c390bd0019ba`.

The cap is the upper endpoint of one row with negative signed multiplier d_cap. Altering only this endpoint from C0 to C contributes exactly d_cap(C−C0) to every chronology's margin. A, q, all other endpoints and the full row/column tau penalty remain fixed. Therefore both recorded extrema shift by the same amount, and their selected assignments remain extrema. The sign and threshold formula C*=C0−G(C0)/d_cap are correct; lowering C increases the margin because d_cap<0.

For a nonempty finite family, strict positivity of the shifted minimum is equivalent to this fixed ray separating every family member; strict positivity of the shifted maximum is equivalent to this ray separating at least one. Thus C below the minimum-derived threshold gives the all-orders statement, and C below the maximum-derived threshold gives the some-order statement. At each threshold its corresponding extreme has zero margin. At the all-orders threshold, other family members may still separate; at or above the some-order threshold, no member has a strictly positive margin for this ray. The root memo correctly uses the phrase “corresponding extreme” and does not claim all margins vanish at either equality.

The row multiplier and tau dependence are not rescaled or dropped. The JSON key `strict_budget_threshold_MWh` means strict inequality in the cap, as explicitly clarified in the memo; these are derived from uniformly expanded-model margins, not tau=0 margins. Restricting the stated claim to nonnegative budgets is consistent. Exact fractions support the thresholds; decimal displays are not decision thresholds.

The source pins the closed completion, checks the12context/6extremizer ledger and recorded min/max relations, locates the single fixed cap endpoint by actual row metadata, and hashes its inputs before/after. It does not independently prove the original extrema or regenerate models. That limitation is stated clearly. The post-hoc interpretation does not choose or run new caps and leaves the original failed transfer at caps26532/48319 intact. It also avoids extending that null into failure at every possible cap.

No hidden feasibility converse, exact UC optimum, finite-energy penalty, universal ray-transfer, weather-realism or novelty claim was identified. The thresholds are valid conditional algebra for this frozen ray, family and encoded model; they do not replace a positive witness or a different certificate. No correctness change is requested.
