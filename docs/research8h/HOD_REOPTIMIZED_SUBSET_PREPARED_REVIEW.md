# Independent prepared gate: fixed HOD subset LPs

Verdict: PASS for the frozen preparation and code, with zero optimizer imports or calls by the reviewer. This does not report target outcomes or authorize execution independently of root's required GO.

Reviewed source SHA256: `3c9d03015a23a277c0f4642be696843d17f2540bac2a2116247e11e0d80f8041`. Protocol SHA256: `eafa85dba6f772668a263f19f37eac086915cb1d6d599fabdc91ebac097ff0d2`. Prepared manifest SHA256: `1d3c54426828dcca5684ca21d6f1af95f2c05cfc87631423ae939a354c867119`.

The independent preparation checker imports only the reviewed NPZ/exact-point kernel, not the producer or its rule implementation. It verified all 155 new frozen bindings and the unchanged 106-entry fixed-ray and 125-entry HOD manifests. All hashes matched before and after review; the execution marker was absent at both checks.

For each of the four fixed models, the reviewer derived the retained row set from parent labels and actual sparse coefficient support. The two-CC rule retains temporal rows only for the two declared generator IDs and every static/network/cap row. The locality rule checks every nonzero state coordinate's actual hour and retains dwell rows only when all those hours lie from 60 through 107, while retaining transition/exclusivity and all static/network/cap rows globally. The independently obtained row counts are 19,985 and 28,689; locality retains 1,023 up and 1,001 down rows.

Every actual retained sparse row, row bound, parent-row index and semantic label matched. All column boxes, generator/bus/column metadata and the original 12,096-coordinate U/Y/Z masks matched. All six files for each model were byte-identical to their already frozen predecessor archives: 24 copy pairs. Each cap is 23,195 MWh with exactly 3,864 coefficient-one entries over the declared 23 fossil generators, excluding nuclear. There are no new subset rules or narrowed variable boxes.

Both full positive controls were independently replayed with the original binary mask and exact `Fraction.from_float(1e-5)` bound expansion. Both pass expanded membership and fail strict membership. All four copied control/rule row maps equal the independently derived restrictions, so exact subset feasibility follows with unchanged columns and boxes. The control denominator is two inputs and four memberships, with no new solve.

The final source includes the requested second clock check after writing the initial launch decision and immediately before `solver.run`; it checks both phase time and UTC time remaining. The four-entry schedule, LP30 settings, no-retry/no-recovery-solve routing, continuous-only interpretation, raw-then-sign-projected certificate candidates and contradiction gate match the protocol. The selected proof is always rechecked against the complete restricted model.

The optional energy arithmetic is also sound. If the cap multiplier is `-s < 0`, removing the cap and dividing other multipliers by `s` yields the fossil-objective residual bound. Its expanded value equals `B + tau + expanded_gap/s`; the source also independently recomputes the finite-box residual correction and widened endpoints. The term `+tau` is required because the cap row itself was widened in the original separation. An accepted lower bound is not an optimum or an upper witness, and the unnormalized ray gap is not MWh.

Machine-readable evidence and reviewer source are in `results/research8h/hod_reoptimized_subsets_independent_review/prepared_review.json` and `prepared_review.py`. The single preparation review exited 0. Post-run proof/point, support, normalized-bound, hash and solver-accounting review remains required before publication.
