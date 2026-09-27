# Final adversarial check: clock-conditioned snapshots

Date: 27 September 2026 UTC. This is a focused primary-source check, not an exhaustive priority search. Previously reviewed Auer, Bahl, RiSES and Saarela papers were not re-searched. No optimizer, model modification or new empirical test was performed. Four additional papers were inspected with the access limits below.

## Decision and exact claim

The defensible advance is a controlled, independently certified benchmark result: equal complete joint hourly-input multisets within each hour of day do not suffice to determine the fossil-cap feasibility of these residence-constrained UC models. For two January week-1 HOD pairs, independent exact lower bounds and binary witnesses also establish finite, positive intervals for the change in optimal fossil MWh. Three later negatives across two previously unseen January weeks strengthen repeatability within this system; the fourth later target is UNKNOWN.

Write the observation precisely as O(X) = ((multiset of X_t for t mod 24 = h) for h=0,...,23, X_0:47, X_120:167), together with the same time-invariant model and boundary conventions. The result is insufficiency of this observation for the declared class. The equality is stronger than matching separate marginal distributions, averages or solar timing because X_t is the joint package. It is weaker than preserving daily profiles, lagged joint distributions, runs or transitions. Whole daily trajectories generally differ. Thus “same diurnal profiles,” “same chronology statistics,” and “representative-day methods cannot work” would be false extensions.

No new general aggregation, optimization, exact verification, dual-bound, or information-theoretic technique has been established by this experiment. An indistinguishability conclusion follows elementarily from a positive/negative pair with the same observation. No exact matching predecessor was established in the inspected material, but this does not establish firstness.

## Primary comparisons

### Merrick, Bistline and Blanford: guaranteed chronological aggregation

