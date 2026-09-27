# Independent exact fixed-schedule witness code review

Verdict: PASS for separately authorized preparation. No actual model preparation, transformation, basis reconstruction, synthetic rerun, solver import or optimization was performed in this review. The prepared archive and any produced rational witness still require their separate independent gates.

Reviewed in full:
- src/research8h_exact_fixed_schedule.py — SHA256 733f57ae928c72dcf063c224e728d1ad1a01d52e93c068f63147d988c16e3a77.
- src/research8h_rational_witness_check.py — SHA256 9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d.
- docs/research8h/EXACT_FIXED_SCHEDULE_WITNESS_PROTOCOL.md — SHA256 d3b3c39a62ca74e2b09cb46e456da5ab2812092eb9c9c25d548a7718e548acab.

## Transformation and basis reconstruction

Substitution retains all 16032 constant rows and checks them exactly. Actual nonzero free-column support, not labels alone, gates hourly separability. All 65 P/theta columns per hour remain, including fixed continuous columns. The aggregate replacement is the exact scaled aggregate minus all nodal equalities, with the same operation on its RHS; retaining every nodal makes this invertible. Nonzero conversion errors are archived and the numerical solver must return the submitted proposal coefficients/endpoints unchanged. Those floating proposal coefficients never define final acceptance.

For a block, basic structural columns B and nonbasic row activities I yield A[I,B] x_B = endpoint[I] − A[I,N] x_N, with |I|=|B|. Fixed nonbasic intervals have a unique value. Other lower/upper statuses require the corresponding finite endpoint; free-zero is accepted only on an unbounded interval and ambiguous nonbasic states fail. Sorted input ordering, the first available nonzero row pivot, exact Bareiss divisibility and rational back substitution are consistent. Rechecking the solved equations and all exact transformed rows protects against a bad or singular numerical basis. Failure remains unresolved and never excludes another schedule.

I directly read the immutable HiGHS 1.12 source [HEkk.cpp](https://github.com/ERGO-Code/HiGHS/blob/755a8e027a99a8d4ecf153a8dde4b2a767cdf384/highs/simplex/HEkk.cpp#L1299-L1376), including solution/basis export and basis import near lines 1181–1200. Export reverses the internal row-variable sign and status direction consistently. The code correctly uses external row statuses as original activity endpoints, with no second sign reversal.

## Acceptance and scientific scope

The separate checker requires canonical reduced rational encodings, exact original-model hash bindings, the full original binary mask and the exact fixed schedule. It checks every original row and column endpoint at tau=0. Supplemental native checks retain the existing mature initial state, clipped end-of-horizon dwell and on-on ramp semantics. Ramp coefficients explicitly rationalize the existing binary64 multiplication of the native per-minute rate by 60, with the alternative exact-multiplication difference archived. DC feasibility comes from the original sparse rows; no independent native network reconstruction is claimed.

A strict original point and exact energy below the old 23195 cap trigger direct replay against that already existing capped identity model. The exact cap/non-cap relation is prepared independently. Energy above the cap yields only an uncapped positive. The numerical solver status or objective is never promoted to an exact optimum. A failed separable proposal or subsequent native-ramp check leaves this fixed-schedule attempt unresolved, not a full UC infeasibility result.

## Provenance, denominator and limits

Source, checker, protocol, design, pinned NPZ kernel, native data, original/capped models, old schedule, implementation-test report and all prepared artifacts are frozen before a call. The original five mathematical/native files are checked against their earlier manifest, and the original matrix/bounds, schedule and generator bytes have explicit bindings. Prepared review should additionally verify the synthetic report's status/source hashes and independently replay the block transformations and constant rows before execution.

A single-use marker, one permitted numerical call, accepted-option checks and the 65-second UTC guard repeated after launch-decision I/O prevent a second or late admitted solve. All 168 hours remain in the ledger; invalid bases, phase/bit limits and exceptions preserve unresolved outcomes. The 900-second arithmetic phase includes final original/native/cap replay, input rehash and outcome serialization; completion serialization is explicitly excluded. Both solver and arithmetic limits are soft and actual overruns must remain visible. An accepted result still requires an independent rational replay before publication.

The synthetic suite was read, not rerun. It supplies implementation checks rather than scientific outcomes. No novelty, exact optimum, physical-measurement precision, AC/security guarantee or historical result change follows from this bounded route.
