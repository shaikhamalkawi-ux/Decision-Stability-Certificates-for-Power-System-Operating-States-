# Forty-eight hours of retained dwell rows suffice in the first fixed twin

For existing seed 26092600, the continuous relaxation remains infeasible when minimum-up/down rows are retained only if their complete direct variable support lies within zero-based hours **60–107**. This is a 48-hour interior window. All static hourly constraints, 41 full-week individual mean equalities, and transition/exclusivity linkage remain global. The positive unpermuted repaired network witness satisfies every corresponding identity relaxation.

This phase was specified before its solves and completed all nine fixed cases in 22.875 seconds, with 30 seconds allowed per LP. There were no timeouts, extensions, adaptive window choices or repeated optimizations. Source functions were bound to baseline `7300129`; the reconstructed full twin matrix and every bound exactly matched the earlier archived arrays. Input/source hashes still matched after completion.

| Retained window (inclusive) | Width | Retained dwell rows | Total rows | Checked outcome |
|---|---:|---:|---:|---|
| Empty | 0 | 0 | 16,289 | Continuous feasible; UC unknown |
| 80–87 | 8 | 212 | 16,501 | Continuous feasible; UC unknown |
| 76–91 | 16 | 564 | 16,853 | Continuous feasible; UC unknown |
| 72–95 | 24 | 918 | 17,207 | Continuous feasible; UC unknown |
| 60–107 | 48 | 2,024 | 18,313 | Exact robust rejection |
| 48–119 | 72 | 3,176 | 19,465 | Exact robust rejection |
| 36–131 | 96 | 4,328 | 20,617 | Exact robust rejection |
| 24–143 | 120 | 5,480 | 21,769 | Exact robust rejection |
| 0–167 | 168 | 8,016 | 24,305 | Exact robust rejection |

Every case keeps all 18,984 continuous P/U/Y/Z coordinates and their original bounds. The restriction removes whole rolling dwell inequalities; it never shortens or restarts them at a window boundary. Because it only deletes constraints and removes integrality/network restrictions, its infeasibility implies infeasibility of the original UC model with matching remaining assumptions. Feasibility of one of these relaxations establishes no UC admission.

## Which constraints enter the 48-hour proof

The model retains 2,024 of the original 8,016 dwell inequalities. Its exact certificate has 558 nonzero row multipliers: 52 minimum-up rows, 20 minimum-down rows, 146 transition identities, 81 aggregate balances, 127 thermal lower-output rows, 101 thermal upper-output rows, and 31 weekly means. The row list, original row IDs, multipliers and complete matrices are saved in `width_048/`. Individual column bounds also enter the box maximum below; they are retained globally. No claim that all listed model rows are individually necessary or that this support is minimal is made.

The 72 dwell rows with nonzero multipliers involve 11 units: `101_STEAM_3`, `101_STEAM_4`, `107_CC_1`, `113_CT_1`, `113_CT_2`, `113_CT_3`, `113_CT_4`, `116_STEAM_1`, `118_CC_1`, `123_CT_4`, and `123_CT_5`. Their direct U/Y/Z support lies entirely in hours 60–107. `certificate_dwell_rows.csv` gives each exact row; `dwell_support_by_unit.csv` gives family/count/hour summaries. This is a multi-unit energy-and-residence contradiction, not an independently isolated single-unit cause.

For a retained minimum-up row with duration L, the inequality is `sum(s=max(1,t-L+1)..t) Y[s] <= U[t]`. Minimum-down uses `sum Z[s] <= 1-U[t]`. Only rows for which every involved hour belongs to the chosen window survive. Global transitions still impose `U[t]-U[t-1]=Y[t]-Z[t]`, including outside the window, and the fixed means still require `sum(t) P[t,j]/168=mu[j]` over the complete week.

## Exact separation, with a readable inequality

Let `l <= A x <= u` be the archived retained rows and `L <= x <= U` the complete variable box. For the archived row multipliers y, define

`b = sum(y_i*l_i for y_i>0) + sum(y_i*u_i for y_i<0)`,

`c = transpose(A)*y`, and

`M = sum(c_j*U_j for c_j>0) + sum(c_j*L_j for c_j<0)`.

Every feasible x must satisfy `b <= c^T x <= M`. Exact rational arithmetic applied to the saved binary64 numbers instead gives `b-M > 0`:

- `b ≈ 95,672.7129161655`.
- `M ≈ 95,109.3026044279`.
- Exact gap, displayed decimally: `563.4103117376047`.
- Exact gap numerator: `51464068318351486523164779363804772137984259536803`.
- Exact gap denominator: `91343852333181432387730302044767688728495783936`.

Relaxing every finite row and column bound outward by `1e-5` in its own units still leaves a positive exact gap, displayed as `563.0519941946116`. The maximum uniform bound-relaxation threshold for this multiplier scaling is approximately `0.01572377135183304`; this mixes MW and dimensionless constraint units and is not a physical uncertainty tolerance. One sign-inadmissible raw multiplier of magnitude `6.54e-16` was explicitly removed in the selected projected candidate, after which the whole separation was recalculated exactly; it was not assumed to be mathematically zero. The raw ray and all candidate checks are retained.

The five rejecting models' chosen certificates and four admitted continuous vectors were replayed from disk without optimization; all nine pass. Positive controls include the complete original identity model and every identity row subset. The permuted empty-window control uses permuted P/U and newly derived Y/Z, and also passes. The largest positive-control residual is `6.821210263296962e-12`.

## Scope and next questions

Forty-eight hours is the shortest **examined centered window**, not a minimum over intervals, not a minimum information requirement, and not an intrinsic memory threshold. The 24-hour relaxation being feasible does not prove that a 25-hour or differently located window cannot reject. The certificate still uses rows outside the window and whole-week means. A startup at its left edge is globally coupled to the preceding status outside the window. Thus the result localizes directly retained dwell inequalities while leaving global information in place; it does not establish a 48-hour raw-data certificate or an isolated-window model. This is one existing development twin, not a new held-out study or evidence of generalization across networks.

Replay command from the repository root: `python src/research8h_locality.py --verify-archived`. It does not optimize. Native reconstruction additionally requires the portable source directory and `--source-v3`; existing run outputs are refused. `input_manifest.csv`, `pre_run_freeze.json`, `positive_controls.json`, `completion.json` and `archive_replay.json` preserve bindings and audit evidence.
