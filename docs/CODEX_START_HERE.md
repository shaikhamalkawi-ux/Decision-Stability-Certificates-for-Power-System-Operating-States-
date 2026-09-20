# Codex Start Here — DSC-Grid

## Canonical Google Drive workspace

Use the project Drive folder for full packages, large data, notebook returns, and final handoff:

https://drive.google.com/drive/folders/1D-KSH5Gv7rP0HRMt9uV5_PAS0Ss1p1LL

Folder roles:

- `00_ACTIVE_BASELINE` — current V7 baseline and journal-facing packages.
- `01_CODEX_INBOX` — instructions, computational inputs, notebooks/returns, and verification outputs.
- `02_CODEX_OUTBOX` — all completed next-version deliverables must be returned here.
- `03_ARCHIVE` — prior baselines and historical packages.

Read first in Drive:

1. `01_CODEX_INBOX/00_INSTRUCTIONS/CODEX_START_HERE_DSC_GRID.md`
2. `01_CODEX_INBOX/00_INSTRUCTIONS/CODEX_FULL_AUTHORITY_EXECUTION_ORDER.md`
3. `01_CODEX_INBOX/00_INSTRUCTIONS/CODEX_PROJECT_HANDOFF.md`

## Starting scientific baseline

Use:

`00_ACTIVE_BASELINE/DSC_Grid_V7_GBReplicationAndNetworkRepairStrengthening_FULL_PACKAGE.zip`

V7 is the starting baseline. It may be superseded only if evidence or a verified correction warrants a substantive new version.

## Authority

Codex has full authority to revise the manuscript, supplement, mathematics, code, figures, tables, references, computational pipeline, reproducibility archive, and journal-facing package when scientifically justified.

Routine methodological/editorial decisions should be resolved autonomously from evidence. Stop only for a genuine blocker.

## Workstreams

Track Issue #1 and execute A–E:

A. Real GB operational evidence from Elexon/NESO.  
B. Independent PyPSA-GB chronology / MILP experiment after parameter provenance audit.  
C. Strongest rigorous closure of the July network-constrained repair problem.  
D. Independent clean-room reproduction of central V7 claims.  
E. 2024–2026 closest-paper / novelty audit.

## Scientific controls

- static feasibility != chronological admissibility != AC feasibility;
- RTS-GMLC native semantics != PGLib-UC stress semantics;
- solver non-convergence != infeasibility;
- incumbent != optimum;
- label exact optima, lower bounds, upper bounds, and feasible witnesses correctly;
- preserve raw evidence, query/source registers, hashes, logs, environment locks, and claim-to-result lineage;
- do not add decorative methods, fuzzy logic, ML, or arbitrary robustness tests without a defined evidence-supported scientific purpose.

## GitHub role

Use this repository for source-controlled code, manuscript/source text, changelog, reproducibility scripts, claim/provenance records, and issue tracking.

Do not commit credentials, private correspondence, restricted data, or huge raw files. Keep those in the controlled Drive workspace and commit acquisition instructions/hashes instead.

If V8 is scientifically justified, document the V7→V8 changes explicitly. If not, retain V7 and return a `NO_NEW_VERSION` audit.

## Final return

Put all completed packages in `02_CODEX_OUTBOX` and also expose the principal full package and journal-submission package as directly downloadable artifacts in the final Codex response.

Do not submit the paper to a journal. Final journal submission authorization remains with the user.

After completion, return the package to the ChatGPT DSC-Grid project page for an independent audit before submission.
