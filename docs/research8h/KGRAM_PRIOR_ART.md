# Adversarial prior-art audit of the finite-window UC construction

Audit date: 2026-09-27 Dubai (2026-09-26 UTC). Scope: eight primary papers, including targeted full-text reads and relevant reads from the same research session. This is a bounded novelty audit, not an exhaustive review. No experiment or candidate construction was changed for this audit.

**Decision:** retain the theorem as a carefully attributed, application-specific limitation result. Do not currently present it as a new principle of information theory, a new word-collision construction, or a new finite-state optimization method. The exact combination of fixed two-hour minimum-up time, a genuinely dispatchable thermal unit, identical arbitrary-order input-factor histograms, and a common resource cap was not located in these eight papers. That absence does not establish priority. Strong prior art covers its two mathematical ingredients, leaving a substantial risk that reviewers will regard the result as an elementary energy application.

## Exact object being compared

The candidate in NOVELTY_DECISION.md fixes thermal minimum-up time at two, minimum-down time at one, and dispatch bounds \(a u_t\le p_t\le u_t\), for a fixed \(0<a<1\). The complete exogenous alphabet is \(Z=(0,0)\), \(F=(1,0)\), \(O=(1,1)\), giving demand and renewable availability. There is no shedding, dumping, storage, or binding ramp constraint. A common upper bound on total thermal energy can equivalently represent emissions with a fixed positive emission rate.

The observer sees all unordered factor counts through length \(k\), matching boundary strings, horizon length, plant data, and the cap. It does not see positions or the ordered factor stream. With \(A_m=O(FO)^m\), the candidate uses

\[
x=Z^kA_{2r}Z^kA_{2r}Z^k,\qquad
y=Z^kA_{2r-1}Z^kA_{2r+1}Z^k,
\]

for \(k\le4r\), with optimal thermal energies \(4r+2ra\) and \(4r+(2r+1)a\). Their intermediate cap separates feasibility.

Plant data stay fixed across the family; the common numerical cap grows with \(r\). Therefore, the uniform statement ranges over horizons **and supplied budgets**. It is not a proof for one fixed numerical cap at every \(k\). This distinction matters when translating the construction into a language-recognition claim.

## Eight-source comparison

“Exact match” below would require the operational separation, not merely indistinguishable strings. “Component generalization” means a prior theorem or framework subsumes one ingredient, not the entire UC theorem. Bibliographic metadata were checked against the linked publisher, institutional, or arXiv records; preprints remain identified as preprints.

