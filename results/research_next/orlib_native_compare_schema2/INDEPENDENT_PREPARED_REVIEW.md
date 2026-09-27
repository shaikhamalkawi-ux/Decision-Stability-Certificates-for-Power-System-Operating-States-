# Independent schema2 source and preparation gate

PASS. The complete source diff and additive protocol were read. Changes are limited to the separate arm/protocol paths, historical provenance bindings, the literal `system` field in the three system-variable aliases, and three invented alias assertions (ten total controls). No coefficient, endpoint, comparison, tolerance or allowed-projection rule changed. AST comparison independently confirms that only `alias_name`, `prepare`, and `self_test` function bodies differ; every scientific comparison function and `run` are unchanged.

One independent byte-only check completed in 0.2927517 seconds. All eleven original descriptors and five captured copies matched their hashes and lengths at entry and close. Every one of the five captured payloads is byte-identical to the original failed arm's preparation. The prepared directory contains exactly these five files and its manifest. The ten-control receipt matches the final source/protocol and records zero scientific reads/comparisons/optimizers. The original source, preparation and failed-run records remain intact; the new `run01` was absent at both checks.

Trusted pins:

- Source: `e9f1065fbd47e9d5b7a67afad92fc6a18816cade310b87c8f1c66a49814c389f`.
- Protocol: `f4ac9b47e6b653c7dfc5a42b6a6c98831204a83c51604355f7676bab87fea775`.
- Manifest: `ea2a05148c0d0b23b2c59faea9f0afcfd4a3b386e6e738adb97ca1b4610ab829`.

Scope: source, fixtures receipt and input integrity only. No scientific payload JSON was parsed, no comparator imported or run, and no Julia, build or optimizer invoked. Nominal and expanded equivalence both remain unestablished. This gate admits a separately authorized comparison; it does not erase the original naming failure.
