# Prior-art audit: temporal information and infeasibility certificates

Audit date: 26 September 2026. Worktree baseline: `7300129`. This is a bounded critical review, not a systematic-review claim or a novelty certificate. Fifteen sources are recorded in the companion CSV: fourteen with verified publication DOI metadata, plus one author-hosted supplement whose main-paper DOI and date remain unverified. Primary full-text sections were inspected for eleven entries (including one inspected by the parent through institutional access); two were assessed from indexed primary-text excerpts; two remain limited to metadata, an abstract or a scanned introduction. Each entry reports its actual reading depth.

## Assessment

The broad ideas are already established: chronological information can be lost by aggregation [L01-L06]; generator aggregation requires disaggregation conditions [L07]; inclusion-minimal infeasible subsystems and alternative-polyhedron selection are classical [L08, L11-L12]; UC feasibility cuts are established [L10, L13]; and independent rational proof checking, including recovery from floating solver output, is established [L09, L14].

The present work can therefore use these tools, but cannot honestly sell their generic combination as a new mathematical principle. The current potentially useful contribution is narrower: an explicitly defined information-equivalence class, an independently checked difference in chronological feasibility within that class, and a transparent account of which additional temporal facts resolve the ambiguity. Whether that specific contribution is sufficiently new or valuable remains open.

The strongest adverse comparisons are Auer et al. for temporal transitions, Fischetti et al. for selecting conditional small infeasible supports, and Szeider for floating-to-exact proof recovery. Their specific scope and the remaining distinctions are recorded below. A compact proof on a known instance is not evidence of a globally minimum information requirement, predictive generalization, or a new certificate algorithm.

## Claims to retain, qualify, or drop

| Proposed claim | Audit judgment | Required qualification or next evidence |
|---|---|---|
| Equal means or snapshot distributions need not preserve chronological feasibility | Defensible as an application result after witness/proof checks; broad principle established | Name the exact equivalence relation, constraints, horizon and boundaries. |
| Transition counts repair missing chronology | Known approach | Compare against L01-L02 and say exactly which transitions are retained. |
| Commitment-vector transition counts are insufficient for this instance class | Currently unproved | Need a feasible/infeasible pair with exactly equal specified counts; LP feasibility and failed replay do not establish it. |
| A few temporal atoms explain infeasibility | Potentially useful conditional diagnosis | State the uncounted fixed background and whether support is merely found, inclusion-minimal, or globally minimum. L08/L12 are direct prior art. |
| Exact rational certificates make a solver result independently checkable | Established verification method | Credit L09/L14; bind the certificate to the actual encoded matrix, bounds and semantics. |
| A minimum-memory or sufficient-information theorem | Not supported by the current experiments | Requires a precisely quantified model/data class and a lower/upper bound over all allowable summaries. |
| Practical speed or data savings | Not established by certificate size alone | Include generation, oracle and checking costs; compare with plain LP, IIS and full UC on held-out periods. |
| Operational inadequacy follows from failure of named-unit energy targets | Not generally valid | Retest a relevant service requirement with justified pooled energy, cost/emissions or dispatch tolerances. |

## Core primary sources

### L01. Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices

