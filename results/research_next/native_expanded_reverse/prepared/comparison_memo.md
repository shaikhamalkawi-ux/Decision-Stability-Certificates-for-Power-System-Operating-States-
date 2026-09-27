# Independent actual reverse-target nominal comparison

**PASS: exact nominal projected correspondence is independently established for the fixed `reverse_4_19__native_penalized` target.** This does not establish equality of uniformly expanded models or transfer any old expanded point, dual, objective bound or signed difference.

The independently authored identity checker `6390b0f51a9385860ff28683c2610008173ea0fcb8b1ed40b686cbbfd7c06d3c` was adapted only for this target's expected-series order and frozen provenance/output schema. The saved source diff shows those changes. Its mathematical routines remain unchanged: binary64 is decoded from sign/exponent/mantissa integers, and rows are compared as exact upper-halfspace-pair multisets, including duplicate multiplicity. No producer comparator was imported or rerun. The original target's model rows/columns were never permuted; only expected parsed load/reserve/penalty were reordered once.

The single independent arithmetic replay verified:

- All 2,712 native semantic aliases, the 2,472 retained columns and all 960 exact binary declarations.
- Every native affine coefficient, constant and endpoint: 4,384 rows with multiplicity, 3,422 distinct signatures and 15,919 raw term occurrences. The complete native and adapter multisets are equal.
- Every retained objective coefficient, zero objective constant and minimization sense. This is objective-function correspondence, not evaluation of an incumbent or proof of optimality.
- All variable domains. Exactly 240 unused nonnegative mfg variables admit the zero lift and occur in no active row or objective. The 480 Q/R finite-box extensions follow from each actual nominal headroom row, nonnegative Q/R and exact binary U; all 24 N extensions follow from actual N=0 rows. There are no other domain differences.
- Exact parsed input agreement for all ten top-level fields and all 18 fields of each of ten units, retaining native default read-and-repair and the explicit single-scenario convention.

All 456 original bindings, 12 captured copies and four producer output files remained unchanged. The producer phase was 11.865268199995626 seconds; the independent replay took 2.799055400013458 seconds. Zero Julia/model builds, optimizer calls, candidate/dual permutations or objective-value calculations occurred in this review. No discrepancies were found.

Stable review source SHA256: `be7240f53f551282625e770307e0d7e6f48ef34057b4f465ee9fe6e40c3e5099`. Report `INDEPENDENT_POSTRUN_REVIEW.json`: `bb44ef305c468a9e334a0a8e5ee63fc84ac8e87aec057c8e05e21ad07a2f8cc6`. Source adaptation diff: `68621cbfffbe9d220df1adde5ebb5af54eb0430b05dab8d2ab1935fe4fb3dd68`. The report binds all four untouched producer outputs and the exact row-multiset signature.

The supported conclusion concerns the nominal mathematical feasible sets after projecting unused mfg variables, for this one actual native export and its fixed input. Expanded-native containment or bounds require their own target-specific proof and point/dual replay. No general implementation equivalence, hard-service guarantee, regret or new-method claim follows.
