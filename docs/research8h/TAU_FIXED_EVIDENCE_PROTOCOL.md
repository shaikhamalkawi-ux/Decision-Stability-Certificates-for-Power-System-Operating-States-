# Fixed-evidence numerical tau sensitivity protocol

Implementation only at initial handoff. Do not prepare or execute without the parent's separate source/protocol, prepared-input and execution gates. The earlier design is `TAU_FIXED_EVIDENCE_SENSITIVITY_DESIGN.md`. This is a retrospective exact arithmetic audit of closed evidence; no solver, multiplier search, new target or physical-model import is used.

## Fixed evidence and model convention

Five capped HOD negative rays are fixed: 26093200, 26093201, 26093210, 26093220, 26093221. Six HOD energy targets are fixed: the same five plus 26093211. Three capped identities and their three class controls are checked, giving six capped point roles. Three uncapped identities and six target uppers give nine uncapped point roles. No case is dropped based on its interval width or a limiting threshold. The six-case capped ledger retains 26093211 UNKNOWN.

The archive's matrices, nominal endpoints, objectives, original 12,096 U/Y/Z binary coordinates, witness vectors, row multipliers, cap values and model encodings stay fixed. Only the uniform numerical expansion tau varies. Nominal caps are 23195, 26532 and 48319 for the three January weeks; their expanded cap rows are B+tau. Uncapped energy models retain no cap or named-unit means. Each of the three identity and six target uncapped matrices is explicitly compared with its corresponding capped matrix after deleting only that cap row, retaining every other coefficient, endpoint and column box. Fossil energy sums the same 23 Coal/Oil/NG generators over one-hour intervals, excluding nuclear.

Tau is a numerical bound expansion in mixed native units, not one physical error magnitude. Its validity range depends on the chosen row/column units and normalization. Invariance under exact positive rescaling of one fixed ray does not imply invariance under reformulating or rescaling model rows. There is no additional tau<1 restriction and no reliance on the separate no-dwell lift theorem.

Existing certificate JSONs already contain a floating per-ray `maximum_uniform_bound_relaxation` diagnostic. The new scope is the exact simultaneous range requiring accepted fixed positive witnesses and all five negative/six energy proofs. No new robustness theorem or minimum-information claim is made.

## Mathematical calculations

For each of the 15 model/vector/mask roles, evaluate every finite row/column inequality as an exact rational expression. Require all original state coordinates exactly zero or one. The fixed point is accepted exactly for tau at least

`p = max(0, all finite row violations, all column violations)`.

The endpoint is included. Tau cannot repair a nonbinary point. Capped positives include their actual cap row; uncapped positives use their actual uncapped boxes/rows. Matrix hashes alone never identify a point role: bounds, vector and mask are separately bound.

For each fixed admissible cap ray d, reconstruct its archived raw orientation/sign projection and sparse multipliers. With `q=A^T d`, set `Delta0=beta-max_box(q^T v)` and `S=||d||_1+||q||_1`. Separation holds exactly for `Delta0-tau*S>0`. The strict upper threshold is `Delta0/S` when S>0. At equality, the proof no longer separates.

For each fixed target-energy projected dual, reconstruct its raw projection and exact residual `eta=c-A^T d`. Compute `L0=beta+sum_j min(eta_j a_j,eta_j b_j)` and `S=||d||_1+||eta||_1`. Then `L_T(tau)=L0-tau*S`. Let U_I and U_T be exact energies of the fixed identity and target binary points. With both points accepted, the optimal-energy difference is strictly positive if `L_T(tau)>U_I`, yielding strict upper threshold `(L0-U_I)/S`. No identity lower bound, ratio bound, numerical optimum or optimal witness is needed.

The runner reconciles every target's fixed projected-dual bound with the archived selected bound at tau0. It does not maximize over a new collection of duals, choose another witness or substitute the zero-dual baseline as tau changes. Direct coefficient, sparse-residual and cap-only-deletion checks ground the formulas in the actual archives.

Zero slope with positive numerator means no finite upper restriction; zero slope with nonpositive numerator means no strict-proof range. Positive slope with nonpositive numerator likewise yields no nonnegative range. A negative slope is an error. All exact endpoints and ties are preserved; no clipping or repair is permitted.

## Intersections and displays

Report five individual ray ranges and their optional same-week control-inclusive ranges, six energy pair ranges, and three aggregate ranges: capped evidence, energy evidence, and their joint intersection. The lower endpoint is the largest required point threshold and is closed. The upper endpoint is the smallest strict proof threshold and is open. Equal endpoints or an empty proof condition imply an empty range. List all limiting proof/point labels, including ties.

Use exactly `tau0=Fraction.from_float(1e-5)`. Every closed-evidence claim and every reported common range must contain tau0; otherwise preserve the discrepancy and fail without choosing another certificate or retrying computation. Whether the common range extends strictly below and above tau0 is a computed outcome, not assumed in advance.

Fractions are authoritative. A displayed safe inner validity band uses 18 digits after the decimal, rounding the lower endpoint UP and the upper endpoint DOWN, retaining the open upper endpoint. If this decimal subset collapses while the rational range is nonempty, report both facts. Outward rounding must not be used to label a certified validity band. Approximate floating endpoints are descriptive only. Outside a fixed-evidence range do not infer reversal, feasibility, absence of other proofs, or physical uncertainty robustness.

## Preparation and binding

The new runner is `src/research8h_tau_fixed_evidence.py`; output is a new `results/research8h/tau_fixed_evidence/` directory. `--prepare` creates only the fixed descriptor, explicit selected-file hash/size manifest and a preparation record. It imports no verifier, runs no synthetic check and performs no mathematical sensitivity evaluation. Existing independent review statuses and historical manifest digests must match. The selected closure contains actual matrices, boxes, objectives, original masks, vectors, row labels, exact/raw duals, sparse residuals, certificate bindings, native fuel CSV and source/protocol/helper files. Historical manifests are hash-pinned; this arm does not claim to replay every entry in every historical arm.

The unchanged standard-library verifier is pinned to `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`; unchanged old-wrapper pure bound helpers are pinned to `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85`. Dynamic imports occur only in `--run-prepared`, with bytecode writes disabled. No producer or native-model code is imported.

After independent source/protocol review, a separately authorized preparation freezes all selected bytes and the case descriptor. Independent prepared review must verify complete case/point roles, actual model/vector/mask correspondence, source hashes and no execution marker. Only explicit execution GO permits `--run-prepared`. Its marker prevents repeat execution. All outputs use exclusive creation; any failure preserves partial outputs and prohibits automatic rerun.

## Checks and outputs

Small synthetic endpoint tests exercise zero slopes and numerator signs, negative-slope rejection, included lower versus excluded upper endpoints at tau0, tied limiting cases, empty equal-endpoint intersections, and an inward-rounded decimal collapse of an exact nonempty range. Full point and certificate arithmetic uses the existing kernel; its fixture suite is not silently redefined as new sensitivity tests.

Outputs are exact point thresholds; fixed capped-ray ranges; fixed energy-dual ranges; common intersections; synthetic endpoint records; and completion or failure. Point records retain maximum exact row/column violations and their worst side, source/mask/vector digests, strict membership and exact binary-mask count. Every range records open/closed semantics, active limits and exact tau0 comparisons. Completion rehashes all frozen selected files and requires independent post-run review before any manuscript or publication claim. No old evidence file is edited.
