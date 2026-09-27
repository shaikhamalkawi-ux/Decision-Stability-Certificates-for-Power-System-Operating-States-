# Independent exact affine-cut replay

**PASS.** One independently authored replay completed in 1.1875687 seconds on 27 September 2026. Both world cuts are valid consequences of their original uniformly expanded rows and boxes. All 73 frozen inputs and 33 producer outputs were unchanged at entry and close. No optimizer, producer import, source reselection, control rounding or old full-point membership replay occurred. The pinned standalone NPZ/CSR decoder was reused; the endpoint aggregation and verification arithmetic were independently implemented.

For each world, the reviewer reconstructed the exact signed upper halfspace for every saved original row/box endpoint and used its nonnegative rational multiplier. It checked the retained hourly source keys and branch choices, their generation normalization, and complete cancellation across all **23,016 original columns**. Every surviving coefficient is on original U. The reconstructed coefficient vector, right side, alpha and cap match the saved rational records exactly, including all original tau contributions and no extra derived-row tolerance.

Both cuts reject the frozen union by the exact amount

`242967941527088396181895 / 590295810358705651712 MWh`, approximately **411.6037032 MWh**.

The already accepted, unrounded continuous joint point satisfies the new cuts, with exact positive slacks approximately **1,525.7268000** and **1,520.6478492 MWh** in identity and day321 respectively. Its prior full membership is inherited through pinned original model/control records. This review checked only the newly derived inequalities at that point, not the old model rows again. The point remains fractional and supplies no binary witness.

Each cut has **82 positive U coefficients and no negative U coefficient**, supported on 24 U-hours. Therefore every binary commitment componentwise above the union also violates each cut. Any feasible common binary commitment must turn off at least one of the union's on-bits; simply adding on-hours cannot repair the cap. This conditional-corollary premise is now verified from the actual coefficients. It does **not** exclude schedules that rearrange commitment, prove that no common schedule exists, or identify a dwell-specific obstruction. The unrestricted common question remains **UNKNOWN**.

The two cuts are **not identical**; both are retained. Each proof uses 151 original row endpoints and 3,442 box endpoints, with 3,593 unmerged endpoint uses including the cap. Its 82 surviving state coefficients do not mean that only 82 original inputs were needed: the proof retains all 168 selected hourly bounds and a global energy-cap dependency. No minimality, raw-information compression or new-method claim is justified.

Producer ledger: one schema2 arithmetic execution, 1.2298321 seconds, no soft overrun and zero optimizer calls. The earlier original arm failed before constructing any cut because its declared NPZ schema omitted three existing members. That zero-cut failure and the initial unexecuted reviewer draft remain untouched. This separate reviewer explicitly reads the existing four-member NPZ schema; the control/model/proof-selection bytes are unchanged. No numerical retry or alternative proof selection was introduced.

Reviewer source SHA256: `d076806a21d0c76768a949bdba471c46d45c20ea8226d9b76ab5a02a6ae08144`. The sibling `independent_postrun_review.json` records exact fractions, support counts, trusted source/protocol/freeze/inventory hashes and the complete two-case denominator. All new reviewer files are separate from the immutable producer records.
