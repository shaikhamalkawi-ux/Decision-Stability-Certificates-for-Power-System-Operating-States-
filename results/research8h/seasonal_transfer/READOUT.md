# January service-order experiment: two certified negatives

Both prescribed January ordinary twins are infeasible in the full continuous
DC-network relaxation under the frozen shared fossil-energy cap. Each has an
exact rational certificate for the archived binary64 model, with strictly
positive separation after outward 1e-5 relaxation of every finite row and
column bound. Therefore the encoded binary model is also infeasible. There are
no individual generator-mean constraints in these models.

| Case | Changed hours | Hourly network/cap control | Binary or exact-certificate outcome | LP solve seconds |
|---|---:|---|---|---:|
| January identity | 0 | Pass | Verified binary-network witness | Not solved |
| Ordinary seed 26093100 | 72 | Pass | CERTIFIED_INFEASIBLE | 4.2529755 |
| Ordinary seed 26093101 | 71 | Pass | CERTIFIED_INFEASIBLE | 3.8980971 |
| Commitment-class control 26100100 | 33 | Pass | Verified binary-network witness | Not solved |

Every ordinary hourly-network control jointly permutes the reference dispatch,
rounded commitment, angles and complete native physical inputs. Its exact
fossil-energy sum is preserved. These particular permuted schedules have 278
and 286 dwell violations; those failed candidates alone are not the negative
evidence. The separate exact LP certificates rule out every schedule in the
declared relaxation. The commitment-class control leaves the entire binary
commitment chronology unchanged and passes direct dwell, transitions, ramps,
native dispatch, network and cap checks. Both 48-hour edge blocks remain fixed.

The January cap is **23,195 MWh**, calculated as ceil(101 E / 100) from the exact
binary64 fossil sum in the archived January returned vector. Here
E = 22,964.941239556443 MWh, with headroom 230.05876044355804 MWh, or
1.0017824911621743% of that reference. All 23 Coal/Oil/NG units enter with unit
weights, and `121_NUCLEAR_1` is excluded. This is a reference-based fossil-energy
benchmark, not a carbon cap or an independently selected policy requirement.
The January reference was a verified incumbent from a time-limited solve, with
reported dual bound 22,616.830716809134 MWh and relative gap 0.01515834589411876;
it was not established optimal. Thus this cap is not described as 1% above the
unknown optimum.

The two proof supports contain 1,715 and 1,253 nonzero row multipliers and 5,667
and 5,138 nonzero combined variable-bound coefficients, respectively. Their
positive robust separation margins are 46,526.78957194592 and
194,355.96483466134 in the unnormalized ray scales; these numbers are not MWh
gaps and are not comparable measures of case difficulty. Both certificates use
the global fossil-cap row, which depends on all 168 hours. Nonzero rows carry
120 and 114 distinct hour labels, without any claim of minimum chronological
information or memory. Raw rays, rejected candidates, selected sign-cone
projections and full exact fraction results remain archived. Projected rays
are new candidate vectors whose complete separation is checked exactly.

The inherited generic support metadata counts mixed generator, bus and branch
labels under `individual_units_in_nonzero_rows` and mentions target means in a
generic interpretation string. Neither field establishes a generator count or
the presence of mean constraints here. Use each proof's separately classified
`support_clarification.json` together with the actual row-family counts. The
frozen source and original proof files remain unchanged.

The subsequent solver-free archived replay passed for both certificates, with
model/metadata hashes and exact gap numerators/denominators matching the original
records. Classified thermal-generator row labels number 23 and 22. The selected
exact variable-bound columns by P/U/Y/Z/theta block are
3557/762/788/486/74 and 3499/572/696/325/46. These clarify proof support without
removing the all-hour global-cap dependency. See
`archived_certificate_replay.json` and the per-certificate support sidecars.

All 136 frozen source, reference, generated-model, permutation and control files
passed the end-of-run size/SHA-256 check. All models and controls were frozen
before the first LP. Exactly two LP calls ran, totaling 8.1510726 solver seconds;
the predeclared routing skipped both MIPs after robust exact rejection. Recorded
generation/preflight time was 160.8368168 seconds and solve/postprocessing time
10.9044835 seconds. The script reports 171.794086 seconds from entering `main`;
this excludes earlier Python import/startup delay on the shared host and is not
a hardware benchmark.

January is the only eligible held-out week. April seeds 26093400/26093401 and
control 26100400, and October seeds 26094000/26094001 and control 26101000,
remain **NO_REFERENCE / NOT_RUN**, without replacement. The existing old July
reference passed an additional identity implementation check and is outside
the held-out denominator. The predeclared gate requiring negative replication
in at least two held-out weeks is **not met**, because only one eligible week
exists. The two January draws are nested within that week, not two independent
seasonal replications.

The result establishes order-sensitive chronological obstruction under this
specific benchmark cap despite constructive hourly-network feasibility. It
does not establish that the cap is indispensable, a finite energy penalty,
uncapped binary feasibility, new-network generalization, a field result, or
novelty of the checking method. Those require additional evidence outside this
frozen arm. Earlier July mean-target negatives, service LP positives, failed
fixed schedules and unrestricted MIP timeouts retain their separate scopes.
