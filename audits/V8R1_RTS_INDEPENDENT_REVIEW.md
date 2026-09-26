# Independent RTS seasonal review and exploratory residence certificate

Date: 2026-09-26. Reviewed `src/v8r1_rts_seasonal.py` and the fixed eight-week protocol. The necessary-condition analysis below was conceived **after inspecting the seasonal solver results**. It is an exploratory explanation and independent computational check, not part of the initial fixed seasonal protocol. No month was added or removed.

## Conclusion and strongest correction

The eight archived schedules independently pass the stated hourly on/on ramp constraints. More strongly, those constraints are analytically redundant under the selected RTS parameters: for **all 24 thermal units**, the source ramp rate multiplied by 60 exceeds the entire online dispatch range. Thus this is a nonbinding control under the chosen one-hour, on/on-only semantics, not empirical evidence that physically realistic ramping generally preserves feasibility.

The minimum-residence formulation is consistent with its explicitly weak boundaries. HiGHS reports all eight complete-mean targets infeasible. An independent solver-free necessary-condition check explains **seven** of those rejections; **June remains without this independent certificate**. Passing the necessary condition in June establishes neither feasibility nor an error in the solver result.

## Inputs, target and horizon

The driver checks all eight predefined first weeks: January, February, March, April, May, June, July and October. January and July are internal controls. Each target is the complete 41-coordinate arithmetic mean of 168 hourly archived dispatch vectors, not a scalar total-generation mean. Source dispatch and published dispatch are compared by named generator columns, and source row/time mapping is checked against native load timestamps. The source model's `Ramp Rate MW/Min` is converted to MW/hour by multiplication by 60, and minimum times in `Min Up Time Hr` / `Min Down Time Hr` become ceiling integer counts for hourly snapshots.

The independent certificate script reloads the original V3 model, generator table, native time-series tables and target CSVs without importing the new seasonal driver. Source SHA-256 hashes and per-target hashes are recorded. It does not use any optimization solver; importing the original model does not call its solve functions. It independently confirms balance, availability, conditional dispatch bounds, fixed hydro, source row/time mapping and the archived on/on ramp witness for every week. The witness is the original target schedule, hence preserves all target coordinates by construction.

This does not verify the raw benchmark against the external RTS publisher a second time. Both implementations still rely on the admitted V3 source package and its hydro-as-fixed-output and rooftop-PV-as-negative-load conventions. The result is conditional on those conventions, aggregate area balance, no shedding, and a free initial status. It is not an AC feasibility result or an independent-system replication.

## Ramp proof

For binary status `u[t]`, online dispatch satisfies `Pmin <= p[t] <= Pmax`. Therefore two consecutive online snapshots necessarily obey

`|p[t]-p[t-1]| <= Pmax-Pmin`.

Writing the hourly source ramp as `R=60*r`, the ramp constraint is redundant whenever `R >= Pmax-Pmin`. This holds for every one of the 24 thermal units. The smallest margin is **30 MW**, for `123_STEAM_3`: `R=240 MW`, online range `350-140=210 MW`. The complete table is `results/v8r1/rts_certificate/native_hourly_ramp_redundancy.csv`.

The seasonal driver's big-M form is algebraically sound:

`|p[t]-p[t-1]| <= R + M*(2-u[t]-u[t-1])`, with `M=max(Pmax[t],Pmax[t-1])`.

When both statuses are one this is the normal rate bound. For a switching pair, nonnegative dispatch and the commitment upper bound give an absolute change no greater than `M`, so the relaxed inequality is redundant for nonnegative `R`. When both statuses are zero dispatch is zero. The proof applies to the explicitly chosen switching-unrestricted ramp family, not startup trajectories, finer time resolutions or additional ramp constraints.

The original optimization log is correctly retained: May's 60-second ramp solve was unresolved. Its later admission comes from an independently checked existing witness, not relabelling the time limit as a solver success. All eight direct archived witnesses have exactly zero positive on/on ramp excess in the check.

