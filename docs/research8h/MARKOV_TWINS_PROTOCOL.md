# Prospective commitment-transition-preserving twin test

Written 2026-09-26 before generating any Euler permutations or inspecting their
outcomes. This follows the initial pilot and the primary-literature review of
Auer, Tejada-Arango and Wogrin (2025), https://arxiv.org/abs/2510.18555.
That paper's representative-period states differ from the endogenous commitment
states below; this experiment is not a direct test of its particular formulation.

Question: can the same snapshot-package multiset, full generator-energy vector
and exact one-step transition counts of the entire 24-unit commitment vector
still accompany opposite chronological mean-admission verdicts?

Use the verified repaired July network witness, its unchanged full 41-unit
means, and the same free initial and clipped terminal dwell conventions. Keep
hours0--47 and120--167 fixed. Define each state as the exact 24-bit thermal
commitment vector from this witness, with no clustering or fitted threshold.

For each interior hour t=48..119, make one uniquely labeled directed edge with
tail U[t], head U[t+1], and payload equal to the entire original hour-t package.
Use randomized Hierholzer traversal from U[48] to U[120], shuffling outgoing
edge lists with NumPy PCG64. The resulting 72 edge labels determine the reordered
interior packages. This preserves all internal directed transition counts and
the two boundary transition pairs, as well as the full 168-hour package multiset.

Fixed seeds: 260926100 through260926115 inclusive (16 cases). All are retained;
do not replace duplicate sequences or uninformative outcomes. The traversal
does not sample uniformly from Euler trails. Report distinct raw orders,
distinct commitment sequences, and direct seed residence violations separately.

For every case, verify exact global commitment-pair counts, generator means,
inverse restoration of full nodal/availability/dispatch/status packages, static
network feasibility and fixed edges. If the reordered seed remains a valid
chronological network witness, label it ADMITTED_NETWORK_WITNESS. A failed
replay alone never establishes infeasibility.

Run the same continuous chronology relaxation for all16 cases, with a30-second
limit per case, one thread and no presolve. Check any separating ray by exact
rational arithmetic on the archived binary64 matrices and require the existing
outward1e-5 bound robustness check. Positive LP status means only relaxation
admission. A negative LP certificate alongside a verified seed witness is an
error that must be investigated. Save unknowns and time limits explicitly.

There is no tuning or holdout claim here: all16 are a prospective fixed sample
from one previously studied week. Matching the full commitment transition matrix
does not match exogenous representative-period transitions or higher-order
windows. A positive counterexample would show insufficiency of this specific
summary, not novelty of the general statement that first-order statistics miss
longer memory. If all cases are feasible or unresolved, report that outcome.
