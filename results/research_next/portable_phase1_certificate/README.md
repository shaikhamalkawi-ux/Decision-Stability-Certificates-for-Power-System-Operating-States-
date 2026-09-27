# Portable exact verification of one fixed-schedule rejection

This folder is self-contained for checking one archived matrix certificate. It needs Python 3.10 or later and its standard library only. It does not need a solver, NumPy, SciPy, the research repository, or an account. Obtain the separately published SHA256 of MANIFEST.json from the delivery verification record, then run from this folder:

`python -I -S verify.py --bundle . --manifest-sha256 PUBLISHED_MANIFEST_SHA256`

Do not substitute a newly computed hash for the externally published hash when checking authenticity. The manifest binds every required file, including the verifier and the reviewed CSR/NPZ decoder. The verifier reconstructs the complete signed row combination and all original residual coefficients using exact rational arithmetic on the supplied binary64 values. The 12,096 fixed binary coordinates are exact zero or one. Continuous rows and bounds use the explicit uniform expansion tau = Fraction.from_float(1e-5); this expansion defines the checked mathematical model, not a physical uncertainty claim.

The archived model contains 69,362 rows and 33,936 columns. The result establishes a globally necessary state inequality and rejects this one supplied schedule. Its positive weighted proof margin is not a quantity in MWh or a cost difference. It does not exclude every possible common schedule. The certificate's selected rows are a static network condition at one hour, not a ramp or minimum-duration mechanism.

This check authenticates and recomputes the supplied matrix proof. It does not rebuild a physical network from original data, replay the solver or backend, prove that the source matrix is a complete real-world model, verify all additional diagnostic fields in the archived producer certificate, or repeat the historical fractional feasible-control check. Those broader provenance and independent-review records are available separately in the research repository. Hash integrity requires an independently trusted published digest.

A clean copied-folder test on the same Windows host is reported separately. It is a portability smoke test, not second-machine replication. No scientific result is newly discovered by repeating this certificate calculation.
