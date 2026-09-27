# One official Julia raw export: producer closure

**OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON.** The fixed identity/native penalized OR-LIB case was read once and built once with the unmodified pinned UnitCommitment default formulation and no attached optimizer. There were zero optimizer calls and no repeated scientific case or build. One external Julia launch closed exit0; cold package precompilation used owned runtime subprocesses. The owned parent was absent at closure.

The measured native backend has2712variables,960ZeroOne declarations and4384scalar-affine rows. Native variable bounds, duplicate rows, objective terms and binary64 coefficient bits were exported without adding boxes, dropping mfg or normalizing coefficients. These counts alone do not establish equivalence with the archived Python encoding. A separately reviewed comparison remains pending.

Overall allocation elapsed430.988289s (2026-09-27 11:08:22.310476–11:15:33.299004UTC), import/pre-read wall time403.985525s, and native read/build/export24.003000s. Neither600s overall nor120s native allocation was exceeded. Final receipt writing is excluded from the stated elapsed sample as frozen in the protocol. This cold-host run is not a solver or build-performance benchmark.

The frozen433input bindings were unchanged at successful closure. Preparation SHA256 `348efe5b5a98baacb082b4bd11bd58974f50517b4ac02d9d2a78c7928c70bd5b`; launcher `da982ca456ed4ed83f0050c8c92c9d10460dcff46b60ef27c5233f262a601fbb`; exporter `969f7cf9780c940185ee48ba505c6b8da7a94c4bb86f700c56c4136eb8e01320`; protocol `bf16b49f9fe4ed7dd17b6a85f6653f1665676b200e6a79c86ec156d59dfc36eb`.

- External completion: `637d72f5fd632ffac7904b49571f79e34271df1b3ce0766eee8009086ac82ad4`.
- Native completion: `5328052ad2d29636013efea6fcf70e90853336cb8fceac81b4e5bbc1a4a1a75c`.
- Raw model (8630839bytes): `028ca4d025389eecd6fa91dc278b32f262a358eede3dece50d05080cc61b0160`.
- Parsed instance (401554bytes): `f47bec57919401282d15d2a091291a9489e00557f5276db4062c19d8f444e139`.

The original twelve optimization results and historical NOT_TESTED statement remain immutable. This new export uses the separately admitted two-depot environment; it retains the incomplete full-registry readback and Windows whole-package-tree verification caveats. The launcher checks actual selected metadata and18native source blobs, without claiming an adversarial filesystem or network sandbox. No explicit network or Pkg-resolution operation was requested during export. Private logs are not selected for publication by this readout. No comparator or further Julia execution occurred in producing it.
