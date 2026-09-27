# Certified limits of clock conditioned summaries for chronological power system feasibility

Research note for author review · version 2

Ghassan Malkawi and Ahmed Abdelaziz Elsayed

Working draft version 2, incorporating independently reviewed fresh-week energy and fixed-template proof-limit results completed on 27 September 2026. Exact nominal-encoding diagnostics remain a separate ongoing audit and are not included.

## Abstract

A collection of hourly power-system inputs can admit a feasible operating schedule in one order and reject every schedule in another, even when the entire joint input distribution conditional on hour of day is unchanged. We construct and independently verify such pairs in 168-hour RTS-GMLC Area 1 models with 24 buses, 41 generators and binary thermal operating states. Five of six prescribed hour-preserving targets across three nonoverlapping January weeks are infeasible under their week-specific fossil-electricity caps, while the original chronologies and class controls admit verified schedules; the sixth target remains unresolved. Two original unrestricted targets are also certified infeasible. All statements refer to archived binary64 coefficients with every finite numerical bound expanded outward by the exact binary64 value of 1e-5; binary coordinates remain exact. Uncapped follow-up establishes strictly positive lower bounds on increased optimal fossil electricity for all six hour-preserving targets across the three weeks, including the unresolved capped case. Each increase has a finite enclosure from an accepted binary upper witness and an exact lower bound; none requires claiming that a solver reached the optimum. Two previously useful compact row templates admit exact continuous points on both first-week targets, excluding any linear Farkas proof within those fixed templates. Whole-day and cross-season experiments retain positive and unresolved cases. The contribution is an observation-specific benchmark and evidence chain; broad methodological novelty and external-network generalization are not established.

## 1 Research question and prior work

The useful question is which retained observations suffice to determine a chronological operating verdict. Showing that time order matters is not itself new. Bahl and colleagues already use temporal aggregation with objective-error bounds [1], while RiSES3 combines aggregation and relaxation with feasible upper solutions and lower bounds [2]. Auer and colleagues retain inter-period transition information and evaluate reordered or resampled representative periods on RTS-GMLC [3]. Their 2026 version is a preprint, and its chronology experiments rule out claiming the broad reordering idea as new here.

The author preprint of Merrick, Bistline and Blanford gives sufficient conditions for lossless chronology aggregation, including equal input states, deterministic transitions and equal run lengths [4]. Gonzato, Bruninx and Delarue separate input aggregation from reduced-model error by testing synthetically ordered periods in full models [5]. These are close precedents for chronology sufficiency and ordering experiments. Our clock-conditioned snapshot observation retains no complete daily trajectory or lagged linkage, so these pairs do not refute representative-day or transition-aware methods that distinguish them.

Our narrower experiment fixes a declared observation map, produces two inputs with the same observation, and attaches an independently checkable feasible witness or infeasibility certificate to each. Safe bounds under numerical error [6] and independently verifiable integer-programming results [7] are established methods. We use those principles rather than claim a new Farkas theorem or exact optimization method. A short contradiction can explain one instance without establishing a minimum amount of raw information.

## 2 Model and observations

The underlying data are the updated IEEE Reliability Test System, RTS-GMLC [8]. We isolate Area 1 and retain its 24 buses, 38 internal branches, 41 generators and 24 thermal units. Unit commitment (UC) means choosing whether each thermal unit operates at each hour, together with dispatch and startup or shutdown states; standard formulations are reviewed in [9]. The horizon contains T = 168 one-hour intervals, indexed t = 0,…,167. We use a linear direct-current (DC) network model with native nodal demand, output availability, line limits and angle bounds. The model has no load shedding, storage, startup costs, emissions conversion or individual generator-mean constraints.

