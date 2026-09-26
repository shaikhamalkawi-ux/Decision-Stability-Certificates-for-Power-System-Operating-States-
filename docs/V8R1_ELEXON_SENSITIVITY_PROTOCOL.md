# V8R1 Elexon sensitivity protocol

Protocol fixed on 2026-09-26 before acquiring or examining the additional days.
This is a bounded, descriptive extension of the published two-day comparison.
The original January 11 / July 12 result is already known; this protocol is not
a preregistration independent of that prior result.

## Deterministic sample and comparisons

Use every Wednesday of January 2023 (4, 11, 18, 25) and July 2023 (5, 12, 19,
26). Fetch all eight days from the same B1610 streaming endpoint in this run,
including the two previously studied days. The four ordinal Wednesday pairs
are primary. All 16 January-by-July pairs are secondary descriptive sensitivity
comparisons; they reuse days and are not independent observations. Report no
p-values or population-wide confidence claims. Do not select dates or pairs
based on resulting gap sizes.

## Input and state definition

Preserve each successful HTTP body unchanged, with exact URL, retrieval time,
HTTP status, byte count and SHA-256. Preserve unsuccessful attempt metadata.
Use the original frozen `BMU_REFERENCE_ALL_2026-09-20.json` classification:
`bmUnitType == T`, `productionOrConsumptionFlag == P`, identifier starts `T_`.
This acquisition-date registry is not a historical 2023 registry snapshot.
Do not silently refresh classification. Copy and hash this original registry.

B1610 quantity is half-hour metered energy (MWh); multiply by two to obtain
average MW. Require all settlement periods 1--48 for a coordinate, finite
numeric quantities and no duplicate BMU/period keys. Missing/incomplete units
are excluded explicitly and listed, never filled with zero. Duplicate keys or
unexpected settlement dates/periods stop analysis rather than choosing a run.
Retain finite negative metered values as reported; list them and their units
as diagnostics, without inventing a clipping threshold. Record settlement-run
composition and all unit-level exclusions. A failed acquisition is reported
as missing; it is not replaced by an outcome-selected alternative date.

Primary metrics use the intersection of complete classified coordinates for
each pair. Repeat every comparison using the fixed intersection across all
eight days. Report universe sizes and the exact coordinate lists. These are
different observed fleet restrictions, not an imputation of unobserved units.

## Metrics and verification

For the 48 equally weighted half-hour states `x_s`, `y_t`, report
`M = sum_g |mean_s x_sg - mean_t y_tg|`; `W1` is the minimum mean full-coordinate
L1 matching cost, computed with the Hungarian assignment algorithm. Report
`G = W1 - M`, `100 G / W1`, the mean L1 cost pairing identical settlement-period
indices, and its difference from `W1` (MW and percent). No feasibility or
causal operating intervention is inferred from these descriptive distances.
Record assignments so that costs can be independently summed. Verify
`M <= W1 <= same-period cost` within numerical tolerance and cross-check each
assignment using an independent linear-programming transportation formulation.

Recompute the original two-day metrics from the original frozen responses,
compare with archived metrics, and then compare reacquired values against the
old responses on common BMU/period keys. Report row/key changes, settlement-run
changes, changed quantities and maximum/total absolute quantity changes.
Separate provider revisions from the effect of adding days or fixing the
coordinate universe. Raw-byte changes alone are not numerical revisions.

Summarize primary and secondary comparisons separately using counts, ranges
and medians, retaining the complete per-pair results. Report variation as well
as recurrence, including zero or reversed findings if present. Numerical
nonnegativity of `G` follows the inequality; whether it is substantively large
is an empirical observation and must not be presented as an independent test
of the inequality. This sample does not establish chronological feasibility,
annual robustness, weather-adjusted seasonality or applicability to every GB
unit. The January and July samples include calendar-specific conditions.

## Reproduction

The companion `src/v8r1_elexon_sensitivity.py` implements acquisition and
analysis with explicit input/output directories. Store new raw responses under
`.work/elexon_sensitivity/raw`; store derived results, diagnostics, acquisition
register and environment versions under `results/v8r1/elexon`. Preserve the
existing published release unchanged.
