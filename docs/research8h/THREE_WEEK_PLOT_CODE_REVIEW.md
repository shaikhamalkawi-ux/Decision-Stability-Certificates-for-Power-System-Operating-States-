# Three-week energy figure: independent source review

Status: PASS after the two pre-execution gate corrections. Review date: 27 September 2026. This review neither executed the plot nor edited its source. Rendering and visual inspection belong to the parent task.

Reviewed source: `src/research8h_plot_three_week_bounds.py`, SHA256 `9b84a759c5cb6cf8a84d540d2484f5af4fc4c95b4d916f956fe4c3a664f72b01`.

## Input gates

The original version used a POSIX lookup against Windows-path keys in the fresh independent review and bound only the fresh numerical input to its review. Both findings were communicated before execution. The reviewed revision normalizes slash direction for the fresh and first-week hour-of-day reviews and binds the unrestricted input to its existing `PASS_COMPLETE` review.

A separate read-only script, without importing the plot module, verified all three actual review statuses and exact numerical-input hashes:

- `energy_lp_refinement/refined_brackets.json`: `bd1e8e061a26f82bdb8e0697e03ea4b3f97664b6ee19c21d4886950e85fd1cfd`.
- `hour_of_day_uncapped/energy_brackets.json`: `4915dfe14d94419cbb6c62a52b2079dc10648a349b93a224630ab1b41e11a1f1`.
- `fresh_january_energy/energy_brackets.json`: `ed4e0e6eb4f88b8a660c7b46495a95d30eebce94f715be83cedf4a884930471c`.

The fresh review also requires denominator four and unchanged hashes. The plot records and rechecks its six input/review hashes. The output directory must not already exist.

## Arithmetic and interpretation

For each target the code uses its own week's identity bounds. It recomputes the exact interval `[L_T-U_I, U_T-L_I]` and checks equality with the stored difference. For positive identity and target lower bounds, the percentage interval is exactly `[100(L_T/U_I-1), 100(U_T/L_I-1)]`. These are optimum-to-optimum bounds, not differences from only a selected incumbent.

Independent `Fraction` arithmetic reproduced all eight intervals and percentage intervals. The six-decimal metadata and one-decimal figure annotations round the lower endpoint down and the upper endpoint up. The floor/ceiling expressions also handle negative endpoints correctly. Binary64 conversion occurs only for graphical coordinates.

The prescribed order contains all eight cases: 26093100, 26093101, 26093200, 26093201, 26093210, 26093211, 26093220 and 26093221. In particular, the historically capped UNKNOWN case 26093211 remains present. No case is selected by sign or width. A missing upper witness would remain visible and would not be called a finite optimum enclosure. The axis includes zero and would retain a negative lower endpoint.

The footer correctly separates two unrestricted permutations from six hour-preserving permutations and limits the scope to the same RTS Area 1 and three January weeks. It explicitly distinguishes exact-bound enclosures from confidence intervals and preserves the numerical finite-bound expansion. No statistical, seasonal, external-network or solver-performance inference is made.

No remaining mathematical, data-mapping or execution-gate blocker was found. Figure layout and final manuscript placement require the parent's rendered inspection.