Let v collect dispatch P, commitment U, startup Y, shutdown Z and bus angles θ, in the archived column order. P is measured in MW and θ in radians; U, Y and Z are dimensionless binary variables. Let J denote all 12,096 original state coordinates. The fixed physical parameters and topology are K. For an ordered hourly input sequence X, A_X is the archived noncap constraint matrix, ℓ_X and r_X are its lower and upper row bounds, and a_X and b_X are finite column bounds. Define Fτ(X) by Equations (1) and (2), where 1 is the vector of ones of the matching dimension. The expansion τ is the exact rational 5902958103587057/590295810358705651712, the stored binary64 value of 1e-5. Only finite bounds are widened.

Equation (1): ℓ_{X} − τ1 ≤ A_{X}v ≤ r_{X} + τ1

Equation (2): a_{X} − τ1 ≤ v ≤ b_{X} + τ1,    v_{J} ∈ {0,1}^{|J|}

This is an explicit numerical model convention, not a physical uncertainty set. A numerical bound has its own native units, so the same numerical τ does not represent one common physical error magnitude. Strict nominal membership is checked separately and is not inferred from expanded membership. The small nonzero residuals of the saved positive witnesses preclude calling them exact witnesses for the unexpanded model.

The vector c sums dispatch from the 23 units classified as Coal, Oil or NG over one-hour intervals; its coefficients on all other coordinates are zero. The nuclear unit is excluded. Thus E(v) = cᵀv is fossil electrical energy in MWh, not fuel input, cost or emissions. A nominal energy cap B adds cᵀv ≤ B + τ to Fτ(X). Define the optimal fossil energy E*(X) as the minimum of cᵀv over the uncapped set Fτ(X), whenever this set is nonempty. A valid binary witness and finite dispatch boxes establish a finite attained minimum without requiring the witness to be optimal.

Thermal initial commitment is free with mature prehistory; initial startup and shutdown indicators are zero. Minimum residence requirements are clipped at the final hour, with no cyclic or post-horizon obligation. Native on-to-on ramp limits are redundant under the nominal output bounds in these selected inputs and are checked numerically on accepted witnesses. The interpretation must retain these boundary conventions and the isolation of Area 1.

An hourly physical package s_t ∈ ℝ¹⁰⁷ contains the independently formed aggregate net demand, all 24 nodal net demands, and all 41 lower and 41 upper availability bounds. Including both demand representations preserves the actual binary64 encoding. Dispatch, commitment, absolute timestamps, native source-row identifiers and destination positions are absent from this observation vector. Source-row labels remain in the reproducibility archive, but are not silently treated as chronology retained by a summary. Thus X = (s₀,…,s₁₆₇) is the ordered sequence of hourly packages.

Let H(t) be the hour label t mod 24 and let T_edge be the edge positions 0,…,47 and 120,…,167. The clock-conditioned observation Φ_H(X) retains the multiset of complete s_t vectors separately for each of the 24 hour labels, plus the ordered packages at T_edge. K, B and τ are common to each compared pair. An unrestricted observation Φ_0 retains only the joint multiset and the same ordered edges. Neither map retains adjacency between interior hours.

## 3 Exact evidence and elementary consequences

For this paragraph, A, ℓ and r denote the complete tested row system, including the fossil cap when present; a and b denote its finite column bounds. For a signed row-multiplier vector d, β(d) is the sum of d_i times the lower row endpoint when d_i is positive and the upper endpoint when it is negative. Every selected endpoint must be finite. Set q = Aᵀd and M(q) = max{qᵀv : a ≤ v ≤ b}. M is evaluated by choosing one finite endpoint per coordinate. The norm ‖·‖₁ is the sum of absolute values. Equation (3) gives the exact expanded separation gap.

Equation (3): G_{τ}(d) = β(d) − M(q) − τ(‖d‖_{1} + ‖q‖_{1})

