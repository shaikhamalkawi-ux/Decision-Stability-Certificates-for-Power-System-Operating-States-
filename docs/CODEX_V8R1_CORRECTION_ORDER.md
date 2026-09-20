# Codex — DSC-Grid V8R1 corrective execution order

Continue from candidate V8 commit:

`2b50159c7974413e3599483db65a56aac4f4c9d8`

The independent audit places V8 on HOLD pending a narrow V8R1 correction cycle. Do not open V9 and do not submit to the journal.

## 1. Reopen Workstream B at the pinned PyPSA-GB commit

Pinned upstream commit:
`8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`

Audit at minimum:
- `scripts/generators/integrate_thermal_generators.py`
- `data/generators/generator_data_by_fuel.csv`
- `config/defaults.yaml`
- `scripts/market/solve_wholesale.py`
- the PyPSA version behavior for commitment, minimum up/down, ramp, startup/shutdown, and initial-state attributes
- the upstream source documentation for thermal technical characteristics.

Build a machine-readable parameter-admission table containing carrier, parameter, raw value, source units, PyPSA units, provenance, applying code path, workflow layer, KEEP/HOLD/REMOVE decision, and reason.

Do not blindly run every available parameterization. The pinned repository contains more than one possible UC parameterization. Establish which, if any, is scientifically admissible for the Historical-2020 Reduced-network cases.

If an admissible source-supported parameterization exists, run matched January/July chronology variants where technically separable:
- LP/static;
- ramp-only;
- commitment/minimum-output only;
- minimum up/down;
- full admitted UC.

For rejection, return exact repair or rigorous bounds. Never infer infeasibility from solver failure.

If no parameterization passes the evidence gate, retain Workstream B = HOLD, but state accurately that source parameterizations exist and explain why they are not admitted. Do not say that the pinned model simply lacks chronology parameters.

## 2. Shorten the abstract

Reduce the abstract to 180–195 words and mechanically verify <=200 words.

## 3. Replace stale audit records

Replace the V7-headed `CLAIM_BOUNDARY.md` and V6-headed `MATHEMATICAL_AUDIT.md` with current V8R1 audits. Include the Elexon evidence and corrected GB chronology status.

## 4. Correct Elexon reproducibility wording

Either qualify byte identity to the locked environment plus cross-platform numerical equivalence, or implement canonical serialization and demonstrate portable byte identity.

## 5. Document Elexon date selection

State the actual rule for choosing 2023-01-11 and 2023-07-12. If illustrative, label it so. Add a matched-day sensitivity only if it directly closes the selection objection.

## 6. Rebuild and verify

After corrections:
- rerun affected calculations;
- rerun/expand clean-room claim audit;
- clean-root compile main/supplement;
- verify main <=10 pages and abstract <=200 words;
- verify references/DOIs;
- render-check all pages;
- verify no Type-3 fonts, undefined refs/citations, overfull/clipped content;
- verify ZIP integrity and fresh-extraction manifest;
- synchronize README, STATUS_LOCK, VERSION_SUMMARY, CHANGELOG, cover letter, submission notes, and handoff.

## 7. Delivery

Create `DSC_Grid_V8R1_*` packages and return:
- full package;
- TPWRS submission package;
- Overleaf source;
- manuscript + research supplement;
- NewChat transfer package;
- SHA-256 list/manifest;
- `CODEX_DECISION_REPORT_V8R1.md`;
- `CHANGELOG_V8_to_V8R1.md`;
- updated claim audit;
- chronology parameter-admission table.

Upload all final deliverables to Google Drive `02_CODEX_OUTBOX`, update GitHub on a clearly named V8R1 branch/commit, and expose the principal ZIPs as directly downloadable artifacts.

State **candidate V8R1 pending independent ChatGPT audit**. Final journal submission remains an author decision.
