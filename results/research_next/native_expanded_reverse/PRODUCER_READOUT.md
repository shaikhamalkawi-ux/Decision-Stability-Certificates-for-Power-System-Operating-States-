# Fixed reverse native-expanded certificate: producer closure

**Producer complete; independent post-run replay pending.** The sole authorized frozen run exited 0 on 27 September 2026 at 12:56:46.205295 UTC. It took 22.2671693 seconds within the 120-second soft phase, excluding only the final completion-receipt write. It performed one arithmetic pass, zero optimizer/Julia/native-build calls, and introduced no new candidate, multiplier, permutation or target. The producer reports all frozen inputs unchanged; its eight run files are now immutable.

The unchanged reverse/native-penalized candidate passes the exact expanded raw-native point check: 2712 coordinates, all 4384 affine rows, all 3696 variable-constraint records and all 960 exact binary declarations. The 240 disconnected mfg coordinates alone were lifted to zero. Strict nominal membership fails by a maximum `55/35184372088832`, approximately 1.5631940186722204e-12; therefore the strict nominal upper remains null.

The fixed archived row proof was reconstructed, including every one of its 2472 residuals. No row multiplier required an inadmissible-side projection. The 480-coordinate Q/R containment correction is

`-37729042055296938575703190024456931 / 2658455991569831745807614120560689152`,

approximately -0.014192088255340178 encoded-cost units. The corrected target lower and unchanged accepted target upper are, respectively,

`82491478309267050873273522764190043708347855 / 42535295865117307932921825928971026432`

and

`688637615591450462859699662708988826686810673863 / 348449143727040986586495598010130648530944`.

They are approximately 1,939,365.3348704537 and 1,976,293.0344030275. The exact fractions, not these approximate displays, are authoritative.

## Signed optimum-difference result

Using the unchanged, independently closed native-expanded identity bounds, the producer obtains the exact interval `[L_reverse-U_identity, U_reverse-L_identity]`:

`[111201534240145780850057637442434037732943053161 / 11150372599265311570767859136324180752990208,`

` 21966086441831056243936642064517185594305761991 / 348449143727040986586495598010130648530944]`.

Its six-decimal **outward** display is **[9972.898506, 63039.576470]** in encoded UC cost units. The lower endpoint is positive. Both endpoints refer to native-expanded models with `tau = Fraction.from_float(1e-5)` and exact original binaries. The identity's scientific arithmetic was inherited from its closed independent replay, not run again.

This is a post hoc actual-code fidelity extension of one previously fixed result, pending independent verification of this new arithmetic. It is the difference of separately informed optimal encoded costs; **it is not decision regret**, a common-policy loss, a nominal-model result, physical uncertainty, fossil MWh, calibrated money or exact optimality. The UC objective includes production segments, startup and penalized curtailment. The one-bus synthetic case is not independent transmission-network validation.

The original two target orders × two service variants remain four comparisons. The rotation/native, reverse/hard-service and rotation/hard-service outcomes are unchanged and are not transferred by this arm. No target, failed result or missing strict nominal upper was omitted.

## Closure bindings

| Item | SHA256 |
|---|---|
| Source `src/researchnext_native_expanded_reverse.py` | `494517bef073fca4126b37194c61b9cafbbab347798a7cf950bd548ca18bde6f` |
| Protocol | `3c11f1c47301db1e6d3a4bdd11476010734fc688cb645536f7489b63dd187a6a` |
| Prepared freeze: 499 bindings + 34 copies | `6863fc3027f570a87161c059f08789d967f891f3c87f5dc96add17fc97966eaa` |
| Prepared manifest | `f9b3c147cc517e5e028200c519b32238f4ec144c65b56ca7773a467e6c1635fa` |
| Actual-target nominal comparison independent acceptance | `bb44ef305c468a9e334a0a8e5ee63fc84ac8e87aec057c8e05e21ad07a2f8cc6` |
| `run01/result.json` | `c0e81da4ca275b185820e8616cc3d81c995f666d977ee1e62199a846ed8ce23f` |
| `run01/signed_difference.json` | `ac80cf61d3912985fb480e0bf847053cfffe4891270d52d0d0db54d12eae9663` |
| `run01/native_lower_certificate.json` | `70d380a6ed2042a459367842166b4561f4dbd0c39904ab7d9cb3b358fedf7944` |
| `run01/native_point_check.json` | `50c7ecf402e160bd49fb4a22d93b83d6462fe1f0f234feea71eb3375758a1a3b` |
| `run01/completion.json` | `714f4a3fa85ef0b33f068e221595be51b63bdebca0f301d86aedeace66540294` |

The parent full source read, second source/protocol read (`3061362ae6a226ff57a0dc7f9e2bd0636983a1d1e43a1ad205e6d225247546a6`) and independent prepared gate preceded the run. None replaces the pending independently implemented raw-point, lower-certificate and signed-difference replay. `producer_output_inventory.csv` binds all eight run files plus this readout, using repository-relative paths and excluding itself. Later independent review/closure records must be appended separately, preserving this producer-stage status and every frozen artifact.
