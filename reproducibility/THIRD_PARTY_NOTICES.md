# Third-party sources and rights

The archive's MIT and CC BY 4.0 licenses cover only author-owned contributions.
They do not relicense upstream datasets, software, trademarks, or other rights.
Raw third-party data and original third-party metadata have been excluded.

## Elexon

Contains BMRS data © Elexon Limited copyright and database right 2023-2026.

The Elexon-derived tables come from public Insights API outputs for the dates
and query families listed in the source register. The underlying information
remains subject to Elexon's terms, including applicable third-party exclusions.
Source/license: https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/
API: https://developer.data.elexon.co.uk/
The archive makes no claim that Elexon endorses the research.

## PyPSA-GB

PyPSA-GB, Andrew Lyden and contributors, pinned commit
`8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`.

The pinned software license is MIT, copyright (c) 2022 Andrew Lyden; its license
also identifies ESPENI and ERA5 data as CC BY 4.0. No source software or raw
ESPENI/ERA5 data is redistributed here. Frozen generated dispatch and a derived
carrier classification are provided to support arithmetic inspection.
Pinned source license:
https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/LICENSE

## RTS-GMLC

RTS-GMLC, Grid Modernization Lab Consortium and contributors, pinned commit
`3ece0d3725c844056132393ee252b3083dd4eab4`.
https://github.com/GridMod/RTS-GMLC

Original network data and time-series inputs are omitted. Included dispatch
matrices are the research authors' generated optimization outputs. This archive
does not assert a license for the upstream repository or reproduce its raw data.

## Numerical dependencies

NumPy, pandas, SciPy, and requests are installed separately under their own
licenses. This archive does not include their source or distribution binaries.