If Gτ(d) > 0, the expanded continuous relaxation is empty, hence so is the corresponding binary model. This follows by multiplying its row inequalities, maximizing over its expanded box and obtaining incompatible lower and upper bounds on qᵀv. The certificate checker recomputes both the norm expression and direct widened endpoints using exact rational interpretations of binary64 values. It rejects inadmissible endpoint signs. Any producer sign projection is archived explicitly and independently reconstructed; the checker does not silently repair the supplied vector. The scale of Gτ is arbitrary, so it must not be reported as a required MWh increase.

Positive membership requires exact row and box evaluation and exact zero-or-one values on the original U/Y/Z mask. Solving a projected formulation with only U declared integer is allowed only after auditing the actual transition and exclusivity rows. Acceptance reconstructs canonical Y and Z, leaves P and θ unchanged, then checks the full original mask. A separate numerical check evaluates the native physical equations. A solver status or a fractional continuous point does not substitute for either exact binary membership or a separating certificate.

Observation consequence. If Φ(X) = Φ(X′), but one capped model has a verified binary witness and the other an exact separating certificate, any deterministic binary classifier using only Φ and the common parameters must give the same prediction for both. It cannot be correct for both. It may instead abstain. This is a two-instance logical obstruction, not an estimated population error rate or a claim against methods that retain additional chronology.

Energy consequence. Subscripts I and T identify the original (identity) and permuted (target) inputs; E* with either subscript denotes that input’s optimum. Let L_I and U_I bound the uncapped identity optimum, and L_T and U_T bound a target optimum. Here L denotes a valid exact lower bound and U the energy of an accepted binary witness. Equation (4) encloses the difference; Equation (5) encloses the relative difference when L_I > 0 and L_T > 0.

Equation (4): L_{T} − U_{I} ≤ E*_{T} − E*_{I} ≤ U_{T} − L_{I}

Equation (5): (L_{T})/(U_{I}) − 1 ≤ (E*_{T})/(E*_{I}) − 1 ≤ (U_{T})/(L_{I}) − 1

For the uncapped row system and objective c, set η = c − Aᵀd. Equation (6) gives a valid exact lower bound Lτ(d). The sum ranges over all columns, and min takes the smaller endpoint product. Safe numerical bounds are established prior work [6]. The explicit row and box expansion term here follows directly by minimizing ηᵀv over the expanded box and applying the signed row inequalities; this algebra does not require exact dual stationarity.

Equation (6): L_{τ}(d) = β(d) + Σ_{j} min(η_{j}a_{j}, η_{j}b_{j}) − τ(‖d‖_{1} + ‖η‖_{1})

For a proposed nominal cap B, the sufficient band U_I − τ ≤ B < L_T − τ simultaneously admits the identity witness and excludes the target. Its upper endpoint is open. If Φ_0 is identical for the two finite-optimum instances, any common finite energy estimate has worst-case absolute error at least (L_T − U_I)/2, by the triangle inequality. These are arithmetic consequences for the same pair, not additional solved cases or new information-theoretic methods.

Structural consequence. In the audited model, deleting only minimum-up and minimum-down rows leaves no order-dependent temporal coupling beyond auxiliary transition variables. The global fossil cap still links hourly dispatch, but is invariant under joint hourly permutations. For 0 ≤ τ < 1, the original integer bounds keep U/Y/Z binary. Every retained P/U/θ assignment lifts by Y_t = max(U_t − U_(t−1),0) and Z_t = max(U_(t−1) − U_t,0), with initial zeros. The remaining transition and exclusivity constraints hold exactly. A joint hourly package permutation therefore maps the projected no-dwell feasible sets bijectively and preserves fossil energy. The full matrix audit checked eight supplied target archives. This model-specific explanation depends on the absence of storage, binding ramp coupling, startup costs and initial residence obligations; it is not a general UC equivalence.

## 4 Fixed comparisons and results

