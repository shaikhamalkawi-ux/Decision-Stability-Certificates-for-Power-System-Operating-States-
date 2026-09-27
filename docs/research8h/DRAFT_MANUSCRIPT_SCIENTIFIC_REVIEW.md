# Draft manuscript scientific review

Read-only review completed on 27 September 2026 UTC. The reviewed artifacts are
`.work/research8h_manuscripts/note_en.json` and `decision_ar.json`. This review
does not edit either manuscript or its builder, rerun optimization, or certify
the rendered documents. It assesses the reported scientific claims against
closed evidence, with a separate cross-reference/reference audit by another
agent. No fresh-week outcome was admitted during this review.

## Verdict and requested editorial corrections

**No mathematical or evidence-classification blocker was found in the baseline
draft.** The draft correctly distinguishes exact expanded-model results from
strict nominal feasibility, original binary witnesses from continuous LP points,
and uncapped optimum differences from differences between chosen schedules.
It retains unresolved cases and explicitly limits novelty and external validity.
This scientific review is not a finding of journal readiness.

The following corrections were sent to the manuscript owner:

1. In baseline English block 24, the sentence ending “includes both row and box
   expansion [4]” attributes too much to the cited reading. The local reading
   record for Neumaier–Shcherbina covers publisher metadata/abstract, not the
   precise expansion formula. Attach [4] to the established safe finite-box
   correction principle, and describe the displayed uniform-expansion term as
   the note's direct algebraic deduction. This is an attribution issue, not an
   error in the displayed inequality. The owner accepted the correction.
2. Define the conformable all-ones vector before equations (1)–(2). **Observed
   addressed** in the revised block 7.
3. Make the physical observation dimension explicit and give the mathematical
   value of tau instead of only a Python expression. The owner accepted
   `s_t in R^107`; the exact rational tau was **observed addressed** in revised
   block 7: `5902958103587057/590295810358705651712`.
4. After adding two HOD energy rows to Table 2, preface the 1543/2140 cap-band
   counts with “For the unrestricted pair.” Likewise, Arabic Figure 1 should
   refer to “الحالتين الأوليين في الجدول 2”. These are scope clarifications
   necessitated by the insertion, not changes to the verified numbers.

The manuscript owner was revising the JSON concurrently. Items reported as
accepted but not observed above require the owner's final textual/rendered
check; this review does not silently bind a later changing manuscript version.

## Version bindings

The complete baseline scientific and cross-reference reads used:

| File | SHA256 |
|---|---|
| note_en.json | `1d53491f49fb3b98644e19a11d0ca3a5f928bc6b4850ba69e0d62bec05cd023d` |
| decision_ar.json | `1508270b2c75773077137ea6117d3ac28c2aae97351f51750f8abc9a4915f0aa` |

The complementary reference audit read this baseline at 00:35:45 UTC. It also
checked numbering and reference order on concurrent revisions at 00:38:16 UTC
(English `6caf95619bdbceab6dc1c8f5f662866fbd06b740adf531d0c810d4627b4d5e84`,
Arabic `37e41c0afd82d7b3d19bf25ca9091f097c25cf08841c8edad96b3fe099e219da`).
My later scoped delta read included English
`caeee1e2986a46a0492e374b0582f20aaad1ca44c0d8efdd6ec0273fd4ee15c1`
and the same revised Arabic hash. It checked the new HOD energy table/abstract,
notation changes, and Figure 1 scope; it is not an assertion that no further
owner edits occurred.

## Physical observation and model scope

The complete hourly physical vector contains one independently encoded
aggregate net demand, 24 nodal net demands, 41 lower bounds and 41 upper bounds:
107 coordinates. I independently concatenated these archived native arrays and
checked all four January ordinary targets against the identity arrays. Every
target's 168-by-107 array equals the identity array indexed by its archived
permutation **bit for bit**; both 48-hour edges are unchanged. Both HOD cases
preserve `source_hour mod 24 = destination_hour mod 24`; the unrestricted cases
do not.

