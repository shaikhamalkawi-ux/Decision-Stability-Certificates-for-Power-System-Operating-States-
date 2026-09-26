# V8R1 fixed-date Elexon sensitivity audit

Completed 2026-09-26. **PASS for the stated descriptive experiment and its
numerical checks. This is not a chronological-feasibility or submission-readiness
certificate.** The published V8 release and its raw evidence were not modified.

## Concrete extension

The protocol in `docs/V8R1_ELEXON_SENSITIVITY_PROTOCOL.md` was written before
acquiring or examining additional days. It selects every Wednesday in January
and July 2023: January 4, 11, 18, 25 and July 5, 12, 19, 26. The original
January 11 / July 12 result was already known; this is not an external
preregistration independent of that result.

All eight days were acquired anew from the Elexon B1610 stream, preserving
466,544,910 raw response bytes with exact URLs, timestamps, status and SHA-256.
The original acquisition-date registry was copied and hash-checked. Two
concurrent downloads were used. Eight initial requests using a separate CA
bundle failed local certificate-chain validation; the successful acquisition
used Python's default SSL context and OS trust store with verification enabled.
Failed-attempt metadata is retained. No dates were replaced and no SSL checks
were disabled.

The four ordinal Wednesday pairs are primary. All sixteen January-by-July
pairs are secondary descriptive comparisons and are not sixteen independent
observations. Each comparison was repeated on the common fleet across all eight
days. No p-values or annual/population-wide inference are reported.

## Primary results

The states are **signed B1610 registered-generation BMU outturns**, converted
from half-hour MWh to average MW. `M` is the L1 distance between daily mean
vectors; `W1` is optimal equally weighted full-coordinate L1 matching; `G=W1-M`.
The period premium is the same-settlement-period L1 cost minus unrestricted
`W1`. Percentages use `W1` as denominator.

