# Certificates for temporal observation classes: prior-art preflight

27 September 2026. Bounded primary-source assessment; three core works, selected sections only. No new optimizer, scientific computation, model change or experiment. This is not an exhaustive priority search.

**Verdict:** an independently checkable certificate adds an auditable justification for its stated proposition. Merely attaching it to a temporal summary does not add a class-wide guarantee. Robust commitment/recourse decomposition, operation-informed aggregation refinement and independent proof checking already provide the main ingredients. Our present evidence does not establish a new safe-abstraction or refinement method. A useful narrower contribution would require a precise observation-class contract and a sound, computationally useful class-wide verifier; neither priority nor that benefit follows from the present examples.

## Three primary works and actual reading depth

1. **Dimitris Bertsimas, Eugene Litvinov, Xu Andy Sun, Jinye Zhao and Tongxin Zheng, “Adaptive Robust Optimization for the Security Constrained Unit Commitment Problem,” IEEE Transactions on Power Systems 28(1):52–63 (2013), DOI [10.1109/TPWRS.2012.2205021](https://doi.org/10.1109/TPWRS.2012.2205021).** The [author-hosted paper](https://www.mit.edu/~dbertsim/papers/Robust%20Optimization/Adaptive%20Robust%20Optimization%20for%20the%20Security%20Constrained%20Unit%20Commitment%20Problem.pdf) was directly read in selected §§II–IV, printed pp53–56, including equations (1)–(10) and Theorem 1. Title, authors, issue and DOI are printed in the PDF. This is newly inspected body evidence in this bounded audit. Commitment is common across an uncertainty set; dispatch adapts to its realized member. The model includes chronological operating and network constraints, and uses dual-derived outer Benders cuts. Crucially, its inner nonconcave approximation guarantees only local optimality; slack/penalty terms ensure complete recourse. Therefore its actual algorithm must not be described here as a globally certified hard-service feasibility oracle. Theorem 1 establishes valid cuts despite approximate inner solutions. This is strong architectural overlap, with that implementation limitation retained.

2. **Adriaan P. Hilbers, David J. Brayshaw and Axel Gandy, “Reducing climate risk in energy system planning: a posteriori time series aggregation for models with storage.”** Direct selected body reading used [arXiv:2210.08351v1](https://arxiv.org/pdf/2210.08351v1), submitted 15 October 2022: §§3.1–3.3, printed pp5–7; selected discussion pp11–12; Appendix B pp14–15. The associated journal citation is Applied Energy 334 (2023), 120624, DOI [10.1016/j.apenergy.2022.120624](https://doi.org/10.1016/j.apenergy.2022.120624), from primary institutional indexed metadata; the journal body was not obtained. Publisher opening returned403 and the institutional record later denied access; no bypass or version-equivalence claim. This work was an earlier lead, but this is a new selected-body reading. The method evaluates a preliminary design on the full time series, uses operational importance to retain extreme periods, and incorporates operating variables when clustering. Chronology-linked representative days address storage. Iteration is discussed. The inspected model is continuous planning/storage, not our binary dwell formulation; the inspected sections do not establish an exact universal observation-fiber certificate. Generic operational feedback and difficult-period refinement are nevertheless already present.

3. **Kevin K. H. Cheung, Ambros Gleixner and Daniel E. Steffy, “Verifying Integer Programming Results,” IPCO 2017, LNCS10238:148–160, DOI [10.1007/978-3-319-59250-3_13](https://doi.org/10.1007/978-3-319-59250-3_13).** Selected introduction and §§2–4 were re-read in the [author preprint](https://arxiv.org/pdf/1611.08832v2). The [primary record](https://arxiv.org/abs/1611.08832) confirms v1 on27 November2016, v2 on1 January2019, and the conference citation. This is existing literature-ledger entry L09, not another newly counted paper. The certificate separates production from verification and uses rational inference rules, including linear combinations for LP claims and additional machinery for integer proofs. Consequently, exact arithmetic, portable proof objects and a small independent checker are established mechanisms. They improve trust in a specified result; they do not by themselves certify every chronology represented by a summary.

Deduplication: the historical fifteen-entry ledger already includes VIPR, Benders, chronological UC decomposition and infeasibility-certificate work. Earlier local notes cover generic CEGAR and Bahl's feasibility-step/bound-driven refinement. Those are background, not additional papers inspected here. Two selected-body readings are new in this audit; one is a revisit. No whole-paper/full-code-comprehension claim or revised global paper count is made. See the existing [refinement comparison](REFINEMENT_PRIOR_ART_LIMITS.md) for the two Bahl precedents and their explicit chronology limitations.

## The missing quantifier is the main acceptance boundary

Fix an operational model, its encoding and tolerance, static data, boundaries and service cap. Let `O(x)` be the fully specified temporal observation and `F(o) = {x : O(x) = o}` its admissible input class. Let `Y(u,x)` be continuous dispatch recourse for a commitment `u` and chronology `x`.

These propositions are distinct:

- For a specified commitment: `for every x in F(o), there exists y in Y(u,x)`.
- Existence of a common commitment: `there exists u such that, for every x in F(o), there exists y in Y(u,x)`.
- Individual unrestricted feasibility: `for every x in F(o), there exist u_x and y in Y(u_x,x)`.

One infeasible fixed-policy member refutes the first proposition for that policy. It does not refute existence of another common policy or individual feasibility. A certificate for one member plus proof of membership supplies a pointwise claim. The phrase “certificate attached to the fiber” does not change this quantifier.

The closed whole-day linkage has equal observations with opposite verification outcomes for the inherited fixed commitment. Thus that particular predicate is not constant on the observed class; an exact deterministic classifier receiving only that observation and the same anchor cannot distinguish the two outcomes. This elementary indistinguishability statement is not a new CEGAR theorem. The joint observation-plus-Hindex contrast uses a one-hour fixed-capacity shortfall at zero-based hour119, not a demonstrated dwell or intertemporal bottleneck. Unrestricted infeasibility and impossibility of every common policy remain unproved.

## A precise sufficient certificate and its limits

For the continuous relaxation, write `L(x) <= A z <= U(x)` and finite boxes `l(x) <= z <= u(x)`. Fix a rational multiplier `d`, with every selected row endpoint finite, and set `q = A^T d`. Define

`beta_d(x) = sum_i d_i [L_i(x) if d_i > 0, else U_i(x)]`,

`H_q(x) = sum_j q_j [u_j(x) if q_j > 0, else l_j(x)]`.

Zero multipliers contribute zero without selecting infinite endpoints. For uniform finite-bound widening by the exact nonnegative rational `tau`, the separation margin is

`G_d(x) = beta_d(x) - H_q(x) - tau (sum_i |d_i| + sum_j |q_j|)`.

If `G_d(x) > 0`, no point satisfies the expanded continuous system, and hence no point in its binary subset does. This is an elementary finite-box Farkas certificate, not a novelty claim. It depends on the actual archived coefficients and widening convention, not physical measurement exactness.

For a finite family where `A` and column identities are invariant and every varying selected row or column endpoint is local to one permuted hourly package, its margin can separate as `C + sum_t W(t, pi(t))`. The closed HOD stress arm checks a family of24 independent three-position assignments; exact enumeration of six local permutations gives a global optimum for **that fixed ray over that declared family**.

- `max G_d > 0` proves existence of a rejected member.
- `min G_d > 0` would prove all members rejected by this ray.
- `max G_d <= 0` proves only that this ray rejects no member. It does not establish any member's feasibility or completeness of the certificate method.

The actual later-week negative maximum margins are the third result. They must not be relabeled robust feasibility. Nor does maximizing a sufficient certificate margin maximize operational loss.

**The stress family is not the authentic Auer observation fiber.** Earlier HOD twins were distinct under that observer. Requiring the same selected profiles, weights, transition matrices and possibly Hindex can impose global clustering-dependent conditions on allowed permutations. Those conditions need not factor into the24 independent assignments. The existing assignment calculation therefore cannot certify an extremum over an Auer fiber without a separate proof of equality, inclusion with the correct direction, or a sound treatment of those coupled conditions. Similarly, fixed-matrix/local-endpoint assumptions must hold throughout a proposed family, not merely on sampled files.

## What would support a substantive method claim

The exact fixed-ray family calculation is a sound *incomplete separation test*. It is not a complete robust-feasibility oracle. To certify positive fixed-policy service over a fiber, a future method needs a checkable recourse construction or a rigorous bound on a complete worst-case feasibility problem. To reject every member using a finite collection of rays, it needs a coverage proof of `for every x, some ray has positive margin`; several individual certificates are insufficient.

A refinement method would additionally need an explicit rule, soundness under refinement, and a termination or bounded-scope statement. Its claimed advantage must survive comparison with full-series verification, standard Benders/scenario generation and retention of failing periods, counting acquisition, oracle, refinement and verification costs. The relevant new theorem burden would be a tractable **complete** class-specific verifier or a quantified guarantee/cost improvement under clearly restricted assumptions. Merely specializing known robust-decomposition logic to a temporal-summary class, or serializing its cuts for an independent checker, does not establish this burden.

The present publishable claim should therefore remain an auditable, version-bound observation/certificate test and a specified fixed-ray family calculation. A future sound fiber certificate may add a useful guarantee beyond checking one observed series, but that additional scope comes from proving its universal coverage, not from naming it proof-carrying or counterexample-guided. None of the three inspected works proves an exact-match priority kill for every possible specialized future construction; equally, no novelty is inferred from that absence.

No new numerical study is proposed or authorized by this memo. Closed artifacts, historical UNKNOWN labels and existing manuscript versions are unchanged.
