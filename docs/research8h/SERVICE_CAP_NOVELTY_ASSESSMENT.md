# Adversarial assessment of the January service-cap result

Assessment date: 2026-09-26 UTC. This is a bounded, selective priority check,
not an exhaustive novelty search. No solver, source edit, or outcome-adaptive
experiment was performed. The local independent seasonal review and readout
were read, alongside LITERATURE_CERTIFICATES.md, KGRAM_PRIOR_ART.md, and
ADDITIONAL_PRIOR_ART.md. The January certificate replay is attributed to its
independent reviewer; this memo does not claim to have recomputed those proofs.

**Decision:** the January result materially improves the scientific evidence
over the earlier named-unit-mean examples. At present, its defensible
contribution is a precisely controlled, independently checkable benchmark
result and evidence format. A new general solution method has not been
demonstrated. Priority for the exact paired-instance construction remains
unresolved. Calling the result a discovery that chronology matters, a new
bound/refinement method, or a novel use of infeasibility certificates would
overstate it.

## Exact result under assessment

Two prospectively fixed permutations of one January week retain all complete
hourly input packages, the first and last 48 hours, the native units/network,
and a shared 23,195 MWh fossil-energy cap. There are no named-generator mean
requirements. Identity and the commitment-class control have exactly binary
witnesses in the model with every finite bound expanded outward by
tau = Fraction.from_float(1e-5). Both ordinary twins have exact infeasibility
certificates for the continuous relaxation of that same expanded model.
Their permuted reference witnesses satisfy the static network constraints;
all of their exact expanded row failures are minimum-up/down constraints.

The normalized noncap objective lower bounds are approximately
23,646.57092025 and 23,747.34810412 MWh. The verified original incumbent uses
22,964.9412395564 MWh. Thus necessary increases above that reference are at
least about 681.629681 and 782.406865 MWh, approximately 2.9681% and 3.4070% of its fossil
energy. These are not percentages of total generation, emissions, or cost.
The reference is an incumbent, not a proved optimum. Until an uncapped witness
is established, the twin's necessary requirement may be infinite.

The cap is a reference-derived experimental benchmark, approximately 1%
above the incumbent, not an independently enacted emissions requirement.
The exact statement is about the encoded, explicitly widened DC model, not
strict nominal feasibility or measurement uncertainty. These qualifications
are part of the result, not optional footnotes.

## Three focused primary-source comparisons

### 1. Auer et al.: closely related reordering stress tests already exist

