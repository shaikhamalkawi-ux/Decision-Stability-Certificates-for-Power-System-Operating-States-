# Feasibility of transporting the saved phase-I network template

This is a prospective source/structure assessment, not an executed cut batch. Only saved certificate entries, row metadata, coordinate maps, assembly source and native roster/topology records were inspected. No transported coefficient sum, margin, scientific dot product, backend model or optimizer was evaluated. The existing phase-I certificate and its closed independent review remain unchanged.

## Fixed template and mapping

The saved certificate uses the exact common positive weight

`c = 6004799503160661 / 144115188075855872`.

It must be retained as this rational number, not replaced by `1/24`. Its 24 original-row multipliers are:

| Exact metadata key, with destination hour `t` | Multiplier | Selected finite endpoint |
|---|---:|---|
| `aggregate_balance, t, ALL` | `+c` | lower |
| `thermal_upper, t, uid`, for the 21 names below | `-c` each | upper |
| `nodal_balance, t, 107` | `-c` | upper (equality) |
| `branch_flow, t, 10` | `-c` | upper |

The thermal names are `101_CT_1`, `101_CT_2`, `101_STEAM_3`, `101_STEAM_4`, `102_CT_1`, `102_CT_2`, `102_STEAM_3`, `102_STEAM_4`, `113_CT_1`, `113_CT_2`, `113_CT_3`, `113_CT_4`, `115_STEAM_1`, `115_STEAM_3`, `116_STEAM_1`, `118_CC_1`, `123_STEAM_2`, `123_STEAM_3`, `123_CT_1`, `123_CT_4`, `123_CT_5`. The three omitted thermal units are `107_CC_1`, `115_STEAM_2` and `121_NUCLEAR_1`.

Use each world's `row_metadata.csv.gz` under `results/research_next/common_master_bounded/prepared/{identity,days_321}` to resolve `(family, hour_0based, uid)` to its original row. Then invert the unchanged joint `row_origins.json` entry `(world_index, original_row)` to obtain its joint row. Use `column_maps.json` for original-to-joint coordinates; all U/Y/Z coordinates are shared and P/theta coordinates are world-specific. Do not infer row numbers from a stride, use source-hour permutation assumptions, or copy training-hour endpoints.

A read-only metadata enumeration found all 4,032 required keys uniquely in each world, with unique joint origins: all 336 proposed templates are structurally addressable. This does not yet establish their coefficient patterns or calculate their cuts.

## Source-grounded mechanism

`temporal_lp_certificate.assemble` defines aggregate generation balance and `P - Pmax*U <= 0` thermal upper rows. `research8h_service_network.assemble` defines nodal generation minus `Bbus*theta` equal to native net nodal load, and branch flow as `b*(theta_from-theta_to)` with symmetric continuous-rating limits. `research8h_service_network_mip.build` preserves these rows while shifting columns and recording the final metadata. The common-commitment assembly identifies only state coordinates across worlds.

The pinned native `dscgrid_model.py` filters buses to Area1, retains branches whose two buses are in that area, and resets branch indices in original CSV order. Consequently metadata branch UID `10` means zero-based filtered index10, not upstream UID10. Reading the native records identifies it as upstream branch **A11, bus107→bus108, continuous rating175MW**, the only retained branch incident to107. The only generator at107 is `107_CC_1` (native maximum355MW).

Thus subtracting nodal107 and the outward branch upper row limits how much generation at107 can serve the remainder of the area. Subtracting the 21 thermal upper rows substitutes their committed capacities. The already-saved training coefficient vector has 21 U terms and 19 remaining P terms: the 17 nonthermal generators, `115_STEAM_2` and nuclear. Their variable upper boxes supply the remaining capacity allowance. Its saved theta residual is exactly zero. No dwell, ramp or weekly fossil-cap row is in this certificate's support, so the discovered mechanism is a static hourly network-deliverability necessity, not a temporal or budget certificate.

## Required exact acceptance for a future finite batch

Freeze both worlds and all168 hours, these same 24 keys/signs and `c`, without selecting hours by outcome. For every mapped template, use its actual original matrix, finite selected endpoints and all original continuous boxes to reconstruct the complete rational `d`, `q=A^T d` and `beta`. With exact `tau=Fraction.from_float(1e-5)`, the necessary inequality is

`q_B*z >= beta - support_C(q_C) - tau*(||d||_1 + ||q_C||_1)`.

Here `support_C` is the maximum over the original unexpanded continuous boxes; state variables remain explicit, so there is no extra binary-tau term and no second tolerance on the derived cut. Retain every continuous coefficient, including any angle residual. The training cancellation and physical topology do not authorize discarding rounded coefficients or assuming cancellation in other archived rows. Validate endpoint signs, ordered intervals, finite support boxes, coordinate identities and the actual generator roster for each case. The general row-combination argument remains valid even if an unexpected residual occurs; any implementation that requires the narrower 21-U pattern must fail explicitly on a pattern mismatch.

This is logically useful as one finite batch of necessary cuts before further candidate search: it applies an already identified export bottleneck to all hours directly, avoiding a separate phase-I solve merely to rediscover the same row family. It cannot establish feasibility, exact optimal cost, completeness of the master, or nonexistence of every common commitment. It is trained after observing one nominee and one returned certificate on the same system. It is a classical network-capacity/Farkas implication, with no novelty or minimum-information claim. No such batch has yet been authorized or executed.

## Inspected bindings

| Artifact | SHA256 |
|---|---|
| Saved `common_phase1/run01/exact_candidate.json.gz` | `427dba0e4a75fd7bce5dff278c958fb73dafa2fbf41cf0a1cdc3c08f391a178b` |
| Independent phase-I post-run JSON | `8d16937fb7493b314d439dad48123c6c12dd94c69062b346d9bf8da56858e526` |
| Identity row metadata | `e749fc61f6807729b78154a3cce4a3f9cfa345fd9da946745e74e101b295107a` |
| Days321 row metadata | `eb73c440b322d0218299b5811de3db39e8335eac7dd014247ab4224be92f1efe` |
| Joint column maps | `ced46514e0a6525a21f24aab86dea4b6e3ce0f27440f6dee53a47093dbc0f4bb` |
| Joint row origins | `b2845b979bac228548d6b3557da24d3c6bfea500c4284299a97fe1a20dd253fe` |
| Portable native `dscgrid_model.py` | `01d3e67440b1380b62ed68da07e61ac6895b930ada583ffa8af09a370850be78` |
| Portable native `branch.csv` | `e92d16d13b1c5d2899f7871c0c99c3eb94605528beef157bf9e1ccbcffe5ef4e` |

The native files are under `reproducibility/native_sources/rts_inputs`; this assessment did not import or execute the assembly sources.
