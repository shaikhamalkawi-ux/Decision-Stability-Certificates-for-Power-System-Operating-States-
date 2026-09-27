# Harmless two-arm ownership probe — closed

One authorized run completed at14:23:18.004743UTC, controllerPID57028/parent30548, exit0. Measured phase0.622127200011164seconds. No scientific file, backend import, optimizer, license setting or outer-job configuration was involved. Source/protocol/frozen-class closing hashes all matched their captured expected constants.

| Fixed arm | Observed assignment | Observed cleanup |
|---|---|---|
| One new job, launcher then actual Python | Launcher17092 succeeded; actual76328 failed on assignment2 with Win32 last-error5. Actual membership in the selected new job was false before and after failure. Both processes were already members of some job. | New-job termination succeeded; both exact retained process handles were reaped. Actual's exit code was0 and launcher's73; this does not establish which outer mechanism ended the actual child. |
| One separate new job per exact process | Launcher37504→job0 and actual85140→job1 both succeeded, with membership in their respective new jobs confirmed. | Both job terminations succeeded; actual and launcher were reaped with exit73. No exact-handle termination fallback was required. |

This records a concrete failure position/error in the new harmless reproduction. It does not retroactively add the missing Win32 code/position to the original batch or identify its complete outer-job hierarchy. The observed result is consistent with the parent's job-hierarchy hypothesis; no outer-job internals were inspected.

The second arrangement passed for harmless bounded sleeping children on this host. This is not a test of a scientific solver's timeout, newly spawned solver descendants, numerical correctness or common-commitment feasibility. The closed batch remains UNKNOWN with zero optimizer calls. No scientific arm resumed and no retry occurred.

The complete arm records preserve API booleans separately from membership, immediate Win32 errors, PID/creation-time identities, handshake hashes, cleanup actions and exit codes. A separate source-only correction proposal recommends changing only future ownership grouping, subject to its own authorization and review.
