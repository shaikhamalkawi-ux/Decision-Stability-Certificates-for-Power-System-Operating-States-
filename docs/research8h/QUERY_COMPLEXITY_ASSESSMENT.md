# Positioned-query complexity of repeated UC twins

Assessment date: 2026-09-27 Dubai (2026-09-26 UTC). This is a mathematical application corollary, not a new query-complexity theorem. No numerical solve or experiment was run for this assessment. The independent checker reviewed the copy-adversary argument, boundary assumptions and one-based distinguishing position, and reported no issue under the explicit promise/oracle model.

**Verdict: valid under the stated oracle and instance promise.** The family realizes the classical OR decision problem inside the validated UC construction. Deterministic exact decision requires exactly \(J\) hourly position queries in the worst case. A supplied negative witness can be checked with one such query; a positive observation certificate needs \(J\). These are promise-relative query counts, not Farkas support sizes, IIS cardinalities, memory bounds, or general physical-data requirements.

## 1. Public information, hidden input and oracle

Fix integers \(k,r,J\ge1\) with \(k\le4r\), and a thermal minimum-output fraction \(a\in(0,1)\). Use the two known equal-length words from NOVELTY_DECISION.md:

\[
A_m=O(FO)^m,\quad
x=Z^kA_{2r}Z^kA_{2r}Z^k,\quad
y=Z^kA_{2r-1}Z^kA_{2r+1}Z^k.
\]

Each word has length \(L=8r+3k+2\). The complete physical hourly packages are \(Z=(0,0)\), \(F=(1,0)\), and \(O=(1,1)\), giving demand and renewable availability. Absolute timestamps and unique identifiers are not additional payload coordinates.

The plant has one thermal unit, \(a u_t\le p_t\le u_t\), minimum-up time two, minimum-down time one, initially mature off, and nonbinding ramps. Exact balance with curtailable renewable output is required; there is no storage, shedding or dumping. The terminal zero segment forces the unit off. Retain all other assumptions of the checked base construction.

The hidden input is a vector \(b\in\{0,1\}^J\), with

\[
W(b)=w_{b_1}w_{b_2}\cdots w_{b_J},\qquad w_0=x,\quad w_1=y.
\]

Copy boundaries and templates are public. Any bit pattern is allowed: “independent” means freely variable copies, not an assumed probability distribution. Public metadata consist of \(k,r,J,a,L\), plant data, the common factor-count summary \(\Phi_k\), equal external boundary strings, and the common cap

\[
E_x=4r+2ra,\qquad B=J E_x+a/2.
\]

An algorithm may adaptively request a position \(t\in\{1,\ldots,JL\}\), receiving the exact package \(W(b)_t\). One query costs one position, irrespective of computational effort between queries. Batched retrieval of \(q\) positions costs \(q\), even if implemented as one API call. Queries for global optimal energy, aggregate OR answers, hashes encoding the hidden pattern, or full trajectories are not this oracle.

The upper bound and certificate statements below use the trusted promise that the input belongs to this known family. Checking that promise from unrestricted raw data has its own cost and is not included.

## 2. Factor summaries remain identical after concatenation

For a word \(s\) of length \(\ell\le k\), let \(N_s(v)\) count its contiguous occurrences in \(v\). The validated pair satisfies \(N_s(x)=N_s(y)\). Both templates start and end with \(Z^k\).

Any length-\(\ell\) window crossing a copy seam is \(Z^\ell\). There are exactly \(\ell-1\) such windows per seam, and a window cannot cross two seams because \(L\ge k\). Consequently,

\[
N_s(W(b))
=J N_s(x)+(J-1)(\ell-1)\mathbf{1}_{\{s=Z^\ell\}}.
\]

This is independent of \(b\). All \(2^J\) instances have identical \(\Phi_k\), length \(JL\), and external prefix/suffix \(Z^k\). The repeated zero seams introduce no hidden factor-count clue.

## 3. Optimal energy is additive and implements OR

Every \(Z\) hour has zero demand. Nonnegative dispatch, exact balance and \(a>0\) force \(p_t=u_t=0\). Thus copies cannot share an on-run across a seam. Conversely, the base optimal schedules concatenate legally: each ends off, each begins with an off period, and minimum-down time is one. The checked block-energy result therefore gives

\[
E_{\min}(W(b))
=\sum_{j=1}^J E_{\min}(w_{b_j})
=J E_x+a\sum_{j=1}^J b_j.
\]

The common cap implies

