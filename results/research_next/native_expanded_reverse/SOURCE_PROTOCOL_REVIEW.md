# Native-expanded reverse source and protocol review

Status: **SOURCE_PROTOCOL_PASS — no material blocker found**.

Reviewer: `/root/find_deposit/gb_docs`, 27 September 2026. This is a full source-only second review of all 467 lines of the new certificate source and all 47 lines of its protocol. The reviewer did not author this certificate implementation or protocol. The reviewer previously authored the separate input-transport module; this memo does not claim independent review of that transport.

## Exact read bindings

| Item | SHA256 |
|---|---|
| `src/researchnext_native_expanded_reverse.py` | `494517bef073fca4126b37194c61b9cafbbab347798a7cf950bd548ca18bde6f` |
| `docs/research_next/NATIVE_EXPANDED_REVERSE_PROTOCOL.md` | `3c11f1c47301db1e6d3a4bdd11476010734fc688cb645536f7489b63dd187a6a` |
| Existing invented-control receipt | `3667fceac7a9c5d546ee6815b5cdc499f5f93d414911d79d8a29d6ed9ae54b50` |
| MOI decoder/alias helper | `6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c` |
| Standalone NPZ decoder | `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f` |

The existing receipt reports 12 invented groups, PASS, and the exact source/protocol hashes above. It was read and hashed, not rerun. Relevant helper interfaces were inspected as text, including alias bijection, binary64 affine/set decoding, whole-row-sign-invariant row keys, and strict NPZ member/dtype/shape decoding. The helpers were not imported.

## Provenance and role separation

Source lines 18–39 fix different target and identity records. Lines 119–149 require the closed actual-reverse nominal comparison, its fixed order, manifest and reviewed producer outputs; bind the comparison reviewer; bridge the model bytes to the old reverse target; and require candidate/dual/result membership in the pinned old output manifest. The identity result, certificate, point and completion are separately matched to the closed identity review's producer snapshots. The actual existing comparison manifest and review field names match these accesses. The actual `raw`, `parsed`, `normal` and `model` copy paths coincide with the roles consumed by this source.

The target remains `reverse_4_19__native_penalized`, with its archived destination coordinates. No schedule, dual, model row or candidate permutation occurs. The identity is only the closed `identity__native_penalized` reference. The previous complete nominal multiset/objective comparison is explicitly inherited; the new containment check is not presented as another complete comparison.

Preparation is capture/hash/readback only. Run entry requires an externally supplied freeze hash, validates originals and copies, checks source/protocol hashes, and imports only the two hash-pinned helpers. Separate source/prepared acceptance and execution authorization remain external gates. This review does **not** audit the newly prepared 499 original / 34 copied bindings.

## Mathematical and point checks

The signed-row proof at lines 179–207 has the correct signs. Positive multipliers use finite lower endpoints, negative multipliers use finite upper endpoints, and unsupported signs are projected to zero. With `r = c − Aᵀd`, the nominal bound is the chosen row-endpoint sum plus the componentwise residual minimum over finite boxes. Uniform expansion subtracts `tau * (||d||1 + ||r||1)`. Enlarging only the Q/R upper endpoints by a further tau adds `tau * sum(min(r_j, 0))` over those coordinates. The separate direct endpoint/box expression agrees algebraically and requires a nonpositive correction. The code does not assume stationarity, numerical dual feasibility or solver optimality.

Lines 210–266 recheck the actual target: 960 original binary declarations; the 480 Q/R coordinates and 240 headroom pairs with exact shared width and native lower bounds; 24 N=0 equalities; all remaining retained domains; 240 nonnegative omitted mfg coordinates with no affine or objective support; and the full minimization objective with zero constant. These premises justify containment of the native-expanded **binary** projection in the enlarged finite-box relaxation. They do not assert equality of expanded models or the same containment premise for fractional native U values.

Lines 276–313 preserve all 2,472 candidate entries, add only zero mfg values, traverse every raw constraint record, retain duplicate rows, and test all 960 native ZeroOne declarations exactly. The required census is 4,384 affine and 3,696 variable-constraint records, with a 2,712-coordinate lift. A fractional binary fails even when inside numerical endpoint tolerance. Strict nominal acceptance additionally requires zero maximum nominal endpoint violation. Lines 364–378 bind the native encoded objective and reconstructed target proof to the unchanged archived accepted objective, projected multipliers, every residual and selected LP lower.

## Intervals, nulls and reporting

The exact identity lower/upper are inherited only after result/review/proof equality and matching binary64 tau. The subtraction at lines 325–337 is correctly oriented: `[L_reverse − U_identity, U_reverse − L_identity]`. A target point rejection leaves the upper null and produces no finite two-sided difference. Its remaining lower statement is explicitly conditional on a nonempty target set. Rejection is not treated as infeasibility, and there is no fallback candidate, multiplier or lower-bound selection.

Six-place displays use exact floor/ceiling integer arithmetic and verify outward containment. The sign handling preserves negative and crossing-zero intervals; the source adds neither clipping nor a ratio. Strict nominal upper remains separate from expanded upper. The stated result concerns two separately informed native-expanded optimal encoded costs, not decision regret, nominal optimality, fossil energy, calibrated currency or methodological novelty. The other three original target/service comparisons remain explicitly untransferred.

## Execution and review limits

The 120-second allowance is a soft phase beginning before validation. Checks occur during raw traversals and after serialization and final input/freeze rehash; only the final completion-record write is excluded. It is not a hard process-interruption guarantee. Preserved partial result files are not admission by themselves: a failure record or missing successful completion prevents an admitted bracket, and successful completion remains pending independent postrun review.

No source, helper, test, scientific preparation or scientific arithmetic was executed by this reviewer; no optimizer or Julia call was made. No scientific point, coefficient product, residual, cost endpoint or difference was recomputed. Existing files were left unchanged. This new memo records source/protocol readiness only; prepared-input acceptance and an independent saved-output arithmetic replay remain separate requirements.