| Primary source and verified identifier | Text inspected | Relation to the candidate |
|---|---|---|
| **Aleksi Saarela (2021), “Separating the Words of a Language by Counting Factors.”** *Fundamenta Informaticae* 180(4), 375–393; 30 June 2021. [Publisher/DOI 10.3233/FI-2021-2047](https://journals.sagepub.com/doi/10.3233/FI-2021-2047); [author manuscript](https://amsaar.gitlab.io/articles/sa21fi.pdf). | Definitions, Lemma 5.1 and proof, Theorem 5.4. | **Strong adverse component generalization:** known word-reconstruction collisions; the operational value separation needs an additional argument. |
| **Julien Cassaigne, Juhani Karhumäki, Svetlana Puzynina, Markus A. Whiteland (2017), “k-Abelian Equivalence and Rationality.”** *Fundamenta Informaticae* 154(1–4), 65–94; online 9 August 2017. [Publisher/DOI 10.3233/FI-2017-1553](https://journals.sagepub.com/doi/10.3233/FI-2017-1553). | Publisher definition/abstract and indexed primary-manuscript excerpts of Section 3, including Example 6; full manuscript fetch failed. | **Component overlap; read limitation.** k-switching and redistribution of run lengths within factor-count classes are established. No assertion that the entire paper was inspected or that it excludes an operational specialization. |
| **Juhani Karhumäki, Aleksi Saarela, Luca Q. Zamboni (2017), “Variations of the Morse-Hedlund Theorem for k-Abelian Equivalence.”** *Acta Cybernetica* 23(1), 175–189. [Publisher/DOI 10.14232/actacyb.23.1.2017.11](https://cyber.bibl.u-szeged.hu/index.php/actcybern/article/view/3921); [full text](https://cyber.bibl.u-szeged.hu/index.php/actcybern/article/download/3921/3905). | Section 2 definitions and preliminary equivalence results, relevant early results in Section 3. | **Observation definition already known.** Exact length-\(k\) factor counts with the appropriate equal endpoints encode the shorter-factor counts. This is established k-abelian equivalence, not a new information measure. |
| **Sophie Demassey, Gilles Pesant, Louis-Martin Rousseau (2006), “A Cost-Regular Based Hybrid Column Generation Approach.”** *Constraints* 11, 315–333. [DOI 10.1007/s10601-006-9003-7](https://doi.org/10.1007/s10601-006-9003-7); [author-hosted paper](https://hanalog.ca/wp-content/uploads/2016/09/DPR_CostReg.pdf). | Sections 2, 3 and 3.1, especially weighted layered-graph representation and shortest/longest-path filtering; accessible earlier in this session, later refetch failed. | **Framework generalization of the sequential solver.** Finite-state sequencing combined with cumulative costs is established. It does not itself state that every fixed input-factor histogram fails to determine this UC optimum. |
| **Felix C. A. Auer, Robert Gaugl, Thomas Klatzer, Diego A. Tejada-Arango, Sonja Wogrin (2026 revision), “Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices.”** [arXiv 2510.18555](https://arxiv.org/abs/2510.18555), DOI 10.48550/arXiv.2510.18555; v2 dated 15 July 2026, v1 dated 21 October 2025. [Full v2](https://arxiv.org/html/2510.18555v2). | Sections 2–4.4, representative-period connections, commitment boundary treatment and correction. | **Adjacent, not refuted.** It approximates connections using representative-period transition information. Our exogenous exact-factor observation class and the pilot's endogenous commitment-state transitions must not be conflated with its model or guarantees. |
| **Sonja Wogrin (2023), “Time Series Aggregation for Optimization: One-Size-Fits-All?”** *IEEE Transactions on Smart Grid* 14(3), 2489–2492. [DOI 10.1109/TSG.2023.3242467](https://doi.org/10.1109/TSG.2023.3242467); [primary preprint](https://arxiv.org/pdf/2206.03186). | Sections II–III, LP basis-preserving aggregation and stated assumptions. | **Adjacent; generic model-aware novelty blocked.** Its structural aggregation result excludes period-linking constraints in the analyzed setting. It does not directly subsume the fixed-dwell/global-cap pair. |
| **Luca Santosuosso, Bettina Klinz, Sonja Wogrin (2025), “What Are We Clustering For? Establishing Performance Guarantees for Time Series Aggregation in Generation Expansion Planning.”** [arXiv 2510.09357v1](https://arxiv.org/abs/2510.09357), submitted 10 October 2025; DOI 10.48550/arXiv.2510.09357. [Full text](https://arxiv.org/html/2510.09357v1). | Sections 2.2–2.6, Assumption I, Lemma 1, Proposition 1 and Algorithm 1. | **Strong adjacent theory.** Contiguous, chronology-preserving aggregation gives lower bounds, followed by full-model feasible recovery and refinement. Its binaries represent investment, not hourly UC. The guarantee uses information outside our unordered observation class. The HTML journal label alone was not treated as proof of journal publication. |
| **Ruiqi Zhang, Ensieh Sharifnia, Simon H. Tindemans (2025), “Feedback Enhancement of Time Series Aggregation for Power System Expansion Planning.”** [arXiv 2510.24249v1](https://arxiv.org/abs/2510.24249), submitted 28 October 2025; DOI 10.48550/arXiv.2510.24249. [Full text](https://arxiv.org/html/2510.24249v1). | Sections II-C–II-D, Propositions 1–2, Theorem 1, Section V and Algorithm 1. | **Adjacent; generic adaptive-refinement novelty blocked.** Full operational evaluation identifies representatives to refine. The stated convex operational bound neglects inter-period coupling; the method can still retain within-period structure. It does not establish our arbitrary-\(k\) UC separation. |

## The direct collision overlap

For Saarela's Lemma 5.1, set \(w=FO\), prefix \(X=Z^kO\), separator \(Y=Z^kO\), suffix \(V=wZ^k\), and exponent \(K=2r\). The words \(Xw^KYw^{K-1}V\) and \(Xw^{K-1}Yw^KV\) are exactly our \(x,y\). For the conservative choice \(r=k\), the lemma directly supplies sufficient factor equivalence. The tighter \(k\le4r\) statement uses the candidate's explicit boundary count.

This eliminates a claim that the power-transfer collision itself is new. It does **not** automatically prove different feasibility labels: noninjective word reconstruction can lose distinctions irrelevant to a particular decision problem. [Saarela, Lemma 5.1](https://amsaar.gitlab.io/articles/sa21fi.pdf).

Metadata pitfall: the manuscript has a placeholder DOI/year; use the publisher metadata. Its editors are not paper authors.

## Does generic automata theory make the result immediate?

Not as a logical consequence of merely saying “some regular languages are not locally testable.” Exact factor counts are stronger than the thresholded/presence statistics used in common local-testability notions. For example, total symbol-count parity is already recoverable from exact one-gram counts. It would be a wrong proof to invoke total parity as automatically hidden.

The actual extra calculation is simpler and more informative. On separated alternating blocks the candidate has

\[
\begin{aligned}
E_{\min}
&=\sum_i \bigl[m_i+a\lceil m_i/2\rceil\bigr]\\
&=(1+a/2)\sum_i m_i+(a/2)\#\{i:m_i\text{ is odd}\}.
\end{aligned}
\]

The two words agree on total \(F\) count but differ in the number of odd alternating blocks. The minimum-up constraint creates a path-cover cost that reveals this hidden block parity. A small sequential state machine can track it, with a cost accumulator. This derivation is our mathematical assessment of the candidate, not a theorem attributed to any source.

Consequently, the operational separation is not literally supplied by the inspected general theorem, but combining established collisions with an elementary path-cover calculation makes it accessible. Established cost-regular optimization already supports the corresponding ordered computation. Calling this a new memory requirement would be false: a constant number of control states with numeric accumulators suffices, while an unbounded accumulator can require increasing bit length. [Demassey, Pesant and Rousseau](https://doi.org/10.1007/s10601-006-9003-7).

Likewise, the estimator lower bound is the elementary two-instance argument: identical observations force one estimate, so one error is at least half the gap. The \(\Omega(1/k)\) rate comes from the explicit construction length; it is not a new minimax technique. No upper bound, minimax equality, general bit lower bound, or impossibility for all temporal compressions has been proved.

## Consequences for a possible energy paper

The defensible insight is narrow but concrete: **choosing an unordered observation window longer than the plant's native dwell time does not, by itself, ensure exact global resource-budget feasibility.** The theorem uses complete input packages, equal endpoints, an ordinary upper cap, and a strictly positive dispatch range. These details improve the example over a loose comparison of means.

The primary mathematical novelty claim should nevertheless be reduced until stronger evidence exists. A short limitation proposition with credited combinatorial machinery is more defensible than a claimed foundational theory. The strongest remaining publication case would require a useful consequence for actual summary design or a reproducible operational failure with material margins. Repetition/capacity scaling increases absolute deficits but does not prevent the construction's relative gap shrinking as \(O(1/k)\).

The energy sources also rule out positioning “preserve chronology,” “model-aware aggregation,” “derive a bound,” or “evaluate the full model and refine” as standalone new contributions. They do not rule out a precisely delimited new result. In particular, a method that retains ordered contiguous clusters or invokes the full chronological problem lies outside the restricted observation class and is not contradicted by the candidate. [Santosuosso, Klinz and Wogrin](https://arxiv.org/html/2510.09357v1), [Zhang, Sharifnia and Tindemans](https://arxiv.org/html/2510.24249v1).

## Concrete falsification and decision

The mathematical experiment has already been assigned to an independent checker; this audit did not rerun it. The next **novelty** falsification is a close comparison against any prior result explicitly giving a finite-factor-indistinguishable pair with distinct minimum cumulative costs under fixed finite-state sequencing constraints. If such a primary theorem includes an equivalent parity/path-cover witness, classify the present theorem as an attributed UC specialization even if the precise electricity terminology is absent.

The next **practical** falsification should first test whether the observation actually admits another chronology. If every full hourly input package is distinct, its exact directed bigrams and endpoints reconstruct the original path uniquely. For such data, no nontrivial twin exists already at \(k=2\). Thus the construction is a worst-case finite-alphabet limitation, not evidence that ordinary exact continuous-input bigrams necessarily discard order. This is a direct combinatorial observation, not an empirical claim about the current data.

Only after demonstrating ambiguity should a preregistered operational test preserve full exogenous factor counts and boundary data, and seek a verified positive witness versus a certified infeasible twin under a shared service/emissions cap. Quantizing packages or using representative labels may create ambiguity, but changes the observation class and must be stated explicitly. A solver timeout is not a negative label. Failure to find a pair does not falsify the theorem; it weakens the case for operational relevance. Do not substitute the existing endogenous Markov pilot for this test.

Stop the strong-novelty pitch if the only surviving result is the above elementary construction, if its practical margin is negligible for meaningful \(k\), or if a proposed benefit disappears once the comparator is allowed a small ordered automaton. Retain the reproducible example as a transparent diagnostic and explain its limits.

**Read limitations:** Cassaigne et al. was only partially accessible. A complete review of weighted-series congruences and language separability remains outside this eight-paper audit. Search results without a matching primary theorem provide no proof of novelty. No credentials, copyrighted full-text redistribution, publication, or manuscript edits were used.
