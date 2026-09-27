# Version 3 manuscript scientific and editorial review

Status: INITIAL SNAPSHOT REVIEW COMPLETE; no mathematical or numerical blocker found in the reviewed snapshots. Two small wording corrections are recommended. The planned seasonal addition, evidence commit and Drive readback wording require a subsequent delta review. This is a content review, not journal-readiness approval or rendered-page QA.

Reviewed on 27 September 2026 by the independent task agent, with a complementary read-only symbol/cross-reference/reference-order pass from its child reviewer. Neither reviewer edited the manuscripts. No optimizer, producer replay, network lookup or source-module import was run. Standard-library rational arithmetic checked displayed endpoints against already closed reports.

## Exact draft snapshots

| File | SHA256 |
|---|---|
| `.work/research8h_manuscripts/v3/note_en.json` | `849b62fbb7b6ae27c30197b45c4fe568700eb9f7ad19d9c1a92912a2160757b0` |
| `.work/research8h_manuscripts/v3/decision_ar.json` | `4f4ebedf81543a2823d27ac13fc8d7fea748a03f71596a1f0c99eef6e69654b9` |

The English draft has 74 blocks, eight numbered equations, five tables, one figure and eleven references. The Arabic decision companion has 49 blocks, five tables, one figure and ten references; it does not reproduce the eight displayed equations. Block indices below are zero-based indices in these exact snapshots.

## Actionable wording findings

1. English block 53 says “these three full strict models” immediately after Table 4 lists four cases. The intended three are the identity and the two ordinary targets. Replace that phrase with “the identity and two ordinary-target strict models.” The computations and Table 5 already use the correct three models.
2. Arabic block 9 says “الجدول 1 يفصل الحالات العادية عن هذه الضوابط.” Table 1 contains ordinary cases only, rather than separate control rows. Prefer “يعرض الجدول 1 الحالات العادية، مع استبعاد الضوابط الإيجابية من أعدادها.” This clarifies the denominator without changing a result.

No stray drafting instructions, placeholders, character corruption or unexplained results were found in the full text read. Minor stylistic choices are not blockers.

## Numerical checks

All 32 old angle-model energy endpoints and eight new strict-flow endpoints match exact rational arithmetic and outward six-decimal rounding. Both languages reproduce them correctly: 40 unique endpoints and 80 displayed occurrences in total. The old Table 2 and Table 3 row arrays also match the corresponding version 2 arrays exactly.

For every case the check independently formed the absolute interval `[L_T-U_I, U_T-L_I]` and relative percentage interval `100*[L_T/U_I-1, U_T/L_I-1]` from archived numerator/denominator pairs, checked the stored interval algebra, and applied integer floor/ceiling at six decimal places. It did not use the approximate floating-point fields as proof.

| Model / case | MWh interval | Percentage interval |
|---|---|---|
| Expanded angle / 26093100 | [1542.835730, 2546.796204] | [6.718221, 11.261126] |
| Expanded angle / 26093101 | [2139.151137, 3077.464141] | [9.314855, 13.607571] |
| Expanded angle / 26093200 | [566.366617, 1336.352662] | [2.466222, 5.908928] |
| Expanded angle / 26093201 | [858.121844, 1408.976215] | [3.736660, 6.230047] |
| Expanded angle / 26093210 | [574.017996, 1815.622131] | [2.185149, 7.016271] |
| Expanded angle / 26093211 | [89.056939, 2303.990067] | [0.339018, 8.903515] |
| Expanded angle / 26093220 | [1082.076498, 1856.243776] | [2.261852, 3.910485] |
| Expanded angle / 26093221 | [1048.824076, 2458.387516] | [2.192345, 5.179001] |
| Strict flow / 26093200 | [568.039414, 1335.344714] | [2.473506, 5.904208] |
| Strict flow / 26093201 | [859.940259, 1407.968267] | [3.744578, 6.225312] |

The authoritative bound reports are:

