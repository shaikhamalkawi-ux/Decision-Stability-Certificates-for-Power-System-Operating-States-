# Data dictionary

All dispatch and repair quantities below are in MW unless named otherwise.
These are generated research outputs, not redistributions of upstream raw
network/time-series inputs. Original generator coordinate names are retained
for traceability.

| Path | Rows / meaning | Required columns / units |
|---|---|---|
| `data/processed/rts/month_*_first_week_dispatch.csv` | Hourly generated RTS Area-1 dispatch, first week of the named month | `timestamp`; generator coordinate columns in MW. Identical column order defines comparisons. |
| `data/processed/gb/{january,july}_generator_dispatch.csv` | Hourly generated PyPSA-GB LP dispatch for Jan/Jul 1-7, 2020 | First column is timestamp; generator columns in MW. |
| `data/processed/gb/coordinate_classification.csv` | Derived classification of coordinates common to Jan/Jul | `name`, `carrier`, `included_internal_coordinate`. Exclude `EU_import`; 2,685 internal coordinates remain. Carrier is derived from the frozen metadata, using July on duplicate names. |
| `data/processed/chronology/native_minud_repair_month_07.csv` | Generated mean repair per coordinate | `generator`, `target_mean_MW`, `repaired_mean_MW`, `delta_MW`, `abs_delta_MW`. Summed absolute change is 8.020508464286115 MW. |
| `data/processed/network_repair/network_repair_mean.csv` | Generated feasible network repair witness | `target`, `repaired`, `delta`, `abs` (MW); sum `abs` is approximately 11.9262964643 MW. Arithmetic alone does not verify witness feasibility. |
| `data/processed/ac_shared/ac_projection_results.csv` | Saved per-hour solver outcomes | `month`, `success`, `restoration_L1_MW`, and solver/residual fields. Only saved successful witnesses enter each reported median. |
| `data/processed/elexon/b1610_operational_evidence_metrics.*` | Derived matched-day operational summaries | Source units converted from half-hour MWh to average MW before computing L1 metrics. See metric names and acquisition/analysis code. |
| `data/processed/elexon/b1610_optimal_transport_matching.csv` | Derived matching of Jan 11 / Jul 12, 2023 settlement periods | Matched period identities and per-pair L1 transport cost in MW. |
| `data/processed/elexon/b1610_mean_coordinate_changes.csv` | Derived per-BMU means and changes | BMU identity and Jan/Jul mean outputs and absolute differences in MW. |

The upstream metadata hash records establish which classification inputs were
used, but those original files are not redistributed. The archived arithmetic
checks are reproducible directly from this schema; regeneration from upstream
models and validation of all scientific statements remain separate tasks.
