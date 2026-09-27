# Certified limits of clock conditioned summaries for chronological power system feasibility

Research note for author review · version 3

Ghassan Malkawi and Ahmed Abdelaziz Elsayed

Working draft version 3. New experiments and exact checks completed on 27 September 2026; frozen V8/V8R1 releases remain separate.

## Abstract

Hourly power-system inputs can admit a feasible schedule in one order and reject every schedule in another, despite an unchanged empirical joint input distribution conditional on hour of day. We construct and independently verify such pairs in 168-hour RTS-GMLC Area 1 models with 24 buses, 41 generators and binary thermal operating states. Five of six prescribed hour-preserving targets across three January weeks are infeasible under their week-specific fossil-electricity caps; original chronologies and class controls admit verified schedules, while the sixth target remains unresolved. These angle-model statements use archived binary64 coefficients with finite bounds expanded by the exact binary64 value of 1e-5 and exact binary states. A separate flow-conserving DC encoding admits rational identity and control witnesses and rejects both first-week hour-preserving targets with no bound expansion. The strict variant also has finite, positive optimal-energy penalty enclosures for both targets. Exact equivalence of the encodings is not asserted. In the expanded angle model, uncapped optimal fossil energy strictly increases for all six hour-preserving targets, including the unresolved capped case. Finite enclosures combine accepted binary upper witnesses with exact lower bounds; they do not assume solver optimality. In the expanded angle model, two previously useful compact row templates admit exact continuous points on both first-week targets, excluding linear Farkas proofs within those templates. A four-target seasonal follow-up certifies three positive energy differences and retains one case without a finite upper witness. The contribution is an observation-specific benchmark with independently checked evidence; broad methodological novelty and external-network generalization remain unestablished.

## 1 Research question and prior work

The useful question is which retained observations suffice to determine a chronological operating verdict. Showing that time order matters is not itself new. Bahl and colleagues already use temporal aggregation with objective-error bounds [1], while RiSES3 combines aggregation and relaxation with feasible upper solutions and lower bounds [2]. Auer and colleagues retain inter-period transition information and evaluate reordered or resampled representative periods on RTS-GMLC [3]. Their 2026 version is a preprint, and its chronology experiments rule out claiming the broad reordering idea as new here.

The author preprint of Merrick, Bistline and Blanford gives sufficient conditions for lossless chronology aggregation, including equal input states, deterministic transitions and equal run lengths [4]. Gonzato, Bruninx and Delarue separate input aggregation from reduced-model error by testing synthetically ordered periods in full models [5]. These are close precedents for chronology sufficiency and ordering experiments. Our clock-conditioned snapshot observation retains no complete daily trajectory or lagged linkage, so these pairs do not refute representative-day or transition-aware methods that distinguish them.

Kebrich and colleagues test investment designs across weather years and refine planning using observed supply gaps, synthetic time series and added inequalities [6]. Operational validation followed by corrective refinement is therefore also established prior work. The present study does not implement or compare a new refinement algorithm.

Our narrower experiment fixes a declared observation map, produces two inputs with the same observation, and attaches an independently checkable feasible witness or infeasibility certificate to each. Safe bounds under numerical error [7] and independently verifiable integer-programming results [8] are established methods. We use those principles rather than claim a new Farkas theorem or exact optimization method. A short contradiction can explain one instance without establishing a minimum amount of raw information.

## 2 Model and observations

The underlying data are the updated IEEE Reliability Test System, RTS-GMLC [9]. We isolate Area 1 and retain its 24 buses, 38 internal branches, 41 generators and 24 thermal units. Unit commitment (UC) means choosing whether each thermal unit operates at each hour, together with dispatch and startup or shutdown states; standard formulations are reviewed in [10]. The horizon contains T = 168 one-hour intervals, indexed t = 0,…,167. We use a linear direct-current (DC) network model with native nodal demand, output availability, line limits and angle bounds. The model has no load shedding, storage, startup costs, emissions conversion or individual generator-mean constraints.

Let v collect dispatch P, commitment U, startup Y, shutdown Z and bus angles θ, in the archived column order. P is measured in MW and θ in radians; U, Y and Z are dimensionless binary variables. Let J denote all 12,096 original state coordinates, and |J| their count. The fixed physical parameters and topology are K. For an ordered hourly input sequence X, A_X is the archived noncap constraint matrix, ℓ_X and r_X are its lower and upper row bounds, and a_X and b_X are finite column bounds. Define Fτ(X) by Equations (1) and (2), where 1 is the vector of ones of the matching dimension. The expansion τ is the exact rational 5902958103587057/590295810358705651712, the stored binary64 value of 1e-5. Only finite bounds are widened.