Felix C. A. Auer, Robert Gaugl, Thomas Klatzer, Diego A. Tejada-Arango and Sonja
Wogrin, *Connecting Representative Periods in Energy System Optimization
Models using Markov Transition Matrices*, arXiv:2510.18555v2, 15 July 2026.
[Primary full text](https://arxiv.org/html/2510.18555v2);
[DOI](https://doi.org/10.48550/arXiv.2510.18555).

Inspected Sections 2, 3.1-3.3, 4.2, 4.3.1-4.3.2, and 4.4. Most adverse is
Section 4.3: besides original RTS-GMLC data, they shift representative-period
transition matrices and sample new sequences of unchanged representative
periods. They compare operational deviations and full-model investment
regret. Therefore altering order while retaining period content, using
RTS-GMLC, and quantifying its operational value are not standalone innovations.

The inspected construction does not establish preservation of the exact
complete hourly multiset, fixed 48-hour ends, common cap, and independently
rational positive/negative evidence used here. Its transport network,
representative-period states, and boundary relaxations also differ. These
distinctions delimit our benchmark; they do not refute their method or prove
our priority. The earlier commitment-state Markov pilot is not a substitute
for a head-to-head comparison with their representative-input-period method.

### 2. Bahl et al.: full chronological checks and objective-driven refinement

Björn Bahl, Theo Söhler, Maike Hennen and André Bardow, *Typical Periods for
Two-Stage Synthesis by Time-Series Aggregation with Bounded Error in Objective
Function*, Frontiers in Energy Research 5:35, published 8 January 2018.
[Primary publisher text](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2017.00035/full);
[DOI](https://doi.org/10.3389/fenrg.2017.00035).

Inspected indexed primary full-text Sections 2.2, 2.3, 2.4 and 3.2; PDF/HTML
refetches intermittently timed out. The method preserves within-period
chronology, solves full-series operation for a fixed design, adds feasibility
time steps, and refines periods/segments using objective error. It expressly
does not preserve chronology between representative periods. Section 3.2
reports failures despite including peak demands and acknowledges that its
heuristic need not find the minimum number of time steps.

This is direct adverse prior art against generic claims for checking a
compressed solution, adding diagnostic periods, bounding objective error, or
finding a small useful representation. It is not an inspected proof of our
specific paired-cap statement. Our complete static-witness controls are
stronger than checking only peaks, but constitute a controlled experimental
distinction, not a newly invented verification principle.

### 3. RiSES3: LP lower bounds plus feasible-operation upper bounds are known

Nils Baumgärtner, Björn Bahl, Maike Hennen and André Bardow, *RiSES3: Rigorous
Synthesis of Energy Supply and Storage Systems via time-series relaxation and
aggregation*, Computers & Chemical Engineering 127:127-139, 4 August 2019.
[Publisher](https://www.sciencedirect.com/science/article/pii/S009813541831127X);
[institutional record](https://juser.fz-juelich.de/record/877607);
[DOI](https://doi.org/10.1016/j.compchemeng.2019.02.006).

Publisher and institutional metadata/abstract were inspected; the full body
was not obtained. They explicitly combine LP-relaxation and aggregation-based
lower bounds, feasible full-operation upper bounds, and iterative tightening
for time-coupled energy systems including storage. This already blocks a broad
claim that pairing a relaxation bound with an operational witness is new.
It does not establish whether their full text contains an equivalent exact
multiset-pair result or rational certificate mechanism. Obtain the body through
the existing library access before claiming a distinct new bounding method.

The nearby 2018 decomposition predecessor was checked only as a routing
lead: its primary introduction explicitly excludes chronological coupling.
It is therefore not treated as an exact adverse theorem for this model.

## Claim ledger

| Proposed claim | Assessment | Defensible wording or missing evidence |
|---|---|---|
| Two January twins are incompatible with the common service cap despite identical complete hourly multisets and static feasibility. | Supported new numerical instances in this project. | State the two cases, expanded model, matching positive witnesses, and exact negative certificates. Do not turn new instances into a priority claim. |
| The examples go beyond failure to reproduce named-unit energies. | Supported and scientifically important. | Zero named-mean rows; a shared aggregate fossil cap permits redispatch across all units. |
| A histogram of complete hourly packages plus these boundary inputs determines cap feasibility. | Falsified on this declared class by the pair. | Any deterministic rule restricted to those identical observations gives the same answer, so cannot correctly classify both. This elementary indistinguishability inference is not a new information-theoretic technique. |
| Order necessarily raises fossil requirements by at least the reported amounts. | Supported necessary bound, with qualification. | A normalized exact noncap lower bound exceeds the verified original incumbent. The gap is valid even though the original optimum is unknown; it may be infinite without an uncapped witness. |
| The finite price of order equals 2.9681% or 3.4070%. | Not supported. | These are lower bounds relative to incumbent fossil energy, not attained penalties or exact optimality gaps. |
| Rational Farkas/finite-box validation is a new method. | Established methodology. | Attribute existing exact LP/IP verification, dual residual repair, and alternative-polyhedron/IIS machinery documented in the earlier local audit. |
| Certificate-guided temporal refinement or LP lower bounds plus feasible upper bounds are new. | Broad claim contradicted by prior art. | A distinct algorithm, theorem, or demonstrated advantage over existing approaches would be needed. |
| The observed multiset pair refutes state-aware, contiguous-period, or Markov aggregation generally. | Unsupported. | Those methods retain observations absent from an unordered snapshot multiset. Exact distinct-package bigrams can even reconstruct order. |
| Small proof support implies minimum temporal information or data-acquisition savings. | Unsupported. | The global cap and underlying full matrix use all hours; generation and checking accessed the full data. Support minimization and information acquisition are separate questions. |
| The finding generalizes across seasons or networks. | Not established. | Only January is an eligible held-out week; two draws within it are not two seasonal replications. April/October remain no-reference/not-run. |
| The method is computationally advantageous. | Not established. | The ordinary LP itself rejected both cases in about four solver seconds each. Count preprocessing, model generation, proof construction and checking before claiming savings. |
| This is the first exact paired multiset/service-cap benchmark. | Priority unresolved. | No exact match was established by this bounded review; absence of a match does not establish firstness. |

The separate arbitrary-k construction remains a possible attributed
limitation proposition, with the prior k-abelian and weighted-automaton
overlap recorded in KGRAM_PRIOR_ART.md. The January one-gram result does not
experimentally validate the arbitrary-k claim. July's feasible service LPs,
unresolved binary cases, and positive named-mean repair radii remain different
questions and must not be pooled into a success rate.

## Publication value and the strongest next discrimination

There is a plausible computational-note or benchmark contribution: release
the paired matrices, native mappings, constructive witnesses, exact proof
objects, normalized energy bounds, and an independent checker with one clear
decision statement. The coherent exact domain for positive and negative
evidence is a substantive reproducibility improvement. It is not yet enough
to advertise a new general aggregation or certification algorithm.

The main limitations are a single week and test-network area, an experimental
cap, unrestricted shuffling inside 72 hours, missing seasonal replication,
and no evidence that a deployed aggregation method would misclassify these
instances. Shuffling preserves cross-sectional physical packages but can
destroy realistic weather/load serial structure; the result is a controlled
stress test, not an estimate of operational failure frequency. The 48-hour
edge control does not establish invariance to other horizon conventions.

The ongoing uncapped arm is necessary to replace a possibly infinite
requirement with a finite achievable one. It will strengthen the energy
interpretation but will not, by itself, create methodological novelty.

One subsequent discriminating test would be a prospectively fixed paired
decision comparison against a published chronology-aware aggregation method
on these exact cases, using a common physical model and cap. Freeze the
mapping from that method's output to admitted/rejected/unknown, its
representative-period settings, boundary treatment and complete runtime
accounting before looking at results. Include direct full LP rejection as
the inexpensive baseline and preserve native positive controls. If an
existing method correctly rejects both with comparable effort, position the
work as a verified benchmark rather than a better screening algorithm. If it
admits a case with a material certified violation, the benchmark has concrete
diagnostic value; a new method claim would still require a remedy tested on
fresh cases. Do not use a mismatched commitment-state alphabet to claim a
failure of Auer's input-period method.

Recommended claim ceiling at this checkpoint: **exactly checkable paired
counterexamples to order-blind service-cap assessment, with certified
necessary fossil-energy increases on one held-out RTS-GMLC week.** This is a
specific supported research result. Its priority and broader usefulness remain
open research questions.