| January / July 2023 | Common BMUs | M (MW) | W1 (MW) | G (MW) | G/W1 (%) | Period premium (MW) | Premium/W1 (%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4 / 5 | 259 | 16,056.269 | 17,170.445 | 1,114.176 | 6.4889 | 268.614 | 1.5644 |
| 11 / 12 | 260 | 19,553.648 | 20,776.837 | 1,223.190 | 5.8873 | 239.650 | 1.1534 |
| 18 / 19 | 260 | 19,570.993 | 20,951.370 | 1,380.376 | 6.5885 | 369.895 | 1.7655 |
| 25 / 26 | 260 | 16,178.164 | 18,716.087 | 2,537.924 | 13.5601 | 461.713 | 2.4669 |

The primary shape share ranges from **5.8873% to 13.5601%**, median 6.5387%.
The primary same-period premium ranges from **1.1534% to 2.4669%**, median
1.6649%. The original pair is therefore neither representative of a fixed
universal percentage nor an isolated example of a substantial shape gap.

Across all sixteen nonindependent cross-pairs, shape gaps range from 877.101
to 2,666.356 MW (3.4608%--13.5601%, median 7.0548%). Period premiums range from
196.439 to 2,010.440 MW (0.7463%--9.3549%, median 2.1162%). The substantial
variation should be retained in the interpretation, rather than reporting
only that all gaps are positive. Nonnegativity follows the metric inequality;
the observed size and date dependence are the empirical findings.

The fixed eight-day intersection contains 259 BMUs. Its primary shape shares
are 5.8913%--13.5663%, median 6.5405%; the maximum shape-gap change across all
sixteen pairs is only 0.087917 MW, and the maximum share change is 0.010060
percentage points. Same-period premiums in MW are unchanged to reported
precision. The one coordinate present in the original 260-BMU pair but absent
from the fixed intersection is `T_LARKS-1`. Thus the observed variation across
these dates is not explained by the 259-versus-260 coordinate difference.

## Input diagnostics and interpretation corrections

January days have 259, 260, 260 and 260 complete classified coordinates;
July days each have 268. Every retained coordinate has all 48 periods. No
classified duplicate BMU/period keys, incomplete observed units, nonfinite
quantities or unexpected periods/dates were found. All returned settlement-run
types are `DF`. Registry IDs absent for an entire day are listed explicitly
(83/82 in January and 74 in July), rather than padded with zeros.

The frozen registry contains 343 selected rows but 342 unique BMU IDs.
`T_WLNYO-4` has two EIC aliases with identical classification, name and fuel
labels. Both source rows are retained in diagnostics; the identifier set has
one coordinate, as in the original analysis. No conflicting classification
labels were found.

Across the eight days, 24,052 classified half-hour values are negative and
are preserved without clipping. All twelve `PS`-coded units are included in
every day's complete fleet and the fixed intersection. The most negative
observation is `T_DINO-3`, registry name Dinorwig 3, `PS`, at -299.4 MW on
January 11; that day also includes Dinorwig 5 at -288.0 MW, Dinorwig 6 at
-286.5 MW and Dinorwig 2 at -284.3 MW. Current-registry names elsewhere include
BP Load and Heysham 2 Station Demand, with unspecified fuel fields. These
records justify the signed-outturn description. Production classification
alone does not establish a nonnegative generator dispatch vector, and signs
or names alone do not establish a specific physical cause.

The registry is a 2026 acquisition-date classification, **not** a historical
2023 registry. These results do not establish chronological admissibility,
explain causal changes in station operation, control weather, or establish
annual robustness. They strengthen the observed-data evidence only for the
specified months, weekday and coordinate definitions.

## Provider revisions and verification

The two original dates were reacquired consistently with the six additional
days. Their raw bytes/hashes differ from the original archive, but there are
**zero** changed BMU/period keys, quantity values or settlement-run labels
across all 252,912 January rows and 253,728 July rows. The four archived
metrics reproduce exactly, with absolute difference zero. Therefore the
expanded-date findings are not explained by numerical revisions to the
original pair. This comparison does not assert equality of every other
metadata field or byte serialization.

All 32 sensitivity calculations (16 pairs, two coordinate universes) satisfy
`M <= W1 <= same-period cost` and agree with independent continuous
transportation-LP solutions. The largest LP-versus-Hungarian difference is
1.0914e-11 MW. The original frozen baseline also passes the LP check
(3.6380e-12 MW difference). Eight new input hashes and registry identity were
verified. These numerical checks do not substitute for the scientific limits
stated above.

## Files and reproduction

- `src/v8r1_elexon_sensitivity.py`: guarded acquisition and full analysis.
- `results/v8r1/elexon/pair_metrics.csv`: all 32 comparisons, without selecting
  favorable outcomes.
- `sensitivity_summary.json`, `verification.json`,
  `baseline_and_provider_revisions.json`: summaries, checks and revision counts.
- `daily/`: complete signed-MW matrices, excluded IDs and negative observations.
- `classified_registry_units.csv`, `registry_duplicate_identifier_rows.csv`,
  `registry_fuel_coverage_by_day.csv`, `negative_outturn_unit_summary.csv`:
  transparent fleet and sign diagnostics.
- `optimal_transport_assignments.csv` and `pair_coordinate_universes.csv`:
  independently summable matchings and exact coordinates.
- `acquisition_register.json`, `acquisition_attempt_history.json`,
  `analysis_input_sha256_register.csv`, `environment.json`: provenance.

Run from the repository root, with the original frozen directory containing
the registry and original two B1610 responses:

```powershell
python src/v8r1_elexon_sensitivity.py --original-raw ORIGINAL_RAW --acquire --analyze
```

Existing successful downloads are reused only after hash verification;
the original raw directory cannot be the new acquisition directory. New raw
payloads are retained locally under `.work/elexon_sensitivity/raw`, which is
Git-ignored. Derived CSVs and reports are candidate-revision artifacts;
neither a new GitHub release nor a Zenodo version was published in this task.