Equation (1): ℓ_{X} − τ1 ≤ A_{X}v ≤ r_{X} + τ1

Equation (2): a_{X} − τ1 ≤ v ≤ b_{X} + τ1,    v_{J} ∈ {0,1}^{|J|}

This is an explicit numerical model convention, not a physical uncertainty set. A numerical bound has its own native units, so the same numerical τ does not represent one common physical error magnitude. Strict nominal membership is checked separately and is not inferred from expanded membership. The small nonzero residuals of the saved positive witnesses preclude calling them exact witnesses for the unexpanded model.

The vector c sums dispatch from the 23 units classified as Coal, Oil or NG over one-hour intervals; its coefficients on all other coordinates are zero. The nuclear unit is excluded. Superscript T denotes transpose. Thus E(v) = cᵀv is fossil electrical energy in MWh, not fuel input, cost or emissions. A nominal energy cap B adds cᵀv ≤ B + τ to Fτ(X). Define the optimal fossil energy E*(X) as the minimum of cᵀv over the uncapped set Fτ(X), whenever this set is nonempty. A valid binary witness and finite dispatch boxes establish a finite attained minimum without requiring the witness to be optimal.

Thermal initial commitment is free with mature prehistory; initial startup and shutdown indicators are zero. Minimum residence requirements are clipped at the final hour, with no cyclic or post-horizon obligation. Native on-to-on ramp limits are redundant under the nominal output bounds in these selected inputs and are checked numerically on accepted witnesses. The interpretation must retain these boundary conventions and the isolation of Area 1.

Let ℝ denote the real numbers. An hourly physical package s_t ∈ ℝ¹⁰⁷ contains the independently formed aggregate net demand, all 24 nodal net demands, and all 41 lower and 41 upper availability bounds. Including both demand representations preserves the actual binary64 encoding. Dispatch, commitment, absolute timestamps, native source-row identifiers and destination positions are absent from this observation vector. Source-row labels remain in the reproducibility archive, but are not silently treated as chronology retained by a summary. Thus X = (s₀,…,s₁₆₇) is the ordered sequence of hourly packages.

Let H(t) be the hour label t mod 24 and let T_edge be the edge positions 0,…,47 and 120,…,167. The clock-conditioned observation Φ_H(X) retains the multiset of complete s_t vectors separately for each of the 24 hour labels, plus the ordered packages at T_edge. K, B and τ are common to each compared pair. An unrestricted observation Φ_0 retains only the joint multiset and the same ordered edges. Neither map retains adjacency between interior hours.

## 3 Exact evidence and elementary consequences

For this paragraph, A, ℓ and r denote the complete tested row system, including the fossil cap when present; a and b denote its finite column bounds. Here i indexes rows. For a signed row-multiplier vector d, β(d) is the sum of d_i times the lower row endpoint when d_i is positive and the upper endpoint when it is negative. Every selected endpoint must be finite. Set q = Aᵀd and M(q) = max{qᵀv : a ≤ v ≤ b}. M is evaluated by choosing one finite endpoint per coordinate. The norm ‖·‖₁ is the sum of absolute values. Equation (3) gives the exact expanded separation gap.

Equation (3): G_{τ}(d) = β(d) − M(q) − τ(‖d‖_{1} + ‖q‖_{1})

If Gτ(d) > 0, the expanded continuous relaxation is empty, hence so is the corresponding binary model. This follows by multiplying its row inequalities, maximizing over its expanded box and obtaining incompatible lower and upper bounds on qᵀv. The certificate checker recomputes both the norm expression and direct widened endpoints using exact rational interpretations of binary64 values. It rejects inadmissible endpoint signs. Any producer sign projection is archived explicitly and independently reconstructed; the checker does not silently repair the supplied vector. The scale of Gτ is arbitrary, so it must not be reported as a required MWh increase.

Positive membership requires exact row and box evaluation and exact zero-or-one values on the original U/Y/Z mask. Solving a projected formulation with only U declared integer is allowed only after auditing the actual transition and exclusivity rows. Acceptance reconstructs canonical Y and Z, leaves P and θ unchanged, then checks the full original mask. A separate numerical check evaluates the native physical equations. A solver status or a fractional continuous point does not substitute for either exact binary membership or a separating certificate.

Observation consequence. If Φ(X) = Φ(X′), but one capped model has a verified binary witness and the other an exact separating certificate, any deterministic binary classifier using only Φ and the common parameters must give the same prediction for both. It cannot be correct for both. It may instead abstain. This is a two-instance logical obstruction, not an estimated population error rate or a claim against methods that retain additional chronology.

