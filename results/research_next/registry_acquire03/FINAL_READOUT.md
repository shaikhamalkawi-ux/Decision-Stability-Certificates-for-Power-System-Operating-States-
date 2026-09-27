# Registry-only acquisition 03 — closed

The single authorized run finished `READY_PINNED_REGISTRY_ARCHIVE_ONLY` (process exit 0). Source and protocol remained unchanged. The preserved incomplete attempt02 archive also remained unchanged.

- Actual phase: 2026-09-27 09:26:56.016103–09:28:23.016824 UTC; 87.0004604 seconds, zero allocation overrun. Exec session 61272; owned curl PID 21108 exited normally without termination.
- Exactly one curl invocation: normal TLS verification, HTTP 200, no redirects, no retries or continuation. Selected public transport fields are in the receipt; raw headers and diagnostics remain private.
- Archive: 11,820,236 bytes, SHA256 `53e48326acc56f53ac4527a41e7362a29622d3bf9d406234c5ddc05566869211`.
- Gzip full EOF/CRC/ISIZE and tar safety checks passed: 87,080,960 decoded bytes, 75,641 tar members, 61,167 regular files, 28,433,677 payload bytes, 8,192 zero tail bytes. No links, special or sparse members were admitted. There was no filesystem extraction.
- Reconstructed Git tree `f39bab42a09b8a82574435c6e402e598b3200dc3` exactly matches official General commit `416a13c3e4888af4b245812d8f4ab040a042c38f`.
- Julia invocations, Pkg calls, model builds and optimizer calls: all zero. This resolves registry acquisition only. Environment compatibility and official native coefficient-export fidelity remain untested.

Authoritative producer receipt: `run01/receipt.json`, SHA256 `86eeaf107b46baaabd4abc88b54507b934822956d18d0d917e4ccda2682788d5`. Full file inventory: `run01/registry_file_inventory.json`, SHA256 `cc8d9ce6757ffc70a1347ab3bf9e74a2bbaba87f4131bb3737746a52c19f0f42`.

The private archive is `.work/researchnext_julia_export/registry_acquire03/General.tar.gz`. It and closed attempts01/02 must remain unchanged. The next step is a separately reviewed fresh setup driver following `docs/research_next/JULIA_AFTER_REGISTRY_SETUP_PLAN.md`; that plan has not been executed and no setup follows this acquisition automatically. No Git or external publication occurred in this subtask.
