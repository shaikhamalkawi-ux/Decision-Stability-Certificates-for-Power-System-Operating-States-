# Four seasonal reference attempts: one new verified reference

The frozen four-case experiment produced one new verified January binary DC-network reference. April, July and October reached their time limits without returned incumbents. Those three optimization attempts are UNKNOWN, not infeasibility results. Separately, the pre-existing repaired July schedule passed the exact new no-mean/no-cap model preflight, so verified physical seed schedules are currently available for January and July; this experiment did not establish new references for all four seasons.

| First week of 2020 | New MIP result | Verified incumbent fossil electrical MWh | Solver dual bound, MWh | Solver relative gap | Measured solve seconds |
|---|---|---:|---:|---:|---:|
| January | Time limit; verified reference | 22,964.941239556443 | 22,616.830716809134 | 1.5158345894% | 131.985 |
| April | Time limit; no incumbent | — | 42,178.564764400886 | unavailable/infinite | 121.304 |
| July | Time limit; no incumbent | — | 180,075.1924900012 | unavailable/infinite | 120.373 |
| October | Time limit; no incumbent | — | 123,931.33744939975 | unavailable/infinite | 128.881 |

Every solve used HiGHS 1.12.0, a configured 120-second limit, one thread, seed zero, default presolve and relative-gap target 1e-8. There were exactly four optimization calls, sequential in declared month order, without warm starts, tuning or reruns. Actual solve calls exceeded the configured limits slightly, totaling 502.543 seconds versus 480 seconds configured. Another independent single-thread MIP experiment and other work shared the host, so these timings are not a performance benchmark. None of the four cases establishes numerical optimality.

## Model and verification

The objective has exactly 3,864 unit coefficients, one for each of 23 fossil-unit hourly dispatches across 168 hours. Nuclear remains in the model with zero objective coefficient. The measure is fossil electrical MWh, not carbon emissions, fuel input or operating cost. Every individual-unit mean equality and the shared assembly's temporary fossil-cap row were removed. Four archived models were prepared and source-hashed before the first solve; all source/model hashes remained unchanged afterward.

Each model has 41 dispatch units, 24 thermal units, 24 buses, 38 lines, 34,680 rows, 23,016 columns, 141,724 nonzeros and 12,096 binary U/Y/Z columns. It follows the established fixed-hydro, no-shedding DC+UC interpretation: source availability, native minimum up/down times, nodal balance, continuous branch ratings, reference angle and ±pi angle bounds. Native hourly on/on ramps are analytically redundant for the 24 units and were checked directly. Startup/shutdown ramp restrictions, AC equations, contingency security and reserves are not added.

Initial status is free and mature, with Y0=Z0=0. Within-horizon changes incur native residence obligations only through the final modeled hour; no pre-horizon history, cyclic closure or post-horizon commitment is asserted. These boundary conventions matter when using the schedules in later experiments.

January passed both archived-matrix verification and the separate direct physical checker. Independent replay from the saved CSVs reproduced the NPZ vector exactly and verified native dispatch/status/transition/dwell/ramp behavior, all bus balances, line ratings, angles and objective. Maximum direct residual was 2.5510e-11 MW versus tolerance 1e-5; there were zero residence violations. Details are in `INDEPENDENT_WITNESS_REPLAY.md` and `month_01/witness_verification.json`. The source/model review is in `INDEPENDENT_SOURCE_REVIEW.md`.

The existing repaired July schedule has fossil energy 180,555.91891299986 MWh and passed the new complete no-cap/no-mean model before solving. This older schedule was not supplied as a warm start, counted as a new solver incumbent, or used to fill the missing outcome. Its checks are in `existing_July_witness_preflight.json`, with the original dispatch/commitment files bound in `input_manifest.csv`. July's physical feasibility is therefore already demonstrated separately despite the new optimization timeout.

## Usable artifacts and unresolved work

January's `month_01/candidate_dispatch.csv`, `candidate_commitment.csv`, `candidate_startup.csv`, `candidate_shutdown.csv` and `candidate_angles.csv` are the newly verified reference. The word candidate in their filenames preserves the uniform save convention; the passing result/check files establish their reference status. Raw values were retained rather than rounded or repaired after the solve.

All months retain their matrix, bounds, integrality, objective, native input arrays, timestamp/native-row mapping, metadata, logs and status. `summary.json`, `summary.csv` and `completion.json` preserve missing incumbent/gap values explicitly. The exact frozen runner/protocol hashes are `6844c70fdfe298d85cb2e247ca828cd3b0a1046f3bfc70f306743f74ac0e7805` and `c8d8612432e2f04fba9625af0629b74a99942f86a0deff4633b7fbf4795aff99`, respectively.

No energy-cap or permutation comparison was run. Obtaining April and October references, or improving the January/July reference objectives, requires a separately declared extension; no success or failure is inferred for those prospective experiments here.

To inspect returned archived vectors without optimization:

```text
python src/research8h_seasonal_reference.py --source-v3 PATH_TO_v8r1_rts_inputs --output results/research8h/seasonal_reference --verify-only
```

Normal execution refuses to overwrite the existing result directory. Use a fresh output location only for an explicitly separate reproduction run. This evidence was produced after Checkpoint01 and does not change that immutable archive.
