# Independent energy-LP refinement review

**PASS COMPLETE.** The earlier preflight is preserved in full in `independent_review.json`. This post-run review made zero optimization, native-control or full-point-replay calls.

All three raw/projected row duals were replayed independently by exact Fraction accumulation down sparse-matrix columns. Their sign projections, row terms, finite-box terms, stationarity residuals, nominal lower bounds and outward-tolerance deductions match every archived rational result. All 59 frozen manifest hashes and byte counts match; the existing binary-upper point hashes and exact upper energies are unchanged.

| Case | Previous lower MWh (approx.) | Refined lower MWh (approx.) | Existing binary upper MWh (approx.) |
|---|---:|---:|---:|
| january_identity | 22114.085669100 | 22615.822769091 | 22964.941239556 |
| seed_26093100 | 23646.570920250 | 24507.776969812 | 25162.618972557 |
| seed_26093101 | 23747.348104115 | 25104.092377194 | 25693.286909557 |

The exact maximum of old and new expanded lower bounds is used for each case. All three new bounds improve their priors; none exceeds its existing exact binary upper witness. Continuous LP primal values are not used as binary uppers or exact optimality proofs.

Outward six-decimal optimum-to-optimum difference intervals:

| January order | Lower MWh | Upper MWh |
|---|---:|---:|
| seed_26093100 | 1542.835730 | 2546.796204 |
| seed_26093101 | 2139.151137 | 3077.464141 |

Each interval is [best target lower - existing identity reference energy, existing target binary upper - best identity lower]. The separately saved chosen-reference excess interval retains the reference energy at both subtractions; both formulas and all rational endpoints were checked. 49 outward display records passed.

These are bounds for the same uncapped original-binary models after the explicitly declared uniform tau expansion. This refinement supplies no new season, network, data or replication. It does not assert exact solver optimality or nominal exact model feasibility.

Prepared manifest SHA-256: `b85b1260ded4d4f0a2576c921a4d84581360bfe7adddac361d5ad8826fd6e32d`.
Detailed review SHA-256: `94c10b498dc600f92d55c77987325a106d7dcbb64f201a284a8295b756528401`.

The final READOUT and summary CSV correctly distinguish optimum-to-optimum differences from excess over the chosen identity reference. Every absolute bound and interval display matches its exact rational with the declared outward six-decimal rounding. Their hashes are recorded in the detailed review.

The arithmetic-only ratio addendum also passes independent exact reconstruction: for positive identity and target optimum bounds, [L_target/E_reference - 1, U_target/L_identity - 1] encloses the relative optimum penalty. All eight ratio/percentage rational records, sixteen outward-decimal strings, CSV fields, source/script hashes, and unchanged absolute brackets match.

| January order | Relative optimum penalty, outward percent |
|---|---:|
| seed_26093100 | [6.718221%,11.261126%] |
| seed_26093101 | [9.314855%,13.607571%] |

These ratios compare the two expanded-model optima. They do not divide an absolute-difference interval by the chosen incumbent. This reporting addendum involved no optimization or additional matrix/full-point replay. All previously bound mathematical output hashes remain unchanged.
