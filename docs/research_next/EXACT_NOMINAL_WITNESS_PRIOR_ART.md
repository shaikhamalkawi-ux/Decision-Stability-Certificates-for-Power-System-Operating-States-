# Exact nominal witnesses: primary-source boundary and bounded follow-up

27 September 2026. Source/theory only; no candidate reconstruction or optimizer has run.

Gleixner and Steffy, *Linear Programming using Limited-Precision Oracles*, DOI [10.1007/s10107-019-01444-6](https://doi.org/10.1007/s10107-019-01444-6), [author report](https://optimization-online.org/wp-content/uploads/2019/12/7507.pdf), develops exact LP solution from limited-precision calculations. Selected reading covered §§1.2–1.3, 3.1–3.2, 4.2 and 6.1, not the entire paper or every proof. Basis verification solves rational systems; reconstruction instead proposes rational coordinates and checks them exactly. Their guarantees require stated oracle/convergence assumptions. Merely rounding an approximate point supplies neither a feasible point nor a reconstruction guarantee. These established methods prevent a claim that converting floating-point UC outputs into exact witnesses is itself a new algorithm.

The present identity upper is accepted only with a uniform outward expansion. Its tiny strict residual is still nonzero. A separate nominal witness would strengthen the scientific interpretation without rewriting that result. The lightweight proposal below is a single heuristic candidate construction followed by exact checking; it is not an implementation of the paper’s iterative solver or a convergence theorem.
