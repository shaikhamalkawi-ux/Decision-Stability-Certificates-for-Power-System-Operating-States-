# Independent native-expanded identity result

**PASS.** One independent standard-library replay completed in 1.5347554 seconds. It imported neither the producer nor either of its mathematical/NPZ helpers. It made no Julia, native-model-build or optimizer call and created no new candidate. The 37 original bindings, 23 copied payloads and all six producer run files were unchanged at entry and close.

The replay checked the 2,712-coordinate lift: all 2,472 retained candidate entries are unchanged and only the 240 disconnected mfg coordinates are zero-lifted. It evaluated every raw constraint record, including 4,384 affine rows with their duplicate multiplicity, 3,696 variable-constraint records and all 960 exact ZeroOne declarations. Raw objective terms and the full retained objective agree. The point passes the declared uniform rational expansion, but fails strict nominal membership: its largest exact nominal violation is `453/70368744177664`, approximately 6.4375e-12. Consequently the strict nominal upper remains absent.

For the lower proof, an independently written narrow NPY reader decoded the archived raw signed multipliers. The replay reconstructed their sign projection, all 4,384 row contributions, all 2,472 exact residuals and every selected finite-box minimum. It also checked the actual 240 native headroom relations, corresponding nonnegative Q/R domains and exact U declarations underlying the 480-coordinate correction. The correction is

`-19028708447742701067805971085719535 / 1329227995784915872903807060280344576`,

approximately -0.014315609141610166 encoded cost units. An explicit interval-minimum calculation agrees exactly with the original expanded lower plus that correction. Neither numerical optimality nor exact dual stationarity is needed.

The certified native-expanded identity cost bracket has exact endpoints:

- Lower: `20345200474536725055412689839003651156387479 / 10633823966279326983230456482242756608`.
- Upper: `21513444555664356003273356714053400780148197047959 / 11150372599265311570767859136324180752990208`.

These are approximately **[1,913,253.4579331875, 1,929,392.4363641317]**; the fractions, not the displayed decimals, are authoritative. This is one identity/native-penalized OR-LIB10 case and the unchanged full encoded UC objective. It establishes neither exact optimality nor expanded-model equality, and transfers no target-minus-identity interval, hard-service result, fossil-energy bound or calibrated physical uncertainty. Its validity combines the separately closed nominal correspondence with the reviewed containment theorem; it does not reinterpret the nominal comparison as an expanded-equivalence result.

The producer's completed arithmetic phase took 2.0989193 seconds, excluding its final completion-record write as declared. This independent replay uses raw MOI term evaluation, binary64 decoding through `struct` and direct rational interval minima. Both implementations run on the same host and use Python's exact rational arithmetic; this is an independent implementation, not an independent-host replication. The source/record review by `/root/find_deposit/gb_docs` is separate from this sole mathematical replay.

Stable reviewer source: `94c0e0f8462815c75607a1ab6d284d26eed54317d72999fee4f958d825bf5bc0`. Reviewer JSON: `8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1`. The JSON records every producer output hash, exact bracket/correction and input counts. No producer artifact was edited.