| Report | SHA256 |
|---|---|
| `results/research8h/energy_lp_refinement/refined_brackets.json` | `bd1e8e061a26f82bdb8e0697e03ea4b3f97664b6ee19c21d4886950e85fd1cfd` |
| `results/research8h/hour_of_day_uncapped/energy_brackets.json` | `4915dfe14d94419cbb6c62a52b2079dc10648a349b93a224630ab1b41e11a1f1` |
| `results/research8h/fresh_january_energy/energy_brackets.json` | `ed4e0e6eb4f88b8a660c7b46495a95d30eebce94f715be83cedf4a884930471c` |
| `results/research8h/branch_flow_strict_energy/outcomes.json` | `ec069eaf704bb60536fbca167ec799722ffc34092f8a2a2a9c405fb543ef4a13` |

The strict-encoding comparison was also checked directly from `branch_flow_encoding/january_identity/representation_differences.json` (SHA256 `7320dc2eea55387917e9731ba395bd1464be448dc63d912e2a0cff32835958ec`): 15 changed nodal coefficients, maximum absolute difference exactly `3/2199023255552`; 160 nonzero hourly nodal-sum/old-aggregate RHS differences, maximum exactly `37/281474976710656` MW. These support the manuscript's explicit refusal to assert exact equivalence or nesting.

## Equations, definitions and inference scope

All eight English equations have preceding definitions and prose explaining their role. Dispatch, commitment/startup/shutdown, angles, original binary mask, matrices, row and column bounds, fixed parameters, time index, objective, cap and expansion are introduced before their displayed use. The matching all-ones vector, transpose, real-number notation and the identity/target optimum notation are explicit. In the strict section the dimensions, orientation and units of `P`, `theta`, `f`, `n`, `D`, `C` and `kappa` precede Equations (7) and (8).

Equations (1)–(2) preserve the exact original binary mask while widening only finite bounds. The rational expansion is the exact binary64 value of `1e-5`. Equations (3) and (6) have the correct signed endpoint, box and norm corrections; no numerical dual stationarity or solver optimality is assumed. Equations (4)–(5) compare the two binary optima, with the positivity condition for the ratio stated. The safe-bound precedent and the elementary expansion algebra are distinguished. The sufficient cap interval has the correct included lower and excluded upper endpoints.

The physical observation has 107 coordinates: independently formed aggregate demand, 24 nodal demands, and 41 lower plus 41 upper bounds. It excludes outputs, labels and timestamps. Clock-conditioned multisets and fixed ordered edges are distinguished from daily trajectories and transition-aware observations. The structural no-dwell argument is explicitly restricted to the audited original angle model and its boundary conventions. It is not applied to storage, general binding ramps, startup costs or the newly specified strict encoding.

The strict flow model is separately declared. The manuscript retains its changed exact coefficients and aggregate-balance semantics, does not transfer old-model lower bounds into it, and does not count the same two known permutations as new temporal replication. The old fixed-template exclusion concerns continuous points and linear Farkas proofs only in the expanded angle model. Fractional admission is not presented as binary or strict feasibility.

The fixed-evidence tau band is appropriately restricted to the old angle model, its fixed witnesses/rays/duals and its mixed-unit normalization. Zero is outside that evidence band; failure outside it is not reversal. No physical-uncertainty or row-rescaling-invariance claim is made. The complete six-target hour-conditioned energy denominator is retained, including the capped UNKNOWN case 26093211.

## Tables, figure and references

Every table and Figure 1 has a textual callout and a caption in each language. English equation numbering is unique and sequential from 1 through 8. The figure's eight old-model rows remain separate from strict Table 5 and are described as optimization bounds, not statistical confidence intervals. This review checked source callouts and numeric content, not image placement, typography or rendered cross-reference fields.

Reference first appearances are ordered 1–11 in English and 1–10 in Arabic, accounting for grouped ranges and Arabic comma-separated citations. No unused numbered reference or missing first-use citation was found. The nine DOI entries and two version-specific arXiv citations in the English list match the existing local metadata audit; this review did not repeat external resolution checks. Arabic omits the UC-formulation reference and consequently has ten entries in its own first-use order.