James H. Merrick, John E. T. Bistline and Geoffrey J. Blanford, *On representation of energy storage in electricity planning models*. Journal metadata: Energy Economics136,107675 (August2024), [DOI10.1016/j.eneco.2024.107675](https://doi.org/10.1016/j.eneco.2024.107675). **Body read:** [author preprint arXiv2105.03707v2](https://arxiv.org/pdf/2105.03707), dated31May2021, Sections2.2,3.4 and AppendixA.4, printedpp4–6,10–12,28–29. Journal body not read; version equivalence is not assumed.

The preprint gives sufficient lossless aggregation conditions: identical demand/availability within states, deterministic successor/predecessor structure and equal run durations. It explicitly distinguishes state frequency from residence duration and does not prove minimality. This is strong prior art against claiming a new general chronology-sufficiency theory. Our HOD snapshot observation omits precisely such linkage information; failure is compatible with their theory. Their inspected formulation is continuous storage/capacity planning, not the exact paired UC fossil-cap certificate construction here.

### Gonzato, Bruninx and Delarue: full-model checks of reordered synthetic inputs

Sebastian Gonzato, Kenneth Bruninx and Erik Delarue, *Long term storage in generation expansion planning models with a reduced temporal scope*, Applied Energy298,117168 (15September2021), [DOI10.1016/j.apenergy.2021.117168](https://doi.org/10.1016/j.apenergy.2021.117168). **Body excerpts read:** [project-hosted author paper](https://www.epocbelgium.be/sites/epoc/files/2.2.5.2%20Gonzato%2C%20Bruninx%2C%20Delarue_2021_Long_Term_Storage_In_Generation_Expansion_Planning_Models_with_a_Reduced_Temporal_Scope.pdf), indexed Section2.1.2/2.2, Sections4.1–4.2/equation42 (printedp8), Section7 (p12), conclusion(p13). Direct PDF fetch failed; this is indexed body inspection, not full-document reading.

They construct synthetic time series from selected/ordered representative periods and solve full-year models to distinguish input-aggregation error from reduced-formulation error. Therefore controlled ordering studies and judging representations through downstream optimization are established. Their ordering may replace or combine representative periods and need not retain every original joint hour or the exact HOD-conditioned multiset. The inspected tests are linear generation-expansion/storage models. This is close methodological adjacency, not an established exact match to the common-cap UC pairs.

### Orgaz, Bello and Reneses: daily trajectories and system-state transitions

Alberto Orgaz, Antonio Bello and Javier Reneses, *Modeling storage systems in electricity markets with high shares of renewable generation: A daily clustering approach*, International Journal of Electrical Power & Energy Systems137,107706 (May2022; onlineNovember2021), [DOI10.1016/j.ijepes.2021.107706](https://doi.org/10.1016/j.ijepes.2021.107706). Metadata verified at the [authors' institution](https://www.iit.comillas.edu/publicacion/revista/en/1824/Modeling_storage_systems_in_electricity_markets_with_high_shares_of_renewable_generation%3A_a_daily_clustering_approach). **Body excerpts read:** [institutional manuscript](https://repositorio.comillas.edu/xmlui/bitstream/handle/11531/64001/IIT-21-194R.pdf?isAllowed=y&sequence=1), Section2.1 step7, Section2.2 equations1–6 (printedp5), concluding discussion. Direct PDF opening failed.

The model groups days, then hours into states, and retains consecutive blocks/state switches for intra-day storage. Hence their observation includes trajectory information absent from a clock-conditioned snapshot histogram. Our HOD pair is not a counterexample to their representation. The inspected study assesses market-model accuracy versus computational detail, not rationally certified feasibility separation under a shared fossil cap.

### Shortt, Kiviluoma and O'Malley: chronological UC effects and diurnality

Aonghus Shortt, Juha Kiviluoma and Mark O'Malley, *Accommodating Variability in Generation Planning*, IEEE Transactions on Power Systems28(1),158–169 (February2013), [DOI10.1109/TPWRS.2012.2202925](https://doi.org/10.1109/TPWRS.2012.2202925). **Primary body read:** [UCD manuscript and metadata](https://researchrepository.ucd.ie/server/api/core/bitstreams/614163a0-f76e-4ea5-8feb-4812e2f414b8/content), introduction, SectionIII and late discussion/conclusion (manuscriptpp1–3,11); indexed passages supplement direct PDF access.

Their UC-versus-dispatch comparison already quantifies system-dependent chronology/cycling cost effects and highlights diurnal demand patterns. The discussion reports omitting minimum-up/down constraints after checking their schedules for violations, while warning that long dwell requirements can require them. Thus our dwell-driven common-cap result is not their demonstrated mechanism. It still cannot be described as discovering that chronology or daily variation has economic consequences.

## Claim ledger and publication consequence

| Claim | Current assessment |
|---|---|
| Same HOD-conditioned complete joint snapshot data can have opposite common-cap feasibility. | Supported for the archived expanded models; a precise new result in this project. Priority unresolved. |
| Fixing hour of day removes the explanation that solar/loads were merely moved to a different clock hour. | Supported as a control. Within-day trajectories and inter-hour relations still change. |
| Optimal fossil requirements rise by a known exact percentage. | Unsupported phrasing. Report rigorous rational intervals, not exact optima or point estimates. |
| Exact certificates make the experiment independently auditable. | Supported implementation/evidence contribution; exact verification methodology is established. |
| The result defeats representative-day, state-transition or chronology-aware aggregation. | Unsupported: those approaches may distinguish these inputs immediately. |
| Three later negatives demonstrate broad seasonal/network generalization. | Unsupported. They are two additional January weeks in the same system; retain one UNKNOWN. |
| This is the first clock-conditioned UC impossibility benchmark. | Not established by this bounded search. |

The strongest paper framing is an auditable insufficiency result for one explicitly defined data representation, with a proof-bearing UC benchmark and honest nulls. The practical value is clearer than the original arbitrary-hour shuffle: time-of-day alignment, static feasibility and named-unit-mean confounds have been controlled. It remains a synthetic stress test, not a plausible-weather generator or evidence of a field operating change.

One discriminating comparison, if a future study is authorized, is to expose an established representative-day or state-transition representation to the paired inputs and measure whether its retained information distinguishes them before solving UC. This would separate a limitation of clock-conditioned snapshots from a limitation of a real aggregation method. It should be fixed before outcomes, retain the complete native model, and avoid claiming solver benefit merely because a certificate checks quickly. No such head-to-head comparison was run here.
