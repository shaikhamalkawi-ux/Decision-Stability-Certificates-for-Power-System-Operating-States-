# Efficient infrastructure attempt — closed before Julia

The single run ended `SETUP_FAILED_PRESERVED_NO_RETRY`, exit 1, at 2026-09-27 10:31:59.535445 UTC. It started 10:01:59.364875 UTC and consumed 1800.1696561 seconds, with 0.1696594 seconds reported overrun. The exception was the fixed 1800-second allocation expiring during `full_registry_content_tree_readback_before_Julia`.

All 61,167 admitted regular files and 14,474 directories including the root were materialized from the already verified archive. The extractor matched each payload's archive size, mode and SHA256 to the frozen inventory, used exclusive creation, and checked the written file's type/reparse flags and size. Extraction finished at 10:11:29.091633 UTC (phase elapsed 569.7261302 seconds). The subsequent complete on-disk content/tree readback **did not finish and was not admitted**. Successful archive admission and completed extraction must not be described as completed on-disk tree verification.

Julia invocations, Pkg attempts, scientific model builds and optimizer calls are all zero. No Julia launch record or package marker exists; the package phase was never entered, so private Julia logs are empty. There is no package compatibility result or resolved environment. The official native coefficient comparison remains untested.

Source, protocol and admitted archive were unchanged at closure. The materialized registry and all partial outputs remain preserved; no repeat extraction, setup restart or scientific call followed this outcome. The authoritative receipt is `ENVIRONMENT_ACQUISITION.json`, SHA256 `bdfae531e4721bf617444d1014e6d3917b93468d10e1472056511e42017c5989`.

A new source-only proposal may explicitly narrow the local-registry trust contract and reuse this completed extraction. It must retain the incomplete-readback limitation and non-adversarial local mutation/storage assumption, keep normal TLS and all scientific pins, and receive a separate source/execution gate. The closed attempt and its stronger unfulfilled readback requirement remain immutable.