Energy consequence. Subscripts I and T identify the original (identity) and permuted (target) inputs; E* with either subscript denotes that input’s optimum. Let L_I and U_I bound the uncapped identity optimum, and L_T and U_T bound a target optimum. Here L denotes a valid exact lower bound and U the energy of an accepted binary witness. Equation (4) encloses the difference; Equation (5) encloses the relative difference when L_I > 0 and L_T > 0.

Equation (4): L_{T} − U_{I} ≤ E*_{T} − E*_{I} ≤ U_{T} − L_{I}

Equation (5): (L_{T})/(U_{I}) − 1 ≤ (E*_{T})/(E*_{I}) − 1 ≤ (U_{T})/(L_{I}) − 1

For the uncapped row system and objective c, set η = c − Aᵀd. Equation (6) gives a valid exact lower bound Lτ(d). The index j ranges over all columns, and min takes the smaller endpoint product. Safe numerical bounds are established prior work [7]. The explicit row and box expansion term here follows directly by minimizing ηᵀv over the expanded box and applying the signed row inequalities; this algebra does not require exact dual stationarity.

Equation (6): L_{τ}(d) = β(d) + Σ_{j} min(η_{j}a_{j}, η_{j}b_{j}) − τ(‖d‖_{1} + ‖η‖_{1})

For a proposed nominal cap B, the sufficient band U_I − τ ≤ B < L_T − τ simultaneously admits the identity witness and excludes the target. Its upper endpoint is open. If Φ_0 is identical for the two finite-optimum instances, any common finite energy estimate has worst-case absolute error at least (L_T − U_I)/2, by the triangle inequality. These are arithmetic consequences for the same pair, not additional solved cases or new information-theoretic methods.

Structural consequence. In the audited original angle model, deleting only minimum-up and minimum-down rows leaves no order-dependent temporal coupling beyond auxiliary transition variables. The global fossil cap still links hourly dispatch, but is invariant under joint hourly permutations. For 0 ≤ τ < 1, the original integer bounds keep U/Y/Z binary. Every retained P/U/θ assignment lifts by Y_t = max(U_t − U_(t−1),0) and Z_t = max(U_(t−1) − U_t,0), with initial zeros. The remaining transition and exclusivity constraints hold exactly. A joint hourly package permutation therefore maps the projected no-dwell feasible sets bijectively and preserves fossil energy. The full matrix audit checked eight supplied target archives. This model-specific explanation depends on the absence of storage, binding ramp coupling, startup costs and initial residence obligations; it is not a general UC equivalence.

## 4 Fixed comparisons and results

The first January reference is an accepted binary schedule with exact fossil electricity approximately 22964.941240 MWh. Its cap is B = ceil(101Eref/100) = 23195 MWh, where Eref is the exact energy of that reference and ceil rounds upward to an integer. Two unrestricted permutations use seeds 26093100 and 26093101; their 72-hour interior may change while both 48-hour edges stay fixed. Two later hour-preserving permutations use seeds 26093200 and 26093201: for each hour of day, the three interior-day packages are shuffled only among that hour’s three positions. All choices within each arm were fixed before its target solves.

Positive controls permute only within groups sharing the complete reference commitment vector; the clock-preserving arm additionally fixes hour of day. The original and class-control witnesses pass the expanded binary and native checks. Every ordinary transferred schedule also passes the static model after deleting dwell rows. Its own failure under dwell constraints is not a model-infeasibility proof: the separate exact rays reject every possible schedule under the declared cap.

Table 1 reports historical ordinary-target capped-run classifications. Both unrestricted and both hour-preserving January cases are certified infeasible in their expanded continuous relaxations. The latter pairs have identical Φ_H observations, so the obstruction persists after controlling the placement of each package by clock hour. Within-day trajectories still change. These are synthetic ordering interventions in one January week, not observed weather histories or four independent replications.

Table 1 Historical capped-run outcomes for ordinary targets

| Experiment | Cases | Feasible | Infeasible | Unresolved |
| --- | --- | --- | --- | --- |
| January unrestricted interior | 2 | 0 | 2 | 0 |
| January fixed hour of day | 2 | 0 | 2 | 0 |
| January whole interior days | 5 | 1 | 0 | 4 |
| April and October continuation | 4 | 0 | 0 | 4 |
| Fresh January 8–14, fixed hour | 2 | 0 | 1 | 1 |
| Fresh January 15–21, fixed hour | 2 | 0 | 2 | 0 |

