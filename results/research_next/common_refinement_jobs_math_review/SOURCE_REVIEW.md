# Independent source review: recovery-trajectory mathematical checker

**SOURCE_REVIEW_PASS.** Reviewer: `/root/find_deposit/gb_docs`, 27 September 2026. No material blocker was found in the reviewed source for the fixed, closed recovery trajectory. This is a source review, not a scientific replay, proof acceptance, or execution authorization.

Reviewed in full: `src/researchnext_common_refinement_jobs_math_review.py`, all 581 lines, SHA256 `26f703af2e31761f45cdb3bc1609f49fddb731669c3e05f2d53ee18aa751a163`. The reviewer also read the recovery protocol and relevant producer/helper source contracts for nomination, saved candidate checks, phase proof construction, sequential output writes and final admission. No producer or checker source was changed.

Source bindings checked during this review:

- Recovery producer: `fa1548f4d7765ac84e2f74a06df2fde640c713b85a1c27bdc29c99f3bb1b2973`.
- Recovery protocol: `14f9a4f2fb11966eec851e1c69187945f2daa523f1d5fd1a5b389900ecdf7b1f`.
- Stdlib model decoder: `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`.
- Separate historical native-check source: `090aba46d707e01c21cc4713073c41b718d98ca9d2bb3192674e274508f21e98`.

The checker pins the current prepared freeze `8053a3795c9ed14d53c84df5dddefa355fb29572be9ce213758bf75a3922347c`, manifest `4478c4637b2b81256cc31e9cdc2516b2112309c30096176d5df42ba205dd09a6`, and 1,769 input bindings. Its source requires initial and final binding checks, external closure/inventory hashes and count, unique confined inventory entries, complete run-file coverage, and an unchanged closing snapshot. These are reviewed implementation requirements; this reviewer did not audit the prepared inputs or scientific output payloads.

The 336 original seed proofs are inherited from closed mathematical review `205b8118a0a01d5cb63a1435b5b8dbdc0089ca1aad7e2cbb153b9117ac63738a` and its separately pinned encoding review. The code checks their historical input/copy/index bindings and fixed order, then deserializes admitted state terms and endpoints solely to verify appended master rows. It does not reconstruct their multipliers, residuals, support, anchor or old full-point membership. The inherited control is used only for each new phase-cut consistency calculation; its old membership is not replayed.

The independently written new phase reconstruction uses admissible endpoint signs, exact binary64-to-Fraction conversion, every original coefficient, exact-zero-only sparse omission, canonical endpoint and norm cancellation identities, and the continuous finite-box support. Its necessary cut subtracts tau times the original row-multiplier norm plus the continuous residual norm, with no extra binary or derived-row tau deduction. Full and compact proof fields, state coordinates, support records, origin margin and unrounded-control consistency are checked. A verified rejection excludes its nominated state; it does not prove absence of all common commitments.

Nomination review independently restores the complete 12,096-bit state, derives the 336 deterministic minimum auxiliaries, and checks all exact rational master rows and boxes without an additional tolerance. It checks full duplicate records, fixed prescriptions, chronological cut provenance and the optional eighth-round terminal model. The terminal model is not treated as another nomination.

For a saved new recourse candidate, the code checks all prescribed states and their raw distances, bitwise preservation of every continuous coordinate, the full original joint model, both original-world projections/masks, all shared bits and the separate native checks. No nominal-feasibility claim is inferred from expanded feasibility. A mathematically accepted point is reported separately from authoritative acceptance, which additionally requires complete producer derivatives, the relevant worker completion and the final on-time record.

The partial-output branches permit fully written valid file prefixes: raw master without admission, candidate without later world/check files, and full phase proof without its compact form. Downstream files require their source dependencies; only a complete compact, strictly separating propagated cut can enter the next master. The artifact census prevents silently skipping recognized mathematical files. A raw-only phase record is not reconstructed into an unsaved certificate. A truncated or unparseable individual JSON, GZIP or NPZ file fails closed and preserves a failure record; it is not silently treated as a valid incomplete prefix or a mathematical contradiction.

Actual numeric coefficient transport, binary rounding implications, worker/process ownership, call accounting and timing remain the separate backend/encoding/lifecycle review's responsibility. This source review and the prospective mathematical report do not replace that mandatory gate. The review is specific to the admitted finite-box models and pinned schemas, not a generic checker guarantee.

The existing invented-only receipt `INVENTED_CONTROLS.json`, SHA256 `2bd6194c9d92c6fd416eff669a16adefa34c8789dc5ee7115d74591acad710c8`, records 16 groups passing on the exact reviewed source, with zero scientific reads/replays, optimizer calls and backend/producer/helper imports. This reviewer read and hashed the receipt but did not rerun the controls.

No scientific payload values were inspected or evaluated in this review. No module was imported, no checker or producer function was executed, no coefficient/point/cut/bound calculation or solver call was made, and no scientific file was edited. This memo is the sole new file written by the review task.
