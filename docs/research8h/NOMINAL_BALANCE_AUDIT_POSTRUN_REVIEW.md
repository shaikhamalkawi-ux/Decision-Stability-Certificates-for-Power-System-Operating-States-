# Nominal balance audit: independent post-run review

Verdict: PASS for arithmetic reproduction, with a null infeasibility result. The independent replay used its own NPZ/NPY decoding and scaled-integer dyadic arithmetic, not the original Fraction checker. It matched all 672 hourly differences, all coefficient/RHS/box intervals and all 1,344 signed strict/expanded gaps. All 15 frozen inputs matched their size/hash before and after replay. No optimizer was used and no original artifact changed.

All four weeks have zero exactly redundant combinations, zero strict separating combinations and zero expanded separating combinations. Every difference contains 15 nonzero angle coefficients, but each right-hand side remains within its column-box range. This is evidence of exact representation-level nonredundancy without a box-based infeasibility certificate. It is not a feasibility proof, a general conditioning guarantee or a reason to relabel expanded witnesses as strict ones.

The complete result table, limitations and hash bindings are in `results/research8h/nominal_balance_audit/READOUT.md`; per-hour originals remain in `month_01.json`, `month_04.json`, `month_07.json`, and `month_10.json`. Independent evidence is `independent_replay.json` (SHA-256 `94651de2095f3555c7462101722155434b51b017cab383dfa164ddc6eebd9d74`), produced by `independent_replay.py` (SHA-256 `852614e1d77ee4f2b4c88b97edb04e6296e3984663f372750aecc453f9ce567d`).

The nominal replay completed before the seasonal cap prepared-archive review began. Its document writeup was deferred until after that gate, as requested. Seasonal target execution subsequently started only after the separate prepared review PASS; no target LP/MIP outcome is used by this balance diagnostic.
