# Auer supported-signal adapter: source and preflight protocol

Status: source/preflight implementation only, 27 September 2026. Parent source review precedes actual archived-array preparation. **No scientific clustering is enabled by this revision's CLI.** A subsequent execution harness, solver/tie/time-limit contract and independent source/prepared review are required before the fixed-data clustering experiment. Author code is not replaced by a generic clustering implementation.

## Question and denominator

Can the actual published author preprocessing, applied to the explicitly projected supported signals, distinguish the six existing HOD pairs? This does not compare UC dispatch, optimization costs or runtimes, does not claim a lossless 107-coordinate encoding, and does not alter any archived label.

Twelve distinct inputs are fixed: each January week1/2/3 identity, its two ordinary targets and its class-preserving positive control. Targets are 26093200/01,26093210/11,26093220/21; controls26100200/10/20. The future invocation order is identity, first target, second target, control, repeated identity for each week in that order: fifteen calls. The repeats are determinism checks. Positive controls need not have equal representations. The historical capped UNKNOWN remains in the denominator. No cases/R choices/tie policies are selected using representation outcomes.

## Immutable author route and license

Author repository tag commit `ce97428aa225037dcbcd848889ef55f3b67c17ba`; InOutModule gitlink `8b1f53a75d152645e5ff8c7d5f417befaf316da5`. Exact unmodified `Utilities.py`, `CaseStudy.py`, `ExcelReader.py`, `printer.py`, empty package initializer, both MIT license notices and the author environment file are copied to the isolated `.work/auer_projection_author_ce97428/` directory. `AUTHOR_CLOSURE.json` records immutable raw URLs, response-byte hashes, sizes and revisions. The adapter additionally hardcodes all eight source/license/environment hashes and rejects extra files, source mismatch, symlink/reparse paths, or preloaded author modules. Only this small import closure is preserved; no claim of a complete repository checkout is made.

The adapter constructs a declared in-memory table carrier with `copy()` and the required author field names. It does not execute `CaseStudy.__init__`, so it neither loads Excel nor silently merges buses/scales units. Actual functions remain the pinned `Utilities` functions. The pinned unbound `CaseStudy.get_rpTransitionMatrices` is used on the resulting Hindex. This replaces only file/constructor plumbing with an explicit input adapter, not feature extraction, k-medoids selection, representative-table copying, or transition calculation.

Author defaults are fixed: R=3,24hours/RP, `aggregated`, `maxInvestment`, `sum_production=False`, no rescaling and Gurobi. No demand stretching, unit merging, chronological shifting, altered transition probabilities or dwell clipping is invoked. The adapter preserves 48-hour dwell in common metadata, but never builds a UC model. Author grouping/merge multiplicities are preserved even when the resulting feature's demand sum differs from a physical total. A separate report makes those multiplicities visible.

## Supported signal projection

Input provenance is the pinned existing HOD/fresh-target manifests, with SHA256

- week1: `078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc`;
- weeks2/3: `56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd`.

Each input's `native_inputs.npz`, `model_metadata.json` and `permutation.csv` must have exact covering parent bindings. Native `gen.csv` and `dscgrid_model.py` are similarly bound; the native source is inspected, never imported. Only relevant bound files are rehashed, not unrelated full result corpora.

The input consists of168 ordered hours,41named units and24named buses. The signal tables contain24nodal demands,11utility-scale PV/wind capacity factors and6hydro inflows per hour. The author VRES metadata table contains these17named signal generators, with native ratings, one existing unit and no investment. The hydro entries in that table support the author's existing inflow join; hydro does not also get a VRES-profile row. There is no energy-storage device.

Native code first subtracts fixed rooftop PV from gross nodal demand. The adapter copies that nodal-net signal and **does not create rooftop PV profiles**. Utility-scale PV and wind are separate decision-unit bounds and have not already been subtracted. The projection therefore does not intentionally double count rooftop PV. Nevertheless the projected signals and author feature sums are not an operational load balance.

PV/wind availability is divided by its positive native nameplate rating. Multiplication back may differ in binary64; every mismatch is recorded with original/recovered hexadecimal values and an exact rational error. It is a declared conversion, not silently called lossless. Demand and hydro values are copied. Negative nodal-net values are retained, not clipped. Nonfinite values, inverted bounds, unexpected nonzero renewable minima, nonfixed hydro, duplicate IDs, mismatched widths or varying omitted thermal ratings cause failure.

Hydro's archived lower=upper fixed generation is represented only as a supplied inflow signal; this does not preserve its must-dispatch constraint. The independent aggregate-net equation is omitted explicitly; its difference from the sum of nodal values is reported. Thermal bounds/dwell, bus and unit identities remain common metadata. No fictitious buses, technologies or raw source-hour identifiers are appended as clustering features.