The bibliographic identity checks rely on `docs/research8h/MANUSCRIPT_V3_REFERENCE_AUDIT.md` (SHA256 `cb5ed6fa3a5dd6effb37236805a949a38f3c75df1e6f7ae5687e043072c8df00`) and `results/research8h/manuscript_v3_reference_metadata.json` (SHA256 `78d9652c190e558b442a9cc7cedf9996a2d1cfc5bcaf3ede2d04ded8d93e12e7`). They establish the locally audited citation identities; this content review makes no fresh network-availability assertion.

## Pending controlled edits and limits

The baseline's old science commit and absent new seasonal energy section were explicitly declared pending by the authoring task. They are not silently treated as final availability statements. The final revision must separately identify the historical four seasonal capped UNKNOWN outcomes, three later finite energy intervals, the fourth NO_UPPER case, and the new posthoc expanded-model capped positive for 26094000. The earlier conditional seasonal gate remains unmet. These unrestricted interior permutations must not be added to the six hour-conditioned energy cases.

The baseline's statement that Drive content cannot be verified is also pending replacement: a newly confirmed raw download path permits whole-artifact byte/hash comparison. Final delivery assertions must follow the actual readback performed, not merely a pilot or metadata check. The existing Zenodo DOI is correctly scoped to the frozen V8 release rather than the new experimental branch.

A later appended review should bind the revised manuscript hashes and verify only the actual additions and corrections while confirming that inherited table values and references remain unchanged. This initial review does not cover those future edits or prove rendered PDF/DOCX quality. It establishes no journal acceptance, broad novelty, independent-network validation or physical measurement exactness.

## Seasonal delta review — 27 September 2026

Status: PASS for the reviewed seasonal/content delta. No new scientific or editorial blocker found. This addendum preserves the initial review above.

Reviewed revised English SHA256 `d2ed0ffe4981f286b87736d0b837ea1dcae729f9eb667b331af2c74bb3c861c7` and revised Arabic SHA256 `85fa4dbdecda11b1437d0e75f2a297d6679e634e79fa69091ce180595715cd3e`. Both previously recommended wording corrections are implemented. English Section 4.2 and Table 6, the corresponding Arabic section, abstract replacement and amended historical-outcome prose were read in full. The English abstract contains 248 whitespace-separated words.

The twelve new finite endpoints, repeated in both languages, were checked from exact fractions in `results/research8h/seasonal_all_four_energy/energy_brackets.json` (SHA256 `2aa331b8b04e0b1e7ea62880bdfef3440d2fef14d3880249de678b0ca8dd21e0`). Forming `[L_T-U_I,U_T-L_I]` and `100*[L_T/U_I-1,U_T/L_I-1]` reproduces every table entry with outward six-decimal rounding:

| Case | MWh interval | Percentage interval |
|---|---|---|
| 26093400 | [422.215678, 1460.098124] | [0.988706, 3.461710] |
| 26093401 | [273.680850, 1596.186199] | [0.640881, 3.784357] |
| 26094000 | [689.463677, 904.158184] | [0.556323, 0.729564] |
| 26094001 | No finite upper witness | Not established |

For 26094001, downward rounding of the exact `L_T-U_I` gives 766.016260 MWh. Both texts make that necessary difference conditional on the target being nonempty and explicitly withhold feasibility and finite absolute/relative optimum intervals. It is not silently counted among the three finite positive results.

The section explicitly identifies the original expanded angle model, unrestricted interior observation `Phi_0` rather than clock-conditioned `Phi_H`, seasonal calendars, unchanged reference uppers and cap-only follow-up. The five accepted upper points are described as expanded-model admissions that fail strict nominal membership. The three finite seasonal results are not added to the six January hour-conditioned cases or presented as independent-network validation. The fixed-evidence tau and strict-flow sections retain their original scopes.