\[
\mathrm{Feasible}(W(b),B)
\iff \sum_jb_j=0
\iff \neg\mathrm{OR}_J(b).
\]

This is a global energy/emissions upper-cap statement, not an exact named-unit energy target. The positive instance has a constructive concatenated schedule. A negative instance with \(h\) bad copies exceeds the cap by \(a(h-1/2)\).

## 4. Exact deterministic query complexity

**Lower bound.** Follow the algorithm on the all-\(x\) instance. If it stops after fewer than \(J\) queries, some copy has never been queried. Change only that copy to \(y\). All public information and every answer already received remain identical, but feasibility changes. The same deterministic transcript cannot correctly label both inputs. Hence at least \(J\) queries are needed on the positive instance.

More precisely, every copy must receive a query at a position where \(x\) and \(y\) differ. Visiting a copy only at common positions cannot certify its type. This proves the lower bound despite adaptive query selection and unlimited computation.

**Upper bound.** In one-based within-copy indexing, the position

\[
d=k+4r
\]

contains \(F\) in \(x\) and \(Z\) in \(y\). The shorter first alternating block of \(y\) ends at \(d-1\), while \(x\) continues with \(F\). Query positions

\[
t_j=(j-1)L+d,\qquad j=1,\ldots,J.
\]

Stop and report infeasible upon the first \(Z\); otherwise report feasible after all \(J\) answers are \(F\). Thus the deterministic worst-case complexity is exactly \(J\).

With the tight parameter choice \(r=\lceil k/4\rceil\),

\[
D=J=\frac{T}{8\lceil k/4\rceil+3k+2}
\ge\frac{T}{5k+8},\qquad T=JL.
\]

This is an \(\Omega(T/k)\) lower bound on positioned queries for this restricted observation interface, with \(T\) ranging over the displayed multiples. For fixed \(k\), it grows linearly with horizon length.

The lower bound also applies to any exact deterministic algorithm for a larger instance class containing this family. The \(J\)-query upper bound need not extend to that larger class.

## 5. Certificate asymmetry, with the necessary qualification

For the known family, any infeasible word has a one-query observation certificate: give an index \(j\), and verify \(W(b)_{t_j}=Z\). This identifies one \(y\) copy. The proven baseline \(E_x\) for every other copy then gives

\[
E_{\min}(W(b))\ge (J-1)E_x+(E_x+a)>B.
\]

A positive certificate needs a distinguishing observation in every copy; otherwise an unobserved copy can be changed to \(y\). Therefore the respective minimum observation counts are \(1\) and \(J\).

These statements count verified observations. Encoding the negative witness's copy index can require \(\lceil\log_2J\rceil\) bits. Finding that index may take \(J\) queries even though checking a supplied index costs one. A small witness does not imply cheap discovery.

Most importantly, one bad copy generally does **not** exceed the whole \(J\)-copy budget by itself. The negative argument uses the family promise and lower bounds on all remaining copies. It is therefore not an unconditional one-hour physical proof, a one-row IIS, or a one-row Farkas certificate. In an explicit LP, many baseline constraints may be required to derive the remaining energy. Under unrestricted raw inputs, observing that one hour is \(Z\) need not establish anything comparable.

Example, by direct arithmetic: \(k=3,r=1,a=1/2,J=3\) gives \(L=19\), \(E_x=5\), and \(B=15.25\). The distinguishing positions are 7, 26 and 45. Three \(x\) copies use at least 15; one \(y\) and two \(x\) copies use at least 15.5. This is an illustration, not a newly executed numerical test.

## 6. Margin and practical limits

The smallest positive slack and negative excess are both \(a/2\), independent of \(J\). Relative to \(B\), the margin is

\[
\frac{a}{2J E_x+a},
\]

which decays as \(1/J\) and, for the tight family, as \(1/(Jk)\). Repetition produces a growing query cost but not a growing smallest deficit. Capacity scaling increases the absolute margin and budget together, leaving their ratio unchanged.

Exact oracle replies and templates are assumptions. Aggregate modeling or measurement errors can accumulate across copies; an uncertainty allowance comparable to \(a/2\) can erase this separation. This corollary alone does not establish a material field-operational data burden.

The theorem also excludes the cost of preparing and verifying the public summary. If a workflow already loaded all chronological inputs to construct \(\Phi_k\), there is no basis for describing subsequent solver reasoning as avoiding that original acquisition. The result concerns an agent whose access genuinely starts at the stated restricted interface.

