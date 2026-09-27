# Independent exact native projection review

PASS, completed once at 2026-09-27 11:35:31 UTC in 0.6617616 seconds. This independently written standard-library reviewer did not import or rerun the producer comparator. It decoded native binary64 hexadecimal values by integer sign, mantissa and exponent arithmetic, and represented each affine row as its exact pair of upper-bound halfspaces. This gives a different implementation of sign-invariant row comparison, retaining duplicate-row multiplicity and every finite endpoint.

The check establishes exact nominal projection equivalence for the single frozen identity/native-penalized OR-LIB10 fixture and the saved official UnitCommitment native export:

- All 2,712 native variables have unique complete semantic aliases: 2,472 retained variables and 240 `mfg` auxiliaries. The complete 960-variable binary declaration agrees.
- Every one of the 4,384 affine rows agrees as a multiset, including duplicates (3,422 distinct signatures; 15,919 raw term occurrences). Constants are moved to endpoints exactly, without rescaling or tolerance.
- The complete objective agrees, including zero constant and minimization sense.
- All 240 omitted `mfg` variables have precisely a nonnegative domain and zero affine/objective support. Setting them to zero therefore lifts every retained feasible point back to the native model without changing its objective.
- The only 504 domain differences are proved redundant at the nominal endpoints. For each of 480 Q/R bounds, an actual native row gives Q+R <= width*U, with Q,R >=0 and U binary in [0,1], so each is <=width. The exact width matches the archived binary64 subtraction. For the other 24 variables, an actual native equality gives N=0. All remaining domains agree directly. Thus native points project into every added adapter box, and adapter points lift to native feasible points.
- The parsed-instance comparison was independently reconstructed separately: all ten top-level fields and all eighteen fields of each of ten uniquely named thermal units agree exactly, including histories, ramps, dwell, costs, segment data, reserve and system fields.

All sixteen admitted input descriptors were checked at entry and close; the three producer run files stayed unchanged. The producer's single admitted comparison took 1.4881442 seconds excluding the final completion-record write. Its status and detailed domain explanations agree with this independent proof. The earlier original-arm name-mapping failure remains preserved.

This is an exact statement about the archived nominal models, not about every runtime/version or every instance. It neither establishes equality of uniformly expanded native/adapter models nor transfers the old expanded cost bounds to the native model. No target-world, hard-service, network-transfer, historical author-environment, new optimization or feasibility result follows. This review made zero Julia/build/optimizer calls and changed no producer files.

Stable evidence:

- Reviewer source: `6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c`.
- Reviewer JSON: `50191cce91e6a4e8479500bfa0a1740b03d812848ee37620480b3e41ce584080`.
- Admitted manifest: `ea2a05148c0d0b23b2c59faea9f0afcfd4a3b386e6e738adb97ca1b4610ab829`.
- Producer comparison: `2ad303026121cbef1952f234c2e65eade9ac897fb669aa138a1ffcae6ffb3125`.
- Producer completion: `4d5298fd1895c18f4a062680f42a6f66e98c01578120d83c6f048f3914468773`.

The reviewer uses the same ordinary mathematical definition of exact rational linear constraints; its independent implementation does not imply independence from Python's arithmetic/runtime.