The first three rows use cap 23195 MWh. The seasonal continuation uses April cap 43131 MWh and October cap 125172 MWh, each fixed from its accepted reference by the same rule. The fresh January weeks use caps 26532 and 48319 MWh respectively. Feasible means an exact expanded binary witness; infeasible means an exact expanded separating certificate. Unresolved includes fractional LP admission followed by a time-limited MIP with no accepted binary witness. Controls are checked separately and excluded from the ordinary-case denominators. One October class-control draw was the identity and is retained as such. These are outcomes of those capped runs. A later uncapped study supplied a new capped witness for seasonal target 26094000 (Section 4.2); the historical four-UNKNOWN ledger is preserved.

For fresh-week transfer, the two lowest unused January windows, native rows 168:336 and 336:504, were selected without inspecting their target outcomes. Reference solves and exact acceptance preceded fixed cap construction. The same clock-preserving perturbation family and unchanged edge rule were then applied with seeds 26093210/11 and 26093220/21. Both new identities and both preselected clock/commitment-class controls pass full expanded binary checks; controls change 25 and 2 hours and are not redrawn. Independent replay certifies targets 26093210, 26093220 and 26093221 infeasible. Target 26093211 has an expanded continuous point with fractional states and no accepted binary incumbent after its one 300-second MIP attempt, so it remains unresolved.

This is transfer to distinct, nonoverlapping weeks of the same network and month. It does not establish seasonal, network or statistical independence. All four fresh targets remain in the denominator. Exactly four 30-second-limit LP calls ran, followed by the one conditional 300-second-limit MIP; actual totals were 20.172922 and 300.446834 seconds. No retry, substituted draw or additional reference was used. The original failed seasonal negative-replication gate remains unchanged; the subsequent energy study is reported separately in Section 4.2.

For the unrestricted January pair, the identity lower and upper bounds are approximately 22615.822769 and 22964.941240 MWh. Target lower bounds are 24507.776970 and 25104.092377 MWh; target binary witness energies are 25162.618973 and 25693.286910 MWh. For the later hour-preserving targets, the respective lower and upper energy bounds are approximately [23531.307857, 23952.175431] and [23823.063084, 24024.798984] MWh. Equations (4) and (5) yield Table 2: its first two rows are unrestricted and its last two preserve hour of day. Displayed interval endpoints are rounded outward; stored rational fractions are authoritative. Figure 1 compares the optimum-difference enclosures in Tables 2 and 3.

Table 2 Certified optimal energy increases for the first January week

| Seed | Difference interval in MWh | Relative interval |
| --- | --- | --- |
| 26093100 | [1542.835730, 2546.796204] | [6.718221%, 11.261126%] |
| 26093101 | [2139.151137, 3077.464141] | [9.314855%, 13.607571%] |
| 26093200 | [566.366617, 1336.352662] | [2.466222%, 5.908928%] |
| 26093201 | [858.121844, 1408.976215] | [3.736660%, 6.230047%] |

The uncapped follow-up included all four fresh-week targets irrespective of their capped labels. It used the unchanged reference upper witnesses, two reference LP calls, four target MIP calls and four target LP calls, with fixed 60-second LP and 600-second MIP limits and no retries. All four targets have independently verified original-mask binary upper witnesses, and all six LP lower bounds pass exact residual evaluation. Table 3 gives the resulting optimal-to-optimal enclosures. The four MIPs used 2400.887156 seconds in total and the six LPs 10.294393 seconds; these shared-host timings are accounting records, not a speed comparison.

Table 3 Certified optimal energy increases in the two further January weeks

| Week | Seed | Difference interval in MWh | Relative interval |
| --- | --- | --- | --- |
| 2 | 26093210 | 574.017996–1815.622131 | 2.185149–7.016271% |
| 2 | 26093211 | 89.056939–2303.990067 | 0.339018–8.903515% |
| 3 | 26093220 | 1082.076498–1856.243776 | 2.261852–3.910485% |
| 3 | 26093221 | 1048.824076–2458.387516 | 2.192345–5.179001% |

Every interval in Table 3 has a strictly positive lower endpoint. In particular, target 26093211 requires at least 89.056939 MWh more optimal fossil electricity even though its original capped verdict stays unresolved: its lower bound of approximately 26358.110476 MWh is below 26532 + τ, while its accepted upper witness is above that cap. Positive optimal-energy separation and a decided verdict at one preselected cap are different claims. The old capped ledger is unchanged. All targets and references remain within the same January Area 1 model, and none of the finite enclosures asserts exact optimization.

![Figure 1 Exact-bound enclosures of the target optimum minus its own week’s original-order optimum. The first two rows allow unrestricted interior-hour permutations; the remaining six preserve hour of day. Bars are optimization bounds, not confidence intervals. All eight intervals have strictly positive lower endpoints; interval width reflects incomplete optimization. Original binary states and the uniform finite-bound expansion are retained.](../../../results/research8h/three_week_energy_figure/optimal_energy_differences.png)

