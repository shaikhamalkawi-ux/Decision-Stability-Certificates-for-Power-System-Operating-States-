# Manuscript version 2: independent scientific and cross-reference review

Status: PASS for the reviewed JSON content, with no outstanding material scientific or arithmetic finding. Review date: 27 September 2026. This is a source-content review, not a declaration of journal readiness or a rendered-page review. No manuscript, builder, frozen experiment, or plot source was edited by this reviewer. No optimizer ran.

## Exact draft bindings

The full initial read used:

- `.work/research8h_manuscripts/v2/note_en.json`: `f8414a759c5c28d35bb1a3f470ee8d0308749272d892968fd68ac350c9a5e736`.
- `.work/research8h_manuscripts/v2/decision_ar.json`: `40af9a6256b53a86fb3fb13a264dd31eb87c2ebefc8ecc7b7b90fa4a52433891`.

Two nonblocking first-use clarifications were sent to the parent. The parent added an explicit definition of `X=(s_0,...,s_167)` at the hourly-package paragraph and identified identity/target subscripts and their optima before Equations (4)–(5). Both changed paragraphs were subsequently read back. The final English draft hash is `f989e3ed8ac7bd6261647be3150562a88c8216bfe95107aa25b57c35d8ef7aad`; Arabic is unchanged. These edits alter no reported number, table or reference.

## Numerical replay and denominators

A separate read-only exact-rational calculation loaded the three archived energy-bracket datasets, recomputed every optimum difference and relative percentage, checked equality with the stored exact difference endpoints, and matched all 32 outward-rounded values in Tables 2–3 of both drafts. It did not import or run the plot source.

| Target | Optimum difference enclosure, MWh | Relative enclosure, percent |
|---|---|---|
| 26093100 | [1542.835730, 2546.796204] | [6.718221, 11.261126] |
| 26093101 | [2139.151137, 3077.464141] | [9.314855, 13.607571] |
| 26093200 | [566.366617, 1336.352662] | [2.466222, 5.908928] |
| 26093201 | [858.121844, 1408.976215] | [3.736660, 6.230047] |
| 26093210 | [574.017996, 1815.622131] | [2.185149, 7.016271] |
| 26093211 | [89.056939, 2303.990067] | [0.339018, 8.903515] |
| 26093220 | [1082.076498, 1856.243776] | [2.261852, 3.910485] |
| 26093221 | [1048.824076, 2458.387516] | [2.192345, 5.179001] |

All eight cases remain visible. All six hour-preserving targets have strictly positive energy-difference lower bounds. Five of six have independently certified capped infeasibility, while 26093211 retains its original capped UNKNOWN classification. Its uncapped lower bound is below `26532+tau` and its accepted upper witness is above the cap, so the energy result does not decide capped feasibility. Both drafts preserve this distinction.

Table 1 retains the complete ordinary denominators: unrestricted January 2, first-week hour-of-day 2, whole-day 5, April/October continuation 4, fresh week 2 two, and fresh week 3 two. The one whole-day positive and all seasonal/whole-day unknowns remain. Controls are separate, and the October identity control draw is disclosed. The five hour-preserving negative count is two first-week plus one second-week plus two third-week cases, not a new denominator assembled from successful outcomes.

The fresh capped accounting agrees with independent closure: four LP calls, one conditional MIP, 20.172922 LP seconds and 300.446834 MIP seconds. The fresh uncapped accounting agrees with independent closure: two identity LPs, four target MIPs and four target LPs; totals 2400.887156 MIP seconds and 10.294393 LP seconds. These are soft-limit shared-host accounting records, as the text states.

Primary new closure bindings inspected:

- `fresh_targets_postrun_review/final_ledger.json`: `3dfdfd25590e9a7cc7904f45cea3d23c7b7f39f83fd095b5894b484ed0825d4f`, status `INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS`.
- `fresh_energy_review/postrun.json`: `e71c1c8c553efcaa952ab4afc728ff6af52a60b21df0343170c9dc05feee9d89`, status `INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS`, all 378 frozen bindings unchanged.
- `hod_reoptimized_subsets_independent_review/postrun_review.json`: `6ed59296e66737a113acb73b1d4ff0c2a5c47ccec1f65de3d0198d8ac4ce6bf8`, status `INDEPENDENT_HOD_SUBSET_POSTRUN_PASS`.

## Mathematical and physical claims

Equations (1)–(2) clearly define the uniformly expanded finite-bound model and preserve exact U/Y/Z binary coordinates. The displayed rational tau equals the archived binary64 value of 1e-5. The text distinguishes mixed native units, numerical expansion and strict nominal membership; it does not turn expanded positive witnesses into strict unexpanded witnesses.