The first January reference is an accepted binary schedule with exact fossil electricity approximately 22964.941240 MWh. Its cap is B = ceil(101Eref/100) = 23195 MWh, where Eref is the exact energy of that reference and ceil rounds upward to an integer. Two unrestricted permutations use seeds 26093100 and 26093101; their 72-hour interior may change while both 48-hour edges stay fixed. Two later hour-preserving permutations use seeds 26093200 and 26093201: for each hour of day, the three interior-day packages are shuffled only among that hour’s three positions. All choices within each arm were fixed before its target solves.

Positive controls permute only within groups sharing the complete reference commitment vector; the clock-preserving arm additionally fixes hour of day. The original and class-control witnesses pass the expanded binary and native checks. Every ordinary transferred schedule also passes the static model after deleting dwell rows. Its own failure under dwell constraints is not a model-infeasibility proof: the separate exact rays reject every possible schedule under the declared cap.

Table 1 reports ordinary target classifications. Both unrestricted and both hour-preserving January cases are certified infeasible in their expanded continuous relaxations. The latter pairs have identical Φ_H observations, so the obstruction persists after controlling the placement of each package by clock hour. Within-day trajectories still change. These are synthetic ordering interventions in one January week, not observed weather histories or four independent replications.

Table 1 Full-network fossil-cap outcomes for ordinary targets

| Experiment | Cases | Feasible | Infeasible | Unresolved |
| --- | --- | --- | --- | --- |
| January unrestricted interior | 2 | 0 | 2 | 0 |
| January fixed hour of day | 2 | 0 | 2 | 0 |
| January whole interior days | 5 | 1 | 0 | 4 |
| April and October continuation | 4 | 0 | 0 | 4 |
| Fresh January 8–14, fixed hour | 2 | 0 | 1 | 1 |
| Fresh January 15–21, fixed hour | 2 | 0 | 2 | 0 |

The first three rows use cap 23195 MWh. The seasonal continuation uses April cap 43131 MWh and October cap 125172 MWh, each fixed from its accepted reference by the same rule. The fresh January weeks use caps 26532 and 48319 MWh respectively. Feasible means an exact expanded binary witness; infeasible means an exact expanded separating certificate. Unresolved includes fractional LP admission followed by a time-limited MIP with no accepted binary witness. Controls are checked separately and excluded from the ordinary-case denominators. One October class-control draw was the identity and is retained as such.

For fresh-week transfer, the two lowest unused January windows, native rows 168:336 and 336:504, were selected without inspecting their target outcomes. Reference solves and exact acceptance preceded fixed cap construction. The same clock-preserving perturbation family and unchanged edge rule were then applied with seeds 26093210/11 and 26093220/21. Both new identities and both preselected clock/commitment-class controls pass full expanded binary checks; controls change 25 and 2 hours and are not redrawn. Independent replay certifies targets 26093210, 26093220 and 26093221 infeasible. Target 26093211 has an expanded continuous point with fractional states and no accepted binary incumbent after its one 300-second MIP attempt, so it remains unresolved.

This is transfer to distinct, nonoverlapping weeks of the same network and month. It does not establish seasonal, network or statistical independence. All four fresh targets remain in the denominator. Exactly four 30-second-limit LP calls ran, followed by the one conditional 300-second-limit MIP; actual totals were 20.172922 and 300.446834 seconds. No retry, substituted draw or additional reference was used. The original failed seasonal gate and later April/October nulls remain unchanged.

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

## 5 Negative findings and scope limits

Among all five nonidentity permutations of the three complete interior days, one has an accepted binary witness and four remain unresolved. Fixing the original reference commitment makes all five restricted dispatch problems exactly infeasible, but this rejects only that particular commitment; the full positive day permutation directly demonstrates why a fixed-schedule rejection cannot stand in for UC infeasibility. The completed April and October continuation yields no new certified ordinary negative, so the declared two-week seasonal replication criterion is not met. The original failed short reference attempts and later successful reference continuation remain separately recorded.