The new positive for 26094000 is grounded in the independent full-parent sidecar `seasonal_all_four_energy_independent_review/new_historical_cap_points.json` (SHA256 `65c9c6f2d8392b19a10c7433753954238a9e6f219e0e143299b5f0c66573127e`). The manuscript correctly separates its later accepted expanded binary/native point under the unchanged 125172 MWh cap from Table 1's historical four-UNKNOWN run ledger. The approximate energy 124835.463673 MWh is consistent with the exact archived point. Failed old-cap checks of the two April points are not turned into infeasibility proofs; the fourth case retains no upper witness. None of the four objective lower bounds produces a new capped negative. The failed original seasonal negative-replication criterion remains unchanged.

The ten-call accounting matches the closed audit: two identity LPs, four target MIPs and four target LPs, with prescribed 60/300 second limits, all four MIP time limits retained, totals 1212.990578 MIP seconds and 73.277904 LP seconds, and 12.990578 seconds of aggregate soft-limit overrun. These statements agree with `producer_timing_audit.json` (SHA256 `cc19a5aae739eebccddb199177eb7c624ebf211720248d37cf3c70c85086286e`) and the closed independent postrun review (SHA256 `da0264aeba0ade3a27140acd91d51d4dba4335e26c9f7c3704470de6de642ec8`). No optimizer or duplicate producer replay was run for this manuscript check.

Table 6 is called out before its appearance in each language. Existing equation/table references remain coherent, and the six-table numbering is sequential. The newly added prose introduces no bibliographic citation or equation and does not alter the previously checked reference-first-use order. The inherited Table 1 counts are deliberately unchanged and now labeled historical; Tables 2–5 retain their checked numerical values. Availability science pin, Drive whole-artifact readback wording and any later portable-completion statement remain separately pending as requested by the authoring task; this PASS does not preapprove those future edits or rendered layout.

## Availability-only delta review — 27 September 2026

PASS for English SHA256 `36e0f1b5b73f7a8fae229ea72763abf1e65c08b67eaabbacc5dd1ff378325f96` and Arabic SHA256 `2f785821f4c687edc0105ddf29b95d6236e17fcfcb694bc7499bfbcd0be7dfe2`. Read the revised availability paragraphs in full. Replacing only that paragraph in memory with its preceding reviewed text reconstructs each preceding seasonal snapshot SHA256 exactly; all scientific text, equations, tables, figures and references are therefore byte-for-byte unchanged by this edit.

The evidence pin is now `d6dc003ec46085a2508e1f2590b50b8329d8a76a`, the independently published/read-back science checkpoint supplied by the authoring task. This content review did not repeat a remote fetch. Both languages now distinguish local archive manifests, upload metadata/destination/sharing checks, and actual downloaded-byte SHA256 comparisons. They make no blanket assertion that all delivered files already passed a full downloaded-content check. Actual receipts must support any such individual claim. A later portable-completion paragraph and rendered-page QA remain outside this gate.

## Abstract scope clarification — 27 September 2026

PASS for English SHA256 `f699bb5232dd0edb2e928801508ebd55dfaeb34c604866a0b5d7538bea4c58f3`; Arabic remains unchanged at `2f785821f4c687edc0105ddf29b95d6236e17fcfcb694bc7499bfbcd0be7dfe2`. The abstract now expressly attributes all six uncapped hour-preserving optimal-energy increases to the expanded angle model. This resolves potential scope carryover from the preceding strict-flow sentences. It is supported by the six finite positive intervals and retains the unresolved capped case distinction. The revised English abstract has 247 whitespace-separated words.

Replacing this one sentence in memory with its preceding wording reconstructs the preceding English SHA256 `36e0f1b5b73f7a8fae229ea72763abf1e65c08b67eaabbacc5dd1ff378325f96` exactly. No other mathematical text, result, reference or availability claim changed. No numerical producer replay was repeated.

## Portable strict replay and notation delta — 27 September 2026

