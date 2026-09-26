# Independent review of the January seasonal-transfer evidence

Verdict: **PASS.** Both archived Farkas certificates reproduce exactly and retain positive separation under the declared bound expansion. Independent native-input and constructive-witness checks pass. Additional exact rational evaluation establishes a coherent paired statement for the explicitly expanded encoded model: January identity and the constructive control have binary feasible witnesses; both ordinary twins have infeasible continuous relaxations. No optimization or witness editing was performed in this review.

The machine-readable record is `results/research8h/seasonal_transfer/independent_review.json`. All 136 frozen manifest entries, source/protocol hashes, certificate/model bindings, permutation mappings, and parent-versus-LP/MIP matrices and bounds match. The complete model has 34,681 rows, 23,016 columns, 24 buses, 38 branches, 41 generators and 12,096 U/Y/Z binary columns in its mixed-integer interpretation. The feasibility objective is zero. There are **zero named-unit mean rows** and exactly one fossil-energy-cap row.

## Inputs and constructive controls

The reference is the saved January seasonal dispatch, with exact binary64 fossil-energy sum

```text
Eref = 1654798412944827657145 / 72057594037927936 MWh
     approximately 22964.941239556443 MWh.
B    = ceil(101 Eref / 100) = 23195 MWh.
```

The 23 included thermal fuels are NG, Coal and Oil; nuclear is excluded from the fossil sum but remains in the physical model. The exact headroom is approximately 230.05876044355804 MWh. This is the declared reference-derived benchmark, not an external carbon policy or an optimal-reference claim.

A separate reviewer regenerated all three PCG64 permutations and native source arrays. Ordinary seeds 26093100 and 26093101 change 72 and 71 interior hours; control 26100100 changes 33 hours. Both 48-hour edge blocks stay fixed. Every availability, nodal net-load, native-row, reference dispatch and angle package follows the same mapping. The positive control permutes only within equal full 24-bit U classes, so its pointwise commitment sequence remains unchanged. Startup and shutdown indicators are recomputed from that sequence, not independently permuted. Every exact fossil-energy sum equals Eref.

Identity and the constructive control pass native dispatch, binary coupling, transitions, minimum up/down, on/on ramps, nodal DC balance, branch ratings, angle bounds, slack and cap checks. The ordinary reference permutations pass the static network and cap checks but have 278 and 286 direct dwell-run violations, respectively. Those candidate failures are not the infeasibility proof; the independently replayed Farkas certificates provide that proof. Native on/on ramps are redundant at the one-hour interval under the source operating ranges and also pass direct witness checks.

## Exact positive and negative statements use the same expanded model

Set tau to `Fraction.from_float(1e-5)`. Expand **every finite row and column bound** outward by tau. In particular the cap becomes B+tau, equality rows become intervals, and continuous box bounds expand. Positive U/Y/Z coordinates are still exactly zero or one. This is a mixed-units numerical expansion of the encoded binary64 model, not a model of measurement uncertainty or AC operation.

Every row dot product for the four archived constructive vectors was recomputed as a sum of exact rational products of individually converted binary64 values. No floating matrix product or floating residual was used to infer exact feasibility. All column bounds were checked in the same arithmetic. Identity and control satisfy all expanded bounds exactly, with exactly binary U/Y/Z. The ordinary static witnesses satisfy the expanded bounds after removing only `minimum_up` and `minimum_down` rows; their full chronological checks fail those rows as expected.

The largest exact nominal violation among the retained constraints is approximately 2.5498884647111388e-11, so these saved points are **not** asserted to be exactly feasible for the unexpanded nominal model. They are exactly feasible for the specified expanded model. The two certificates reject precisely that continuous expanded model. Consequently the binary positive-control and ordinary negative conclusions have a consistent exact-arithmetic domain despite tiny nominal witness residuals. Exact expanded row violations for the ordinary candidates are confined to minimum-up/down families; they do not compromise the static controls.

## Independent Farkas replay

