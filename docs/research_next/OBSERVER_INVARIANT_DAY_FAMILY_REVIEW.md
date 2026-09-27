# Observer-invariant day family: independent source/theory review

27 September 2026. Source/theory only: no scientific arrays evaluated, clustering, optimizer, new case, objective enumeration or old proof replay. Reviewed proposal SHA256 `c29265224b36e671ae5652a638fbb25ec05d24e2226dc52dcc7cc3ed980e31b1`.

**Verdict:** the conditional equivariance argument is sound for an exact, fully specified observation map satisfying all its hypotheses. A bounded exact audit of the saved k-medoids problem is worthwhile only as an upgrade from numerical optimal-status evidence to an exact coefficient-level certificate. It does not by itself prove authentic-observer invariance across an unobserved family. For the currently protected seven-day instances, all six interior-day orders have already been observed, so it adds no new input-case coverage or empirical extremizer.

## What the conditional statement must mean

If day-feature preprocessing commutes with complete-day permutations, the clustering partition is uniquely determined up to labels, and the **complete consumed representative tables** are uniquely determined for each cluster, then exchanging days within their original cluster preserves the positioned cluster-label sequence. The same simultaneous RP relabeling preserves Hindex, counts, weights and circular transition matrices. This is the proposed elementary implication.

Two qualifications are necessary. First, mathematical objective uniqueness concerns an ideal optimum; a floating-point solver reporting Optimal does not prove that every future call returns that optimum. A statement about the actual executable requires verified returned-optimum selection or a sound numerical-error/margin argument. Second, uniqueness of a96-dimensional aggregate feature vector is insufficient: Auer copies full selected nodal-demand and named-generator tables. Equal aggregate features can conceal different consumed tables. Benign ties can be allowed if **every** permitted choice produces the same complete observation, but that is an additional check, not automatic uniqueness.

## What the35-center enumeration covers

The pinned TSAM2.3.9 `_setup_k_medoids` has49binary variables, seven client-assignment equalities, one diagonal-sum equality selecting three centers, and49constraints `z[i,j] <= z[i,i]`. The comment referring to population constraints does not correspond to additional constraints in this implementation. Thus all `choose(7,3)=35` center sets exhaust its center choices.

However selected centers are **forced to self-assign**: `z[j,j]=1` already consumes that client's assignment equality. For a selected set `S`, the exact optimum is

`V(S) = sum(j in S) d[j,j] + sum(j not in S) min(i in S) d[i,j]`.

Use the actual saved directed coefficient entries and do not assume symmetry or silently replace diagonal values. The formula equals the saved Pyomo objective; it does not replace Euclidean distances by squared distances. Each selected set has four remaining clients, so at most `3^4=81` complete assignments;35sets cover2,835 feasible binary assignments. Minimum-cost assignment ties must all be retained. Uniqueness of a center set alone does not establish assignment or partition uniqueness; conversely different optimal center sets may induce the same partition. The relevant partition comparison ignores only cluster labels.

The saved `solver_input.json` contains the7×7 binary64 distance table, and `solver_result.json` the returned assignment. Treating each finite coefficient as its exact dyadic value permits an exact objective and gap comparison without another optimizer. This can genuinely strengthen one frozen problem's numerical-status evidence. It does not establish equality with the mathematical unrounded Euclidean objective or validate an unobserved run's coefficients.

## Actual preprocessing and post-clustering obstacles

Read source: author `Utilities._extract_scenario_data`, `_prepare_aggregated_data`, `_run_kmedoids_clustering`, `_build_representative_periods`, `_build_scenario_weights_and_indices`; `CaseStudy.get_rpTransitionMatrices`; TSAM preprocessing, k-medoids routing and medoid representation; and the installed scikit-learn Euclidean distance path. No author or scientific module was imported in this review.

The configured author path forms hourly aggregated features, including its declared demand multiplicities; sorts by hour; and uses per-column MinMaxScaler followed by complete24-hour vectors. `sameMean=False`, no rescaling, no extreme-period augmentation, no segmentation and a complete168-hour input remove several possible cross-day operations. The generated calendar supplies indexing, not a calendar feature. This supports the structural equivariance hypothesis. It does not prove bitwise permutation equivariance of every pandas group reduction, BLAS product and floating summation. Such a claim needs bound/ordering analysis or explicit coefficient-transport checks, with signed-zero policy retained.

