# Published chronology-aware comparator: design and current HOLD

Assessment date: 2026-09-27. **HOLD for execution.** A real author implementation was located, so an honest representation-only comparison is plausible. Its immutable code/submodule identity and our input adapter have not yet been established. No package was installed, no clustering or optimization was run, and no comparator outcome was obtained. This memo fixes a candidate experiment; it is not a completed benchmark or authorization to run it.

## Primary-source audit

**Auer et al., arXiv:2510.18555v2, 15 July 2026**, *Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices*: body Sections 3 and 4.1 and Data availability were read. It combines representative-period profiles and transition information; it is not an assertion that hour-of-day snapshot distributions suffice. The paper directly links the LEGO-Pyomo research/MarkovTransition branch. The paper's method therefore cannot be dismissed using our equal clock-conditioned distributions alone. [Paper and code link](https://arxiv.org/html/2510.18555v2).

The author branch's [Markov.py](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/research/MarkovTransition/research/MK/Markov.py) was inspected at lines 253–259, 349–395 and 1083–1105. It calls Utilities.apply_kmedoids_aggregation before building its models. Importantly, it clips dwell times to the representative-period length; our native 48-hour dwell would change under 24-hour periods. Calling the whole script is consequently unsuitable for an unchanged-physics performance comparison. The isolated preprocessing function is the candidate route. The [experiment README](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/research/MarkovTransition/research/MK/README.md) documents cluster selection and model-solving entry points; none was invoked.

The branch [environment](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/research/MarkovTransition/environment.yml) pins TSAM 2.3.9 and includes Gurobi/Pyomo dependencies. Its [.gitmodules](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/research/MarkovTransition/.gitmodules) points to InOutModule; the branch [license](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/research/MarkovTransition/LICENSE) is MIT. The exact gitlink commit was not resolved in this bounded check. API/branch-browser fetches failed; one read-only git ls-remote returned no ref. These failures do not establish absent code.

