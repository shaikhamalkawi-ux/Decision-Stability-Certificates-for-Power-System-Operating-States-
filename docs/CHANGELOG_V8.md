# Changelog V7 to V8

- Added frozen Elexon B1610, PN, dynamic-parameter, and BMU reference evidence.
- Corrected the B1610 unit interpretation explicitly: MWh per half hour is
  converted to average MW by division by 0.5 h.
- Added common- and union-coordinate operational transport analyses.
- Added PyPSA-GB generator chronology-parameter audit and HOLD gate.
- Added warm-started HiGHS 1.12.0 network-MILP rerun and full status log.
- Added 26-claim clean-room arithmetic reproduction.
- Added bounded 2024-2026 closest-paper audit.
- Revised manuscript abstract, design, results, discussion, limitations,
  conclusion, references, and data/code availability.
- Expanded supplement and claim ledger.
- No V7 numerical lock was changed or silently reclassified.
