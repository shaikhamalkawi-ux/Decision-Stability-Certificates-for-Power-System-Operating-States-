# Independent source and model review

A separate reviewer independently checked native calendars, dimensions, fuel classification and the seasonal runner without optimization or edits. No blocking defect was found in source preparation or the model adapter.

| First week, 2020 | Native zero-based rows | Hours |
|---|---:|---:|
| January | 0–167 | 168 |
| April | 2184–2351 | 168 |
| July | 4368–4535 | 168 |
| October | 6576–6743 | 168 |

The five native Load/Hydro/PV/RTPV/WIND calendars match all timestamps and Period equals hour plus one. Availability bounds are finite, ordered arrays of shape (168,41). There are 24 buses and 38 internal branches; bus, line and generator identifiers are unique. Slack bus is 113. Full/reduced nodal susceptance ranks are 23/23.

The 24 thermal units comprise 9 NG, 8 Coal, 6 Oil and one Nuclear unit. Excluding `121_NUCLEAR_1` from the objective leaves 23 fossil units. Equal coefficients on hourly electrical dispatch measure fossil electrical MWh, not fuel input, carbon emissions or financial cost. Nuclear remains a dispatchable thermal unit with its native commitment rules and zero objective coefficient.

The reviewed adapter removes exactly the single temporary `fossil_energy_cap` row and its bounds and label. The upstream unfixed-UC builder removes all 41 `target_mean` rows. The final objective is nonzero on exactly 168 times 23 fossil dispatch coordinates; it is zero on nuclear, renewable, hydro and every state/angle variable. The unfixed thermal dispatch bounds come from the UC model, not the all-on network helper. No cap or named-unit mean is imposed.

Free initial commitment, zero initial startup/shutdown and truncated ceil residence times match the declared boundary convention. The direct checker uses observed rounded-status runs independently of rolling-window rows, checks actual on/on ramps, reconstructs native DC flows from dispatch, and separately verifies supplied-angle balance, ratings, angle bounds and slack. It has no mean-target or energy-cap argument.

The native hourly `solve_hour` implementation includes load shedding and does not enforce hydro's declared hourly lower availability in the same way as the chronology helpers. Accordingly these references must be described as the established fixed-hydro, no-shedding DC+UC interpretation of the source inputs, not literal equivalence to every constraint in `solve_hour`. Startup/shutdown ramp limits are not added; on/on hourly ramps are analytically redundant for these 24 thermal units, with minimum redundancy margin 30 MW.

This document records the source/model review. It is not a claim that a solver found a schedule, nor an independent optimality proof. Returned witness and solver-status evidence is recorded separately per month.

After model preparation, the reviewer independently checked all four archived models: 34,680 rows, 23,016 columns and 141,724 nonzeros each; 12,096 binary columns exactly covering U/Y/Z; 3,864 objective coefficients equal to one exactly on fossil dispatch; zero cap/mean rows; sequential row numbering; U bounds [0,1]; initial Y/Z fixed zero. All 50 manifest file hashes, five bound helper hashes, and the all-model freeze binding matched. Script SHA256: `6844c70fdfe298d85cb2e247ca828cd3b0a1046f3bfc70f306743f74ac0e7805`; protocol SHA256: `c8d8612432e2f04fba9625af0629b74a99942f86a0deff4633b7fbf4795aff99`.
