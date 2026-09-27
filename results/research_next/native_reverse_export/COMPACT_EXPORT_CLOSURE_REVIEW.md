# Compact native reverse export closure review

Status: **COMPACT_RAW_EXPORT_CLOSURE_PASS**. Read-only inspection completed on 27 September 2026, approximately 12:32 UTC, by `/root/find_deposit/gb_docs`.

This review covers the closed `reverse_4_19__native_penalized` raw export's ledger, selected source/preparation bindings, payload integrity, schema counts and timing. It does **not** establish target-model fidelity, nominal or expanded equivalence, witness feasibility, objective bounds, or a target-minus-identity cost claim. The producer's status remains `OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON`, and the raw model records `NOT_COMPARED`.

## Closed execution and timing

The launcher completion records one Julia invocation, one native read attempt, one native build attempt, zero optimizer calls, exit code zero, no stream errors, no retry and `owned_parent_alive=false`. Its PID and command agree with `julia_launch.json`; the executed command equals the frozen prepared command, including the derived gzip digest as its final argument. The native marker progression is `(read, build) = (0,0)`, `(1,0)`, `(1,1)`, followed by a build-return marker and successful native completion. Every inspected marker retains zero optimizer calls. No live process query was made; closure is assessed from the archived receipts and the previously reviewed source.

The launcher records 448.38420460000634 seconds against the 600-second soft allocation and zero overrun. Independent subtraction of its recorded UTC timestamps gives 448.383860 seconds. The native read marker at `12:27:46.792Z` precedes native completion at `12:29:25.733Z`, a difference of 98.941 seconds against the 120-second allowance; the launcher's floating-point elapsed field agrees to its representation precision. The exporter separately records 100.4167478 seconds from its earlier internal ledger start, which is a different start point. The final launcher completion-receipt write is explicitly excluded from elapsed time.

## Selected immutable bindings

Current payload hashes agree with the known source hashes and closed records:

| Artifact | SHA256 |
|---|---|
| `src/researchnext_native_reverse_launcher.py` | `bbfc95b40199956220554a51b4bcd2fa7ab8134e238abb90b4a1129628db73df` |
| `src/researchnext_native_reverse_export.jl` | `568b4819c78a73fe368002b663d768b16380c2540e3a1c84182abd54af95dfa4` |
| `src/researchnext_native_reverse_transport.py` | `1640604de92ba2d9711d116c919c57e8e984229d4e7418687acc1fe278963d26` |
| `docs/research_next/NATIVE_REVERSE_EXPORT_PROTOCOL.md` | `05ce332e378544ba8c937c26934045d321a58b6edb671d12f00d12da134fc7ad` |
| `prepared/prepared.json` | `631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675` |
| `prepared/target_case.json.gz` | `0acc7728ebab28731f6f2bbc5a97025db1c4381a1a4016f798e040dd72f073d8` |
| `prepared/transport.json` | `dbb927af6d16f589ba4118aa9fff582725325acbbecac0cd63493e5ca5d5dc96` |
| `launcher01/completion.json` | `d52d7b7488d8f3978d3e0278e7f4a142b82cf3354618d5384dd5e551b1942977` |
| `run01/completion.json` | `71a3b644ba77340c006f43c4b564155f144032ef46f328c100b0c35b231ac03b` |

The prepared manifest contains 445 bindings. Their complete replay belongs to the separate prepared audit and was not repeated here. This reviewer authored the transport module; this memo does not represent independent review of that implementation or scientific transport.

## Closed outputs

All ten public artifact entries in the launcher completion were independently checked against actual file byte lengths and SHA256 hashes: three launcher markers, five native ledger/completion files, and the two payloads below. Both payload hashes agree with native completion and the launcher artifact manifest.

| Payload | Bytes | SHA256 |
|---|---:|---|
| `run01/official_raw_model.json` | 8,630,839 | `8cd0adfe027727c1d0599a1a291c8e0b289995bc1749b72f13dfe6795289e6d6` |
| `run01/official_parsed_instance.json` | 401,554 | `455814d618b3a84fe7d4bd4e2027155f8917d5a9dd57721b76ece2e472bfc227` |

Raw schema is `official-orlib-MOI-raw-binary64-v1`, optimizer state is `NO_OPTIMIZER`, and counts agree with both completions: 2,712 variables, 960 native ZeroOne constraints and 4,384 affine rows. The raw arrays contain 2,712 variables, 2,712 aliases, 960 binary indices and 8,080 total constraint records. This is a schema/count check; alias semantics and individual coefficients were not compared. The parsed JSON exposes the expected scenario/time, thermal-unit, bus, reserve, penalty and native-read/repair fields; their scientific values remain for the subsequent comparator.

The two private log files also match their recorded byte lengths and hashes. Both paths lie under the designated `.work/researchnext_julia_export/native_reverse_export01_launcher/` directory. Their contents were not inspected or published; publication status remains `NOT_SELECTED_PENDING_REVIEW`. No producer readout or closure inventory appended after the original completion manifest is admitted by this memo.

## Limits and actions

No producer or scientific helper was imported or executed, no native read/build was repeated, no optimizer was invoked, and no scientific coefficient, point or lower-bound arithmetic was performed. No existing artifact was edited. This new memo is the only file written by this closure task. Subsequent target correspondence and mathematical certificate reviews are still required before any native target-cost transfer can be claimed.