## Minimum-residence formulation and independent verifier

The transition equality `u[t]-u[t-1]=y[t]-z[t]`, binary variables, and `y[t]+z[t]<=1` identify observed startup/shutdown transitions. Summing startups over the preceding `U` snapshots and requiring that sum to be at most `u[t]` enforces each observed startup's remaining minimum-on period; the analogous shutdown window enforces minimum-off time. At time zero `u[0]` is free and `y[0]=z[0]=0`. No pre-window dwell is imposed. Constraints cease at hour 167, so terminal residence is truncated. The independent finite-state analysis uses exactly those weak boundaries.

Initial review identified two witness-checker limitations and reported them to the root task:

1. Checking distance to the nearest integer alone does not check binary domains. Explicit finite-value and `[0,1]` bounds were subsequently added by the root task.
2. Dispatch coupling evaluated against raw near-integer status can differ from coupling against the rounded status used for chronology. An example is `u=1e-6`, `Pmax=100 MW`, `p=1e-4 MW`: raw coupling passes, but rounded-off dispatch exceeds `1e-5 MW`. The root task subsequently added `commit_upper_rounded_MW` and `commit_lower_rounded_MW`; their presence was independently confirmed in the final source. The archived witnesses used here have exactly binary statuses derived independently, so this issue does not affect their admission.

The absolute mean tolerance `1e-5 MW` corresponds to `0.00168 MWh` per coordinate over 168 one-hour observations. Infeasible results are solver status assertions, not feasible-witness checks. The independent certificate below adds a separately implemented explanation for seven cases.

## Solver-free necessary-condition certificate

Let `E[g]=168*mu[g]` be the fixed per-unit target energy and `d[t]` be net demand. Start with interval bounds `[L[t,g],U[t,g]]`: nonnegative dispatch, native available maximum, and fixed hydro output. Any feasible dispatch obeys the following necessary implications:

`L[t,g] >= d[t] - sum(i != g) U[t,i]`

`U[t,g] <= d[t] - sum(i != g) L[t,i]`

`L[t,g] >= E[g] - sum(s != t) U[s,g]`

`U[t,g] <= E[g] - sum(s != t) L[s,g]`.

Each update intersects the existing interval with these bounds. The implementation enlarges balance and energy equalities outward by `1e-5 MW` and `0.00168 MWh`, respectively. If a thermal upper bound falls below `Pmin`, its status must be off; a strictly positive lower bound forces it on. Conservative numerical margins of `1e-5 MW` are used in these implications. Iteration stops only after comparing against the start-of-iteration bounds; the earlier weaker stopping check was corrected and rerun, with all conclusions unchanged. Its preliminary summary is preserved separately.

For a constant-bound thermal unit with integer online-hour count `N[g]`, the exact model requires

`Pmin[g]*N[g] <= E[g] <= Pmax[g]*N[g]`,

so

`ceil(E[g]/Pmax[g]) <= N[g] <= floor(E[g]/Pmin[g])`.

The implementation relaxes the numerators outward by the energy tolerance and the capacity denominators outward by the power tolerance. This only broadens the admissible count interval relative to the exact original model. Thus disjointness remains a sufficient rejection condition for that exact model. The method is a floating-point computational certificate with recorded margins, not a formal rational-arithmetic proof assistant artifact.

An exact finite-state recurrence enumerates reachable counts under minimum residence and the forced-status hours. A state at time `t` is `(s,r,n)`: current binary status, remaining compulsory same-status snapshots after `t`, and accumulated online count. Initially either status is allowed, with `r=0` because prior dwell is free. A stay step maps to `(s,max(r-1,0),n+s)`. A switch is allowed only when `r=0`, mapping to `(1-s,max(T[1-s]-1,0),n+1-s)`. Forced-on/off constraints filter the choices. All terminal residuals are accepted, reproducing the truncated endpoint. Integer count sets are stored as bitsets, with no numeric optimization.

