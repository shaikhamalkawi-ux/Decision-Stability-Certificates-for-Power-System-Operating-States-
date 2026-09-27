# Independent code review: portable replay of new closed results

Verdict: PASS for separately authorized candidate preparation, with the link-handling condition below. This is a read-only code and archived-schema review; it is not an execution result.

Reviewed source: reproducibility/replay_new_closed_results.py, SHA256 073d04a21dac59fc34926912ac3a58b6399b32e40017584047828608a5606b51 (51760 bytes).
Reviewed protocol: docs/research8h/PORTABLE_NEW_RESULTS_REPLAY_PROTOCOL.md, SHA256 72093987ce0d0ea421ed5238e1cad8a977c233b1b26953610569f44b72e82df2 (11240 bytes).

## Mathematical and model scope

The objective lower-bound calculation includes the signed row-endpoint term and exact finite-box correction for every stationarity residual. Inadmissible infinite-endpoint signs are explicitly projected and the saved projection and residuals are compared. Bounds are recomputed for the strict and uniformly expanded archived models without clipping negative lower bounds. The four optimal-difference/selected-incumbent/relative/percentage interval definitions and outward decimal rounding have the appropriate endpoints and denominators.

The original 12096-coordinate binary mask is checked separately from the U-only projected mask and the explicit zero mask used for continuous subset admission. Full reference/target points require original-mask integrality and expanded membership. Four subset points establish continuous admission only; they do not establish binary or strict nominal feasibility. The two full HOD controls imply four rule-specific memberships through independently reconstructed row deletion and unchanged boxes. Expected continuous nonbinary counts are retained.

The six fresh energy archives are checked against their capped parents with exactly one cap row removed, the original fossil objective and native roster. Identity archives have a special identity retained-row map and are also matched against the uncapped reference archives; target archives use capped-parent row indices. Full hourly packages and the fixed HOD/edge mapping are checked as archived values. This does not reconstruct the physical model from native data.

## Archived schemas and provenance

Read-only schema checks confirmed the identity row CSVs omit source_row_0based whereas target CSVs include it. The conditional label check and separate identity/target retained-map checks match those real archives. Model metadata contains the required column_order and fossil/unit fields.

The four stored exact_continuous_point dictionaries have the deterministic schema of the pinned standalone kernel; whole-dictionary equality is appropriate. Fresh energy and reference review hash dictionaries use repository-relative paths with Windows separators, normalized by relative_name. The subset post-run dictionary contains 61 arm-relative files and is passed its arm base. Its later 71-entry artifact manifest instead uses the repository/package root. The two historical closure stages remain distinct. Prepared/review status strings and the historical capped UNKNOWN case agree with the archived records inspected.

The outer manifest and pinned helper/kernel sources precede mathematical replay, accessed files must be package-bound, historical path maps use exact component prefixes, and final inventory/rehash checks are required. Duplicate JSON keys, nonfinite JSON, conflicting bindings, unsupported archive schemas and missing required outcomes fail closed. Producer native-check flags are read as provenance rather than presented as a rerun.

## Link condition and execution gate

The source resolves paths and rejects escapes but can accept an internal symlink. The earlier design promised link rejection more broadly. Before replay, candidate preparation should explicitly reject every symlink/reparse link in its copied inventory, or the producer should introduce and separately review an equivalent source guard before freezing. This is a packaging condition, not a mathematical defect in the reviewed arithmetic.

No new wrapper import, candidate preparation, focused fixture, mathematical replay, optimizer, installation or network operation was performed for this review. The source's proposed small checks were inspected but not executed. Candidate preparation and actual replay still need their separate authorization and recorded results.

The coverage claim is limited to six fresh lower bounds, six original-mask uppers, four interval records, four continuous subset points, and two auxiliary controls/four inheritances. It does not replay every historical figure row, two unrestricted first-week energy intervals, strict nominal witnesses, or solver optimality; it makes no second-machine or independently rebuilt native-model claim.
