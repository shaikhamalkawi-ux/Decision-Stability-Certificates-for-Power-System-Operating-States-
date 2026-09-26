# Fixed-date Elexon sensitivity outputs

See `../../../docs/V8R1_ELEXON_SENSITIVITY_PROTOCOL.md` for the fixed design and
`../../../audits/V8R1_ELEXON_SENSITIVITY.md` for results and interpretation.
These candidate-revision outputs do not alter the published V8 release.

`pair_metrics.csv` contains all 16 January-by-July Wednesday comparisons in
both the pairwise and fixed eight-day coordinate universes. The boolean
`primary_ordinal_pair` identifies the four prespecified primary pairs.
Daily matrices contain signed average-MW B1610 outturns. No zeros were imputed
and negative observations were retained. The `PS` category and registry names
with station-demand wording occur within the production-flagged coordinate
set; the vectors should not be called uniformly nonnegative dispatch.

`verification.json` records exact replay of four original archived metrics,
32 independent transportation-LP cross-checks, and input-hash checks.
`baseline_and_provider_revisions.json` separates old/new byte changes from
quantity, settlement-run and key changes. `environment.json` records package
versions and the analysis-script digest.

To regenerate from frozen raw responses, use the script documented in the
audit. Raw response bodies are retained outside Git under
`.work/elexon_sensitivity/raw`; the acquisition register records the URLs,
retrieval dates and hashes. A future live fetch can be numerically revised
by the provider and is not assumed byte-identical to the frozen responses.
The original frozen registry and baseline raw responses are also required
for full original-versus-reacquired verification.

All secondary pairs reuse dates, so they are not independent samples. The
findings are descriptive; they are not a field intervention or a test of
chronological operational feasibility.
