# Fixed-evidence numerical tolerance sensitivity — closed

The producer and independent exact-arithmetic replays both passed. The same five capped negative certificates and six positive uncapped optimal-energy-gap proofs remain valid simultaneously, with their required fixed binary witnesses, throughout

\[
\tau\in\left[\frac{956037}{281474976710656},\;
\frac{457789350028493018114625663499329}{621701836709484966419597220796298272}\right).
\]

The lower endpoint is included; the upper endpoint is excluded. A certified inner decimal band is **[0.000000003396525728, 0.000736348717339262)**, rounded upward at the lower end and downward at the upper end. It contains the archived binary64 value of `1e-5` and extends strictly below and above it. The exact fractions, not approximate decimal ratios, are authoritative.

The energy-only common interval equals this joint interval. The capped-only common interval is

\[
\left[\frac{21705}{281474976710656},\;
\frac{2492379768657912937223539632714337}{1370919491694646724217109087977258307}\right),
\]

with safe inner decimal band **[0.000000000077111651, 0.001818035109834922)**. All endpoints, individual ranges and active ties are retained in `common_ranges.json`, `point_thresholds.json`, `capped_ray_ranges.json` and `energy_ranges.json`.

The joint lower limit comes from the fixed binary target witness for `26093210`; the upper limit comes from the fixed energy dual for `26093211`. The capped-only lower limit is shared by the week-2 identity and class control, and its upper limit comes from the ray for `26093210`. The historical capped verdict for **26093211 remains UNKNOWN**: a positive uncapped optimal-energy gap does not establish cap infeasibility.

The audit retained all 15 point roles (six capped, nine uncapped), five rays and six objective duals. It checked original 12,096-coordinate binary masks and used the prescribed uniform outward expansion of every finite row and column bound. The producer ran once in 34.6717182 seconds; the separate independent replay took 28.882485 seconds. Neither used an optimizer, network, new witness, multiplier search or outcome-based case selection. Nine focused endpoint/degenerate-case checks passed. All 211 frozen inputs and 11 closed producer files remained unchanged in the independent audit.

This is a numerical sensitivity result for fixed archived evidence, using mixed row/column units. Its range depends on the chosen units and normalization; invariance to scaling a fixed ray does not imply invariance to rescaling model rows. It is not a physical uncertainty guarantee, strict nominal positive-feasibility result at zero, new robustness theorem or external replication. Outside the band these fixed witnesses/proofs stop jointly certifying the claim; no reversal, infeasibility of the positives or absence of alternative proofs follows. Earlier per-ray diagnostics and all historical outcomes remain intact.

Independent gate: `results/research8h/tau_fixed_evidence_independent_review/postrun_review.json`, status `INDEPENDENT_TAU_FIXED_EVIDENCE_POSTRUN_PASS`, SHA256 `ec967e2ad645a910c846dc541a4355da35d9bd816eded55f3c33483e9880642f`. `ARTIFACT_INVENTORY.csv` binds the full frozen input closure, producer outputs, independent review code/results, design/protocol/review notes and this readout; it excludes its own self-reference. No frozen file was edited to create these final delivery records.