## Observation contract

The dormant author-call function returns actual extracted clustering features, selected full `dPower_Demand`, `dPower_VRESProfiles`, `dPower_Inflows`, RP/K weights, fresh circular integer transition counts and both normalized matrices. Cached matrices are recomputed because the author's isolated table-update helper does not refresh them; its normal file-reload route does.

This is the complete supported no-storage temporal preprocessing observation, with unchanged common metadata. The future comparison must normalize all three RP labels together (six permutations) and compare numeric values exactly, retaining signed-zero policy explicitly. It must not count medoid day IDs/provenance indices as unequal scientific observations. Hindex is preserved for provenance. It becomes scientifically consumed information for any later long-duration-storage or full-schedule-reconstruction question, which is outside this no-storage observation claim. A full active-module audit remains necessary before any broader downstream-equivalence claim.

This revision deliberately stops short of the fifteen-call execution harness, canonical-output serialization and solver timeout/tie policy. `author_representation` is source-reviewable but has a default-disabled scientific guard and no CLI execution route. Thus the existing parent authorization to draft an adapter cannot accidentally perform clustering through a convenience command.

## Allowed checks and stage gates

1. `--preflight`: importlib package metadata only, exact author-byte/AST import inventory, bound native generator roster metadata, and predicted feature multiplicities. No scientific arrays, author imports, solver calls or license checkout.
2. `--self-test`: invented table fixtures only. Check negative net signals, separate renewable/hydro roles,48-hour metadata, multiplicities, and adversarial rejection of rooftop double counting, altered hydro/thermal semantics, nonfinite data, zero ratings, duplicate IDs, unexpected renewable minima and width mismatch. It also checks the scientific-execution guard. This tests the adapter, not the author's clustering.
3. `--prepare-only`: separately authorized after source review; reads all twelve fixed arrays, creates explicit projection JSON plus conversion diagnostics, and freezes cases and all selected input bindings. It imports NumPy to read NPZ, but no author modules/TSAM and makes no optimizer call. No representation-equality outcome is calculated. New output directories are exclusive; partial failures remain visible.
4. Scientific clustering requires a later reviewed execution source and explicit parent GO. Nothing in a passed synthetic fixture or package-install log grants that execution gate.

Report locations are under `results/research_next/auer_projection_preflight/`; old research8h results remain unchanged. Native source paths may point to the already pinned earlier workspace; this is not yet a portable scientific package.

Pre-preparation source amendment: capture adapter/protocol, both parent-manifest and all author-source hashes before reading the arrays; rehash these, every selected input and every projected output at close. Any intervening change prevents the final freeze. Earlier synthetic/preflight reports retain their original source hash; this amendment changes only closure bookkeeping and does not silently relabel those runs.

## Dependency and solver readiness

The initial authoritative `-I` probe (site enabled) found NumPy2.3.5,pandas3.0.1,matplotlib3.11.2,openpyxl3.1.5,HiGHS1.12.0, but no TSAM,Pyomo,gurobipy or rich. An earlier `-I -S` probe hid site packages and is not evidence that the environment lacked NumPy. That probe correction is retained in the preflight record.

Parent subsequently authorized free official dependencies in a **separate** `.work` environment; preserve the prior solver environment. Match the author pins pandas2.2.3,TSAM2.3.9,Pyomo6.9.2,Gurobi13.0.0,rich14.0.0,openpyxl3.1.5,matplotlib3.10.3, record a complete installed-version inventory and the local Python3.12.14 versus author3.12.11 patch difference. Metadata matching does not establish licensed solver readiness. A single invented tiny Gurobi license probe may run with an explicit separate ledger, no model data, no purchase, no credentials/environment-secret output, and no claim that it is a scientific call. No paid license acquisition is requested.

If the author backend is unusable, retain that outcome. One possible **labeled variant** is the pinned TSAM/Pyomo implementation with a verified supported HiGHS backend; another is exhaustive exact selection among the35possible three-medoid subsets of seven days, preserving the actual normalized-distance definition and predeclared tie rule. Neither is currently implemented/selected, neither is automatically equivalent in ties to Gurobi, and neither may be substituted silently. TSAM normalization, distance construction, tie handling and actual solver-call boundaries still need source inspection before scientific execution.

## Interpretation

Different complete outputs mean the published preprocessing distinguishes that pair under this projection; that defeats a collision claim for the pair, not the method. Equal outputs establish only projection/configuration-specific indistinguishability, conditional on a complete output contract. Neither result demonstrates recovered binary dispatch, improved feasibility classification, a speed benefit, novelty, or applicability to an independent network. Installation and synthetic checks are readiness evidence only.
