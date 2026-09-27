# Regret prior art: direct 2023 overlap

27 September 2026. Primary-source reading only; no experiment or change to closed evidence.

**Verdict:** minimax regret for energy time-series aggregation, and bounds on its resulting objective loss, are already explicit prior art. Our two-world criterion is a specialization of that classical loss structure, not a new regret method. Its possible contribution remains a certified result about a complete, version-bound observation collision and a declared UC decision contract.

## Source and actual reading

Ryohei Yokoyama, Yuji Shinano and Tetsuya Wakui (2023), “An effective approach for deriving and evaluating approximate optimal design solutions of energy supply systems by time series aggregation,” Frontiers in Energy Research 11:1128681, published 10 July 2023, DOI [10.3389/fenrg.2023.1128681](https://doi.org/10.3389/fenrg.2023.1128681).

Read the publisher PDF directly: §2 p.3; §§4.1–4.4 pp.4–6; §§5.1.1–5.2 pp.6–7, including Figure 3. Equations on pp.5–6 were additionally inspected visually. §6.1 p.7 was checked only for implementation context. This is selected-body reading, not a whole-paper, supplement, source-code or reproduction claim. The initial HTML/PDF web fetches intermittently timed out; the [official alternate CDN PDF](https://public-pages-files-2025.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2023.1128681/pdf) was subsequently downloaded privately and read. PDF SHA256: 8e9ddff95e9c3f9f86030ab1e4a6788c7746f046411596718a038e0f2e85b299. No full text is redistributed.

## Formulation and algorithm inspected

In compressed notation, let V(x,y)=min_z f(x,y,z). Their Eqs.(5)–(8) give fixed-design regret and its worst-demand bound:

R*(x̄)=V(x̄,Y)−min_x V(x,Y),

R̃(x̄)=max_y[V(x̄,y)−min_x V(x,y)],

0≤R*≤R̃ and V(x̄,Y)−R̃≤F*≤V(x̄,Y).

Equations (9)–(12) select within-cluster demand candidates and common cluster operations; Eq.(14) minimizes the maximum regret over x̄. Sections 5.1.1–5.1.2 alternate lower/upper bounds, candidate demands and integer operating patterns; continuous subproblems use duality. Section 5.2 applies hierarchical MILP. Section 4.4 handles service infeasibility through a prior penalty objective, with its concrete formulation omitted. Section 2 excludes storage/transients; §4.1 exploits independent per-period operations. [Publisher source](https://doi.org/10.3389/fenrg.2023.1128681).

## Comparison with our proposed decision problem — inference

Substitute the common full-week commitment u for design x, one of our two raw inputs i for y, and adaptable continuous dispatch for z. The resulting min_u max_i[C_i(u)−C_i*] has exactly the same nested regret structure. Reducing the uncertainty set to two members does not create new optimization theory. Adding exact rational checks changes the strength and portability of evidence, but does not make regret or bound-driven aggregation new.

The meaningful distinctions are the question and domain. Our uncertainty set is deliberately a pair proven indistinguishable under one authentic complete observation including Hindex; the action must depend only on that observation. The benchmark allows separate informed commitments. Our model retains temporal residence restrictions and hard service, and the loss is fossil-electricity MWh. The paper optimizes a common equipment design over clustered demand candidates and treats annual cost. These differences justify an application-specific test, not a priority claim. Its per-period aggregation step must not be transplanted as a theorem for chronological UC: our proof would work directly on the full joint worlds and require independent positive controls.

The proposed near-optimal-set intersection test remains logically discriminating, but its burden is now clearer. A verified common action with W_i−L_i≤epsilon refutes a loss exceeding epsilon for the pair. Exact rejection at the looser U_i+epsilon thresholds, with finite individual witnesses, proves that unavoidable loss. A fixed anchor's failure, different individual optima, a timeout, or an observation collision alone proves neither. A common capped witness would settle the cap question positively without settling regret.

**Do not claim:** first use of regret to assess aggregation; a new robust/refinement algorithm; an impossibility result for Auer's actual operating policy; or a guarantee over its entire observation fiber. A paper-worthy stronger result would need a nontrivial certified loss for the precisely stated information/action contract, plus controls and a fair prior-art comparison. Current shared-binary UNKNOWN does not supply it.

This note adds one isolated reading record. It does not revise the historical closed 40-record count or claim an exhaustive novelty search. Earlier 2018/2021 papers referenced by this source were not newly read here.
