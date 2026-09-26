# Prior art for exact postprocessing and safe objective bounds

Primary sources checked on 26 September 2026 UTC. These original reading notes
supplement the chronology/aggregation review. No article fulltext is redistributed.

Neumaier and Shcherbina, **Safe bounds in linear and mixed-integer linear
programming**, Mathematical Programming 99, 283–296 (2004),
[DOI 10.1007/s10107-003-0433-3](https://link.springer.com/article/10.1007/s10107-003-0433-3),
already establish verified bounds and infeasibility safeguards from numerical LP
computations using finite variable bounds and reliable arithmetic. Publisher
metadata and abstract were read; the subscription body was not obtained. The
publisher distinguishes online publication in May 2003 from the March 2004 issue.

Jansson, **Rigorous Lower and Upper Bounds in Linear Programming**, SIAM Journal
on Optimization 14(3), 914–935 (2004),
[DOI 10.1137/S1052623402416839](https://epubs.siam.org/doi/10.1137/S1052623402416839),
also predates the present objective-bound checking. The author institution's
[repository record](https://tore.tuhh.de/entities/publication/54a09f8e-7fb5-4841-a492-145d986334c4)
describes rigorous objective enclosures for exact or interval input and finite
simple bounds. Reading coverage here is metadata/abstract, not the full body.

Cook, Koch, Steffy and Wolter, **An Exact Rational Mixed-Integer Programming
Solver**, IPCO 2011, LNCS 6655, 104–116,
[DOI 10.1007/978-3-642-20807-2_9](https://link.springer.com/chapter/10.1007/978-3-642-20807-2_9).
The [author-hosted November 2010 manuscript](https://www.math.uwaterloo.ca/~bico/papers/exactmip_bb_short.pdf)
was read in its introduction, hybrid-computation discussion and indexed
finite-box dual-correction passage. It explicitly uses approximate multipliers
to construct valid bounds through variable-bound corrections and credits earlier
safe-bounding work. Its rational/native-number distinctions are directly relevant
to avoiding claims of nominal feasibility from tolerance-only primal vectors.
The 2013 journal extension has a different title and DOI; it is not substituted
for the manuscript actually read here.

Hoen and Gleixner, **Analyzing the Numerical Correctness of Branch-and-Bound
Decisions for Mixed-Integer Programming**, CPAIOR 2025, LNCS 15763, 35–50,
[DOI 10.1007/978-3-031-95976-9_3](https://link.springer.com/chapter/10.1007/978-3-031-95976-9_3).
The [public author preprint](https://optimization-online.org/wp-content/uploads/2025/02/Analyzing_the_numerical_correctness_of_B_B_decisions_for_MIP-1.pdf)
was read at Sections 2.2–2.3 and the conclusion; publication details were checked
against the [author institution](https://www.htw-berlin.de/forschung/online-forschungskatalog/publikationen/publikation/?eid=16600).
It distinguishes different erroneous solver decisions and combines safe bounds,
rational reconstruction, exact basis factorization and exact LP solving for
postprocessing. It also discusses fixing integer assignments for exact primal
verification. These ideas therefore cannot be presented as new methods here.

For the present study, the signed-dual plus finite-box residual expression,
exact rational Farkas replay, and independent saved-point checking are established
verification techniques. Our uniform-bound expansion formula follows directly
from those inequalities. The scientifically assessable new content must be the
specific paired chronology instances, their verified energy intervals, controls,
transfer failures and reproducible evidence. This search supports an overlap
assessment; it does not prove exhaustive absence of a prior identical benchmark.
