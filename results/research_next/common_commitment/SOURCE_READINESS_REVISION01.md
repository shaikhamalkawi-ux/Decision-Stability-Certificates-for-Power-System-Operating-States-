# Pre-preparation provenance correction

27 September 2026. Parent source review requested consistent captured-byte provenance before any scientific preparation. The revised source reads each selected historical payload once, verifies that buffer against the trusted manifest digest/length, binds its actual captured digest/length and writes the copy from the same bytes. Raw GEN, historical manifests and closed selection records use the same capture rule. This removes the previous separate verify/bind/copy reads. The preparation plan also records Python executable/version and installed NumPy, SciPy and highspy versions through standard-library package metadata.

Final review candidates:

- `src/researchnext_common_commitment.py`: SHA256 `039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284`.
- `docs/research_next/COMMON_COMMITMENT_PROTOCOL.md`: SHA256 `08838becbd0d679f6131421c566534f19c93f535e7baa3b4b00d30b985ccab21`.

The change affects provenance and environment reporting, not formulation, witness arithmetic, ray arithmetic, selection, options or budgets. An AST-only syntax check passed. The original eight invented fixtures were not rerun: their receipt remains SHA256 `d6d62ea8247121d9b39b734769e3f966e7c22af1e56c55a2b25c803ec8482da4`, truthfully bound to the original source `90571aa1…`. The original readiness note is retained as history.

At this revision there is still no `prepared/` or `run01/` directory and no scientific preparation or solver call. Source re-review and separate preparation authorization are pending.