As noted in KGRAM_PRIOR_ART.md, exact bigrams of distinct full hourly packages can reconstruct a chronology. This repeated finite-alphabet family intentionally has many collisions. Applying its lower bound to actual data requires checking that the deployed summary/oracle admits the relevant ambiguity.

### Optional changed promise: material gap versus probabilistic testing

This paragraph changes the decision promise and cap; it is not an amendment to the main result. Promise either \(b=0^J\) or \(|b|\ge s\), with \(1\le s\le J\), and choose

\[
B_s=J E_x+a s/2.
\]

Both promised classes have margin at least \(as/2\). A deterministic exact algorithm needs and suffices with \(J-s+1\) distinguishing queries: after \(q\le J-s\) all-good answers, \(s\) unqueried copies may still be bad; any \(J-s+1\) queried copies intersect every set of \(s\) bad copies.

For \(s=\lceil\rho J\rceil\), \(0<\rho<1\), this preserves a positive relative margin as \(J\) grows, for fixed \(k\), and retains a linear deterministic bound. However, allowing error changes the problem sharply: \(q\) uniformly sampled copy queries miss all bad copies with probability at most \((1-\rho)^q\). Thus \(O(\rho^{-1}\log(1/\delta))\) samples suffice for error at most \(\delta\), independently of \(J\). This is classical promise-OR behavior, not a new randomized-query result.

## 7. Prior art and the correct interpretation

**Classical decision trees.** Harry Buhrman and Ronald de Wolf, “Complexity Measures and Decision Tree Complexity: A Survey,” *Theoretical Computer Science* 288(1), 21–43 (2002), DOI [10.1016/S0304-3975(01)00144-X](https://doi.org/10.1016/S0304-3975(01)00144-X). [Author paper](https://homepages.cwi.nl/~rdewolf/publ/qc/dectree.pdf); [institutional metadata](https://www.dare.uva.nl/id/3d767a7b-b5d0-42d6-89ae-955b8ed6329a). Inspected Sections 1–3, Boolean OR definition and deterministic/adaptive query model. The proof above is an explicit OR reduction and uses standard certificate-versus-query distinctions; it is not new query theory. Later section refetches timed out, so no broader full-text inspection is claimed.

**Counterexample-guided refinement.** Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu and Helmut Veith, “Counterexample-Guided Abstraction Refinement,” CAV 2000, LNCS 1855, 154–169, DOI [10.1007/10722167_15](https://link.springer.com/chapter/10.1007/10722167_15). [Author paper](https://www.cs.cmu.edu/~emc/papers/Conference%20Papers/Counterexample-guided%20Abstraction%20Refinement.pdf). Inspected the introduction, Section 2 and Section 3 overview. An abstract counterexample is checked against the concrete model, and spurious traces trigger refinement. That established idea does not itself count newly acquired hourly inputs; the concrete-model access must be charged separately in our oracle setting. Calling ordinary full-model certificate extraction an active acquisition algorithm would conflate these resources.

**Active queries.** Dana Angluin, “Queries and Concept Learning,” *Machine Learning* 2, 319–342 (1988), DOI [10.1007/BF00116828](https://doi.org/10.1007/BF00116828). [Primary paper at an institutional host](https://homepages.math.uic.edu/~lreyzin/papers/angluin88.pdf). Inspected Sections 1–2.3, query definitions and adversary lower bounds. The paper makes oracle choice essential: membership, equivalence and other queries have different power. Our position query concerns one fixed hidden trajectory, rather than learning an unknown concept from labeled examples. This is adjacent established methodology, not evidence for new active-learning theory. The publisher and PDF give 1988; some secondary indexes list 1987.

## 8. Recommended use and kill conditions

Use this as a short application corollary explaining why a compact infeasibility explanation does not imply equally cheap acquisition or positive certification. It supplies a precise separation between public local summaries, positioned input access, and full-model proof extraction.

Reject an expanded claim if any of the following occurs:

1. The input interface supplies an aggregate query, oracle-generated counterexample, fingerprint, ordered scan or metadata that reveals several hidden copies at one unit of the stated cost.
2. The algorithm is allowed probabilistic error but a deterministic bound is advertised without identifying that restriction.
3. Cross-copy operational constraints or altered boundary semantics destroy additivity or invalidate the displayed positive schedules.
4. The one-observation negative certificate is described without its known-family and baseline-energy assumptions.
5. Query counts are relabeled as IIS size, memory bits, solver complexity, measured sensor requirements, or savings in a workflow that already read all data.

No mathematical kill was found for the stated corollary. Its value is conceptual precision and a transparent reduction; it does not materially strengthen the claim to new foundational mathematics.
