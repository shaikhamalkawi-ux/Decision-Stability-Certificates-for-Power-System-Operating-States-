# Original research computation scripts

These author-written research scripts are preserved from the V8 source tree.
They include chronology, network-repair, solver-witness, AC-restoration,
replication, and frozen-input auditing routines. They are provided under the
MIT license in the archive root. This directory is a historical source snapshot;
scientific and editorial corrections remain pending.

These scripts are **not** part of the portable 26-claim arithmetic verification.
They expect the original research layout, upstream data, earlier processed
artifacts, and in some cases additional scientific solver dependencies. Some
paths/imports reference `upstream_lock/V3`, `results`, or other legacy package
locations. The raw inputs and complete legacy package are not redistributed
here, and placing these files under `code/research` does not recreate that layout.
Use the pinned sources, omitted-input hashes, and `ACQUISITION.md` to identify
inputs, then inspect each script's paths and arguments before reconstructing
its environment. `requirements.txt` records the research dependency set;
third-party packages retain their own licenses.

The frozen-input PyPSA-GB gate script inspects the particular exported inputs
it is given. Its outputs must not be generalized to an absence of chronology
parameters in the pinned upstream repository: those parameters exist upstream,
and any blanket absence claim requires correction. No GB chronology result
is validated by this source-code release.

The archive's validated portable command remains:

```bash
python code/verify_26_claims.py . verification/26_claims
```

Preserving these scripts makes the research implementation inspectable. It does
not assert successful end-to-end regeneration, validate all scientific claims,
or turn solver nonconvergence into a proof of infeasibility.
