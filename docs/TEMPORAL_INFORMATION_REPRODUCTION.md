# Reproduce the temporal-information pilot

Research branch: `codex/temporal-information`. The existing V8R1 candidate
manuscripts and V8 release are unchanged. This pilot has not been deposited as
a new Zenodo version or submitted to a journal.

## Recorded findings

| Test | Cases | Recorded outcome |
| --- | ---: | --- |
| Repaired July identity | 1 | Verified feasible network/chronology witness |
| Frozen interior permutations, single-unit screen | 16 | 16 UNKNOWN, including all four confirmed negatives |
| Full chronological MILP, preselected first four permutations | 4 | 4 Infeasible |
| Strict represented-unit energy pooling, original weeks | 8 | 8 Infeasible |
| Same pooling, first four permutations | 4 | 4 Infeasible; pooled identity witness passes |
| Independently assembled continuous relaxation | identity + 4 | Identity feasible; four exact binary64 Farkas rejections |
| Greedy explanation extraction on previously inspected weeks | 8 | Seven cores with 1, 2, 1, 1, 3, 1, 5 status atoms; June UNKNOWN |

Only the first four permutations were selected for complete solves. The other
twelve remain unresolved. All permutations share one July week; no independent
population accuracy estimate follows. The first eight / last eight seed split
applies to the unchanged single-unit screen only. Pooling and LP strengthening
are transparently labeled post-pilot development, not held-out evaluation.

The original row packages include nodal demand and embedded PV, complete
generation availability, and witness dispatch/commitment. Inverse permutation
restores the package arrays exactly. All 41 target means stay fixed. First and
last 48 hours are unchanged. This preserves the specified order-free joint
empirical law, not lag distributions or clock-hour conditioning in the new order.

## Environment and inputs

Python 3.12, with the pinned numeric environment in `src/requirements-v8r1.txt`:
NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1, HiGHS/highspy 1.12.0. The optional plot
requires Matplotlib. Inputs use the same pinned RTS commit and hashed CSVs as
V8R1; no targets are reoptimized during preparation.

```bash
python -m pip install -r src/requirements-v8r1.txt
python src/v8r1_prepare_rts_inputs.py --output .work/v8r1_rts_inputs --report .work/temporal_input_reconstruction.json
```

Preparation downloads eight pinned public CSVs with verified TLS and SHA-256,
copies the published target tables and restores the native model. The complete
repaired positive witness is already in `results/v8/network_repair/`. Historical
absolute paths in run manifests identify the author's input locations; the
portable commands above reconstruct those inputs under the current checkout.

## Verify the archived linear certificates without optimization

```bash
python src/temporal_lp_certificate.py --verify-archived
```

This reads archived matrices, bounds, witnesses and hexadecimal multipliers;
checks their bindings; and recomputes the separating inequality using exact
Python fractions. It writes `independent_archive_replay.json` in that result
directory. HiGHS is not imported or invoked by this mode. Matrix-to-source
reconstruction is a separate check; arithmetic replay alone does not establish
that arbitrary supplied model matrices encode the claimed physical system.

The proof is exact for the archived binary64 coefficients. Its positive margin
also survives an outward `1e-5` relaxation of every finite row and variable
bound in that bound's units. These units are mixed; this is numerical robustness,
not a physical uncertainty radius. Raw solver rays with inadmissible signs are
rejected; a sign-projected candidate is accepted only after exact rechecking.
See the LP execution notes for all attempts and the actual solver limit.

Reconstruct the five archived LP models from the prepared native inputs, recheck
all 17 permutation/control maps, and reread all seven historical status cores:

```bash
python src/verify_temporal_information.py --source-v3 .work/v8r1_rts_inputs --report .work/temporal_reconstruction_verification.json
```

This also invokes no optimizer. The recorded author run passed all five exact
matrix/bound comparisons, four rational negative certificates and seven cores.

## Regenerate the fixed experiment

Use fresh output directories to preserve the archived evidence:

```bash
python src/check_temporal_core.py --output .work/temporal_checker_validation.json
python src/temporal_information_pilot.py --source-v3 .work/v8r1_rts_inputs --output .work/replayed_twins
python src/temporal_equivalence_audit.py --source-v3 .work/v8r1_rts_inputs --output .work/replayed_equivalence
python src/temporal_equivalence_audit.py --source-v3 .work/v8r1_rts_inputs --twins --output .work/replayed_equivalence_twins
python src/temporal_existing_cores.py --source-v3 .work/v8r1_rts_inputs --output .work/replayed_existing_cores
python src/temporal_lp_certificate.py --source-v3 .work/v8r1_rts_inputs --output .work/replayed_lp_certificate
```

The pooled-twin and LP commands deliberately read the **committed** permutation
maps and group definition, rather than select new cases from regenerated results.
Regeneration can change solver timings and dual rays; compare valid witnesses,
verdicts, matrix definitions and checked contradictions, not wall-clock equality.
No computational speedup claim is made from these small runs.

Optional figure:

```bash
python -m pip install matplotlib
python src/plot_temporal_information.py --source-v3 .work/v8r1_rts_inputs --output .work/temporal_figures
```

## Evidence boundaries

Strict groups match 55 non-identity source columns, base cost and full-year
availability profiles. Both identifier fields and an artificial index cost tie
breaker are excluded. Unit-specific placeholder emissions are disclosed; actual
emissions equivalence is not asserted. Only weekly energy equalities are pooled;
all physical units and their chronology remain separate.

The small status cores belong to the old development corpus. They are
inclusion-minimal for the selected unit and fixed energy bounds, not globally
minimum-cardinality. Deriving a single retained status can depend on all 168
hours and all generators. The independent count checker validates the temporal
contradiction; it does not independently reimplement all bound propagation.

The new four negative cases require the stronger full-model evidence. Their LP
certificates use 656--1,017 row multipliers spanning 163--168 hours, plus
variable-bound terms and global energy constraints. They do not demonstrate
minimum memory or data compression. The pilot
establishes a model counterexample and a limitation of the cheap screen, while
leaving the minimum-information research question open.
