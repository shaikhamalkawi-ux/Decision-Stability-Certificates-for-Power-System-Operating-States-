# Evidence map for the research note and Arabic decision report

This map covers completed evidence through commit
`520fe5974a4d92892906c42ce51a9d12ef304d3a`. Later follow-ups must be reviewed
separately before entering a manuscript. A numerical solver label, an exact
continuous point, a binary witness and a separating certificate are different
types of evidence. Uniform finite-bound expansion is the archived binary64
value of `1e-5`; strict nominal flags remain separate.

| Scientific statement | Authoritative archived evidence | Qualification |
|---|---|---|
| First January unrestricted targets have opposite common-cap verdicts to the identity. | [Seasonal service-cap evidence](../../results/research8h/seasonal_transfer/), [energy-bound review](../../results/research8h/energy_lp_refinement/independent_review.json) | Two permutations of the same week; cap 23195 MWh; no individual generator means. |
| Fixing each package's hour of day still permits opposite common-cap verdicts. | [HOD independent review](../../results/research8h/hour_of_day/independent_postrun_review.json), [HOD readout](../../results/research8h/hour_of_day/READOUT.md) | Two ordinary cases; complete joint snapshots are preserved, daily trajectories are not. |
| The same HOD family produces certified negatives in two further January weeks. | [Fresh target final review](../../results/research8h/fresh_targets_postrun_review/final_ledger.json), [three rays](../../results/research8h/fresh_targets_postrun_review/negative_certificates.json), [all four outcomes](../../results/research8h/fresh_january_weeks/targets/outcomes.csv) | Three negatives and one UNKNOWN, all four retained; same grid and month. |
| Each fresh week has an independently accepted binary reference. | [Week 2 review](../../results/research8h/fresh_reference_postrun_review/week_2.json), [week 3 review](../../results/research8h/fresh_reference_postrun_review/week_3.json) | These are feasible upper witnesses, not proven optima; strict nominal membership is false. |
| The original unrestricted optimum penalties lie in two positive finite intervals. | [Energy refinement review](../../results/research8h/energy_lp_refinement/independent_review.json) | Exact lower bounds plus accepted binary uppers, outward decimal rounding; optimum differences, not merely incumbent differences. |
| First-week HOD optimum penalties also have positive finite intervals. | [HOD energy review](../../results/research8h/hour_of_day_uncapped/independent_postrun_review.json), [exact brackets](../../results/research8h/hour_of_day_uncapped/energy_brackets.json), [display table](../../results/research8h/hour_of_day_uncapped/summary.csv) | [566.366617,1336.352662] and [858.121844,1408.976215] MWh, outward six decimals; neither optimum solved exactly. |
| The full-day ordering experiment includes a positive and unresolved cases. | [Day-block independent review](../../docs/research8h/DAY_BLOCK_POSTRUN_REVIEW.md) | One expanded binary positive, zero certified negatives and four UNKNOWN out of all five nonidentity day orders. |
| Fixing one commitment can fail even when the full UC model is feasible. | [Fixed identity evidence](../../results/research8h/day_fixed_identity/independent_review.json), [day-block readout](../../results/research8h/day_blocks/READOUT.md) | All five fixed-commitment restrictions fail; day312 remains feasible under a different commitment. |
| April and October do not supply a new certified ordinary negative. | [Seasonal continuation review](../../results/research8h/seasonal_cap_continuation/independent_postrun_review.json) | Four continuous points; all four binary target outcomes UNKNOWN. The older seasonal gate remains unmet. |
| Dwell-row deletion explains the model's order dependence under its assumptions. | [Exact no-dwell replay](../../results/research8h/no_dwell_symmetry/independent_replay.json), [proof protocol](../../docs/research8h/NO_DWELL_SYMMETRY_PROTOCOL.md) | Eight supplied archive mappings plus a canonical Y/Z lifting argument; no claim for storage or binding inter-hour ramps. |
| Cap bands and half-gap error floors follow for the two original unrestricted pairs. | [Cap-band review](../../docs/research8h/CAP_BAND_INDEPENDENT_REVIEW.md) | Arithmetic consequences of existing bounds; no cap sweep, new cases, population error estimate or minimum-bit theorem. |
| Six fixed shorter proof candidates do not transfer to the HOD targets. | [Root replay](../../results/research8h/hod_fixed_ray_transfer/root_independent_review.json), [full null ledger](../../results/research8h/hod_fixed_ray_transfer/summary.json) | Valid nonseparating vectors are not feasibility witnesses and do not rule out another certificate. |
| A portable standard-library checker reproduces selected archived mathematics. | [Relocation replay](../../results/research8h/relocation_smoke/summary.json), [checker](../../src/research8h_standalone_verify.py) | Same-host fresh-directory replay, 35 adversarial fixtures and four real cases; native input assembly is a separate check. |
| General chronology aggregation and numerical certification have strong prior art. | [Primary metadata audit](REFERENCE_PRIMARY_METADATA_AUDIT.md), [safe-bound reading limits](SAFE_BOUND_PRIOR_ART.md), [clock-conditioned comparison](CLOCK_CONDITIONED_PRIOR_ART_FINAL.md) | Exact firstness or a broadly new method is not established. Each reading note states its actual access scope. |

The first-week energy figure depicts only the two original unrestricted targets
and the identity. The four-row energy table adds two HOD targets. Fresh-week
capped verdicts do not automatically provide finite uncapped energy penalties.
No field, AC-network, fuel-input, emissions or monetary-cost result follows.

The original V8 Zenodo DOI and frozen V8/V8R1 manuscripts remain separate from
these experimental findings. Delivery manifests bind bytes and published Git
commits; remote Drive metadata checks do not constitute remote content hashing.
