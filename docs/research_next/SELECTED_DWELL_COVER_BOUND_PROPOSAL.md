# One next discriminator: selected-unit residence plus capacity-cover bound

**Proposal only; no new scientific table, threshold, model, optimization or implementation has been run.** Proceed, if authorized, with one exact time-expanded shortest-path lower bound on the sum of fossil electrical generation in the two original worlds. Retain residence dynamics for three fixed units and relax the other chronology/network constraints. This is classical dynamic programming and a necessary-bound construction, not a new algorithm or a minimum-information result.

## Why this particular bounded step

The original HiGHS and SCIP common searches returned no accepted binary point; their timeouts do not prove nonexistence. The complete hourly cover bound was independently verified but is about 845.2394288 MWh below each cap. The two new affine inequalities reject the pointwise union and all binary supersets, but allow the saved fractional point and do not reject all possible commitments. A useful next calculation must incorporate some chronological integrality without simply extending a solver timeout or rerunning the same hourly cover.

Read-only inspection of the closed native specification, generator CSV, fractional census and two actual cut records gives a specific choice:

| Retained unit | PMin / PMax MW | Native minimum up / down h | Recorded exact-nonbinary U entries |
|---|---:|---:|---:|
| `115_STEAM_3` | 62 / 155 | 8 / 8 | 36 |
| `116_STEAM_1` | 62 / 155 | 8 / 8 | 32 |
| `118_CC_1` | 170 / 355 | 8 / 5 | 35 |

These three units account for 103 of the saved 173 exact-nonbinary U coordinates. This is a **post-hoc structural choice from a closed census**, not an unseen-data selection or evidence that these units cause infeasibility. Freeze these exact three labels before any new bound calculation; do not replace them after a null.

The longest-residence units are `123_STEAM_3` (140/350 MW) and `121_NUCLEAR_1` (396/400 MW), each with minimum up24/down48. Neither appears in the saved fractional-U census or either82-term cut. That makes blindly fixing them to their observed LP values unpersuasive, and their apparent integrality is not a valid universal fixing proof. The proposed relaxation leaves their decisions unrestricted (and relaxes their residence), so a negative bound still covers all of their possible full-model schedules.

The cuts have only positive U coefficients. Their support includes six hours of `115_STEAM_3`, one hour of `118_CC_1` and no `116_STEAM_1` hours; most support lies on other units. Thus their union rejection cannot be promoted to a three-unit fixing. This proposal does not add an unreviewed resource-state approximation of those cuts or assume the other commitments equal their LP/union values.

## Exact relaxation and lower bound

Reuse the independently checked original row/box premises and fixed two-world/hour denominator from `common_capacity_cover`. For each world/hour, keep its existing valid floor `d_it` on fossil generation. Let `a_j,b_j` be the common integer minimum-output and capacity coefficients of the23 fossil units, and `tau = Fraction.from_float(1e-5)`.

For a current on/off pattern `s` of the three retained units S, use the remaining20 fossil units R in a complete exact-capacity 0/1 cover table. Their chronology is deliberately relaxed, but they remain binary within each hourly cover. The necessary residual capacity threshold is

`h_t(s) = max(0, ceil(max_i d_it - 23*tau - sum_(j in S) b_j*s_j))`.

Let `M_R(h)` be the complete-table minimum of `sum_(j in R) a_j*u_j` over binary subsets with capacity at least `h`. If no cover exists, that selected pattern is impossible at that hour. Otherwise define

`m_t(s) = sum_(j in S) a_j*s_j + M_R(h_t(s))`,

`g_it(s) = max(d_it, m_t(s) - 23*tau)`.

The two23*tau terms have the same separate roles as in the accepted hourly proof: one comes from the23 thermal upper rows and one from the23 lower rows. Do not replace either by20*tau merely because three units are conditioned. The original aggregate/box expansions remain inside d; each original cap retains its own single tau.

Every full common binary solution projects to a feasible residence trajectory for the three selected units. At every hour its remaining20 binary commitments form an eligible cover, so its fossil outputs satisfy both `g_it`. Use a single fixed arc cost

`g_0t(s) + g_1t(s)`.

Let L be the exact minimum total arc cost over all admissible selected-unit trajectories. Then **every** original common binary solution satisfies `E_0 + E_1 >= L`. The required total cap is `2*23195 + 2*tau`. A strict `L > 2*23195 + 2*tau` proves common binary infeasibility in the original uniformly expanded model. An empty layered graph also gives a negative certificate. Equality or a lower value is a null. The scalar sum is chosen prospectively; do not add alternative scalarizations, separate optimized objectives or a Pareto-frontier search after observing it.