For the unrestricted pair, the sufficient cap bands contain 1543 and 2140 integer-MWh caps respectively. Safe closed decimal subsets are [22964.941230, 24507.776959] and [22964.941230, 25104.092367] MWh. For a common Φ_0-based energy estimate, the corresponding worst-case absolute error lower bounds, rounded downward, are 771.417865 and 1069.575568 MWh. These counts describe arithmetic bands from two pairs and must not be counted as thousands of experimental replications.

A retrospective fixed-evidence audit of the original angle model varies the numerical expansion while keeping all 15 binary witness roles, five cap rays and six energy duals unchanged. The largest exact row or box violation of each point gives an included lower threshold; the strict inequalities in Equations (3) and (6) give excluded upper thresholds. Their joint intersection contains the certified inner decimal band [0.000000003396525728, 0.000736348717339262), with lower endpoint rounded upward and upper endpoint downward. The fixed target-26093210 witness limits the lower end; the energy dual for 26093211 limits the upper end. Thus all five cap-negative and six positive-energy-gap claims hold together throughout this band, including the original expansion. Independent arithmetic replay reproduced every threshold and intersection without optimization. The capped verdict for 26093211 remains unresolved. The range depends on row and column units and normalization; it is not a physical uncertainty margin. Zero is outside this fixed-evidence range, and failure of this evidence outside it establishes no reversed verdict or absence of other proofs.

## 4.1 Strict evidence in a separately specified network encoding

To test whether a chronology obstruction can also be certified without widening bounds, we separately declare a flow-conserving DC variant on the already known first January week. Let Pₜ ∈ ℝ⁴¹ collect hourly generator dispatch, θₜ ∈ ℝ²⁴ the bus angles, fₜ ∈ ℝ³⁸ oriented branch flows in MW, and nₜ ∈ ℝ²⁴ the native nodal net loads in MW. Let D be the 24-by-38 incidence matrix, with +1 at each branch’s origin and −1 at its destination, and C the 24-by-41 generator-to-bus incidence matrix. The vector κ contains the 38 archived branch coefficients in MW per radian; diag(κ) places them on a diagonal. Equations (7) and (8) impose branch definitions and nodal balance using exact rational interpretations of these coefficients.

Equation (7): f_{t} = diag(κ)D^{T}θ_{t}

Equation (8): CP_{t} − Df_{t} = n_{t}

All old unit-state rules, dispatch and angle boxes, topology, branch limits, boundary conventions and the 23195 MWh cap are retained; the separate rounded aggregate-balance equation is omitted. Summing Equation (8) gives aggregate conservation exactly because each column of D sums to zero. This is a distinct declared model. Eliminating f changes 15 entries relative to the independently rounded nodal angle operator, by at most 3/2199023255552. The native nodal sum differs from the old aggregate RHS in 160 of 168 hours, by at most 37/281474976710656 MW. These nonzero differences are retained. No exact feasible-set equivalence or nesting is claimed.

Table 4 reports strict results at τ = 0. One fixed-schedule numerical proposal supplied a basis; exact rational reconstruction of all 168 hours yielded a point that passed all 34513 full rows, 29400 coordinate bounds, 12096 original binary states and direct native checks. The control moves 14 hour positions, preserves Φ_H and has the same exact fossil energy, approximately 22964.941240 MWh. Both ordinary targets preserve Φ_H but admit exact full-relaxation separators at the unchanged cap, proving binary infeasibility. Independent replay recomputed both positive points and both complete separator candidate sets without optimization. Separator gaps depend on multiplier scale and are not energy penalties.

Table 4 Strict feasibility evidence in the separate flow-conserving model

| Case | Bound expansion | Certified capped verdict |
| --- | --- | --- |
| January identity | 0 | Binary feasible |
| Control 26100200 | 0 | Binary feasible |
| Target 26093200 | 0 | Continuous infeasible |
| Target 26093201 | 0 | Continuous infeasible |

A separate uncapped follow-up deletes only the cap from the three full strict models for the identity and two ordinary targets, excluding the control. The inherited strict identity point supplies its upper bound; three globally relaxed LPs supply new exact lower bounds through Equation (6) at τ = 0. Two additional LPs fix only the target schedules inherited from the earlier energy arm. Rational reconstruction and complete strict/native checks admit both target points. The new strict identity optimum lies between approximately 22616.830716 and 22964.941240 MWh. Applying Equations (4) and (5) to these new-model bounds yields Table 5. Both lower penalty endpoints are strictly positive. All 15 predetermined multiplier candidates, all 336 target-hour checks and the five-call ledger were independently replayed. No new integer search, alternate schedule or retry was used; no old-encoding objective bound was transferred.