Felix C. A. Auer; Robert Gaugl; Thomas Klatzer; Diego A. Tejada-Arango; Sonja Wogrin. 2026 (v2); 2025 (v1). arXiv:2510.18555v2; submitted to Applied Energy. DOI: [10.48550/arXiv.2510.18555](https://doi.org/10.48550/arXiv.2510.18555). [Primary record](https://arxiv.org/abs/2510.18555); [open/full-text route](https://arxiv.org/html/2510.18555v2).

Read: Full relevant sections; v2 Sections 2, 3.1-3.3, 4.1-4.4; earlier v1 also inspected. Transition matrices, expected predecessor boundary values, and minimum-up/down windows already address chronology loss. Boundary binaries are relaxed. Approximate operational fidelity, not an exact binary-feasibility certificate. Our commitment-vector labels differ from their representative input periods.

Implication: Adversarial baseline; use latest v2 metadata and RTS-GMLC case. v2 revised 2026-07-15; title and author list changed from v1.

### L02. Enhanced Representative Days and System States Modeling for Energy Storage Investment Analysis

Diego A. Tejada-Arango; Maya Domeshek; Sonja Wogrin; Efraim Centeno. 2018. IEEE Transactions on Power Systems 33(6):6534-6544. DOI: [10.1109/TPWRS.2018.2819578](https://doi.org/10.1109/TPWRS.2018.2819578). [Primary record](https://ieeexplore.ieee.org/document/8334256/); [open/full-text route](https://arxiv.org/pdf/1810.09539).

Read: Full relevant sections; Section III-F, equations 5a-5b; Section IV. Representative-period transition counts, commitment linking, and moving-window storage chronology predate the present work. Does not establish arbitrary finite-summary sufficiency for all coupled UC feasibility questions.

Implication: Do not describe preserving transition counts or reconnecting periods as a new idea. Publisher DOI and open author preprint checked.

### L03. Time Series Aggregation for Optimization: One-Size-Fits-All?

Sonja Wogrin. 2023. IEEE Transactions on Smart Grid 14(3):2489-2492. DOI: [10.1109/TSG.2023.3242467](https://doi.org/10.1109/TSG.2023.3242467). [Primary record](https://graz.elsevierpure.com/en/publications/time-series-aggregation-for-optimization-one-size-fits-all); [open/full-text route](https://arxiv.org/pdf/2206.03186).

Read: Full relevant sections; Sections II-III and stated limitation on linking constraints. Optimization-aware aggregation and basis-oriented preservation of LP outcomes are established, beyond statistical input similarity. The displayed result excludes time-linking constraints; it is not a theorem for arbitrary coupled mixed-integer UC.

Implication: A possible extension must state exactly what temporal coupling changes; generic decision-preserving compression is insufficient. Preprint 2022; journal publication 2023.

### L04. Typical Periods for Two-Stage Synthesis by Time-Series Aggregation with Bounded Error in Objective Function

Bjorn Bahl; Theo Sohler; Maike Hennen; Andre Bardow. 2018 (online); 2017 (volume). Frontiers in Energy Research 5:35. DOI: [10.3389/fenrg.2017.00035](https://doi.org/10.3389/fenrg.2017.00035). [Primary record](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2017.00035/full); [open/full-text route](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2017.00035/full).

Read: Full relevant sections; Sections 2.2-2.4 and 3.2. Full-series feasibility checks and iterative addition of feasibility time steps already refine aggregated designs. Feasibility-time-step treatment and interperiod storage assumptions matter; does not prove minimum summary size.

Implication: Benchmark any certificate-guided refinement claim against existing feasibility-driven refinement. Published 2018-01-08 in volume labeled 2017; author diacritics normalized in CSV.

### L05. Extreme events in time series aggregation: A case study for optimal residential energy supply systems

Holger Teichgraeber; Constantin P. Lindenmeyer; Nils Baumgartner; Leander Kotzur; Detlef Stolten; Martin Robinius; Andre Bardow; Adam R. Brandt. 2020. Applied Energy 275:115223. DOI: [10.1016/j.apenergy.2020.115223](https://doi.org/10.1016/j.apenergy.2020.115223). [Primary record](https://publications.rwth-aachen.de/record/804267/); [open/full-text route](https://arxiv.org/pdf/2002.03059).

Read: Full relevant sections; Sections 2.2-2.3. Slack-based extreme-period selection uses full operational checks to repair reduced-design feasibility. Application is residential energy design; representative periods must still cover relevant storage cycles.

Implication: Do not equate discovery of one blocking period with novel minimal-information theory. Author diacritics normalized in CSV.

### L06. Time-Adaptive Unit Commitment

Salvador Pineda; Ricardo Fernandez-Blanco; Juan Miguel Morales. 2019. IEEE Transactions on Power Systems 34(5):3869-3878. DOI: [10.1109/TPWRS.2019.2903486](https://doi.org/10.1109/TPWRS.2019.2903486). [Primary record](https://portaldelainvestigacion.uma.es/documentos/66369073cbe02b47e5870e94?lang=en); [open/full-text route](https://arxiv.org/pdf/1810.00206).

Read: Full relevant sections; Section III time-adaptive UC formulation. Temporal aggregation with duration-aware ramping and minimum-up/down constraints is established. The inspected formulation uses a copperplate system; it does not settle networked exact-feasibility indistinguishability.

Implication: Any claimed new temporal representation must compare with duration-aware formulations. Preprint 2018; journal 2019.

### L07. Exploiting Identical Generators in Unit Commitment

B. Knueven; J. Ostrowski; J.-P. Watson. 2018. IEEE Transactions on Power Systems 33(4):4496-4507. DOI: [10.1109/TPWRS.2017.2783850](https://doi.org/10.1109/TPWRS.2017.2783850). [Primary record](https://www.osti.gov/servlets/purl/1421648); [open/full-text route](https://www.osti.gov/servlets/purl/1421648).

Read: Indexed primary full-text excerpts; direct PDF fetch failed; Sections II-III excerpts on ramp stealing, aggregation and disaggregation. Naive aggregation can create false flexibility; exact formulations and disaggregation conditions for identical generators are established. Identical-unit pooling is a sensitivity check, not a contribution by itself.

Implication: Keep energy pooling mathematically tied to native physical equivalence and distinguish commitment from power disaggregation. Author initials retained to avoid expanding an unverified given name.

### L08. Locating Minimal Infeasible Constraint Sets in Linear Programs

John W. Chinneck; Erik W. Dravnieks. 1991. ORSA Journal on Computing 3(2):157-168. DOI: [10.1287/ijoc.3.2.157](https://doi.org/10.1287/ijoc.3.2.157). [Primary record](https://pubsonline.informs.org/doi/10.1287/ijoc.3.2.157); [open/full-text route](https://www.sce.carleton.ca/faculty/chinneck/docs/ChinneckDravnieks.pdf).

Read: Indexed primary full-text excerpts; direct PDF fetch failed; Pages 158 and 164 excerpts; deletion/filtering and bound dependence. Deletion filters, minimal infeasible subsystems, and treatment of variable bounds have long-standing methods. Inclusion-minimal does not imply globally minimum cardinality; retained background constraints define what a small core means.

Implication: Describe current cores as conditional and inclusion-minimal only when every allowed deletion was checked. No claim to have read all pages.

### L09. Verifying Integer Programming Results

Kevin K. H. Cheung; Ambros Gleixner; Daniel E. Steffy. 2017. IPCO 2017:148-160. DOI: [10.1007/978-3-319-59250-3_13](https://doi.org/10.1007/978-3-319-59250-3_13). [Primary record](https://arxiv.org/abs/1611.08832); [open/full-text route](https://arxiv.org/pdf/1611.08832).

Read: Full relevant sections; Sections 2-4 on linear, rounding and branching derivations. Independent exact rational checking of linear/Farkas and integer-programming certificates is established by VIPR. A valid proof certifies the encoded model, not physical data accuracy or omitted constraints.

Implication: Use exact checking as verification infrastructure; do not claim the certificate format or generic proof principle is new. Preprint first posted 2016; revised 2019; related conference DOI confirmed by arXiv record.

### L10. Contingency-Constrained Unit Commitment With Intervening Time for System Adjustments

Zhaomiao Guo; Richard Li-Yang Chen; Neng Fan; Jean-Paul Watson. 2017. IEEE Transactions on Power Systems 32(4):3049-3059. DOI: [10.1109/TPWRS.2016.2612680](https://doi.org/10.1109/TPWRS.2016.2612680). [Primary record](https://experts.azregents.edu/en/publications/contingency-constrained-unit-commitment-with-intervening-time-for/); [open/full-text route](https://arxiv.org/pdf/1604.05399).

Read: Full relevant sections; Section III Benders feasibility-oracle construction. UC master decisions can be rejected by continuous recourse feasibility tests and Benders cuts. Contingency recourse differs from fixed energy-vector admissibility; the generic oracle-cut architecture is not new.

Implication: State the precise additional information certified by our diagnostic beyond a standard feasibility oracle. DOI contains 2016; journal year is 2017.

### L11. Identifying Minimally Infeasible Subsystems of Inequalities

John Gleeson; Jennifer Ryan. 1990. ORSA Journal on Computing 2(1):61-63. DOI: [10.1287/ijoc.2.1.61](https://doi.org/10.1287/ijoc.2.1.61). [Primary record](https://pubsonline.informs.org/doi/10.1287/ijoc.2.1.61); [open/full-text route](https://pubsonline.informs.org/doi/pdf/10.1287/ijoc.2.1.61).

Read: Publisher metadata and abstract only; Abstract. The abstract relates enumeration of minimally infeasible subsystems to vertices of a related polyhedron. Detailed theorem assumptions and its exact connection to our chosen certificate sparsity have not been checked.

Implication: Priority library request before claiming an original sparse-IIS or alternative-polyhedron method. Title, authors, year, pages and DOI verified directly with publisher.

### L12. A note on the selection of Benders' cuts

Matteo Fischetti; Domenico Salvagnin; Arrigo Zanette. 2010. Mathematical Programming 124:175-182. DOI: [10.1007/s10107-010-0365-7](https://doi.org/10.1007/s10107-010-0365-7). [Primary record](https://link.springer.com/article/10.1007/s10107-010-0365-7).

Read: Primary full text inspected by parent through UAEU library; Pages 175-178, Section 2, equations 5-8; parent reported direct PDF reading. Alternative-polyhedron vertices support inclusion-minimal IISs; weighted multiplier objectives seek small supports and can exclude always-active background rows. Heuristic small support is not exact minimum cardinality. This closely overlaps minimizing chronological atoms against retained static rows.

Implication: Treat conditional sparse-certificate selection as prior art unless a distinct theorem or verified benchmark improvement is demonstrated. Licensed EBSCO full text read by parent using existing institutional session; no credentials handled or copyrighted text copied.

### L13. Partitioning procedures for solving mixed-variables programming problems

J. F. Benders. 1962. Numerische Mathematik 4:238-252. DOI: [10.1007/BF01386316](https://doi.org/10.1007/BF01386316). [Primary record](https://link.springer.com/article/10.1007/BF01386316); [open/full-text route](https://www.im-uff.mat.br/puc-rio/disciplinas/2006.1/soe/arquivos/benders-numerische-mathematik-1962.pdf).

Read: Metadata and indexed introduction only; scanned full text not extracted; Introduction excerpt. Classical decomposition provenance; modern explicit UC feasibility-cut use is checked in L10. No detailed claim is based on unread scanned derivations.

Implication: Use for historical attribution only unless full body is obtained. Public university-hosted scan; no local copy stored.

### L14. VIPR Certificate Construction from Black-Box ILP Solvers

Stefan Szeider. 2026. CP 2026, LIPIcs 379, Article 52:1-52:14. DOI: [10.4230/LIPIcs.CP.2026.52](https://doi.org/10.4230/LIPIcs.CP.2026.52). [Primary record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2026.52); [open/full-text route](https://drops.dagstuhl.de/storage/00lipics/lipics-vol379-cp2026/LIPIcs.CP.2026.52/LIPIcs.CP.2026.52.pdf).

Read: Full relevant sections; Sections 2-4.4 and 5.1-5.3. Floating dual/Farkas multipliers can be rationalized, repaired with variable bounds, and independently checked; certificate size is already benchmarked. This overlaps our verification mechanism strongly. It does not supply our application-specific temporal indistinguishability experiment.

Implication: Adversarial methodological reference; any proof-compression claim needs comparison with established rationalization/repair. Publisher primary full text; DOI printed on first page. Current 2026 work, not a speculative lead.

### L15. Supplementary Material for Identifying Integer-Variable-Induced Disjointness Within Security Region Considering Unit Commitment Adjustments

Zhirou Wang; Zhengshuo Li; Tao Niu; Lin Xue. Not verified from primary supplement. Author-hosted supplement; main journal record pending verification. [Primary record](https://github.com/ZhirouVan/Security-Region-Considering-Unit-Commitment-Adjustments); [open/full-text route](https://github.com/ZhirouVan/Security-Region-Considering-Unit-Commitment-Adjustments/blob/main/Supplementary%20Material%20for%20%E2%80%9CIdentifying%20Integer-Variable-Induced%20Disjointness%20Within%20Security%20Region%20Considering%20Unit%20Commitment%20Adjustments%E2%80%9D.pdf).

Read: Entire three-page primary supplement; main paper unavailable; Appendices A-E; parsed directly from public PDF in memory. Fixed-UC Farkas exclusion halfspaces and iterative identification of infeasible regions inside continuous relaxations are presented. Main DOI/year remain unverified. No temporal-order theorem is visible; extracted inequalities have an apparent sign inconsistency requiring visual/main-paper review.

Implication: Adversarial overlap for claims about certifying holes in UC relaxations; verify main publication and distinguish chronology before citing. Title and four authors verified on PDF. Owner self-identifies as Zhirou Wang at Shandong University. Claimed but unverified main DOI: 10.1109/TPWRS.2026.3681482.

## Best next falsification test

The most useful immediate challenge to the proposed information-loss claim is the preregistered transition-preserving twin experiment. Keep the complete multiset of joint hourly packages, the energy vector and fixed first/last 48 hours; additionally preserve the exact directed transition counts of the complete 24-unit commitment vector from the verified reference witness. A feasible reference and a certified infeasible twin would show that this particular first-order summary is insufficient, even when it is much richer than individual-unit startup counts.

This statement is deliberately about the selected summary. Auer's representative input-period states are different from these endogenous commitment-vector labels. Consequently, the proposed twin construction is not a direct refutation of Auer's formulation and should not be described that way.

The Euler-trail construction should retain every labeled edge once, its tail state's hourly package, and the fixed start/end states. Validate counts across both joins as well as inside the shuffled block. Report the number of distinct state sequences separately from the number of package permutations: permuting self-loop packages can change input order without changing residence structure. A reference-witness label is additional model information, not a free summary available before solving.

At the time of this audit, the parent reports that all 16 transition-preserving twins have feasible LP relaxations, while replay of the original witness violates some residence constraints. This is preliminary parent-reported status, not an independently audited result in this document. It supplies no certified Markov counterexample. Resolve only the prespecified full-UC sample under its declared budget; record timeouts as unknown. A verified feasible alternative schedule defeats the proposed counterexample even when replay failed.

If this arm finds no counterexample, publish that negative result without converting it into a general sufficiency theorem. The next useful experiment would compare held-out weeks and model-relevant equivalence classes under a prospectively fixed design, rather than tuning bins or seeds until rejection occurs. A method claim also needs comparisons against direct LP/IIS/Benders diagnostics. In the existing ordinary-permutation pilot, the compact residence screen did not reject the four solver-infeasible cases, while their LP relaxations did: that is an adverse baseline for claims of screening utility.

## Library queue and unresolved lead

1. **Gleeson and Ryan (L11)** remains the essential verified bibliographic item whose body was not obtained. Read its exact alternative-polyhedron/IIS assumptions before claiming a new sparse certificate theorem. DOI [10.1287/ijoc.2.1.61](https://doi.org/10.1287/ijoc.2.1.61).
2. **Fischetti, Salvagnin and Zanette (L12)** was initially requested, then the parent obtained institutional full text and inspected pages 175-178. This resolves the main access gap for the weighted conditional-support overlap. No credentials were entered by this agent; no licensed full text is redistributed here.
3. **Wang et al. (L15): main-paper metadata still pending.** The [author-hosted supplement](https://github.com/ZhirouVan/Security-Region-Considering-Unit-Commitment-Adjustments) verifies the manuscript title and four authors on its first page. All three appendix pages were read. The claimed main DOI `10.1109/TPWRS.2026.3681482` still requires publisher verification. This is a substantive overlap lead, not a verified journal citation. Obtain the main text before comparing its exact assumptions or accepting its convergence argument.

## Scope and reproducibility notes

This review stores citations and original critical notes only. No copyrighted full-text corpus has been added to the repository. Bibliographic date discrepancies are explicit: L01 uses the July 2026 revision rather than its October 2025 first version; L04 has a 2017 volume label and January 2018 publication date. The source list is selective and may miss relevant literature. No novelty conclusion follows from failure to find an exact title match.

Companion data: `results/research8h/literature_certificates.csv`. Source URLs and DOI metadata were checked against publisher, author-deposited, institutional or official proceedings records where indicated. Read-depth limits are part of the result and must survive later manuscript editing.
