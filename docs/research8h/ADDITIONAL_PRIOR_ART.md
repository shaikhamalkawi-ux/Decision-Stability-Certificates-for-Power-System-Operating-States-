# Additional primary-source checks, 26 September 2026 UTC

These are original reading notes. No subscription article is included. They
supplement the earlier literature audit and do not revise any frozen protocol.

## Qin et al., July 2026: direct overlap in state-aware aggregation

Jishuo Qin, Bin Yang, Fan Li, Hanqing Liang, Taikun Tao and Yawei Xue,
“Quality-Aware Feasibility-Preserving Unit Aggregation for Smart-Grid Production
Simulation,” *Energies*19(15),3487 (24July2026).
[Publisher and DOI](https://doi.org/10.3390/en19153487).

Read the publisher's indexed text covering Sections2,3,5,6 and7. Direct page
opening returned429; this is not a claim to have inspected every equation/PDF.
The paper combines inherited-state grouping, conservative flexibility
envelopes, member-unit disaggregation and cross-window state updates. Failure
to implement an aggregate schedule triggers rejection or finer clustering.
It evaluates13/39-unit cases and a13–104-unit scaling exercise, and separates
scheduling-quality proxies from detailed electrical validation.

This is strong prior art against broad novelty claims for remembering unit
history, checking inverse implementability, or trading aggregation against
verification effort. Our January experiment instead supplies paired complete
input multisets and exact rational infeasibility evidence under one shared
resource cap. That distinction describes the evidence produced here; it does
not establish methodological novelty or an empirical advantage over QFEA.
No head-to-head implementation comparison was run.

## Energy2017: full-series feasibility and objective bounds predate this work

Björn Bahl, Alexander Kümpel, Hagen Seele, Matthias Lampe and André Bardow,
“Time-series aggregation for synthesis problems by bounding error in the
objective function,” *Energy*135,900–912 (2017).
[Publisher record](https://www.sciencedirect.com/science/article/pii/S0360544217310769),
[DOI](https://doi.org/10.1016/j.energy.2017.06.082).
[Institutional author metadata](https://publications.rwth-aachen.de/record/696025?ln=en).

The primary publisher abstract/highlights and indexed introduction describe objective-based
aggregation accuracy and full-time-series feasibility. Direct full-page access
returned403. Exact model assumptions and the treatment of chronological
constraints were not established from the inspected material. Therefore this
is prior art against claiming that objective-linked aggregation assessment or
full-series verification is new. The later primary paper below explicitly
describes this predecessor as lacking chronological coupling. It is not a
verified equivalence to our specific chronological cap construction.

## Bahl et al., January2018: objective-bounded chronological refinement

Björn Bahl, Theo Söhler, Maike Hennen and André Bardow, “Typical Periods for
Two-Stage Synthesis by Time-Series Aggregation with Bounded Error in Objective
Function,” *Frontiers in Energy Research*5,35, published8January2018.
[Primary full text and DOI](https://doi.org/10.3389/fenrg.2017.00035).
The DOI/year-volume carries2017 while the publication date is2018; preserve
that distinction when formatting references.

Read the abstract, introduction, formulation and workflow overview through
the start of Section2.2. Later section refetch timed out. This extension
explicitly handles chronology needed for storage/startup behavior. It selects
period length, clusters periods and chronological segments, checks full-series
operation for the chosen design, and refines temporal resolution using an
objective-error criterion. Its workflow already includes feasibility checking.

Consequently, neither chronological refinement nor evaluating aggregation in
the objective domain is new here. Our direct rational infeasibility records and
paired multiset construction are a specific evidence format; their added value
still requires demonstration. No claim is made that these inspected sections
establish or refute our particular resource-cap proposition.

## Zhou2026: diagnostic temporal refinement is also current prior art

Z.Zhou, “SOC-informed feedback enhancement of time-series aggregation for
storage-embedded power system expansion planning,” TU Delft master thesis,
graduation2July2026.
[Institutional record](https://resolver.tudelft.nl/uuid:0eedcf31-923b-450b-909e-21ee4485d063).

Read the institutional abstract and metadata, not the full thesis. It uses
chronological storage-state diagnostics to identify inadequate representative
days and feed selected days back into planning. This is another reason to avoid
claiming generic diagnostic temporal refinement as our invention. It is a
thesis, not a peer-reviewed journal article; storage and UC-cap certificates
are different objects.

## Consequence for the research decision

The new January service-budget evidence removes a material limitation of the
earlier named-generator-mean examples. It does not make the already known fact
that chronology matters novel. A defensible contribution would need a sharply
stated certified benchmark, demonstrably useful certificate mechanism, or a
new result beyond these established aggregation/verification approaches.
Exact support size still does not count minimum raw information acquisition.
