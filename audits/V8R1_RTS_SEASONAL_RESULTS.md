# Eight-week RTS chronology extension

The fixed selection is every archived week in the original static comparison:
January (source-week control), February, March, April, May, June, July and
October 2020. Each window contains 168 hours and the same 41 coordinates.
The protocol was written before the seasonal optimization runs.

| First week of month | Archived schedule passes native online ramps | Exact mean with minimum up/down |
|---|---|---|
| January | Yes | Rejected |
| February | Yes | Rejected |
| March | Yes | Rejected |
| April | Yes | Rejected |
| May | Yes | Rejected |
| June | Yes | Rejected |
| July | Yes | Rejected |
| October | Yes | Rejected |

The minimum-time results are explicit HiGHS 1.12.0 Infeasible statuses for the
no-network exact-mean model, using source-native minimum output, availability,
hydro treatment, hourly balance and weak/free boundaries. Each solve received
60 seconds, one thread and seed zero; every minimum-time run finished before
the limit. The primary statuses, logs and witnesses are in
`results/v8r1/rts_seasonal/`. Infeasibility here excludes stricter models with
the same semantics; this does not certify every possible operating model.

All eight original archived schedules themselves satisfy the separate native
online-to-online ramp family. Their exact target means therefore have a direct
feasible witness, verified against source inputs with a 1e-5 MW tolerance.
This is stronger than relying on a new search to rediscover each schedule.
The original May ramp optimization reached its 60-second limit without an
incumbent; that search outcome remains recorded as UNRESOLVED. It is superseded
for admission by the independently verified archived schedule, not relabelled
as an optimal solve. See `results/v8r1/rts_archived_ramp/`.

The verifier checks finiteness, status bounds and integrality, generation and
hydro bounds, aggregate balance, all coordinate means and on/on ramps. A
separate implementation checks the archived ramp result and derives additional
single-unit residence necessary conditions; see
`audits/V8R1_RTS_INDEPENDENT_REVIEW.md` and `results/v8r1/rts_certificate/`.

## Interpretation

The previously demonstrated distinction is not confined to the March and July
targets within the archived sample. The January source-week control also
fails the minimum-time model. The experiment therefore compares laws generated
by a static benchmark with a stricter chronological set; it does **not** show
a transition from a previously certified chronological source schedule.
No annual prevalence, independent-system chronology replication, field
intervention, new repair optimum or combined network/AC schedule is claimed.

## Reproduction

The original experiment used the legacy V3 source directory. Readers can now
reconstruct equivalent inputs without that directory using the verified pinned
acquisition procedure in `docs/V8R1_RTS_INPUTS.md`:

```powershell
python src/v8r1_prepare_rts_inputs.py
```

Use `.work/v8r1_rts_inputs` as `<extracted-V3-directory>` in the commands below.
All eight upstream hashes, target arrays, timestamps and model inputs matched
the original experiment. The preparation creates no new target dispatches.

```powershell
python src/v8r1_rts_seasonal.py --source-v3 <extracted-V3-directory>
python src/v8r1_rts_seasonal.py --source-v3 <extracted-V3-directory> --output results/v8r1/rts_archived_ramp --verify-archived-ramp-only
python src/v8r1_rts_residence_certificate.py --source-v3 <extracted-V3-directory> --output results/v8r1/rts_certificate
```

The last two commands verify existing schedules and necessary conditions
without solving a mixed-integer model. Input hashes are recorded with the
results. The immutable V8 companion package is not overwritten by this work.

## Execution record detail

An initial JSON-export attempt rejected HiGHS' infinite unavailable residual
for an infeasible result. The exporter was corrected to record null for that
unavailable diagnostic, and the unchanged model/protocol was rerun. January
logs retain both attempts. Raw solver logs retain the solver's whitespace;
source/document whitespace checks exclude those unmodified evidence logs.
The final portable-input replay passes all eight archived ramp witnesses and
is stored in `results/v8r1/rts_portable_witness_replay/`.