Table 5 Strict optimal energy increases in the separate flow-conserving model

| Seed | Difference interval in MWh | Relative interval |
| --- | --- | --- |
| 26093200 | [568.039414, 1335.344714] | [2.473506%, 5.904208%] |
| 26093201 | [859.940259, 1407.968267] | [3.744578%, 6.225312%] |

Table 5 contains finite bounds on differences between the strict binary optima, not merely energy differences between chosen schedules. Displayed endpoints are rounded outward from the stored rational values. These intervals supplement, and do not replace, the expanded angle-model intervals in Table 2. The old and new numerical encodings remain distinct; the same two known input permutations are reused.

These results add strict positive and negative certificates in a precisely declared DC representation. They do not establish a new network formulation, unseen-week replication, strict admission of the old encoding, or physical measurement exactness. The original nominal candidate-construction failure remains unchanged. The flow-conserving variant reuses the known first-week cases, so its two ordinary results are not added to the six-target transfer denominator.

## 4.2 All-four seasonal energy follow-up

A retrospective uncapped follow-up retained all four previously unresolved April/October ordinary targets in the original expanded angle model. These preserve Φ_0, not Φ_H, and use the actual seasonal calendars and unchanged reference upper witnesses. Two reference LPs, four target MIPs and four target LPs ran once, with 60-second LP and 300-second MIP limits. Three targets yielded accepted full-mask binary/native upper witnesses. All six objective lower bounds passed independent exact evaluation. Table 6 applies Equations (4) and (5), retaining the fourth target without a finite upper bound.

Table 6 Seasonal optimal-energy differences in the expanded angle model

| Target | Month | Difference, MWh | Relative difference |
| --- | --- | --- | --- |
| 26093400 | April | [422.215678, 1460.098124] | [0.988706%, 3.461710%] |
| 26093401 | April | [273.680850, 1596.186199] | [0.640881%, 3.784357%] |
| 26094000 | October | [689.463677, 904.158184] | [0.556323%, 0.729564%] |
| 26094001 | October | No finite upper witness | Not established |

Target 26094001 has no accepted binary upper witness. Its exact lower bound exceeds the identity upper by at least 766.016260 MWh, rounded downward, conditional on the target being nonempty. This establishes neither target feasibility nor a finite optimum-difference or relative interval. All five accepted points, including the two references, fail strict nominal membership and pass expanded membership. The three finite positive intervals provide within-system seasonal energy evidence; they do not extend the six January clock-preserving cases or establish another-network validation.

A separately labeled post-hoc check tested all three new accepted target points against their complete old capped parent models. Target 26094000 now has a verified expanded binary/native capped witness: its energy is approximately 124835.463673 MWh, below the unchanged 125172 MWh cap. Thus current knowledge resolves this case positively, while Table 1 retains its historical capped-run UNKNOWN record. Both April witnesses exceed their old caps, which does not prove capped infeasibility; target 26094001 still lacks a witness. None of the four lower bounds exceeds its old cap plus τ, so no new capped negative or success of the original seasonal negative-replication criterion follows.

All four seasonal MIPs reached their time limits. Actual totals were 1212.990578 seconds for the MIPs and 73.277904 seconds for the LPs; the 12.990578-second aggregate soft-limit overrun is retained. Independent replay checked all 397 frozen bindings, six bounds, five binary upper points, every finite/conditional reporting branch, and all ten calls without optimization. The same isolated network, numerical expansion and boundary limitations apply.

## 5 Negative findings and scope limits

Among all five nonidentity permutations of the three complete interior days, one has an accepted binary witness and four remain unresolved. Fixing the original reference commitment makes all five restricted dispatch problems exactly infeasible, but this rejects only that particular commitment; the full positive day permutation directly demonstrates why a fixed-schedule rejection cannot stand in for UC infeasibility. The completed April and October continuation yields no new certified ordinary negative, so the declared two-week seasonal replication criterion is not met. The original failed short reference attempts and later successful reference continuation remain separately recorded.

The July experiments provide an additional warning about observation definitions. All 168 exact exogenous observations in each audited raw alphabet are distinct. Their exact labelled bigrams and endpoints therefore determine the entire order by following the unique next edge. A changed sequence that preserves only endogenous commitment bigrams does not preserve these exogenous bigrams. Finite-alphabet factor-count collisions exist and are already studied in the literature [11], but that fact does not establish information loss for an injectively labelled raw dataset. No generic impossibility claim about Markov summaries follows from our pairs.