Including aggregate demand is substantive: its binary64 value differs from
the floating sum of the nodal values in 44 identity hours. Treating it as an
exactly redundant coordinate would therefore change the claimed observation.
All packages are finite. Dispatch, U/Y/Z, absolute timestamp, source row and
destination index are correctly excluded from the observation itself. Common
topology, physical constants, cap and numerical convention are retained outside
the observation, as declared.

The source assembly confirms radians for angles, MW for dispatch, 168 one-hour
steps, 24 buses, 38 internal branches, 41 decision generators and 24 thermal
units. Exactly 23 Coal/Oil/NG units define the one-hour fossil electrical MWh
sum; nuclear is excluded. No fuel-input, emissions, monetary or AC conclusion
is warranted or claimed. Initial U is free with mature prehistory, Y0/Z0 are
zero, and dwell obligations truncate at the terminal hour. The note correctly
keeps these assumptions and Area 1 isolation in scope.

## Mathematical checks

The nominal row system and finite box are interpreted as exact rationals of the
stored binary64 coefficients. Every finite row/column endpoint is expanded by
the exact binary64 tau; original U/Y/Z remain exactly binary. The same numerical
tau has mixed native units, so it is correctly not presented as physical input
uncertainty. Positive witnesses have tiny strict nominal violations and are not
claimed as strict witnesses.

For admissible signed row multipliers, beta is the selected-endpoint row lower
bound. With q = A-transpose d, beta minus the finite-box maximum minus
tau*(||d||1+||q||1) is the correct expanded separation gap. Positivity rejects
the continuous superset and hence the binary model. Raw ray scale is arbitrary
and the manuscript correctly avoids reporting this gap as MWh.

For objective c, eta = c - A-transpose d gives the exact lower bound beta plus
the minimum finite-box eta product, less tau*(||d||1+||eta||1). This remains
valid without exact dual stationarity or a numerical optimality status. It
supports the displayed uncapped-model bounds. A finite binary witness and a
closed, finite box establish an attained finite minimum, without asserting
that the witness is optimal.

The optimum-difference interval [L_T-U_I, U_T-L_I] is valid. For positive
identity and target lower bounds, [L_T/U_I-1, U_T/L_I-1] is the correct relative
optimum interval. It is distinct from dividing the absolute-difference interval
by a chosen reference schedule. Direct Fraction arithmetic independently
reproduced the two unrestricted gap and percentage intervals in Table 2,
1543/2140 integer-cap counts, and the downward-rounded minimax-error bounds
771.417865/1069.575568 MWh. The cap band's upper endpoint must remain open; the
listed closed decimal subsets lie safely inside the exact band.

Equal observations coupled with one positive and one certified negative imply
the stated deterministic binary-classifier obstruction. This is a two-instance
logical result, not a population error rate. Abstention and use of additional
chronology remain allowed. The half-separation energy-estimation consequence
also follows directly by the triangle inequality.

## Structural explanation and result classification

The no-dwell proof is sound for the audited formulation. For 0 <= tau < 1,
integer transition residuals within tau remain zero and exclusivity remains at
most one. Canonical positive/negative differences of successive U therefore
lift any retained P/U/theta assignment to Y/Z with initial zeros. After deleting
only dwell rows in the physical model, the auxiliary rows can be eliminated
through this proof; they are not an additional unproved experimental relaxation.
The retained hourly rows/boxes permute bijectively and the global cap/fossil
functional is invariant. The independent 8-target structural replay passed.
This does not assert strict nonemptiness, a general UC theorem, storage support,
or a field causal effect. Its eight archived targets are the original January
twins/control plus five whole-day orders; do not call that count eight HOD tests.

