# Elexon source/query register

Provider: Elexon Insights API v1  
Base URL: `https://data.elexon.co.uk/bmrs/api/v1`  
Acquisition date: 2026-09-20  
Selected settlement dates: 2023-01-11 and 2023-07-12

Dataset responses were fetched with:

`/datasets/{DATASET}/stream?from={DATE}T00%3A00Z&to={DATE}T00%3A00Z&settlementPeriodFrom=1&settlementPeriodTo=48`

for `B1610`, `PN`, `MELS`, `MILS`, `MNZT`, `MZT`, `RURE`, and `RDRE`.

The BMU registry was fetched from `/reference/bmunits/all`.

Effective dynamic/rate snapshots were fetched from:

- `/balancing/dynamic?bmUnit={BMU}&snapshotAt={DATE}T00%3A00Z`
- `/balancing/dynamic/rates?bmUnit={BMU}&snapshotAt={DATE}T00%3A00Z`

for `T_KEAD-2`, `T_LBAR-1`, `T_TORN-2`, `T_DRAXX-2`, `T_SPLN-1`,
`T_HRTL-2`, `T_HEYM28`, `T_SHBA-1`, `T_PEMB-41`, `T_PEMB-11`,
`T_STAY-1`, and `T_STAY-3` on both dates.

`analysis/input_sha256_register.csv` is authoritative for the byte counts and
hashes of every admitted raw response. `code/acquire_elexon_evidence.py`
reconstructs the exact endpoint family and writes a timestamped URL register on
a fresh acquisition.
