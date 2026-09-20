# V8 version summary

## Why a new version is justified

V8 is not a formatting-only revision. It adds source-independent operational
data that substantively extends the evidence base: the mean/shape and
conditioning distinction is observed in settled Elexon B1610 outturns. It also
adds a verified correction to the evidence boundary by demonstrating from the
frozen metadata that PyPSA-GB chronology is not natively parameterized. These
changes affect the abstract, experimental design, results, discussion,
limitations, supplement, claim ledger, code, and provenance.

## Workstream disposition

| Workstream | Decision | Result |
|---|---|---|
| A - Elexon/NESO evidence | ADMIT | Matched-day observational result; 5.89% shape share and 1.15% same-period premium. |
| B - PyPSA-GB chronology | HOLD | Frozen LP inputs contain no committable/min-up/min-down/ramp parameterization. |
| C - July network repair | RETAIN BRACKET | Warm-started HiGHS run returns the existing endpoints; no optimum claim. |
| D - clean-room reproduction | PASS | 26/26 central numerical claims reproduced without importing project analysis code. |
| E - 2024-2026 novelty audit | PASS WITH NARROW CLAIM | Close robust-dispatch, UC, path, and AC-restoration work is mapped; no absence proof claimed. |

## Manuscript changes

- Added the Elexon operational-data design, result table, evidence boundary,
  discussion, and data-availability language.
- Added the PyPSA-GB chronology parameter audit and explicit HOLD decision.
- Recorded the new network-MIP run without changing the certified bracket.
- Updated the 2024-2026 closest-literature map and references.
- Added the clean-room audit and machine-readable claim checks.

## Unchanged central conclusions

The RTS native minimum-up/down rejection, AC witness interpretation, and
PyPSA-GB static/conditional replication are unchanged. Static support,
chronological admission, and AC feasibility remain separate questions.