The review reads saved hexadecimal multipliers and verifies their exact equality to the explicitly sign-projected raw solver rays. The raw rays have 48 and 24 inadmissible sign entries, respectively; the saved projected candidates, rather than the unmodified rays, are certified. Matrix, bounds, row metadata and experiment-manifest hashes match their bindings.

For each candidate d, exact rational arithmetic reconstructs the signed lower row sum beta, the combined coefficient vector r=A^T d, its maximum over the finite variable box, and the gap delta=beta-max(r^T x). It matches every saved rational numerator and denominator. The expanded gap is delta-tau*(sum|d|+sum|r|), also recomputed exactly.

| Ordinary seed | Nonzero certificate rows | Nominal gap, arbitrary ray scale | Expanded gap, same scale | gamma = -d_cap |
|---|---:|---:|---:|---:|
| 26093100 | 1,715 | 46,620.25505093238 | 46,526.78957194592 | 103.03318596460402 |
| 26093101 | 1,253 | 194,627.6885720027 | 194,355.96483466134 | 351.8722466960352 |

Both gaps are strictly positive. **The unnormalized gap is not MWh.** Its numerical size changes with ray scaling. Generic inherited support text that counts network bus/branch labels as unit identifiers, or mentions target means, is not used here; actual row families and zero mean rows were checked directly.

## Necessary uncapped fossil-energy bounds without another solve

Let the sole cap row be c^T x <= B and its certificate multiplier be d_cap=-gamma with gamma>0. Remove that row entirely. For the remaining constraints A0, define s=d_other/gamma using exact rational division, without rounding normalized multipliers back to floats. Let beta0 be the signed lower contribution of those normalized rows and q=c-A0^T s. The finite box gives

```text
c^T x >= beta0 + min(L<=x<=U) q^T x = LB.
```

The review independently constructs this objective lower bound from the noncap rows and box, including every exact stationarity-residual term. It then verifies the algebraic identities

```text
q = -r/gamma
LB = B + delta/gamma.
```

For outward expansion of **only the remaining noncap row bounds and the variable box**, the independently evaluated bound is

```text
LB_noncap,tau = LB - tau*(sum|s| + sum|q|)
              = B + expanded_full_Farkas_gap/gamma + tau.
```

The final +tau matters: the energy-cap row has been removed and must not contribute an expansion penalty. There is no cap left in this objective-bound problem. The direct row-and-box computation and both identities agree exactly for each certificate.

The following energy lower bounds are conservatively rounded downward to six decimals:

| Seed | Nominal necessary fossil-energy LB, MWh | Noncap/box-expanded necessary LB, MWh | Nominal necessary excess over B, MWh | Nominal necessary excess over Eref, MWh |
|---|---:|---:|---:|---:|
| 26093100 | 23647.478049 | 23646.570920 | 452.478049 | 682.536810 |
| 26093101 | 23748.120316 | 23747.348104 | 553.120316 | 783.179077 |

The expanded-model necessary excesses above Eref are approximately 681.6296806931 and 782.4068645590 MWh. These are lower bounds applying to any feasible uncapped candidate. **No uncapped feasible witness was established by this audit.** Therefore no finite energy penalty, attainable minimum, or optimal uncapped schedule is claimed; the uncapped model could itself be infeasible, in which case the necessary bounds remain valid but are not finite achievable penalties.

## Scope and conclusion

This arm gives an exact paired order-effect result for two declared ordinary permutations of one January week under the explicitly expanded DC-network/chronology model and reference-derived cap. It has a constructive binary positive control, static network controls, no named-unit mean requirements, and independently verified robust negatives. Free mature initial status, zero initial transitions and truncated terminal residence conventions remain as declared in the frozen protocol.

January is the only eligible held-out seasonal reference in this arm. April and October remain `NO_REFERENCE_NOT_RUN`; the design's gate requiring at least two held-out weeks is not met. No new-network, field, AC, novelty, Markov-alphabet, uncapped-feasibility or broad seasonal-generalization claim follows from these two cases. Frozen evidence and solver artifacts were not edited, and no new optimization was run.
