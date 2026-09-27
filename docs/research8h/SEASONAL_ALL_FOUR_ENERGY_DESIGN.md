# April/October all-four uncapped energy follow-up — design only

This is a new retrospective energy question after all four capped binary targets were UNKNOWN. The earlier conditional follow-up had zero eligible certified cap negatives and remains untriggered. The original replication gate and later augmented cap criterion remain NOT_MET. This design does not modify those records or turn the new question into a prospective test of known labels.

All four targets enter without label filtering. They are unrestricted interior-package permutations (Phi0), not hour-of-day-preserving permutations (PhiH). Any eventual seasonal energy result must remain separate from the six January HOD cases and cannot satisfy the failed cap criterion.

## Fixed inputs

All paths below are repository-relative under `results/research8h/`.

| Month and source hours | Both fixed target directories | Historical cap | Reference directory |
|---|---|---:|---|
| April 1–7, 2020; rows 2184–2351 | `seasonal_cap_continuation/seed_26093400`, `seasonal_cap_continuation/seed_26093401` | 43131 MWh | `seasonal_reference_continuation/month_04` |
| October 1–7, 2020; rows 6576–6743 | `seasonal_cap_continuation/seed_26094000`, `seasonal_cap_continuation/seed_26094001` | 125172 MWh | `seasonal_reference_continuation/month_10` |

Each reference upper is its unchanged `recovered_vector.npz`. The archived exact energies are respectively `6154272335876697791701/144115188075855872` and `558140738732395069817/4503599627370496` MWh. Their vector SHA256 values are `b932e6f2b53e4672cd810308981632663a61ba204e9b7aee60aa9812afe1bbc6` and `4de2dca8c652b56170749bbc15e8a17322aec8678295a43c3545ebd985eec4e5`. The corresponding capped identities are `seasonal_cap_continuation/month_04_identity` and `month_10_identity`, with `constructive_vector.npz` and original full masks.

Pin the completed reference manifest `cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b` and cap-parent manifest `d5ae06005d333ee20b6ef5a466c72fd7c5530462ada923fc83a07e26b14e8055`, their completion/post-run inventories, prepared and independent post-run PASS records, all four outcomes, and the two `month_*_reference.json` cap records. Recheck their bound bytes rather than accepting status text alone. The cap-parent independent post-run sidecar SHA256 is `14a72a7adb98509d73a6c59ad3303d892dc91d28ea08323fe31d3c87c3cadd0c`.

Use the same native input root recorded in the freezes: `C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs`. Bind its author-owned model, pinned RTS CSVs, original source-hour mappings, and each archive's native arrays. No new downloads, hour selection, reference solve, seed or permutation draw is proposed.

## Necessary adapter differences and acceptance gate

The reviewed `src/research8h_fresh_january_energy.py` (SHA256 `0ad4536f7b9be7d681a4e164eb8546cc1755ddccb2b49e90887e92d4f08b250d`) supplies a pattern for cap deletion, signed-dual bounds, finite-box corrections, guards and interval reporting. It cannot be reused unchanged:

- Reference continuation `integrality.npz` is the 4032-coordinate U-only solver mask. Acceptance must instead load `original_integrality.npz` (all 12096 U/Y/Z coordinates), together with the original physical metadata. Targets use their full `integrality.npz`; their projected mask is separate.
- Seasonal permutations use columns `new_hour_0based,source_hour_0based,source_native_row`. Check the saved bijection, fixed first/last 48 hours and exact transport of the full 107-coordinate native package. Do not impose the January HOD modulo-24 assertion.
- Load the actual monthly source calendar/row map. January's `(week-1)*168` adapter and its review-schema keys are inappropriate here.

Preparation would retain the two already-uncapped reference matrices and delete exactly one `fossil_energy_cap` row from each target. Independently prove each reference equals its capped identity after only cap deletion. Every other CSR coefficient, bound, native array and original binary mask must remain identical. Audit 34680-by-23016 reduced matrices, zero means, 24 buses, 38 branches, 41 generators and 24 thermal units. The objective is one on 168-by-23 native Coal/Oil/NG dispatch coordinates and zero elsewhere, excluding nuclear. Do not inherit the capped parent's zero feasibility objective.

All accepted points require original-mask exact membership after uniform outward expansion of every finite row/column bound by `Fraction.from_float(1e-5)`, plus the native no-cap checks. Record strict nominal flags separately. Recovery may round eligible U and derive canonical Y/Z; P/theta remain unchanged. Preserve mature free initial U, initial Y/Z zero, finite-horizon dwell and original on/on ramp semantics. Any schema/source/mask mismatch produces HOLD with preserved records, not a substituted case or model.

## Fixed bounded schedule, if separately approved

Prepare and freeze all six model/objective archives first. Require root source/protocol review, independent prepared PASS and a separate explicit execution GO. Then, sequentially: identity LP60 for April and October; target U-only MIP300 for seeds 26093400, 26093401, 26094000, 26094001; target LP60 in that same order. Maximum configured solver time is 1560 seconds. No warm starts, retries, new identity MIPs or outcome-dependent omissions.

LPs use simplex, presolve off, thread 1, seed 0; MIPs use presolve on, thread 1, seed 0, gap 1e-8. Propose a 2100-second soft phase including validation, with actual-call guards of 305/65 seconds against both remaining phase and 04:00 UTC on September 27. Record skips, actual times and all overruns; the guard is not a hard latency guarantee. The full allocation fits before 04:00 only if preparation/reviews permit a start by about 03:25; otherwise retain skipped calls and the full four-case denominator. Root coordinates concurrency.

Each LP supplies an exact signed-row-dual plus finite-box residual lower bound, subtracting tau times the row-dual/residual L1 sums. Preserve raw/projected duals and never replace proof by the solver's numerical bound. Fix lower selection in advance as the maximum of that valid bound and the separately archived zero-dual bound; never clamp the widened model to zero.

With reference enclosure [LI,UI] and accepted target [LT,UT], retain the full signed optimum-difference interval [LT-UI,UT-LI], including negative or zero-crossing intervals. Report ratios only when both lower bounds are positive; then use [LT/UI-1,UT/LI-1]. Without accepted UT, retain NO_UPPER and the exact lower bound, with no finite-optimum claim. Save all statuses, failed points, nulls and outward-rounded displays. Independent post-run replay precedes publication. Fossil electrical MWh is not fuel, money or emissions; this remains a within-system seasonal comparison.

Metadata inspection supports implementing this separate adapter, subject to the stated gates. No models were generated and no numerical or optimization execution occurred for this design.