The accessible InOutModule **main branch, not a verified paper gitlink**, has [Utilities.py](https://raw.githubusercontent.com/IEE-TUGraz/InOutModule/main/Utilities.py). Inspected functions extract demand/VRES/inflows, aggregate by bus/technology choices, call TSAM k_medoids with rescaling disabled, select medoid profiles, and form weights/Hindex. Default settings include 24-hour periods, aggregated buses, maxInvestment capacity normalization, separate production technologies and Gurobi. The preprocessing itself can invoke an optimization backend; it is not a zero-optimizer operation. Its version and defaults must be audited at the actual gitlink before use. [CaseStudy.py](https://raw.githubusercontent.com/IEE-TUGraz/InOutModule/main/CaseStudy.py), constructor and get_rpTransitionMatrices, counts a **circular last-to-first transition** and returns forward- and predecessor-normalized matrices. This is another representation convention distinct from our free-endpoint UC. The constructor can scale units and merge buses, so adapter round trips and explicit options are essential. Reading current main establishes a route, not historical replication.

**Merrick/Bistline/Blanford:** [EPRI's primary model page](https://esca.epri.com/models/regen/) links [US-REGEN source](https://github.com/epri-dev/US-REGEN). The repository README describes GAMS, a licensed solver and substantial data dependencies. A paper-specific standalone representation entry point/version was not verified. **Orgaz/Bello/Reneses:** the [institutional publication record](https://www.iit.comillas.edu/publicacion/revista/en/1824/Modeling_storage_systems_in_electricity_markets_with_high_shares_of_renewable_generation%3A_a_daily_clustering_approach) was checked; no executable replication link was verified in this audit. Neither is selected as a fallback imitation. This is not a claim that such code does not exist.

## Fixed candidate experiment, subject to the missing gates

Use the **actual author preprocessing at a pinned paper-linked commit**, not a new clustering implementation. Select three 24-hour representative periods, one scenario, the author's audited published/default feature scaling and normalization, no demand stretching, generator merging, transition shifting or random perturbation. K=3 is fixed now; do not sweep K looking for a collision or use K=7 as identity. If pinned-code defaults differ from those above, stop and document the discrepancy before any run. Do not silently substitute another solver or distance metric.

Fix all six January comparisons: week 1 seeds 26093200/26093201, week 2 seeds 26093210/26093211, week 3 seeds 26093220/26093221, each against its own archived identity. Retain the binary UNKNOWN target. Include each week's archived class-preserving control and a repeated identity invocation as preprocessing/determinism controls. Existing UC labels are already known; this is a post-label applicability check, not a blind validation or fresh replication. No case may be replaced based on comparator output.

Before any execution, archive and independently review: exact repository and submodule commits; source/license/dependency hashes; the author example's preprocessing path; complete mapping of our demand, renewable and hydro inputs into its accepted native tables; a lossless round trip for those fields; documented exclusions or constants; units/scaling; chronological day boundaries; and the clustering solver's deterministic options and tie handling. Unsupported hydro/availability semantics are a HOLD, not permission to invent surrogate columns. A full native UC or network adapter is unnecessary for a representation-only test and must not be claimed.

The observation to compare must be the **actual data consumed by the published reduced chronology formulation**: representative profiles, occurrence weights and directed transition probabilities/counts, plus any additional consumed temporal feature revealed by a read-only dependency audit. Preserve the hour-to-cluster sequence for provenance, but do not add it to the tested observation if the published formulation only consumes its transition matrix. Compare modulo all cluster-label permutations (only six for K=3). Raw position IDs and medoid day indices are metadata, not a reason to call representations unequal. Treat profiles as their actual numeric values, counts as integers and normalized counts as exact rational ratios where possible. Keep a numeric difference diagnostic separate from exact equality; never infer equality from a loose tolerance. Incomplete/ambiguous outputs are UNKNOWN.

## What each outcome would mean

- Different complete representations: the published method can distinguish this pair. Our snapshot counterexample does **not** establish information loss for that method; nothing yet follows about its UC feasibility, cost accuracy or solver speed.
- Equal complete representations with independently differing exact UC labels: this fixed representation has a collision on these instances, conditional on the input adapter and complete-consumption audit. It does not prove a downstream implementation returns a wrong answer, because it could abstain or invoke refinement.
- Unequal transition matrices but equal profiles: chronology supplies a concrete distinguishing feature; no need for a downstream UC solve to establish that limited fact.
- Repeated identity differs, solver ties are uncontrolled, or the adapter/version is unverified: report comparator UNKNOWN/HOLD and retain all attempted outputs.

The useful next step is pinning and auditing this real preprocessing route. Unique raw bigrams or unclustered full-day vectors do not substitute for it. Even a successful representation check would be a careful comparison against existing methods, not evidence that the broad idea of retaining chronology is new.


## Follow-up: immutable identity resolved; exact adapter still HOLD

This follow-up supersedes only the unresolved code-identity item above. No clustering, installation, model build or solve occurred. The earlier reference to research/MarkovTransition as a branch was imprecise: the case-sensitive **tag** resolves to **ce97428aa225037dcbcd848889ef55f3b67c17ba**; the lower-case research/markovtransition branch currently points to the same commit. Read-only git ls-remote and the official GitHub commit/tree API independently exposed this identity. Commit author Felix C. A. Auer; timestamp 2026-07-13T14:10:14Z; commit message identifies the journal-submission run list. This closely links the release to v2, but does not independently reproduce all paper results. [Pinned author commit](https://github.com/IEE-TUGraz/LEGO-Pyomo/commit/ce97428aa225037dcbcd848889ef55f3b67c17ba).

The commit tree is aeb759c898ed9ba913ce24d992e6c21f541eba56. Its actual InOutModule gitlink is **8b1f53a75d152645e5ff8c7d5f417befaf316da5**, not whatever main happens to contain. The activation-script gitlink is45c8f9a61f8d94dc11f0ed4f2d868d5de4ad2c79. Main code and submodule have MIT licenses. Relevant UTF-8 response-byte SHA256 bindings, obtained directly from official immutable raw URLs:

| File | SHA256 |
|---|---|
| research/MK/Markov.py | 955e29e9096f01992a615a2b897c0721243475a14db1df56e30fba84ad137e6e |
| research/MK/jobs.txt | ff5b3b070b0de400f51e6988cb550f4e4d5ef05b881f03e47746c665f2fe1710 |
| InOutModule/Utilities.py | f9d6b69fc319ccd51c1e2cffa6ddc6f120e5eab457e451849331f914ce5984f2 |
| InOutModule/CaseStudy.py | dccce27eaa9db4dbeda6e71224e7019da503d654c9613ed481ed7a6220f26663 |
| LEGO/modules/vres.py | dfefd47149a2c81cf46725e2ee5d7d41610c068c6f1b26eb4cebeda3f45f10c3 |
| LEGO/modules/thermalGen.py | 5b91956d8c8c2ee8e0b524b701bbd41db2ee6bfcdb7b43a25a161d4a382bf871 |
| LEGO/modules/power.py | 1cc52bb9bf322e9e459489db5c8137dda6c81af5524c280256c59b5eb83b9fad |

The pinned [publication jobs](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/research/MK/jobs.txt) explicitly include K=3, transport-network operation/investment comparisons and transformed transition cases. These are not our UC model. The pinned [Markov runner](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/research/MK/Markov.py) retains the previously noted dwell clipping.

### Why an exact 107-component adapter is not yet justified

Our hourly package is (41 pmin,41 pmax,1 net,24 nodal), with unit/bus identities fixed. It includes fixed hydro dispatch through equal lower/upper bounds, constant thermal ratings, zero renewable lower bounds, renewable upper availability, net nodal demand after rooftop PV, and an independently evaluated aggregate net value. Our inspected native_rows code calculates net and nodal separately; even their exact binary64 sums are not automatically redundant. Raw source-hour IDs are provenance, not an acceptable hidden feature for a comparator.

The pinned author schema can carry bus demand, renewable profiles and inflows. However, carrying numbers in a table and retaining their **operational meaning and exact represented values** are separate tests:

| Our component | Candidate author field | Unresolved condition |
|---|---|---|
| Constant thermal pmin/pmax | ThermalGen.MinProd/MaxProd | Straightforward as common metadata; verify unchanged units. |
| 24 nodal demand entries | Power_Demand by bus | Numeric copy is possible; constructor/aggregation options and negative-demand admissibility need an explicit check. |
| Renewable pmax | Power_VRESProfiles with native MaxProd | Division into capacity factors followed by multiplication may alter binary64 values; exact round trip is required. |
| Fixed hydro pmin=pmax | Power_Inflows or VRES availability | An inflow/availability record alone does not establish the fixed-output lower bound. |
| Separate aggregate net | No corresponding independent balance datum verified | Recomputing from nodal values loses our exact encoded endpoint unless equality is established or a separate faithful field is found. |

The inspected [pinned VRES module](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/LEGO/modules/vres.py) supplies generation plus curtailment equal to availability; that differs from our mandatory hydro output unless extra documented settings eliminate curtailment. The [power module](https://raw.githubusercontent.com/IEE-TUGraz/LEGO-Pyomo/ce97428aa225037dcbcd848889ef55f3b67c17ba/LEGO/modules/power.py) has load-shedding variables. Neither module is proposed as a replacement for our frozen model. This inspection is sufficient to reject a claim of an already validated unchanged-physics adapter, not a proof that no adapter could ever be constructed.

A TSAM call directly on107 custom columns would avoid schema loss, but it would be a transparently **adapted generic clustering comparator**, not execution of the publication's original preprocessing recipe. Adding dummy buses/technologies or an unconsumed sidecar to smuggle missing columns would also fail the promised comparison. Do not do either under the author-method label.

A narrower authentic test could compare the author's demand/VRES/inflow observation on faithfully mapped supported inputs, while keeping our UC model untouched. Its conclusion would concern that declared projection of our inputs, not lossless107-component representation or native UC performance. Establishing such a projection requires a reviewed input adapter and exact record of excluded/reconstructed fields before execution. Since neither this narrower adapter nor a full exact one has been implemented/validated, the current verdict remains **HOLD**, now for semantics and execution prerequisites rather than missing source identity.
