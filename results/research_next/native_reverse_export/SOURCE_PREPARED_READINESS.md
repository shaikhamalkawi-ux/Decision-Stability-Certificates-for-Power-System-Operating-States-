# Fixed native reverse export: source and preparation ready

**PREPARED ONLY; no native execution.** The sole authorized `--prepare-once` invocation closed with exit 0 in exec session 24294. The final descriptor was written at 2026-09-27 12:18:20.704175 UTC. The preparation created the fixed derived input and froze 445 bindings; Julia imports, official reads/builds, optimizers and old-model rebuilds all remain zero. The `run01` and `launcher01` directories are absent.

| Artifact | SHA256 |
|---|---|
| `src/researchnext_native_reverse_launcher.py` | `bbfc95b40199956220554a51b4bcd2fa7ab8134e238abb90b4a1129628db73df` |
| `src/researchnext_native_reverse_export.jl` | `568b4819c78a73fe368002b663d768b16380c2540e3a1c84182abd54af95dfa4` |
| `src/researchnext_native_reverse_transport.py` | `1640604de92ba2d9711d116c919c57e8e984229d4e7418687acc1fe278963d26` |
| `docs/research_next/NATIVE_REVERSE_EXPORT_PROTOCOL.md` | `05ce332e378544ba8c937c26934045d321a58b6edb671d12f00d12da134fc7ad` |
| `prepared/prepared.json` | `631ca0a7fa07abcd258dd905bc8017d88705bbfc708033157d5ac3e25cd2e675` |
| `prepared/transport.json` | `dbb927af6d16f589ba4118aa9fff582725325acbbecac0cd63493e5ca5d5dc96` |
| `prepared/target_case.json.gz` (2,519 bytes) | `0acc7728ebab28731f6f2bbc5a97025db1c4381a1a4016f798e040dd72f073d8` |
| `prepared/target_case.json` (9,548 bytes) | `1d3446c1826f0420cb9d2f5cb59b252bbb8878dd3dc599c73b18edb32d051d6d` |
| `synthetic_controls.json` | `21dc3050c588ebd978eab75cb2c05edb5848196036238f0dff4dab60f3d3935a` |

Preparation captured the original compressed case, old target model and normalized case once for transformation. It applied the stored destination-to-source order once to load/reserve, preserved all other raw subtrees and the absent penalty field, and matched the archived 4,384-row, 2,472-column, 960-binary target's hourly transport premises. Copies of all three original payloads remain byte-identical. The derived gzip is a new test input; no whole-file equality with the old original-case-plus-order metadata is claimed. `native_model_correspondence` remains `NOT_TESTED_BY_TRANSPORT`.

All 15 invented transport controls passed in one actual synthetic execution. They test ordering, omitted defaults, nonmutation, binary64 preservation, deterministic gzip and rejection of altered rows/mask/penalty or already-transported data. An earlier command encountered the unavailable Windows Store Python alias before Python or any fixture ran; the actual test used the available bundled scientific interpreter in isolated stdlib mode. Agent `/root/find_deposit/gb_docs` authored the transport module and controls; the parent agent read that source in full. This is disclosed authorship, not an independent runtime proof of native correspondence.

The new launcher and Julia sources retain the reviewed identity runtime/export logic with separate paths, the frozen derived-input digest and target identity. Unified source diffs are saved alongside this memo. Source-only Python syntax parsing passed; no Julia parse/import or model build was used as a syntax check. The 600-second execution allocation begins before binding admission and the 120-second native subphase begins at the official-read marker. No package update, download, whole-tree scan or global setting change occurred.

The next gate is independent review of the final sources, 445 bindings, exact input transport and prepared command/environment. A separate explicit GO is required for the one native read/build/export. Even a successful raw export will remain pending target comparison; target native equivalence, transferred cost bounds and an optimum-difference interval have not been computed by this preparation. All closed historical artifacts remain untouched.
