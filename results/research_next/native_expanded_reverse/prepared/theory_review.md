# Independent review of the expanded-native containment proposal

Source/theory PASS for proposal SHA256 `b5342b65753d4440c0c19551dba45fb100731cb4fcd9206499ac38a6c23fc1db`. No new bound, point or scientific model arithmetic was performed for this review. The subsequently completed independent native comparison establishes the required nominal correspondence for the frozen identity/native-penalized instance only; it does not itself establish expanded equality.

The two inclusions are valid. Every expanded adapter point has the same expanded native affine constraints and unchanged exact binary declarations. Its extra finite Q/R boxes only restrict the native model; its N box is implied by the native N=0 row with the same expansion. The disconnected native mfg variables admit the zero lift. Conversely, the actual headroom inequality and native lower bounds imply

`Q + R <= width*U + tau`, `Q,R >= -tau`, `U in {0,1}`, `width >= 0`,

so each of Q and R is at most `width + 2*tau`. Native N lies in `[-tau,tau]`. With every other domain matched, this proves `S_adapter ⊆ projection(S_native) ⊆ S_relaxed`. The same argument also works if U is continuously bounded above by 1, but the proposed binary-set claim must retain the original exact 960 binary declarations. Uniformly widening a ZeroOne declaration into a fractional domain is not this model.

For an independently replayed row-multiplier proof with residual `r=c-A^T*y`, changing only those 480 upper boxes by one additional tau changes the box-support lower bound by exactly `tau * sum(min(r_j,0))`. The sign is nonpositive. Thus it may weaken, never strengthen, this particular lower proof. The resulting lower bound applies to the larger relaxed box model and hence to the projected native-expanded set. An accepted expanded adapter point can be lifted to a native-expanded upper with identical encoded cost; the proposed direct raw-native replay is a useful implementation check. Neither direction certifies a nominal-strict witness.

Required precision and scope:

- Treat archived binary64 numbers as exact rationals. Form `width+tau`, `width+2*tau`, endpoint shifts and the correction rationally, without an extra binary64 addition/rounding step. Width is the actual archived headroom coefficient, whose native/adapter match was already checked, not an independently recomputed real-valued difference.
- Replay the actual chosen multipliers, row sides, residual and finite box support. A rounded displayed bound or an unverified maximum of earlier lower bounds is insufficient. All finite endpoint shifts must follow the same declared tau convention.
- The native-expanded set is a mathematical perturbation of the archived native model; it is not a claim about the numerical feasibility tolerances or acceptance behavior of a Julia/solver runtime. One tau across differently scaled constraints is not a calibrated physical uncertainty set.
- The objective is the unchanged full encoded UC cost, including all retained coefficients and the verified constant/sense. This does not transfer a fossil-energy bound, operational-service claim, or monetary calibration.

The useful next discriminator is whether the existing identity witnesses and dual proofs yield a finite certified bracket for this precisely defined expanded native model after the fixed correction. A premise failure, rejected upper or weak lower is retained as such. A successful identity bracket closes an implementation-fidelity gap; it supplies no temporal separation or methodological novelty by itself. A target-minus-identity result still requires each target's own actual-code correspondence and proof, with the original target denominator fixed. Reusing identity correspondence alone, silently widening further, or selecting a replacement target would defeat that interpretation.