The smaller July explanation rules do not transfer uniformly: in the first January full-network service-cap pair, the fixed two-generator rule rejects zero of two targets and the fixed 48-hour dwell-support rule rejects one of two. This comparison also changes the background model from individual mean constraints without the network to an energy cap with the network. It cannot isolate a seasonal effect. The rule’s temporal support does not count the full background information required by its certificate, and no minimum-support or irreducible-infeasible-subsystem claim is made.

A subsequent zero-optimizer test reused six fixed coefficient vectors on the two known hour-preserving negatives. All six were valid but nonseparating, even before expansion. We then froze and solved the four continuous subset problems in the original angle encoding defined by the same two targets and two rules. The first rule keeps all four temporal constraint families only on the two selected combined-cycle units, together with the unchanged global static, network, cap and box background. The second keeps dwell rows whose complete state support lies in hours 60–107, together with every transition and exclusivity row and the same global background. All four admit independently checked exact expanded continuous points. Therefore no valid linear Farkas certificate using either fixed row/box template can reject these targets. This excludes every coefficient choice within those templates, not only the six initial vectors. The points are fractional and fail strict nominal membership, so this is neither binary admission nor strict feasibility. It does not exclude other supports or proofs using integrality.

Strict nominal checks remain separate. All 1,344 prescribed balance-and-branch diagnostic orientations were nonseparating; that null result establishes no feasibility. A later one-basis attempt reconstructed rational points for all 168 hours of the original January fixed schedule, but every hourly candidate violated an exact row or box. The assembled candidate has 1,670 violations. Independent replay confirms this failed candidate construction; it proves neither fixed-schedule infeasibility nor infeasibility of the full commitment problem. No alternate basis or retry was used.

No AC chronology, independent network, field intervention, fuel-input estimate, emissions benefit or operating recommendation has been validated by these experiments. Network Area 2 and a separate public UC benchmark were assessed for compatibility but not optimized; omitted storage semantics and model-adaptation costs precluded a sound external-system claim within this session. Solver wall times include soft-limit overruns on a shared host and are not performance benchmarks.

## 6 Reproducibility and research decision

Each arm records source and protocol hashes, prepared matrix and bound archives, original masks, native input bindings, prescribed cases, solver logs, witnesses and final checks. The standard-library Python verifier uses exact rational arithmetic without NumPy, SciPy or a solver and passed 35 adversarial fixtures. Two separately closed same-host relocation runs checked declared subsets of delivery archives. The first covered five negative rays, ten original-mask binary points, an additional identity, a continuous diagnostic, six nonseparating vectors and three objective bounds with two energy intervals. The second checked six fresh-week objective bounds, two reference and four target binary uppers, four energy intervals, four fractional subset points and two full controls with four inherited memberships. Both passed without optimizer or network calls, with unchanged package hashes; the unresolved capped case stayed unresolved. Their shared-host times, 59.57 and 72.13 seconds, are accounting records. This is neither second-machine replication nor complete native-data model assembly. The two wrappers do not jointly replay the two unrestricted first-week energy intervals; their independently reviewed original evidence remains archived.

A third same-host relocation replay checked the separate strict flow evidence: five point/model combinations (capped identity/control and uncapped identity/two targets), all eight ray candidates, all fifteen lower-bound candidates and both optimal-energy intervals. It passed in 150.87 seconds with zero optimizer or network calls and unchanged package bytes. It did not rebuild the physical models or run on another machine. An initial package-assembly attempt had stopped before mathematical replay because a broad Git overlay conflicted with historical source versions. The corrected assembly preserved all inherited bytes; no scientific source, matrix or pinned scientific dependency hash was changed to obtain the pass.

The strongest current contribution is the explicit mismatch between clock-conditioned observations and a verified chronological verdict, transferred to two further January weeks and now accompanied by strictly positive optimal-energy differences for all six hour-preserving targets. A separately specified flow-conserving variant now supplies strict identity/control witnesses, two strict negatives and two positive finite energy-penalty enclosures at zero expansion. Exact positive and negative evidence, the failure of two fixed linear-proof templates and retained nulls make the benchmark inspectable. Priority for a broadly new method remains unestablished. A submission should distinguish temporal transfer within one network and month from external validation; the evidence does not establish a new aggregation algorithm or journal readiness.

## Data and code availability

RTS-GMLC source data were provided by the U.S. Department of Energy (DOE), the National Renewable Energy Laboratory (NREL) and Alliance for Sustainable Energy, LLC (ALLIANCE). Their data-use notice and attribution accompany redistributed source-data copies. This acknowledgment does not imply endorsement.

