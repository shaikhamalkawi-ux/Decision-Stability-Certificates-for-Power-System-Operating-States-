# Independent failed-comparison review

PASS for the failure boundary and semantic-name diagnosis, not formulation equivalence. The single producer attempt stopped at the exact native-projection name-set check, before traversal of any affine row, objective or variable-domain comparison. Its preserved failure reports 0.3753343 seconds and no retry. `run01` contains only `started.json` and `failure.json`; no comparison result exists.

The independently authored reviewer rechecked all seven source descriptors and five captured copies at entry and close, and both producer records remained unchanged. It inspected the saved column/alias metadata only. All 2,712 native variables have unique, complete aliases, and the adapter has 2,472 unique retained names plus the declared 240 omitted `mfg` names. The entire set difference is exactly 72 system names: the comparator produces `C:0`, `F:0`, `N:0` through hour 23, whereas the adapter stores `C:system:0`, `F:system:0`, `N:system:0`. Adding the literal `system` component in this diagnostic restores the name inventory exactly. It does not test whether any corresponding coefficient, bound or objective agrees.

This is a naming-contract defect in the comparator, not evidence of a native formulation mismatch. Neither nominal nor expanded-model equivalence is established. The parsed-parameter routine runs before this failure but accumulates differences locally; its result was not persisted, so no parsed-parameter PASS is inferred. No source was repaired or producer rerun by this reviewer. A separately admitted successor is required for any further comparison.

The check completed once in 0.2047993 seconds, using Python standard-library hashing, JSON and name-set operations. No producer imports, Julia, optimizer, scientific coefficient comparisons or new native build occurred. JSON loading parses the container; numerical coefficient objects were not traversed or compared.

Stable evidence:

- Reviewer source `INDEPENDENT_FAILURE_REVIEW.py`: `531429f38eca3e174876418ef9286a8b2edefcd79bf29a945f386ee8c290ab61`.
- Report `INDEPENDENT_FAILURE_REVIEW.json`: `b76ca3828167353fe4f6b1f02864ec9bc0c7467d8efdcc4aa481aa3c5ea54d63`.
- Admitted manifest: `fe20e2535ad3f36e669dbafb1ff9d588d791f0e8c04bbedfa0557bc1830d8b29`.
- Unchanged producer source: `83ee49f623b9bb9b90a27ecbf808e305369ae02046add59a643afb002c0db507`.

The earlier byte-only prepared gate report is `3c976286ab5b3daf41958f08533052105985d9ee1016c63f03a8964708f55a1a`; it establishes copy integrity, not correctness of the alias implementation.