Most importantly, `aggregatePeriods` does **not** preserve the solver's selected centers as the final representatives. `medoidRepresentation` recomputes within-cluster Euclidean distances, sums each column, and uses first-index `argmin`. In an exact symmetric metric, any cluster of two distinct members has two equal medoid costs. This is a structural reason the proposed uniqueness condition can fail; no claim is made here that an actual saved cluster has size two. First-index tie-breaking is positional and need not commute with within-cluster day permutations. Floating summation can also break ideal ties or alter a very small strict gap.

The post-medoid distance table is computed on a cluster-sized array, whereas the archived solver table was computed on all seven days. An exact audit must not silently substitute its submatrix for the actually recomputed table. The code recomputes squared norms and dot products, clamps negative rounded squared distances, sets self-distances to zero and takes square roots. Equality of mathematical distances does not automatically establish equality of these rounded execution paths. The closed harness saved normalized daily profiles and final selected indices, but did not separately archive each post-medoid distance/sum array. Certifying that stage would require a separately specified provenance/error/operation audit; ordinary exact summation of the global saved distances would not certify the author's `np.sum` decision.

Finally, the author's representative builder copies full raw selected tables using final medoid day positions; its transition method consumes the full positioned Hindex and adds the last-to-first transition. Once those selected tables and Hindex truly agree under one map, the remaining configured observation follows. Provenance day IDs themselves need not agree.

## Admission recommendation

**Conditional GO for a small saved-objective certificate audit**, if the parent wants to close the numerical-optimality limitation: freeze the three identity inputs and their original7×7 coefficients/assignments, enumerate all35center sets with all assignment ties, report exact optimal costs/gaps and partition multiplicity, and compare every returned assignment with that optimum. No new solver is needed. Retain any failure or tie, and label the conclusion “exact optimum/uniqueness for the saved coefficient problem.” This would be new verification evidence, not new empirical observer coverage or a new algorithm.

**NO-GO for an automatic fiber-preservation claim from that audit alone.** A further claim needs the full-table tie condition, post-medoid selection proof, numerical preprocessing/solver equivariance, and all consumed-output conditions above. If these cannot be established at reasonable cost, the already verified six-order observation table is the appropriate evidence. Do not downgrade the observation to aggregate features or omit Hindex to manufacture invariance.

For a future larger case with more movable days, a proved invariant family could provide additional coverage without evaluating every order. Its fixed-ray maximization would then be classical day-assignment optimization within clusters, conditional on unchanged UC coefficients and endpoint locality. This review selects no larger case and makes no claim about full-fiber completeness, a new chronology mechanism, novelty or operational feasibility. The native48-hour dwell assumptions remain unchanged; the author's24-hour operational-reference clipping is still a separate comparator limitation.

## Source identity

Author revisions remain main commit `ce97428aa225037dcbcd848889ef55f3b67c17ba` and InOutModule gitlink `8b1f53a75d152645e5ff8c7d5f417befaf316da5`; the inspected files are the isolated licensed copies used by the closed experiments. TSAM is the previously hash-verified2.3.9wheel; scikit-learn is the recorded1.9.1environment variant. Selected source hashes:

- `Utilities.py`: `f9d6b69fc319ccd51c1e2cffa6ddc6f120e5eab457e451849331f914ce5984f2`.
- `CaseStudy.py`: `dccce27eaa9db4dbeda6e71224e7019da503d654c9613ed481ed7a6220f26663`.
- `k_medoids_exact.py`: `096e812d057679362d3310e6a3defeea16351e58f172f90f56b2f80d03cde484`.
- `representations.py`: `d8d2f5c1a9c1846ade09e27c8e1d1a35d231d39617132c8c2663005454b9f93e`.
- `periodAggregation.py`: `87d082d3a8c12cdcb26854cc4729c650c37cedf387dcd75212e83a11c4ec2860`.
- `timeseriesaggregation.py`: `51db23b0ff1103099d047ab4c09c01d877d46a2e77f0d6114242b7d5347d7413`.
- Installed sklearn `metrics/pairwise.py`: `e937cf49dd10c932009938d656b86f1dafe80a916605cd287dfb0f85a751adf9`.

No closed source, result, observation denominator or prior claim was edited.