The July experiments provide an additional warning about observation definitions. All 168 exact exogenous observations in each audited raw alphabet are distinct. Their exact labelled bigrams and endpoints therefore determine the entire order by following the unique next edge. A changed sequence that preserves only endogenous commitment bigrams does not preserve these exogenous bigrams. Finite-alphabet factor-count collisions exist and are already studied in the literature [10], but that fact does not establish information loss for an injectively labelled raw dataset. No generic impossibility claim about Markov summaries follows from our pairs.

The smaller July explanation rules do not transfer uniformly: in the first January full-network service-cap pair, the fixed two-generator rule rejects zero of two targets and the fixed 48-hour dwell-support rule rejects one of two. This comparison also changes the background model from individual mean constraints without the network to an energy cap with the network. It cannot isolate a seasonal effect. The rule’s temporal support does not count the full background information required by its certificate, and no minimum-support or irreducible-infeasible-subsystem claim is made.

A subsequent zero-optimizer test reused six fixed coefficient vectors on the two known hour-preserving negatives. All six were valid but nonseparating, even before expansion. We then froze and solved the four continuous subset problems defined by the same two targets and two rules. The first rule keeps all four temporal constraint families only on the two selected combined-cycle units, together with the unchanged global static, network, cap and box background. The second keeps dwell rows whose complete state support lies in hours 60–107, together with every transition and exclusivity row and the same global background. All four admit independently checked exact expanded continuous points. Therefore no valid linear Farkas certificate using either fixed row/box template can reject these targets. This excludes every coefficient choice within those templates, not only the six initial vectors. The points are fractional and fail strict nominal membership, so this is neither binary admission nor strict feasibility. It does not exclude other supports or proofs using integrality.

No AC chronology, independent network, field intervention, fuel-input estimate, emissions benefit or operating recommendation has been validated by these experiments. Network Area 2 and a separate public UC benchmark were assessed for compatibility but not optimized; omitted storage semantics and model-adaptation costs precluded a sound external-system claim within this session. Solver wall times include soft-limit overruns on a shared host and are not performance benchmarks.

## 6 Reproducibility and research decision

Each arm records its source and protocol hashes, prepared matrix and bound archives, original and projected masks, native input bindings, prescribed cases, solver logs, returned vectors and final checks. A standalone Python standard-library verifier checks signed certificates and exact binary witnesses without NumPy, SciPy or a solver, with 35 adversarial fixtures. One separately closed run from a fresh directory checked a declared subset of the fourth delivery archive: five negatives, ten original-mask binary positive points, one additional identity check, a continuous diagnostic, six nonseparating vectors and three objective lower bounds with two energy-difference intervals. All passed in about 59.57 seconds without optimizer or network calls; artifact hashes stayed unchanged. This is relocation on the same host, not a second-machine test or full reassembly from native data. A portable wrapper and the separately attributed native source-data addendum accompany the new delivery.

The strongest current contribution is the explicit mismatch between clock-conditioned observations and a verified chronological verdict, transferred to two further January weeks and now accompanied by strictly positive optimal-energy differences for all six hour-preserving targets. Exact positive and negative evidence, the failure of two fixed linear-proof templates and retained nulls make the benchmark inspectable. Priority for a broadly new method remains unestablished. A submission should distinguish temporal transfer within one network and month from external validation; the evidence does not establish a new aggregation algorithm or journal readiness.

## Data and code availability

RTS-GMLC source data were provided by the U.S. Department of Energy (DOE), the National Renewable Energy Laboratory (NREL) and Alliance for Sustainable Energy, LLC (ALLIANCE). Their data-use notice and attribution accompany redistributed source-data copies. This acknowledgment does not imply endorsement.

Verified experimental source, protocols and results are published on the codex/temporal-information branch of the project GitHub repository. Evidence for the completed experiments in this note is fixed at commit 8abc5f3df438fe3a54e35aa06c892978adcd0537, independently read back after publication. The separate private Google Drive research folder contains delivery ZIPs and Arabic guides. Each delivery has file SHA256 manifests; uploaded filenames, byte counts, destination and sharing are verified separately. The available Drive metadata does not expose a remote content checksum.

