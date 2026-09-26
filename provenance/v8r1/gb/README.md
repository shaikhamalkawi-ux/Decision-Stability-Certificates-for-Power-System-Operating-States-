# GB chronology parameter provenance

The pinned upstream model contains UC parameterizations. The absence of activated chronology fields in the frozen LP metadata does not establish their absence upstream.

`KEEP` means a documented source fact or an exactly recovered optional model parameter can be retained for its stated scope. It does **not** admit a native historical-network feasibility conclusion. `HOLD` identifies a claim or transfer that is not yet supported.

- `source_manifest.csv`: URLs, pinned revision and SHA-256 of 24 inspected primary-source files under `.work/gb_upstream`.
- `parameter_admission.csv`: 43 parameter/control decisions for the optional wholesale overlay.
- `wholesale_overlay_carriers.csv`: four carrier parameter sets transcribed mechanically from pinned defaults, including initialization and start/stop ramps.
- `raw_fuel_parameter_audit.csv`: 261 field-level audit rows for all 29 raw fuel records, showing literal thermal-code effects without inventing units.
- `wholesale_overlay_candidates.csv`: 104 carrier/nameplate matches across January and July; missing eligibility flags are explicit, never assumed.
- `wholesale_overlay_candidate_summary.csv`: 52 candidate rows and 36,830 MW per month (36 CCGT, 7 OCGT, 3 coal, 6 oil).
- `frozen_metadata_manifest.csv`: hashes and original locations of the two frozen input extracts.
- `build_parameter_audit.py`: deterministic CSV audit builder; performs no optimization.

See `audits/V8R1_GB_PARAMETER_ADMISSION.md` for the full interpretation. Raw primary sources are retained under `.work/gb_upstream`, outside the publication archive. No upstream code was executed and no scientific solver was run for this audit.
