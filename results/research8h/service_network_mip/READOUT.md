# Four full-network service MIPs: unresolved

All four prescribed MIPs reached their time limits without a feasible incumbent.
Each therefore has verdict **UNKNOWN**. No binary-network admission and no
numerical or exact infeasibility conclusion was obtained by this arm.

| Ordinary twin | Solver status | Configured limit (s) | Actual call time (s) | Verdict |
|---|---|---:|---:|---|
| seed_26092600 | Time limit reached | 120 | 190.287427 | UNKNOWN |
| seed_26092601 | Time limit reached | 120 | 127.777051 | UNKNOWN |
| seed_26092602 | Time limit reached | 120 | 188.205085 | UNKNOWN |
| seed_26092603 | Time limit reached | 120 | 197.737501 | UNKNOWN |

There were exactly four optimization calls and no retries, warm starts, or
adaptive changes. HiGHS 1.12.0 ran with one thread, seed zero, presolve on and
a zero objective. The configured total was 480 seconds; measured solver-call
time was **704.007064 seconds**, an overrun of 224.007064 seconds. The configured
HiGHS limit did not impose a strict wall-clock cutoff. Original logs retain the
solver's own timing and no-incumbent status; measured overruns are not hidden or
recast as 120-second execution times. Each run reported zero processed MIP nodes.

Each model contains 34,681 rows, 23,016 columns, 145,588 nonzeros, and 12,096
binary U/Y/Z coordinates. The exact native joint permutations reconstruct the
hourly availability, fixed hydro, aggregate load and nodal load inputs. The unit
matrix and bounds exactly reproduce the corresponding archived continuous
service model before appending full 24-bus/38-branch DC rows and bus angles.
Every model preserves the shared 180555.9189139999 MWh fossil-energy cap and
contains zero individual generator-mean rows. The cap has exactly 23x168
coefficients of one, excludes `121_NUCLEAR_1`, and uses no emissions factors.

Before any MIP call, the original reference passed both this unfixed model and
the independent native physical checker, including direct dwell, transitions,
on/on ramps, reconstructed DC flows and the shared service cap. Its largest
network/matrix residual was 7.96e-12. This preflight validates the assembled
identity model; it does not establish a witness for the four permuted inputs.

The native ramp-versus-output-range proof holds for all 24 thermal units, with
minimum margin 30 MW. The archived models and integrality masks passed separate
solver-free structural checks in `model_archive_checks.json`. All 55 frozen
input/model files match their recorded sizes and SHA-256 values in
`final_input_hash_check.json`. The script and prospective protocol were not
edited after launch.

The failed all-on LP remains a separate fixed-commitment restriction. Likewise,
the earlier four exact negative certificates retain their original individual
generator-mean specification, while the five continuous service-budget LPs
remain verified positive relaxations. These MIP timeouts resolve neither side
of the unrestricted binary-network service question. Any later fixed-reference
LP restriction is a distinct prospective arm, not a revision of these outcomes.
