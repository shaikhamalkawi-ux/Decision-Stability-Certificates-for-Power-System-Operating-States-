# L14 black-box VIPR: source exists, current deployment is not ready

27 September 2026. This is a capability revisit of the already counted L14 paper, not another paper in the reading ledger. No installation, compilation, executable download, oracle call, model export, or scientific experiment was performed.

**Verdict: HOLD for direct use on our common-commitment model.** The published method is relevant to mixed-integer infeasibility and has public source. It is not a ready converter for our existing SCIP/HiGHS results. The available implementation needs a different backend or usable full-size Gurobi installation, a validated exact input path, and an independent complete VIPR checker. A numerical negative from the ongoing search would remain UNKNOWN until those additional steps actually produced and verified a proof of the intended expanded model.

## Primary material and reading depth

Stefan Szeider, *VIPR Certificate Construction from Black-Box ILP Solvers*, CP 2026, LIPIcs 379, 52:1–52:14, DOI [10.4230/LIPIcs.CP.2026.52](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2026.52), published 13 July 2026. Revisited the publisher PDF's front matter, pp. 52:2–52:6, and the beginning of §4, rather than rereading all experiments. The method performs a separate branch-and-bound search, obtains numerical LP multipliers, reconstructs exact derivations, and discharges branch assumptions. The paper explicitly discusses mixed-integer support and the difficulty of recovering exact feasible solutions when continuous variables satisfy coupled equalities. This is established proof construction, not a proposed new method here. [Publisher PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol379-cp2026/LIPIcs.CP.2026.52/LIPIcs.CP.2026.52.pdf).

The paper itself links the author's [VORC repository](https://github.com/szeider/vorc) and [Zenodo supplement](https://zenodo.org/records/20057193). The latter's landing page was read: it describes benchmark CSVs and instance generators, with code hosted separately. Its archive was not downloaded or inspected. GitHub's public API returned tag v1.0.0 and no release entries/assets at this inspection. That establishes no ready release binary from this repository, not absence of every possible third-party build.

