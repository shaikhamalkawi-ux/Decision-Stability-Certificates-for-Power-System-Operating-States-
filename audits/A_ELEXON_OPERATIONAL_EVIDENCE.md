# Workstream A - Elexon operational evidence

## Gate decision

**ADMIT as observational evidence; do not label as a field experiment, causal
redispatch estimate, or chronology-feasibility test.**

The frozen public evidence uses Elexon Insights B1610 generation outturn for two
matched weekdays, Wednesday 11 January 2023 and Wednesday 12 July 2023. Both
days contain 48 half-hour settlement periods and all B1610 rows used the DF
settlement run. B1610 quantities are MWh per half hour and were divided by
0.5 h (multiplied by two) before being interpreted as average MW.

## Primary result

On 260 common, complete transmission-connected production BMU coordinates:

| Quantity | Result |
|---|---:|
| Atoms per day | 48 |
| Mean movement, M | 19,553.647583 MW |
| Empirical L1 W1 | 20,776.837250 MW |
| Shape gap | 1,223.189667 MW |
| Shape share | 5.8873% |
| Same-settlement-period W1 | 21,016.487667 MW |
| Settlement-period premium | 239.650417 MW (1.15345%) |

The 268-coordinate union, with absent coordinates zero padded, changes both M
and W1 by 2.081792 MW and leaves the shape gap unchanged to numerical
precision. The result is therefore not created by dropping July-only units.

Physical Notifications were integrated piecewise linearly over each complete
1,800-second settlement period. The mean period-level L1 difference between PN
and settled outturn was 3,461.403181 MW in January (249 complete coordinates)
and 3,141.137250 MW in July (252 complete coordinates). These are descriptive
notification-to-outturn discrepancies, not causal redispatch volumes.

For twelve deterministically selected high-movement non-wind/solar BMUs, the
archive also freezes effective snapshots of MNZT, MZT, RURE, and RDRE data.
Those samples show that nonzero operational parameters are present in the live
data model, but they are not a complete-system chronology calibration.

## Evidence boundary

- The acquisition-date BMU reference table (20 September 2026) was used to
  classify 2023 BMUs. It is not asserted to be a historical 2023 registry.
- The comparison is two matched weekdays. It demonstrates an operational-data
  instance of mean/shape/conditioning sensitivity, not population generality.
- B1610 exposes the latest available settlement-run value for each BMU/period.
- Negative B1610 values are retained; they are published metered quantities and
  were not silently clipped.
- No claim is made that the PN-to-outturn discrepancy was caused by a specific
  balancing action or by chronology constraints.

## Reproducibility

Raw responses, derived tables, a file-hash register, acquisition code, and
analysis code are included under `results/elexon_operational_evidence` and
`code`. The public endpoint family is Elexon Insights API v1. No API key is
required by the provider.

Final-package rerun check: the released analysis script was executed against
the packaged raw directory, and all fourteen derived CSV/JSON outputs matched
the admitted copies byte-for-byte by SHA-256.
