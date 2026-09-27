# Root source review before preparation

27 September 2026. Read the complete proposed source SHA256 `d5b5fb33c30dbe2ad15bace67ecfa42cb3e4b076769f8ff8a0341827124d30ba` and protocol SHA256 `6b4df1dfa036fbc9a617dc996d66d0dddb52c1c00e2acdd9cdcf528eb767d318`. No scientific arrays, fixing-set arithmetic, preparation or optimizer were executed by this review.

The rule uses exact distance from the saved binary64 LP coordinate to a unique bit, with fixed tau below one half. All original state declarations are retained. Only the selected binary bounds change; the unchanged matrix/mask copies and full state partition are checked after serialization. No arbitrary intermediate bound, new objective or sequential neighborhood is introduced.

The one numerical MIP is a feasibility proposal, with caller-owned attempted/returned accounting and soft-time admission. Candidate recovery changes only eligible state coordinates. Every original joint row/box, both original projections, their full original masks and supplementary native conditions are checked. The identical common-bit requirement is explicit. A restricted numerical rejection or timeout cannot establish unrestricted infeasibility.

Source-level review passes. Preparation is authorized once, conditional on the separate reviewer's source PASS and review of any changed final bytes. Execution still requires independent verification of the actual prepared bound changes and an explicit one-run decision. These are internal verification steps within the user's authorization, not user permission requests. The historical common run and its UNKNOWN result must remain immutable.