Let `Nset[g]` be the terminal reachable counts. If it has no intersection with the energy-compatible integer interval, a necessary condition for the full coupled schedule fails. Since the interval bounds are necessary and the finite-state search relaxes other units' remaining couplings, failure excludes every schedule in the original tested min-up/down relaxation. Success proves no full-system admission.

The recurrence was checked against exhaustive enumeration of binary sequences in **1,125 short-horizon cases**, covering horizons 1–9, minimum times 0–4, random forced states and the same free boundaries. All matched. The archived static schedules were also checked to remain inside the propagated intervals; the interval procedure did not accidentally remove their static feasibility.

## Concrete obstructions

For `123_STEAM_3`, `Pmin=140 MW`, `Pmax=350 MW`, minimum up time is 24 hours and minimum down time is 48 hours.

| Week | Target energy, MWh | Maximum online hours permitted by energy | Minimum reachable online hours | Minimum energy excess, MWh |
|---|---:|---:|---:|---:|
| January | 3,228.521078 | 23 | 100 | 10,771.478922 |
| February | 6,590.548836 | 47 | 101 | 7,549.451164 |
| March | 2,898.640426 | 20 | 50 | 4,101.359574 |
| April | 3,244.765758 | 23 | 50 | 3,755.234242 |
| May | 12,204.019298 | 87 | 123 | 5,015.980702 |

January has a particularly transparent chain. Necessary hourly bounds force this unit on at hours `16,18,64,65,66,67,77,78,89,113,114,115` (zero-based). Consecutive forced-on hours are separated by too little time to accommodate a 48-hour off interval, so it must remain on throughout hours 16–115: at least 100 hours and 14,000 MWh. Its fixed target energy is only 3,228.521078 MWh. This is a residence/coordinate-energy obstruction, not a claim that the original static dispatch pattern itself must be preserved.

**July has a short local contradiction independent of the online-count energy bound once necessary statuses are established.** For `115_STEAM_3`, propagated intervals force it on at hour 2 (`L=61.99999 MW`), off at hour 3 (`U=0.00001 MW`), and on at hour 7 (`L=61.99999 MW`). Its minimum downtime is eight hours. Shutdown at hour 3 forbids restart at hour 7; only four off snapshots can occur. No binary residence sequence satisfies these forced statuses. `123_STEAM_3` independently has an incompatible forced-state pattern that week.

**October** also has several obstructions. `107_CC_1` is forced off at hour 15, on at hour 16, and off at hour 18, contradicting its eight-hour minimum up time. `101_STEAM_4` would need at least 48 online hours while its fixed energy permits at most 39, leaving at least 243.344830 MWh of excess minimum output. Two other steam units also have incompatible forced-state patterns.

**June:** every individual necessary count intersection remains nonempty. In particular, `123_STEAM_3` has an energy-compatible count range 84–168 and reachable counts 29–168; nuclear has energy-compatible counts 163–164 within its reachable set. Coupled feasibility is not established by these intersections. Retain the full-model HiGHS infeasibility result, and state that this reduced explanation does not certify June. Do not imply an eighth independent certificate.

The numerical tables, forced-hour lists, interval matrices, code/input hashes and exhaustive-check result are under `results/v8r1/rts_certificate/`. `failure_margins.csv` gives all 11 failing-unit records across seven weeks.

## Claim boundary for integration

The defensible extension is: **all eight fixed target weeks are rejected by the tested native minimum-up/down no-network relaxation; seven admit an independent reduced residence explanation. The archived schedules meet the on/on-only hourly ramp family, whose rate constraints are analytically redundant at this resolution.**

This strengthens within-system coverage and interpretability. It does not show chronology failure in another system, network/AC admission of the ramp schedules, feasibility with a realistic startup trajectory, all-year representativeness, or a necessary-and-sufficient per-unit characterization. A rejected relaxation excludes stricter models only when they retain the same target, dispatch variables and source conventions; a differently defined physical model is not covered automatically.
