# Interpretation of the frozen fixed-identity models

This arm has five prepared models and no optimization result at preparation time. The source, protocol and all200 preparation bindings were frozen before any of the five planned LP calls. The corrected source uses `raw_solver_ray.npz` for any returned ray and binds row metadata and the experiment manifest in a certificate.

Each case's `model_metadata.json` is an unchanged **parent-model snapshot**. Its zero-feasibility-objective description and original binary-column count describe that parent, not the new LP call. They are retained for source identity, unit order, variable offsets and original-binary verification; no frozen metadata has been silently relabeled.

The actual new optimization is defined by `objective.npz` (3864 coefficients equal to1 for168hours×23fossil units, all others zero), `bounds.npz` (all12096 U/Y/Z coordinates fixed to the exact unpermuted identity sequence), the unchanged matrix/row bounds, and the frozen `DAY_FIXED_IDENTITY_PROTOCOL.md`. HiGHS receives continuous LP variables. P and theta bounds remain unchanged. The saved original integrality mask is used to check recovered points against the original binary model; it is not passed to the LP solver.

`model_binding.json` records exact parent matrix identity, unchanged row bounds and P/theta bounds, fixed state counts, native input hashes and any previously constructive point's state relation to the identity anchor. These are restrictions of the parent UC models. A certified negative can therefore exclude only this fixed identity schedule, while an accepted exact expanded original-binary point is also a full-model positive.

All five day orders, including the previously full-model positive days_312, remain in the fixed denominator. Neither the parent metadata nor prior day-block solver statuses are overwritten by this separate arm.
