# Scope and prior-art limit of the whole-day observation collisions

27 September 2026. Targeted primary-paper/code reassessment after the closed 21-call observation experiment; no additional clustering, UC solve or certificate replay. This is not an exhaustive priority search.

## Direct source comparison

Auer et al., *Connecting Representative Periods in Energy System Optimization Models using Markov Transition Matrices*, arXiv:2510.18555v2 (15 July 2026), explicitly separates profile aggregation error from its period-boundary reformulation. Section 4.1 constructs the chronological reference by replacing original days with their representatives. Sections 3.1–3.2 concern expected boundary values, while Section 3.3 acknowledges fractional boundary decisions and possible dispatch correction. These selected body sections were read directly in the [primary HTML](https://arxiv.org/html/2510.18555v2), together with Sections 4.3–4.4; this is not a new whole-paper reading claim.

The [pinned author runner](https://github.com/IEE-TUGraz/LEGO-Pyomo/blob/ce97428aa225037dcbcd848889ef55f3b67c17ba/research/MK/Markov.py) clips thermal dwell times to the representative-period length before creating its full-hourly reference. The inspected code block contains the `MinUpTime`/`MinDownTime` clipping and subsequent `to_full_hourly_model` call. Thus an untouched 48-hour native dwell model cannot silently be identified with the author's 24-hour operational comparison. That does not invalidate a declared approximation comparator; it limits what operational comparison has actually been performed here.

## What our closed results establish

The fixed denominator contains 15 nonidentity whole-day inputs and three identity repeats. Five targets match the complete declared supported-projection observation; three also match the full Hindex under the same RP relabeling. All 15 raw 107-coordinate sequences actually change. The earlier six HOD targets remain DISTINCT and must stay in the account.

For the three stronger collisions, cluster-label chronology is identical. The lost distinction is consistent with replacing different raw days in a common cluster by the same representative profile. This is an inference from our observed equality, not a new claim made by the paper. It is not a counterexample to the paper's medoid-reconstructed reference or evidence that its transition matrices lost a distinction retained by Hindex. Basic non-injectivity of representative-profile replacement is expected; observing it does not establish a new compression mechanism.

The two first-week primary-only collisions (213 and 231) have different Hindex, so they do demonstrate a distinction absent from the primary transition-based observation. No operational contrast for those cases has been established by this observation stage.

## Additional limitation of the proposed operational linkage

The root reviewer reports that the saved first-week days321 fixed-commitment ray uses only one aggregate-balance row and 22 thermal-upper rows, all at hour 119. Its support contains no dwell, transition, ramp or energy row. The separate root-owned linkage audit will bind that support inspection; it was not recomputed in this memo. If its linkage passes, it shows a one-hour capacity shortfall under a specified inherited commitment. It does not isolate an intertemporal bottleneck, unrestricted UC infeasibility, or impossibility of another common schedule. The historical unrestricted days321 label remains UNKNOWN.

## Claim decision

A defensible result is an executable, version-bound collision of a declared author-helper observation, optionally linked to opposite verification outcomes for one explicitly fixed policy under our unchanged model. Its potential contribution is the exact, independently replayable test record and the precise observation/policy contract. Neither novel methodology nor priority follows from this evidence alone.

Do not claim that Auer's operating method fails, that adding chronological cluster labels cannot fix a temporal constraint, that all feasible commitments differ, or that this result proves a new chronology lower bound. The strongest immediate novelty objection is already explicit in the primary paper: original-profile approximation and boundary reformulation are separate error sources, and our strongest collisions fall in the first category. A broader certificate-guided refinement claim also requires comparison with existing feasibility-step and bound-driven refinement methods; that separate source assessment does not alter the closed experiment.

Evidence: `results/research_next/whole_day_observation_preflight/READOUT.md`, independent report SHA256 `67ec0ae2a75e5c1b239143b5f63f3bca317f4d6f2ec2e0ac4e1b30143a3a441d`, and stable independent memo SHA256 `2804c1b7231f988409bb7284e5f80d5a1212c43f4e2adfc7304710b6a5c32bfb`.
