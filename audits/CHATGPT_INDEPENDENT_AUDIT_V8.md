# ChatGPT independent audit — DSC-Grid V8 candidate

## Decision

**HOLD V8 as a candidate; do not promote it to the active baseline yet.**

The V8 package contains a genuine scientific strengthening: the Elexon operational-outturn evidence is reproducible at the numerical level and is correctly bounded as observational evidence. The July network-repair bracket remains correctly certified, the clean-room arithmetic audit reproduces the central numbers, and the manuscript/package production quality is strong.

A narrow **V8R1** correction cycle is required before independent acceptance.

## Independently passed

- Full-package SHA-256 matches: `1db590a301f6dbefd7ead8b9a2c7eeeaeccd3e06481671a1738e43d8a1d90451`.
- ZIP integrity and package manifest verification pass.
- Main manuscript is 8 pages; supplement is 6 pages.
- Main/supplement compile from source.
- No Type-3 fonts, undefined citations/references, or material visual clipping found.
- 35/35 bibliography entries are cited.
- Clean-room numerical audit: 26/26 central claims pass.
- Elexon B1610 primary metrics were independently reconstructed from packaged raw JSON.
- The July network-constrained chronology statement remains a certified bracket:
  `8.020508464286 <= A_network+minUD+ramp <= 11.9262964643 MW`.
- The upper endpoint remains a feasible-witness upper bound, not an optimum.

## Mandatory correction 1 — reopen the PyPSA-GB chronology gate

V8 correctly observes that the **frozen solved LP extracts** contain no active committable/minimum-up/minimum-down/ramp attributes. However, its conclusion that a GB chronology experiment would necessarily require new externally sourced or imputed parameters is too strong.

At the exact pinned PyPSA-GB commit `8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`:

- `scripts/generators/integrate_thermal_generators.py` explicitly supports MILP mode and can apply `committable`, `min_up_time`, `min_down_time`, and ramp limits from fuel characteristics.
- `data/generators/generator_data_by_fuel.csv` contains nonzero UC/ramp fields for thermal carrier classes.
- `config/defaults.yaml` and `scripts/market/solve_wholesale.py` contain an optional wholesale UC overlay with explicit carrier parameters.

Therefore the correct question is not “are parameters absent?” but “which source-provided chronology parameterization, if any, is admissible for the frozen Historical-2020 Reduced-network experiment?”

V8R1 must audit provenance, units, intended workflow, and compatibility of each candidate parameterization. If one passes the gate, run the admitted chronology experiment. If none passes, retain HOLD with the corrected evidence-based rationale. Do not state that the pinned model simply lacks chronology parameters.

## Mandatory correction 2 — TPWRS abstract length

The current V8 abstract is approximately 210 words after LaTeX stripping. Current IEEE PES guidance requires a 150–200-word abstract. Reduce it to approximately 180–195 words and verify the count mechanically.

## Mandatory correction 3 — stale internal audits

The V8 archive contains:
- `audits/CLAIM_BOUNDARY.md` headed **DSC-Grid V7**;
- `audits/MATHEMATICAL_AUDIT.md` headed **DSC-Grid V6**.

Replace these with V8R1-current audits. Historical audits may be retained only in a clearly historical/archive location.

## Mandatory correction 4 — Elexon byte-reproducibility wording

The V8 Elexon audit states that fourteen derived outputs reproduced “byte-for-byte by SHA-256.” A cross-platform rerun reproduced the scientific/numerical results but not exact output bytes because of environment-dependent serialization (line endings / float text formatting).

V8R1 must either:
- qualify byte identity as applying to the locked V8 environment and add a cross-platform numerical-equivalence statement; or
- canonicalize serialization and demonstrate portable byte identity.

## Recommended clarification — Elexon date selection

The acquisition script hard-codes 2023-01-11 and 2023-07-12. The paper calls them matched weekdays, but the package does not document a prospective/deterministic selection rule for choosing these exact days. State the actual rule. If illustrative, say so explicitly. Add a small sensitivity only if it closes the selection objection without creating decorative robustness.

## What should remain locked unless new evidence overturns it

Do not reopen merely for novelty:
- V7 RTS static/conditional locks;
- native ramp admission result;
- native minimum-up/down rejection in the declared relaxation;
- July exact relaxed repair = 8.020508 MW;
- March 40.018759 MW remains lower-bound only;
- July network repair bracket and witness verification;
- shared AC witness evidence and its non-global-optimality boundary;
- V7 PyPSA-GB LP distributional replication;
- V8 Elexon primary arithmetic and observational claim boundary.

## Status

Create **V8R1**, not V9. V7 remains the last independently accepted baseline until V8R1 passes a second independent audit.
