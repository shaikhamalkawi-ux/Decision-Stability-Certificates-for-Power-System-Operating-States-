# DSC-Grid V8 status lock

Status date: 2026-09-20 (Asia/Dubai)

Decision: **V8 supersedes V7, pending the user's independent ChatGPT project
audit.** The package itself does not mark V8 as the externally accepted active
baseline; that promotion belongs to the independent reviewer.

## Locked scientific values

All V7 locks remain unchanged, including:

- RTS January-July shared mean: 1587.737384570594 MW.
- RTS full empirical W1: 1592.540955999171 MW.
- July same-hour premium: 12.420554404677 MW.
- July fixed-pattern premium: 14.113590035625 MW.
- July exact no-network min-up/down repair: 8.020508464286115 MW.
- July network+min-up/down+native-ramp repair:
  8.020508464286115 <= A <= 11.9262964643 MW.
- March 40.01875927564912 MW: LP lower bound only.
- Shared-continuous AC witnesses: 24/24 for March and 24/24 for July;
  medians 39.208762 and 31.080193 MW.
- PyPSA-GB common internal generation: M=16785.25504628075 MW,
  W1=18651.979267728475 MW, shape=1866.7242214477264 MW (10.008183%),
  same-hour W1=19888.552386016217 MW, premium=1236.5731182877425 MW
  (6.629715%).

New V8 locks:

- Elexon dates: 2023-01-11 and 2023-07-12, 48 half-hour atoms each.
- Elexon common complete transmission-production BMUs: 260.
- Elexon M=19553.647583333335 MW; W1=20776.83725 MW;
  shape=1223.1896666666653 MW (5.8872755846%).
- Elexon same-period W1=21016.487666666668 MW;
  premium=239.6504166666673 MW (1.1534499394%).
- Elexon union sensitivity: 268 coordinates, shape unchanged to numerical
  precision.
- PyPSA-GB chronology gate: HOLD. January/July committable, positive
  min-up/down, and finite ramp counts are all zero.
- Network MIP rerun: time limit at 600.90 s, primal 11.926296464290 MW,
  dual 8.020508464288 MW; no bracket improvement.
- Clean-room claim audit: 26/26 PASS.

## Prohibited overclaims

Do not call the Elexon comparison a field experiment, causal balancing-volume
estimate, or chronology-feasibility test. Do not call the GB LP a UC model. Do
not call the July network witness optimal. Do not infer physical infeasibility
from nonlinear nonconvergence. Do not merge RTS-native and PGLib semantics.
