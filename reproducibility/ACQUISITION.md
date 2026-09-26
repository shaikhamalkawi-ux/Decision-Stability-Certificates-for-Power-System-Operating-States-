# Access to upstream inputs omitted from this snapshot

## RTS-GMLC

Official source: https://github.com/GridMod/RTS-GMLC

Pinned commit: `3ece0d3725c844056132393ee252b3083dd4eab4` (V0.2.3 lineage).
Acquire the relevant `RTS_Data/SourceData` and `RTS_Data/timeseries_data_files`
files directly from the pinned repository. The omitted raw-file SHA-256 values
and original source filenames are in
`provenance/omitted_and_derived_input_sha256.csv`. No project-wide reuse license
for RTS-GMLC has been asserted by this snapshot; obtain and observe the source
terms. Raw RTS-GMLC files and the legacy full-package archive are not included.

## PyPSA-GB

Official source: https://github.com/andrewlyden/PyPSA-GB

Pinned commit: `8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`.
Use `provenance/pypsa_gb_scenario_freeze.yaml` and the generation environment
record to identify the Jan/Jul 2020 Reduced 32-bus LP scenarios. Obtain source
models, external data, and their licenses from that repository. The included
dispatch CSVs are frozen outputs. This snapshot does not package all dependencies
or claim that upstream model regeneration is a one-command operation. Original
generator metadata is omitted; a minimal derived carrier-classification table
and the original metadata hashes are provided.

## Elexon Insights

Official API documentation: https://developer.data.elexon.co.uk/
Base URL: https://data.elexon.co.uk/bmrs/api/v1

The exact datasets, dates, endpoint families, and selected BMUs appear in
`provenance/ELEXON_SOURCE_QUERY_REGISTER.md`. Use:

```bash
python code/acquire_elexon_evidence.py --help
python code/analyze_elexon_evidence.py --help
```

For example, download fresh responses to `local_elexon_raw`:

```bash
python code/acquire_elexon_evidence.py local_elexon_raw
```

No API key is required. Original raw responses are omitted. Compare fresh
downloads with `provenance/elexon_input_sha256_register.csv`; mutable upstream
responses may no longer match the frozen 2026-09-20 acquisition. A mismatch must
be reported as a new acquisition, not silently substituted for the original.
The acquisition script records the exact URLs, timestamps, and hashes.

The original analysis used `BMU_REFERENCE_ALL_2026-09-20.json`. For a fresh
acquisition, pass the actual dated registry filename explicitly, for example:

```bash
python code/analyze_elexon_evidence.py local_elexon_raw local_elexon_analysis --reference-file local_elexon_raw/BMU_REFERENCE_ALL_2026-09-26.json
```

Replace the example date with the actual filename created by acquisition. The
public script adds this optional input-path argument; its numerical analysis is
unchanged. Never relabel fresh responses as historical frozen responses.

## Scope of hashes

The hashes document byte identity and source lineage. They do not confer reuse
rights or show that a source was scientifically admissible. This archive checks
selected saved-output arithmetic and retains scientific corrections pending.