This bound can be stronger than the independent hourly minimum because it enforces the selected units' residence across hours. It remains a relaxation: all other units' residence, ramps and the network are omitted; nuclear is treated by its safe unconditional box exactly as in the old cover proof. Omitting these restrictions enlarges the possible set and is valid only for the negative implication. A minimizing graph path is a relaxed partial commitment, not a verified common candidate or dispatch. This proposal authorizes no subsequent fixed-schedule LP.

## Boundary and original-matrix proof obligations

Use state `(on/off, remaining locked hours)`, with age truncated once the native dwell is satisfied. At hour0, both on and off are mature, matching the original free initial condition; `Y0=Z0=0`. At `t>=1`, a switch is permitted only from an unlocked state, and its new lock is `minimum_dwell(new_status)-1`. Continuing decrements a positive lock. At the end, accept every reached state regardless of remaining lock, matching clipping at the horizon. Do not impose an extra initial or terminal dwell requirement.

Before calculating, compare these rules to every actual selected-unit transition/mutual-exclusion/minimum-up/down row and original state box. The transition/state coefficients and endpoints are integral; with exact binary states and tau<1, their expanded inequalities enforce the same discrete relation. This correspondence must be checked on the archived rows, not inferred solely from the native CSV or helper name. If any selected row/box convention differs, stop as UNSUPPORTED rather than changing the automaton or rounding a parameter. In particular, the gas unit's archived down time is5 hours; do not substitute the raw CSV value4.5.

The inspected assembly source, `src/temporal_lp_certificate.py` (SHA256 `6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4`, lines32–86), fixes the initial Y/Z upper bounds to zero, takes the ceiling of native residence times, and skips temporal rows at hour0. At each later hour it writes `U_t-U_(t-1)-Y_t+Z_t=0`, `Y_t+Z_t<=1`, `sum_(s=max(1,t-up+1))^t Y_s-U_t<=0`, and `sum_(s=max(1,t-down+1))^t Z_s+U_t<=1`. Those formulas explain the proposed mature-initial and clipped-terminal automaton. This is source grounding only; future admission must still verify the actual archived selected rows, exact coefficients, endpoints, masks and initial boxes before using that correspondence.

Retain both selected coal units as separately labeled machines. They share the relevant nameplate/dwell parameters, but are at different buses and are not interchangeable in the full network model. No full-model symmetry reduction or unit aggregation is claimed. Even symmetry valid only in this relaxation is unnecessary at the proposed size and should not be introduced in the first implementation.

## One finite guarded calculation

The selected residence state count is at most `(8+8)*(8+8)*(8+5) = 3328` per hour. There are at most559,104 hour-state cells and at most4,472,832 candidate transitions under the loose bound of eight successor on/off patterns per state. These are design bounds, not measured scientific outputs.

One prospective run would use:

- The fixed two original worlds, selected three labels and original caps; no alternative unit set, schedule fixing or model modification.
- One complete20-item cover recurrence per admitted static coefficient tuple, with the old integer/nonnegative/world-equality checks and capacity sum at most100,000. No cover envelope or fractional fallback.
- Exactly168×8 conditional hourly patterns before the residence recurrence; retain every impossible pattern and both world floors.
- Exact integer arithmetic after one lossless common dyadic scale for the rational hourly costs; fail if the required denominator exceeds256 bits. Archive the scale. Do not approximate costs or drop nearly equal labels.
- One complete layered min-cost recurrence with deterministic state order and no heuristic pruning. Archive every reachable/unreachable state value and the complete transition rule, so a reviewer verifies a **minimum**, not merely one cheap path. A partial table cannot support a negative conclusion.
- A300-second soft arithmetic limit, at most600,000 archived hour-state values and at most5,000,000 transition checks; check time during layer/transition sweeps and after writes. Exceeding any guard is INCOMPLETE, not a bound; no automatic restart, broadened set or longer budget.
- Invented small exhaustive residence/cover controls before input freeze, then source/prepared gates and one separately authorized run. Independent replay of the full recurrence, original selected dwell premises and exact final comparison is required before a scientific rejection claim. No optimizer is used.

## Interpretation and stopping rule

A verified strict excess would be the desired finite integer certificate for the full common question, valid without relying on optimizer infeasibility status. It would use a relaxation incorporating these three residence rules, but would not establish that those rules alone are the physical cause of the full model's infeasibility. The old hourly null was not a feasible counterexample without dwell.

A complete nonexceeding bound is an honest null and leaves the full common question UNKNOWN. It also supplies no defensible full common candidate by itself. Stop this specific arm after that one outcome; any later search or expanded state set requires a separate scientific justification and protocol. This document makes no prediction that the bound will reject.

Source inspection for this proposal read the native specification/GEN rows, existing JSON records and the temporal assembly source. The two cut coefficients were mapped to existing unit labels and the closed fractional census was counted by its recorded labels; no new bound value, conditional threshold, state graph or scientific table was evaluated.
