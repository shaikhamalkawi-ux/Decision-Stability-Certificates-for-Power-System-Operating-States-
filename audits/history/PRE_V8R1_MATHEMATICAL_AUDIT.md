# DSC-Grid V6 — Mathematical and Symbol Audit

## Overall decision

The mathematical layer is internally coherent and aligned with the manuscript's claim boundaries. No equation-level issue was found that requires changing a V6 numerical result. The key methodological safeguard is that three mathematically different objects remain separate: static/support-constrained transport, chronological target-mean admission, and nonlinear AC restoration.

| Equation / object | Mathematical status | Reader-accessibility status | Audit finding |
|---|---|---|---|
| Empirical source law, Eq. (1) | Correct | Immediately interpretable | Weights are positive and normalized; source atoms are hourly dispatch states. |
| Support-explicit transport certificate, Eq. (2) | Correct | Understandable with minor technical background | Source marginal, conditional supports, and transported-mean region are explicit. It is not described as physical reachability. |
| Empirical barycentric specialization, Eq. (3) | Correct | Understandable with surrounding explanation | Jensen/conditional-barycentre reduction is properly framed as a specialization, not a priority claim. Polyhedral/L1 specialization yields an LP. |
| Mean lower bound, Eq. (4) | Correct | Immediately interpretable | Units are MW because the full-coordinate L1 dispatch differences are in MW. |
| Full-law / shape / support gaps, Eqs. (5)-(7) | Correct | Immediately interpretable | The manuscript explicitly distinguishes shape movement from support-induced movement. A support premium is not used when exact target admission fails. |
| Scale/reallocation identity, Eq. (8) | Correct | Understandable with minor clarification already supplied | Correctly prevents the complete L1 change from being called redispatch when total system scale changes. |
| Pullback cost after balance-coordinate elimination | Correct | Understandable with surrounding text | The exact physical-coordinate cost is preserved; replacing it by an arbitrary reduced-space L1 norm would change the estimand. |
| Chronological mean-admission repair, Eq. (9) | Correct | Immediately interpretable | Used only after exact mean rejection. July's value is exact for the declared no-network min-up/down relaxation; March is only an LP lower bound. |
| AC restoration projection, Eq. (10) | Correct but nonconvex/local | Understandable with explicit claim boundary | Successful solves are valid AC witnesses. The returned objective is not claimed globally minimal, and solver nonreturn is not physical infeasibility. |
| Unit on/off and transition equations in chronology section | Correct | Understandable with source definitions | Binary commitment, source Pmin/Pmax, and transition identity are standard and dimensionally consistent. |
| Supplementary minimum-up inequalities | Correct | Understandable with minor technical background | The independent y/z implementation uses weak/free boundary treatment; this is a relaxation, strengthening the logic of rejection. |
| Supplementary minimum-down inequalities | Correct | Understandable with minor technical background | Same boundary logic; no pre-horizon state is fabricated. |
| Supplementary L1 repair linearization | Correct | Immediately interpretable | Absolute mean deviations are linearized with nonnegative positive/negative parts. |
| AC nodal equations / branch apparent-power constraints | Correct for declared steady-state model | Technically dense but adequately explained | P/Q balance, Q limits, voltage limits, transformer taps/shunts, and terminal MVA limits are included. N-1/dynamic security is explicitly excluded. |

## Dimensional and numerical checks

- Static, conditional, chronology-repair, and AC-restoration quantities are reported in MW, but the manuscript explicitly states that they do **not** share one objective and are not additive.
- Voltage limits are dimensionless p.u.; declared range is 0.95-1.05 p.u.
- Branch loading is dimensionless after terminal apparent power is divided by the continuous MVA rating.
- Source ramp fields are MW/min and the harmonized native test converts them to hourly limits with `×60 min/hour`.
- July no-network min-up/down repair table sums to 8.02050846428686 MW, matching the solver value 8.020508464286115 MW to numerical precision.
- Direct native-ramp witness audit finds zero exceedances in 2189 March and 3252 July online-to-online transitions.

## Critical interpretation boundaries retained

1. Infeasibility in the no-network min-up/down relaxation transfers to stricter network-constrained chronology for the **exact target mean**, but the relaxation's repair magnitude is not automatically the exact network-constrained repair.
2. The 8.020508-MW July repair is exact only for the declared relaxation; the 40.018759-MW March value is an LP lower bound only.
3. Shared-continuous AC success establishes local AC-feasible restored witnesses under the declared Area-1 model, not global AC-distance optimality, N-1 security, continuous-path reachability, or real operator redispatch.
4. Fixed-commitment AC witness counts are solver-budget sensitive and are therefore not used as a physical success rate.
