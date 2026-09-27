# Fixed HOD restricted-model follow-up

All four declared LP restrictions contain an independently verified exact point after uniform finite-bound widening by tau = Fraction.from_float(1e-5). Neither of these fixed templates supplies a linear explanation of either full-model negative. The two original HOD full-model infeasibility certificates remain unchanged.

| Target | Fixed retained-row template | Rows / columns | Exact expanded continuous membership | Strict nominal membership | Solver seconds |
|---|---|---:|---|---|---:|
| seed_26093200 | two_cc | 19,985 / 23,016 | verified | not established by this point | 0.350589 |
| seed_26093200 | locality48 | 28,689 / 23,016 | verified | not established by this point | 0.773547 |
| seed_26093201 | two_cc | 19,985 / 23,016 | verified | not established by this point | 0.330389 |
| seed_26093201 | locality48 | 28,689 / 23,016 | verified | not established by this point | 0.763116 |

This conclusion is stronger than the earlier six supplied-ray nulls. A feasible exact point rules out every valid Farkas contradiction formed from that same expanded retained-row/column-box system. Merely trying different multipliers cannot produce an expanded-model linear infeasibility certificate for these four restrictions. This does not establish binary feasibility, strict nominal LP feasibility, or the absence of nonlinear or integrality-based certificates. The inspected returned vectors have 245, 273, 255 and 382 original state coordinates that are not exactly binary, respectively; the independent membership checks deliberately use a zero integrality mask.

The two_cc template keeps all four temporal families for 107_CC_1 and 118_CC_1 only, with the complete static/DC/network/cap background and all column bounds. It removes other generators' transition and exclusivity rows as well as their dwell rows. The locality48 template keeps all transition/exclusivity rows and only complete dwell rows whose actual state support lies within hours 60–107, again retaining the complete background and boxes. These are row restrictions of the full 168-hour model, not standalone two-generator or 48-hour physical systems. There are no named-unit mean constraints; the fossil cap is 23,195 MWh.

Both original positive inputs, january_identity and seed26100200, retain exact expanded binary membership for both templates by actual row deletion: four prespecified control/rule memberships. The independent prepared review replayed both full original-binary points and all four row maps. Strict membership was not claimed.

All four archives are byte-identical copies of the already frozen fixed-ray subset models. Cases, templates, order, objective and budgets were fixed before this run. The previous six nonseparating rays and their parent outcomes remain bound and unchanged. This is a post-label, same-week explanation follow-up, not primary replication, a sparsity search, IIS discovery, a minimum-information result, or a new certificate method.

A single authorized invocation made four LP calls, with no MIP, retry, alternate objective, ray-recovery optimization or adaptive mask. Total actual solver time was 2.2176412000262644 seconds; phase elapsed time was 6.278909800021211 seconds. Configured call limits were 30 seconds, the phase budget was 300 seconds, and the final actual-call guard required 35 seconds remaining before both the phase end and 04:00 UTC. All initial decisions, post-write final guards, call order, one-run logs and zero-overrun accounting passed independent review. Shared-host timings are not performance benchmarks. No dual certificate or normalized energy lower bound was generated because every LP had an accepted continuous point.

Independent prepared and post-run evidence: results/research8h/hod_reoptimized_subsets_independent_review/prepared_review.json and postrun_review.json. The post-run status is INDEPENDENT_HOD_SUBSET_POSTRUN_PASS; all 155 frozen input bindings and all 61 pre-readout producer artifacts were unchanged. Reviewer optimizer calls: zero.

Frozen manifest SHA256: 1d3c54426828dcca5684ca21d6f1af95f2c05cfc87631423ae939a354c867119. Source SHA256: 3c9d03015a23a277c0f4642be696843d17f2540bac2a2116247e11e0d80f8041. Protocol SHA256: eafa85dba6f772668a263f19f37eac086915cb1d6d599fabdc91ebac097ff0d2.