The existing Zenodo record DOI 10.5281/zenodo.22976152 documents the frozen V8 reproducibility release. It does not archive all new experiments in this note and must not be cited as if it did. Frozen V8/V8R1 manuscripts and releases were not replaced. The new materials include original reading notes and citations, not subscription full texts. Some original experiment manifests contain host-specific paths; the standalone verifier supports explicit path-prefix remapping without altering expected hashes.

[Experimental GitHub branch](https://github.com/shaikhamalkawi-ux/Decision-Stability-Certificates-for-Power-System-Operating-States-/tree/codex/temporal-information)

[Google Drive research folder](https://drive.google.com/drive/folders/1cwdmcpJCPQC5sTdopQtQWi4sJpFdAChw)

## References

[1] B. Bahl, T. Söhler, M. Hennen and A. Bardow. Typical Periods for Two-Stage Synthesis by Time-Series Aggregation with Bounded Error in Objective Function. Frontiers in Energy Research 5, article 35, 2018. [doi.org/10.3389/fenrg.2017.00035](https://doi.org/10.3389/fenrg.2017.00035)

[2] N. Baumgärtner, B. Bahl, M. Hennen and A. Bardow. RiSES3: Rigorous Synthesis of Energy Supply and Storage Systems via time-series relaxation and aggregation. Computers and Chemical Engineering 127, 127–139, 2019. [doi.org/10.1016/j.compchemeng.2019.02.006](https://doi.org/10.1016/j.compchemeng.2019.02.006)

[3] F. C. A. Auer, R. Gaugl, T. Klatzer, D. A. Tejada-Arango and S. Wogrin. Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices. arXiv:2510.18555v2, revised 15 July 2026. Preprint. [arxiv.org/abs/2510.18555v2](https://arxiv.org/abs/2510.18555v2)

[4] J. H. Merrick, J. E. T. Bistline and G. J. Blanford. On representation of energy storage in electricity planning models. arXiv:2105.03707v2, 31 May 2021. Author preprint. [arxiv.org/abs/2105.03707v2](https://arxiv.org/abs/2105.03707v2)

[5] S. Gonzato, K. Bruninx and E. Delarue. Long term storage in generation expansion planning models with a reduced temporal scope. Applied Energy 298, 117168, 2021. [doi.org/10.1016/j.apenergy.2021.117168](https://doi.org/10.1016/j.apenergy.2021.117168)

[6] A. Neumaier and O. Shcherbina. Safe bounds in linear and mixed-integer linear programming. Mathematical Programming 99, 283–296, 2004. [doi.org/10.1007/s10107-003-0433-3](https://doi.org/10.1007/s10107-003-0433-3)

[7] K. K. H. Cheung, A. Gleixner and D. E. Steffy. Verifying Integer Programming Results. IPCO 2017, LNCS 10328, 148–160. [doi.org/10.1007/978-3-319-59250-3_13](https://doi.org/10.1007/978-3-319-59250-3_13)

[8] C. Barrows et al. The IEEE Reliability Test System: A Proposed 2019 Update. IEEE Transactions on Power Systems 35(1), 119–127, 2020. [doi.org/10.1109/TPWRS.2019.2925557](https://doi.org/10.1109/TPWRS.2019.2925557)

[9] B. Knueven, J. Ostrowski and J.-P. Watson. On Mixed-Integer Programming Formulations for the Unit Commitment Problem. INFORMS Journal on Computing 32(4), 857–876, 2020. [doi.org/10.1287/ijoc.2019.0944](https://doi.org/10.1287/ijoc.2019.0944)

[10] A. Saarela. Separating the Words of a Language by Counting Factors. Fundamenta Informaticae 180(4), 375–393, 2021. [doi.org/10.3233/FI-2021-2047](https://doi.org/10.3233/FI-2021-2047)