Equation (3) is the signed-row lower bound minus the finite-box support function, with the correct row/box expansion correction. Its positive gap rejects the continuous relaxation and therefore the binary model. Selected row endpoints must be finite and producer sign projection is disclosed. Arbitrary ray scale is not interpreted in MWh.

Equation (6) uses `eta=c-A^T d` and the finite-box minimum correction. It remains a valid objective lower bound without exact dual stationarity. The draft correctly separates established safe-bound prior work from its elementary explicit expansion derivation. Equations (4)–(5), the open upper endpoint of the sufficient cap band, the two integer-cap counts and the downward-rounded half-separation error bounds preserve their previous reviewed meanings. Neither a feasible incumbent nor a numerical solver optimum is called an exact optimum.

The 107-coordinate hourly observation is complete for the declared model encoding: independently stored aggregate net demand, 24 nodal net demands, 41 lower and 41 upper bounds. Including aggregate demand separately is necessary for its actual binary64 representation. Dispatch, commitment, timestamps and source/destination labels are excluded from the observation while remaining available as archive provenance. The clock-conditioned observation preserves the full joint packages within each hour label and the ordered edge packages; it does not preserve interior adjacency or daily trajectories.

The scope is isolated Area 1, 24 buses, 38 internal branches, 41 generators, 24 thermal units and a 23-unit Coal/Oil/NG fossil-electricity objective excluding nuclear. Free mature initial commitment, initial Y/Z zeros, clipped terminal residence and no cyclic obligation are explicit. MW, radians, dimensionless binary states and one-hour MWh accounting are defined. There is no mean-target, storage, shedding, AC, emissions or cost claim.

The observation argument is a valid two-instance obstruction for deterministic classifiers using the declared common observation and parameters. It permits abstention and makes no population-error or representative-day-method claim. The no-dwell argument is restricted to the audited physical model, its canonical transition lift and its absent temporal mechanisms; it does not claim a general UC equivalence. The July distinct-alphabet bigram observation and endogenous/exogenous distinction prevent an unsupported generic Markov impossibility claim.

The fixed-template statement is supported by four exact expanded continuous points in the two fixed row/box subsets. Each point is fractional on the original state mask and fails strict nominal membership. Their existence excludes all valid linear separating multipliers within those expanded templates, while establishing neither full binary feasibility nor the absence of other supports or integrality-based proofs. The six older nonseparating vectors are not used alone to make the stronger statement.

The note and Arabic decision retain scope limitations: same network/month transfer, failed seasonal replication criterion, changed model background in July-to-January rule transfer, fixed-schedule versus full-UC distinction, non-independent synthetic interventions, and no established broad novelty or external-network validation. Active nominal-encoding diagnostics are explicitly omitted.

## Symbols, callouts and references

The bounded child audit independently checked the same initial JSON hashes. English Equation IDs 1–6, Tables 1–3 and Figure 1 resolve. Both languages call out every table and the shared figure. The figure file exists. Reference first-use order is exactly English 1–10 and Arabic 1–9, including citation ranges. DOI and preprint-version strings agree with the existing local primary-source audits; Merrick is explicitly the inspected author preprint. This review made no new network request and does not claim a fresh DOI-resolver or subscription-fulltext check.

The parent resolved both optional symbol clarifications before final rendering. No outstanding cross-reference or reference-order correction was found. Final line wrapping, equation glyphs, table widths, Arabic directionality and figure placement require rendered DOCX/PDF inspection by the parent.

## Reproducibility and availability wording

The scientific commit is updated to `8abc5f3df438fe3a54e35aa06c892978adcd0537` in both drafts. The text clearly distinguishes the new experimental GitHub branch from Zenodo DOI 10.5281/zenodo.22976152, which archives the frozen V8 release rather than all new experiments. It does not claim remote Drive content-hash verification. Native-data attribution and the absence of redistributed subscription texts remain explicit.

The closed portable-replay readout supports the separately reported approximately 59.57-second same-host run, its declared subset, no optimizer/network calls and unchanged hashes. Its scope excludes full reassembly from native CSVs, second-machine reproduction and active subsequent experiments. The manuscript describes those limits rather than promoting relocation into external replication. The earlier 35-fixture suite is distinguished from that later run; no redundant fixture rerun is implied.

The separate plot source review passed at SHA256 `9b84a759c5cb6cf8a84d540d2484f5af4fc4c95b4d916f956fe4c3a664f72b01`, after independent status/hash gates for all three energy inputs were checked. The parent subsequently reported successful rendering and visual inspection; this reviewer did not rerun that plot.
