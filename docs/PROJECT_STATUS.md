# DSC-Grid Project Status

## Active scientific baseline

**V8 — Operational Evidence and Chronology Audit (candidate baseline)**

Target venue: IEEE Transactions on Power Systems (TPWRS).

## Locked scientific interpretation

The same operating-state target can receive different admissibility verdicts as additional operational information is restored. The project therefore keeps three layers separate:

- static feasibility/support;
- chronological admissibility;
- AC feasibility/restoration.

Native RTS-GMLC chronology and PGLib-UC stress semantics are not mixed.

## Evidence-gate outcome

The A-E evidence gate produced a substantive, admissible revision:

- A: frozen Elexon matched-day operational evidence, with non-causal claim boundaries;
- B: PyPSA-GB chronology HOLD because the frozen generator metadata do not contain admissible chronological constraints;
- C: a warm-started HiGHS network-MILP run that leaves the certified July bracket unchanged;
- D: independent clean-room reproduction, 26/26 central claims passed;
- E: a 2024-2026 closest-paper audit supporting the manuscript's narrowed novelty statement.

V8 scientifically supersedes V7, but remains a candidate baseline until the project owner's independent ChatGPT review verifies the calculations, claims, repository state, PDFs, and package integrity. No journal submission has been made.