Author source was inspected at commit [`d7e0c75ef8acf8e29d556f49134985ed5545baf8`](https://github.com/szeider/vorc/commit/d7e0c75ef8acf8e29d556f49134985ed5545baf8), dated 7 May 2026. Read README/Cargo manifest and selected implementation paths: `main.rs` dispatch/infeasibility/solution checks; `oracle.rs` construction, numerical solves, dual/Farkas extraction and retries; `bnb.rs` integer-only branching and infeasibility handling; LP/MPS numeric parsers; rational utilities. Other fetched files were hash-inventoried, not fully audited. This is a capability review, not a correctness audit of the complete codebase.

## What the current code actually offers

The README specifies MIT-licensed Rust source, Rust 1.85+, Gurobi 12.0.3, a usable Gurobi license, and a C toolchain. `Cargo.toml` directly depends on the Gurobi Rust/C interface. `Oracle` is a concrete Gurobi model with `Pi`/`FarkasDual` extraction; no implemented SCIP/HiGHS backend is exposed. Defaults preserve LP row identities by disabling presolve and dual reductions and making bounds explicit rows. [README](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/README.md), [manifest](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/Cargo.toml), [oracle](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/src/oracle.rs).

`main.rs` first runs its own MIP. On numerical infeasibility, it starts its own LP-based proof search with no SOL section and writes an infeasibility certificate only after that search succeeds. It does not import an existing SCIP search tree/status. Branch selection excludes continuous variables. An apparently integral LP point in infeasibility mode causes failure rather than a fabricated contradiction. Thus continuous P/theta variables are not, by themselves, a disqualifier for the negative route. The separate optimality route can fail on exact continuous witness recovery. The CLI exposes a node limit, but not a complete wall-time contract; oracle numerical retries also create additional calls. [Main](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/src/main.rs), [branching](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/src/bnb.rs).

The local Gurobi attempt already failed on model size; wrapping that same backend does not remove the license limit. The recorded PySCIPOpt 6.2.1 / SCIP 10.0.2 build lacks the probed exact-mode/certificate parameters ([closed capability record](../../results/research_next/scip_capability/READOUT.md)). Neither limitation invalidates the black-box concept, which does not need an exact oracle. They do prevent claiming the author's implementation is currently runnable here. No fresh compiler, license, or solver-capability probe was made in this review; the parent's recorded lack of a compiler on PATH is retained as environment context.

## Exact-target input is a separate blocking requirement

The authoritative target is the original 69,362-row, 33,936-column common model, with its complete 12,096-coordinate integer mask and exact dyadic coefficients. Every finite endpoint must be widened by the exact rational value `Fraction.from_float(1e-5)`; an old equality becomes two rational inequalities. A certificate for the nominal model or a nearby decimal model would not prove emptiness of this larger set. All variable boxes and private/shared coordinate maps must remain covered.

The current MPS parser does **not** universally preserve that target: `parse_mps_number` first attempts limited integer/decimal parsing, then falls back through `f64` and bounded-denominator rationalization with limit 10^9. Its own scientific-notation fixture expects `1e-05` to become exactly 1/100000, which differs from our binary64-derived tau. This is input-model approximation, distinct from harmless use of approximate oracle multipliers followed by exact proof checking. [MPS parser, lines 475–500 and 627–645](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/src/mps.rs#L475).

The LP parser's numeric routine uses signed 64-bit numerators (and fraction denominators); long exact dyadic spellings are not generally supported. The token splitter also does not establish an end-to-end rational-slash route merely because the numeric routine has a fraction branch. No parser test was executed here. A full exact readback equality audit would be mandatory; silently shortening coefficients, using ordinary floating MPS export, or accepting the parser's approximated instance is insufficient. [LP parser, lines 208–325](https://github.com/szeider/vorc/blob/d7e0c75ef8acf8e29d556f49134985ed5545baf8/src/parser.rs#L208).

A prospective exact parser/exporter or proved exact row-scaling adapter could address this, but neither exists or is validated by this note. Rounding only the numerical oracle copy would be acceptable in principle if every emitted derivation is checked against the unchanged exact target. Rounding the certificate's original constraints is not that arrangement.

## Alternative oracles and final acceptance

PySCIPOpt publicly exposes numerical `getDualsolLinear` and `getDualfarkasLinear`. This is evidence of relevant API functionality, not a tested replacement for VORC's row-preserving oracle. A port must establish solve stages, original/transformed row mapping, bound contributions, branch push/pop semantics, and all failure statuses. Our existing HiGHS dual/ray work likewise demonstrates numerical access, not an available VORC backend. [Official PySCIPOpt Model API](https://pyscipopt.readthedocs.io/en/stable/api/model.html#getDualfarkasLinear).

The independent [VIPR 1.1 specification](https://github.com/scipopt/vipr/blob/master/cert_spec_v1_1.md) supports rational MILP input, integer assumptions, and complete discharging of those assumptions. Its reference checker is a separate project. The inspected [CMake configuration](https://github.com/scipopt/vipr/blob/master/code/CMakeLists.txt) requires C++14 and GMP, and the current Windows configuration also requires TBB; optional completion has further dependencies. No ready checker executable was verified locally. Our stdlib LP/point checker is not already a VIPR integer-proof checker.

The smallest useful infrastructure next step, if separately authorized, is an invented mixed binary/continuous infeasible instance with a nonempty LP relaxation, exact dyadic expanded endpoints, and an independently checked input round trip; the emitted integer certificate must pass a trusted checker and a deliberately corrupted proof must fail. Only then could a bounded original-model proof search be proposed. It remains a new search that may exhaust resources, not a guaranteed post-processing step after a numerical negative. The common expanded LP already has an exact continuous witness, so a complete negative would need genuinely integrality-dependent steps.

## Immutable source identity

The following author files were fetched as text at the pinned commit and hashed in memory; no author code was executed or installed. These hashes identify the inspected revision, not a validated executable.

| File | SHA256 |
|---|---|
| README.md | aa9a0638f65fbdc474e3e11154fba61bef78f8ace756ad7ae8d45f7d7bf717b2 |
| Cargo.toml | 9dd460b6e9e883acc8097e0cf3fdc7cd663625442b3ce38d3586ad4e2d21304b |
| src/main.rs | 1abd6294bbd8f9ad406c25a712747597bc04634228fb9c1d462074765be64fae |
| src/oracle.rs | f7fd3e791cc959ddf6f708183fd3fdfa92abcd3c95b27ca6951d819082b641db |
| src/bnb.rs | 2076de6d8bfc77f4177f579ee6101be70007f55bf7d08f23092f6f2551089afe |
| src/parser.rs | 5cd2b6562ff37f7d08fcaaf1dbe1b929420d1ce49965941abf10bd664d088152 |
| src/mps.rs | b0646b904749f819128b749a5e10becd160ccc6c8777696581910cb8be63dba3 |
| src/rational.rs | 8a91a0b41da53376af001184faf94e00d339524b7219d926fe95062f01cbed13 |
| src/types.rs (hash inventory; no full audit) | be09fe89245b1bddef8af2c8091ace7b90b0446e010a6199a0f6023cc3d0a50e |
| src/vipr.rs (hash inventory; no full audit) | cee4c4e7199fcb6b6bfe9c118514c64f76eaf53ecca79b9ae9f190f2cea405d2 |

The publisher PDF was successfully read through its primary link; one later page-range fetch timed out. Some guessed VIPR build-file URLs failed before the actual directory listing supplied `CMakeLists.txt`. Those failures do not imply unavailable source. No new paper count, general novelty claim, or proof-readiness claim follows from this revisit.
