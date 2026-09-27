# One local day321 repair proposal

27 September 2026. Read-only proposal based on the already archived constructive schedule. No candidate construction, feasibility replay, network solve or optimization has been performed in preparing this note. The historical UNKNOWN and failed constructive point remain unchanged.

## Fixed candidate

Starting from days_321/constructive_vector.npz, use zero-based hours70 and71:

| Coordinate | Proposed change |
|---|---|
| 101_STEAM_3 commitment U | Set both hours to1 |
| 101_STEAM_3 output P | Add30MW at each hour |
| 101_STEAM_3 shutdown Z at70 | Change1 to0 |
| 101_STEAM_3 startup Y at72 | Change1 to0 |
| 122_WIND_1 output P | Subtract30MW at each hour70/71 |
| DC angles | Change only hours70/71, with the original slack fixed, to accommodate the changed bus injections |

Every other dispatch and state coordinate remains unchanged. This is exactly one candidate, not a search over generators, offsets or repair windows.

The saved steam3 schedule is ON62–69, OFF70–71, ON72–74, OFF75–83, then ON from84. The proposed bridge produces one ON interval62–74 of13hours and retains the9-hour OFF interval75–83. Its native minimum-up/down requirements are8/4hours. The two reported residence events at70 and72 disappear in this schedule logic; every other transition is intended to remain as archived. This is not yet a full residence-matrix check.

Both steam units at bus101 have native30–76MW ranges. The saved output of steam3 at70 is3.197442310920451e-14MW and at71 is0; the proposal adds30 rather than discarding the tiny archived value. Its neighbors at69/72 are approximately30MW. The existing native on/on ramp rate is120MW/hour. At70/71 steam4, the two bus101CTs and bus101solar output are also zero apart from numerical residue. A mere steam3/steam4 label exchange cannot supply the new30MW in these two all-off gaps. This observation does not prove every imaginable same-bus repair impossible.

The explicit compensator is122_WIND_1 at bus122. Its saved outputs are472.68762990000124MW and528.0939634MW at70/71. Curtailing30MW leaves clearly positive output and does not require changing a hydro must-dispatch level or another commitment. The actual archived availability/lower bounds must nevertheless be checked, rather than inferred solely from the nameplate roster.

The proposed fossil-energy increment is60MWh in real arithmetic: original22964.941239556443 becomes approximately23024.941239556443MWh, below the nominal23195 cap by about170.06MWh. Only exact readback of the final saved candidate may establish the actual increment and cap admission; binary64 arithmetic must not be called exact by assertion. Fossil electricity is not a monetary cost or CO2 measure.

## Remaining risk and one possible implementation

The unverified issue is network feasibility after transferring30MW from bus122 to bus101. It cannot be resolved from generation headroom. The original archive reports binding branches somewhere in the horizon, so do not assume the changed hours have30MW transmission slack.

An implementation may solve the original reduced nodal-angle linear system at each changed hour, fixing the archived slack coordinate, with RHS equal to the negative nodal injection change. Use the saved matrix coefficients, not a rebuilt network or a different DC encoding. A fixed exact rational Gaussian solve followed by one binary64 angle rounding is an appropriate zero-optimizer route. Because the separately rounded aggregate/nodal rows need not be algebraically identical over rationals, retain the original aggregate and all24nodal rows in the final check; solving23rows does not by itself prove full admission. Angle/branch bounds and the unchanged slack also require checking.

The final acceptance gate must check the complete original days321 matrix/boxes under the existing tau=Fraction.from_float(1e-5), all12096 exact binary coordinates, every native residence/transition/output/on-on-ramp rule, network/angle limits and the same23-fossil cap. Prove the intended locality by comparing all untouched coordinates with the old vector. Strict tau=0 status is separate; the old point was only expanded-feasible on its retained static rows. A rejected candidate is a failed local repair, not individual-world infeasibility. No alternate donor, power sweep, added LP, relaxed row or second candidate is part of this proposal.

A successful independently checked point would provide the missing individual-positive control for day321 at the original cap. It would not be a common commitment with identity, would not resolve minimax regret, and would not erase any historical timeout/UNKNOWN label. It is a standard local schedule repair, not an algorithmic novelty claim.

## Read-only provenance

- Old constructive check SHA256:88ec521245dbb95d3c1cdc88139c125451f00bbb8c4a1906f4e8d6ff7a3cea5c.
- Old constructive vector SHA256:71cea67428a6ad45ab753b4839be3f2f4d6c1eb4b5a6965c32a5460e15a8c40f.
- Commitment CSV SHA256:e6c117dd77c57de8163b15df57737cad848e013fcae655b1bcbcbf06703e3715.
- Dispatch CSV SHA256:97067e5af9aa1cc51ac95483961d2b7eb4be2cd8597d03faf5763b6fd5a99594.
- Historical producer src/research8h_day_blocks.py SHA256:43441ca2da48c6d8acc2574461502f6f74a4f0f4a3b32ad653c5fd794a5f6a8b.

Read pinned generator/specification and historical source definitions. Implementation/preparation/execution require their separate reviewed protocol; this contemporaneous proposal records the choice before any candidate outcome.
