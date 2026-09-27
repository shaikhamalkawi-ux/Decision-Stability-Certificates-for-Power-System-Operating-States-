# Strict branch-path diagnostic: complete null result

All 1,344 fixed rational candidates were valid and nonseparating, both for the exact nominal model and after the declared uniform finite-bound expansion. All 672 hour/week cases and both orientations were evaluated; none was skipped. The stronger branch-path construction therefore still does **not** settle strict nominal feasibility. It neither proves infeasibility nor supplies an exact nominal positive witness.

The single authorized execution exited 0. Whole-input validation took 1.568905199994333 seconds; the separately measured arithmetic phase took 17.478677600010997 seconds, with no soft-limit overrun. There were zero optimizer calls, retries, alternative path metrics, model changes or result-driven adaptations. The final phase sample includes outcome-ledger serialization and precedes only the final completion-record write.

| Original reference week | Hours | Orientations | Strict separators | Expanded separators | Largest strict gap, approximate |
|---|---:|---:|---:|---:|---:|
| January | 168 | 336 | 0 | 0 | -3.646725872386014e-12 |
| April | 168 | 336 | 0 | 0 | -3.650278586064815e-12 |
| July | 168 | 336 | 0 | 0 | -3.5294863209855976e-12 |
| October | 168 | 336 | 0 | 0 | -3.6289623039920116e-12 |

These displayed gaps are approximations for the fixed original balance-row normalization. All classifications use the archived exact numerator/denominator arithmetic, not these displayed floating values; they are not energy penalties or MWh bounds.

The common tree used the one predeclared exact strict metric `R/|b|` and deterministic complete-row-ID path tie breaking. All non-reference coordinates used their selected paths. The pin was discovered from the original column bounds at index 12, bus ID 113. Each path was reconstructed exactly from its original branch rows. Every candidate preserved the 25 original balance multipliers and added rational branch multipliers, with exact cancellation of every non-reference column and preservation of the correct `sum(q)` reference coefficient.

Both shared-edge and expanded-reference cancellation gains were nonzero for all 1,344 candidates. The strict reference gain was zero. In every case, the direct original-row gap matched the independent path-box expression plus both applicable gains. Every expanded gap satisfied `gap <= |beta| - 25*tau < 0`, as predicted. The fixed synthetic path/tie/rational-coefficient/gain checks passed.

All 31 frozen source/protocol/model/audit bindings matched at final replay. No original audit, matrix, endpoint, point or earlier result was altered. The provenance note preserves the earlier design-only inspection's failed index-zero assumption and its correction; that inspection computed no path or separation outcome.

This is a fixed diagnostic of the archived representation, with one path family. Its null result does not establish stability, exact physical consistency, nominal feasibility or impossibility of another certificate. The existing expanded-model positive and negative claims retain their original scope. Any rational positive reconstruction or physically consistent reassembly would need a separately authorized, frozen study.

Source SHA256: `4622945e972313ac073f9c04bb55d179c7b4491533e03b44ae31accd06c1a0cd`. Protocol SHA256: `6c28f25ae326bdf1fc195d8dccba270c02f464567fe90f02df76b85027b1f735`. Input-manifest SHA256: `c418af87aba6912c8ed70d65233eed828e6d83772ad8ce5a2ede70d0ac2cfd6f`.

Independent post-run reconstruction and root review are pending before publication. The complete evidence is in `common_paths.json`, four `month_XX.jsonl.gz` files, `outcomes.json`, `focused_checks.json` and `completion.json`.