Verified experimental source, protocols and results are published on the codex/temporal-information branch of the project GitHub repository. Evidence for the completed experiments in this note is fixed at commit d491d49fd2d21a798df2911a9b0987532e5dbf7d, independently read back after publication. The separate private Google Drive research folder contains delivery ZIPs and Arabic guides. Each delivery has a file SHA256 manifest. Verification receipts distinguish local archive checks, uploaded filenames and byte counts, destination and sharing checks, and any byte-for-byte SHA256 comparison of downloaded uploaded files. Absence of a provider-supplied checksum is not treated as content verification.

The existing Zenodo record DOI 10.5281/zenodo.22976152 documents the frozen V8 reproducibility release. It does not archive all new experiments in this note and must not be cited as if it did. Frozen V8/V8R1 manuscripts and releases were not replaced. The new materials include original reading notes and citations, not subscription full texts. Some original experiment manifests contain host-specific paths; the standalone verifier supports explicit path-prefix remapping without altering expected hashes.

[Experimental GitHub branch](https://github.com/shaikhamalkawi-ux/Decision-Stability-Certificates-for-Power-System-Operating-States-/tree/codex/temporal-information)

[Google Drive research folder](https://drive.google.com/drive/folders/1cwdmcpJCPQC5sTdopQtQWi4sJpFdAChw)

## References

[1] B. Bahl, T. Söhler, M. Hennen and A. Bardow. Typical Periods for Two-Stage Synthesis by Time-Series Aggregation with Bounded Error in Objective Function. Frontiers in Energy Research 5, article 35, 2018. [doi.org/10.3389/fenrg.2017.00035](https://doi.org/10.3389/fenrg.2017.00035)

[2] N. Baumgärtner, B. Bahl, M. Hennen and A. Bardow. RiSES3: Rigorous Synthesis of Energy Supply and Storage Systems via time-series relaxation and aggregation. Computers and Chemical Engineering 127, 127–139, 2019. [doi.org/10.1016/j.compchemeng.2019.02.006](https://doi.org/10.1016/j.compchemeng.2019.02.006)

[3] F. C. A. Auer, R. Gaugl, T. Klatzer, D. A. Tejada-Arango and S. Wogrin. Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices. arXiv:2510.18555v2, revised 15 July 2026. Preprint. [arxiv.org/abs/2510.18555v2](https://arxiv.org/abs/2510.18555v2)

[4] J. H. Merrick, J. E. T. Bistline and G. J. Blanford. On representation of energy storage in electricity planning models. arXiv:2105.03707v2, 31 May 2021. Author preprint. [arxiv.org/abs/2105.03707v2](https://arxiv.org/abs/2105.03707v2)

[5] S. Gonzato, K. Bruninx and E. Delarue. Long term storage in generation expansion planning models with a reduced temporal scope. Applied Energy 298, 117168, 2021. [doi.org/10.1016/j.apenergy.2021.117168](https://doi.org/10.1016/j.apenergy.2021.117168)

[6] S. Kebrich, F. Engelhardt, D. Franzmann, C. Büsing, J. Linßen and H. Heinrichs. Robust capacity expansion modeling for renewable energy systems. iScience 29(3), 114929, 2026. [doi.org/10.1016/j.isci.2026.114929](https://doi.org/10.1016/j.isci.2026.114929)

[7] A. Neumaier and O. Shcherbina. Safe bounds in linear and mixed-integer linear programming. Mathematical Programming 99, 283–296, 2004. [doi.org/10.1007/s10107-003-0433-3](https://doi.org/10.1007/s10107-003-0433-3)

[8] K. K. H. Cheung, A. Gleixner and D. E. Steffy. Verifying Integer Programming Results. IPCO 2017, LNCS 10328, 148–160. [doi.org/10.1007/978-3-319-59250-3_13](https://doi.org/10.1007/978-3-319-59250-3_13)

[9] C. Barrows et al. The IEEE Reliability Test System: A Proposed 2019 Update. IEEE Transactions on Power Systems 35(1), 119–127, 2020. [doi.org/10.1109/TPWRS.2019.2925557](https://doi.org/10.1109/TPWRS.2019.2925557)

[10] B. Knueven, J. Ostrowski and J.-P. Watson. On Mixed-Integer Programming Formulations for the Unit Commitment Problem. INFORMS Journal on Computing 32(4), 857–876, 2020. [doi.org/10.1287/ijoc.2019.0944](https://doi.org/10.1287/ijoc.2019.0944)

[11] A. Saarela. Separating the Words of a Language by Counting Factors. Fundamenta Informaticae 180(4), 375–393, 2021. [doi.org/10.3233/FI-2021-2047](https://doi.org/10.3233/FI-2021-2047)