PASS for English SHA256 `7ec2cc2357eeffa3622a1b55bbb5cfa3233a574d0a9383b9f9b7b05207fbbd1e` and Arabic SHA256 `6dd3898ac38a8182cf4e795ba495b2725f9ec437d15f91c4fd6f05fb718d955e`. Read the added portable-replay paragraph in each language, the explicit first-use definitions of `|J|` as the number of original binary coordinates, `i` as row index and `j` as column index, and the Table 6 heading correction from Season/الفصل to Month/الشهر. These improve precision without changing any mathematical result.

The new prose matches the closed strict replay summary SHA256 `6bbe5acbe6afda090dbc9c040fbae781f49ed665ff0ed6a457114cfa8a05589a`: five point/model combinations (capped identity/control, uncapped identity/two targets), eight ray candidates, fifteen objective-bound candidates, two penalty intervals, 150.87042219997966 seconds, no optimizer/network/native reconstruction and unchanged package files. The 150.87-second presentation is appropriate. The paragraph explicitly retains same-host relocation and the absence of a raw-data model rebuild or second-machine validation.

The failed first assembly is correctly described as preceding mathematical replay. The corrected assembly preserved inherited scientific dependencies rather than changing a scientific matrix/source to obtain a pass. Following the review suggestion, English now says “pinned scientific dependency hash,” which avoids implying that the regenerated candidate outer-manifest hash stayed the same. The Arabic paragraph already limits this claim to scientific files and their hashes.

The independent compact postrun record, `results/research8h/portable_strict_flow_independent_review/postrun_review.json` (SHA256 `803df43e1dd321ef88372302e10275dd7ebaa858fdf1462523f613afae9457b7`), reports `INDEPENDENT_COMPACT_POSTRUN_REVIEW_PASS`, binds all sixteen producer reports and the summary above, confirms one authentic isolated/no-site wrapper invocation and the declared roles/counts, and explicitly performs no repeated mathematical replay or whole-package hash. This manuscript review read that record and the summary only; it did not repeat the producer's calculations or inflate compact review into a second mathematical replay.

Before the final English wording refinement, reversing only these bounded edits and removing the new paragraph in memory reconstructed the previous reviewed English `f699bb5232dd0edb2e928801508ebd55dfaeb34c604866a0b5d7538bea4c58f3` and Arabic `2f785821f4c687edc0105ddf29b95d6236e17fcfcb694bc7499bfbcd0be7dfe2` hashes exactly. Reversing the final “pinned scientific dependency hash” refinement reconstructs its immediately preceding English snapshot exactly. Thus inherited numerical endpoints, equations, reference ordering and other prose remain unchanged. The science availability pin still points to checkpoint18 in these reviewed snapshots; the announced update to the independently published checkpoint19 remains a separate pending binding.

## Final published science-pin delta — 27 September 2026

PASS for final English JSON SHA256 `ee78fb1fbf44d35c45c2bf02a916dab01718ca049632f0c22bc5d46ad2ca7e30` and final Arabic JSON SHA256 `8fab5d10bbafc14bb79bfbb7370fdecfde7efbc77d9eb827a5b72ba1e61b21bf`. Each contains exactly one availability reference to science checkpoint19 commit `d491d49fd2d21a798df2911a9b0987532e5dbf7d`. The root authoring task reports publication and an independent exact `ls-remote` match for that commit; this bounded text review did not repeat a network query.

Replacing only that commit with the previously reviewed checkpoint18 identifier in memory reconstructs English `7ec2cc2357eeffa3622a1b55bbb5cfa3233a574d0a9383b9f9b7b05207fbbd1e` and Arabic `6dd3898ac38a8182cf4e795ba495b2725f9ec437d15f91c4fd6f05fb718d955e` byte-for-byte hashes exactly. The availability paragraphs were read back and no other source change occurred. Therefore all prior scientific, numerical, symbol, citation and callout checks remain applicable to these final JSON snapshots. No source-content finding remains open within this reviewed scope.

Rendered DOCX/PDF quality, final delivery packaging, independent final-ZIP integrity execution and uploaded-file readback are separate gates. They are not inferred from this final source PASS; no manuscript, builder or QA artifact was edited by this review.
