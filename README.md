# DSC-Grid — Decision Stability Certificates for Power-System Operating States

Research repository for the DSC-Grid project.

## Scientific focus

DSC-Grid studies whether the same distributional power-system operating-state target remains admissible as progressively richer operational information is restored:

1. static support / feasibility,
2. clock-hour conditioning,
3. commitment restrictions,
4. chronological constraints such as ramping and minimum up/down times,
5. network-constrained repair,
6. AC restoration.

The core scientific distinction is between **static feasibility**, **chronological admissibility**, and **AC feasibility**. These are not interchangeable.

## Current active baseline

**DSC-Grid V8 — Operational Evidence and Chronology Audit**

Current journal target: **IEEE Transactions on Power Systems (TPWRS)**.

Current headline evidence includes:

- the locked RTS-GMLC static/conditional operating-state results;
- native chronology showing that ramping alone preserves admission while minimum up/down chronology can reject the same exact target mean;
- a certified July network-constrained chronological repair bracket;
- an independent PyPSA-GB January/July replication of the distributional information effect;
- a frozen Elexon matched-day operational-outturn comparison, explicitly limited to observational evidence;
- a parameter-level audit placing the PyPSA-GB chronology workstream on HOLD rather than imputing missing constraints;
- a warm-started 600-second HiGHS run that retains the certified July repair bracket without calling the incumbent optimal;
- a clean-room reproduction in which 26 of 26 central numerical claims pass;
- AC-restoration evidence handled separately from chronology.

V8 is the candidate successor to V7, pending the project owner's independent ChatGPT audit before the active Google Drive baseline is changed.

## Repository policy

This repository is being prepared as a reproducibility and manuscript-development repository.

- Numerical claims must trace to admitted source data or verified derivations.
- Solver non-convergence is **not** treated as infeasibility.
- Incumbents are **not** reported as optima.
- PGLib-UC stress semantics are kept separate from native RTS-GMLC semantics.
- New methods are admitted only when they answer a defined scientific question.
- Every substantive scientific revision must include provenance, reproducibility checks, and a change log.

## Project structure

```text
manuscript/          Journal manuscript source and release-ready copies
supplement/          Scientific supplementary material
src/                 Reproducible analysis and verification code
data/                Admitted data or acquisition instructions
results/             Locked numerical outputs and machine-readable results
external_validation/ Independent RTS / PyPSA-GB / Elexon-NESO evidence
solver_logs/         Optimization and solver audit logs
provenance/          Source, environment, commit, and hash records
docs/                Scientific status, handoff, and workflow documentation
releases/             Versioned research packages
```

## Current development workflow

The active research workflow is coordinated between ChatGPT, Codex, Google Drive, and this GitHub repository.

Codex may update the research package and manuscript when new evidence or verified corrections justify a new version. The active baseline must not be overwritten silently; changes must be versioned and documented.

## Publication status

**Pre-submission research repository.**  
No journal submission is represented as accepted or published here.

---

Repository maintained for the DSC-Grid research project.
