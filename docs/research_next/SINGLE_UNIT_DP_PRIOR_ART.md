# Single-unit dynamic-programming prior art

27 September 2026. Selected-body reading, not a complete-paper review. [Guan, Pan and Zhou, arXiv:1608.00042v2](https://arxiv.org/abs/1608.00042v2), revised19October2019; [arXiv DOI](https://doi.org/10.48550/arXiv.1608.00042). No journal DOI is claimed.

The introduction and section2.1 distinguish single-generator subproblems from coupled multi-unit commitment. Their interval dynamic program handles minimum dwell and continuous economic dispatch. Section3.2 gives a state graph carrying output, status and capped status age, with ramp-compatible transitions; its linear-in-horizon complexity keeps generator parameters fixed. Section3.3, Lemma1 and Proposition6/Theorem3 derive integral extended formulations from path structure. Selected pages1–7,19–25 and the conclusion were read. This is direct precedent for any generic claim of a new dwell-state graph, unitwise dynamic programming or integral path formulation. It does not solve our coupled two-world network-and-energy-cap problem.

Our inference: changing the pending hourly capacity-cover bound to a dwell-aware unit decomposition would require an explicit coupling/lower-bound proof and a measured benefit; it could not be presented as invention of temporal dynamic programming. The current exact capacity-grid calculation is pseudopolynomial in integer nameplate capacity, a different complexity parameter. No new experiment is authorized or performed by this note.

The cumulative register is now44distinct substantive works:38selected/indexed-body readings and6limited records. This is not44complete papers. Other search hits in this lookup were not read deeply or added.