The baseline Table 1 matches the closed reviews: two unrestricted and two HOD
January negatives; five whole-day cases with one accepted binary positive and
four UNKNOWN; four April/October ordinary cases all UNKNOWN. October's identity
control draw is explicitly retained. The five fixed-identity negatives reject
that restricted schedule only, and the accepted full day-312 model is correctly
used to demonstrate the distinction. The July-to-January fixed-rule comparison
changes both week and background formulation, so its 0/2 and 1/2 results cannot
be attributed purely to season.

The raw July uniqueness/bigram observation is also correctly limited: exactly
labelled exogenous transitions with distinct labels reconstruct the sequence;
preserving endogenous commitment bigrams is a different observation. No generic
Markov impossibility follows.

HOD uncapped results were initially excluded. During this review their separate
post-run gate closed with `INDEPENDENT_HOD_UNCAPPED_POSTRUN_PASS`; review SHA256
`6039f8bbf0dd882cf34f9ada87ec251e95d1e48296291591e6b58914c680c832`.
The subsequently added Table 2 rows correctly state [566.366617,1336.352662] and
[858.121844,1408.976215] MWh and [2.466222%,5.908928%] and
[3.736660%,6.230047%]. Figure 1 remains clearly labelled as the original pair.
Fresh-week results remain excluded from this review and its admitted counts.

## References, cross-references and reproducibility

The separate read-only audit found sequential unique equation IDs 1--6,
valid references to Tables 1--2 and Figure 1, and an existing figure path.
English references 1--8 and Arabic references 1--7 follow first citation order.
Titles/authors/years/DOIs agree with the local primary-metadata audit. This is
a local-evidence consistency finding, not a new external DOI-resolution test
or full-text reading claim. The local RiSES3 and safe-bound reading limitations
remain material and are not enlarged by this review.

I also read the relocation source and summary without rerunning it. The script
checks the known Checkpoint03 ZIP digest, uses an explicit member allowlist,
checks each selected member against the packaged byte/hash manifest, and calls
the extracted standard-library verifier with isolated Python `-I -S` from a
fresh directory. Its archived 35 fixtures, two HOD rays and two binary points
pass. The draft accurately limits this to selected mathematical replay on the
same host, not raw assembly, full manifest provenance, a second-machine test or
a general proof of parser correctness. No new optimization was involved.

The current Zenodo-versus-experimental-branch distinction is correct: the V8 DOI
must not be presented as containing the newer research. This review did not
repeat external GitHub/Drive publication verification or inspect rendered pages.
Those are separate owner checks, as are future final-commit and archive links.

Key evidence bindings read during this audit:

| Artifact | SHA256 |
|---|---|
| energy_lp_refinement/independent_review.json | `94c10b498dc600f92d55c77987325a106d7dcbb64f201a284a8295b756528401` |
| no_dwell_symmetry/independent_replay.json | `ce2216977e6420fbe51c695498fdd2afeed897842b76871daf36a1a5cff90903` |
| hour_of_day/independent_postrun_review.json | `b0d401deacda159c7e7a8799327cc64cb349742f4900383f5bdd0035fc388cb8` |
| seasonal_cap_continuation/independent_postrun_review.json | `14a72a7adb98509d73a6c59ad3303d892dc91d28ea08323fe31d3c87c3cadd0c` |
| day_fixed_identity/independent_review.json | `f1d3df10679dbb83de151aa5d79b1f498725b7239a89a323d1dce3f2d4c0cb60` |
| relocation_smoke/summary.json | `b76d960bf88e20f30bd74851f21aaf3ffb9f4c5cf84435cc630fdc4058065ccb` |
| REFERENCE_PRIMARY_METADATA_AUDIT.md | `e087533499ac77bd69e5aaf098de088c50acf705bcba9210c3e679f9feb96a47` |
| SAFE_BOUND_PRIOR_ART.md | `694f581cd5b6e9f4369e6c0ecb4e6ab1f760a7b265d7ad4a69c4d98747e642fe` |

Result paths in this table are under `results/research8h`; reference-audit
paths are under `docs/research8h`. This review created only this report.
