# Prospective fixed-certificate chronology stress test

27 September 2026. Root mathematical proposal only. No new input was generated, no assignment was evaluated on scientific data, and no new feasibility or performance result is claimed. This is a possible next experiment, subordinate to the direct comparator and independent transfer work. Frozen research8h results remain unchanged.

## Useful question

Can a previously obtained, independently checkable infeasibility certificate identify a more adverse chronology within the same explicitly defined hour-of-day observation class, without repeatedly solving the dispatch model? The experiment would maximize a sufficient certificate margin, not actual UC infeasibility, actual operating cost, or a minimum-information quantity. A null margin does not establish feasibility.

This is not a proposal that dual proof reuse or assignment optimization is new. Witzig, Berthold and Heinz, *Computational aspects of infeasibility analysis in mixed integer programming*, Mathematical Programming Computation13,753–785(2021), [DOI10.1007/s12532-021-00202-0](https://link.springer.com/article/10.1007/s12532-021-00202-0), was read at Sections1,2.2.1–2.2.2 and the start of3.1 on27September2026. The paper derives constraints from dual rays and uses them to establish other local infeasibilities; it also discusses proof strengthening and sparsity. It defeats any broad claim that reusing a dual infeasibility proof is novel. The particular chronological stress-test use still needs direct prior-art comparison. Reading depth is selected body sections, not a full-paper reading.

## Conditional separability proposition

Let an encoded continuous relaxation have rows L(pi) <= A z <= U(pi) and finite column box l(pi) <= z <= u(pi). Here pi permutes complete input-hour packages. Assume A is identical throughout the declared family. Fix signed row multipliers d, and require every row endpoint selected by its sign to be finite throughout that family. Define q=A^T d, and a uniform outward expansion tau>=0 of every finite row and column endpoint. All quantities can be interpreted as exact rationals encoded by binary64 values.

The verified separation margin is

    G(pi) = sum_i d_i B_i(pi) - sum_j q_j V_j(pi)
            - tau (sum_i |d_i| + sum_j |q_j|),

where B_i=L_i for d_i>0 and B_i=U_i for d_i<0; zero multipliers contribute zero. Similarly V_j=u_j for q_j>0 and V_j=l_j for q_j<0. Any feasible point in the expanded model satisfies sum_i d_i B_i - tau||d||_1 <= q^T z <= sum_j q_j V_j + tau||q||_1. Hence G(pi)>0 certifies emptiness even before integrality is imposed.

Suppose every varying selected row or column endpoint is attached to exactly one destination hour t and depends only on its source package X_pi(t); all remaining endpoints are fixed. Because q and d are fixed, the expression groups exactly as

    G(pi) = C + sum_t W(t, pi(t)).

This is an algebraic grouping of an existing proof inequality. It requires no approximation, independence assumption on weather, or claim about the distribution of chronologies.

For the existing168-hour HOD family, fix hours0–47 and120–167. At each clock hour h, permute the three source packages at48+h,72+h,96+h among those same destinations. The family contains6^24 labeled permutations. Its fixed-certificate maximum is

    C + fixed-edge contributions
      + sum_(h=0)^23 max_(sigma in S_3)
          sum_(t in {48+h,72+h,96+h}) W(t,sigma(t)).

There are24 independent six-way exact comparisons, not6^24 model solves. Replacing max by min gives the analogous minimum. Lexicographic source-order tie breaking can select deterministic extremizers. The cardinality counts distinct physical inputs only if the relevant source packages are pairwise distinct, which must be checked separately. Maximizing G does not maximize the true UC objective or measure the fraction of infeasible family members.

## Required applicability checks before execution

The old HOD preparation checks constant native thermal bounds and invariant matrices for its sampled cases. A family-wide statement additionally needs an inspected assembly argument: the only data-dependent coefficients must be the time-constant thermal limits; topology, dwell parameters and all other coefficients stay fixed. It must be checked against the actual archived row and column ordering, not inferred from matching dimensions or one hash.

Every permuted row/column endpoint must be enumerated. Hydro lower bounds, renewable upper bounds, the independently rounded aggregate balance and all nodal balances must remain present. Fixed U/Y/Z/theta bounds, temporal-row bounds and the global fossil cap contribute to C. A varying coefficient matrix, hidden time-dependent parameter, or nonlocal bound invalidates this simple derivation; do not silently drop it or repair it after seeing outcomes.

The proposed source certificate is the already archived full-model ray for HOD target26093200. It must be frozen before any optimization over chronologies. Choice of a previously successful ray is explicitly post-label training, not an independent replication. Other January weeks can be separate fixed-ray applications after exact coefficient/coordinate and sign-domain checks, with their previously fixed native caps. Do not refit the ray on a failed target and still call it transfer.

Before any scientific run, write and review a bounded protocol and exact implementation. Preserve identity, archived target and constructive-class-control margins as controls. Independently assemble and check the chosen extremizer against the original verifier and its full input-provenance contract. Preserve nonseparating outcomes. No new UC solve is needed for the negative certificate itself; any claim about finite operating-cost increase additionally requires a verified feasible upper bound on the new chronology. Report all inherited evidence and optimizer calls separately.

## Decision criterion

Proceed only if this supplies a useful test capability beyond replaying known examples and can be compared honestly with existing aggregation/refinement work. Possible value is a compact, exact, proof-bearing stress generator inside a specified summary class. It is not presently a proven new method, a published-method counterexample, an independent-system result, or a reason to postpone the comparator indefinitely.
