# Independent review of the aggregate fossil-energy sensitivity

Result: **PASS for model reconstruction and all five continuous-witness replays**.
No optimization was performed by this review; HiGHS was not imported. Only this
review and `results/research8h/service_cap/independent_review.json` were written.
The frozen script, protocol, inputs and original experiment records were unchanged.

## Model and budget checks

The code removes exactly the 41 `target_mean` equalities, one for every original
generator coordinate. It retains every other original row and every column bound
exactly, then appends one upper-bound row summing the 23 fossil units' dispatch
across all 168 one-hour periods. The resulting models have 24,265 rows and 18,984
columns. Direct sparse-matrix and bound-array comparisons confirmed that no
additional physical constraint, target relaxation or coefficient change occurred.
Row labels were independently checked against the retained source rows.

The excluded thermal unit, `121_NUCLEAR_1`, has native fuel label Nuclear. The
23 included units comprise 6 Oil, 8 Coal and 9 NG units in the pinned native
generator table. Thus the unit selection matches the declared fossil scope.
The cap does not constrain nuclear, hydro or renewable energy individually;
fixed hourly hydro output still follows its unchanged physical bounds.

Recomputing the sum of the parsed reference dispatch entries with exact rational
arithmetic reproduced the frozen numerator and denominator. Its floating display
is 180555.91891299986 MWh. Upward conversion to binary64 followed by the nominal
1e-6 MWh addition gives the frozen shared cap 180555.9189139999 MWh. The actual
exact difference is approximately 1.0000279484501107e-6 MWh. This small difference
reflects binary64 rounding and is not an independently selected policy margin.

The budget also exceeds the fossil energy implied by the original exact-mean LP
equalities. That check used exact rational values of both the mean right-hand
sides and their stored 1/168 coefficients. Therefore the changed specification
really is a relaxation of the original named-energy specification, rather than
accidentally tightening a rounding boundary. The original binary network witness
also passed every row and bound of the changed identity model within tolerance.

Every frozen input hash and each result's matrix/bounds hashes matched. The
independent JSON records the source generator-table hash and fuel classification.

## Replayed outcomes

All five solver runs reported Optimal and supplied continuous vectors. Reloading
those vectors and directly multiplying them by the archived matrices gave a
maximum row/column-bound residual of 1.7462298274040222e-10 across all cases,
well below the declared 1e-5 checking tolerance. No negative ray was produced,
so there was no Farkas certificate to replay in this sensitivity.

| Case | Continuous LP result | Fractional U/Y/Z coordinates | L1 change in individual mean outputs |
|---|---|---:|---:|
| identity | Verified within tolerance | 506 | 867.543 MW |
| seed_26092600 | Verified within tolerance | 513 | 833.200 MW |
| seed_26092601 | Verified within tolerance | 578 | 810.530 MW |
| seed_26092602 | Verified within tolerance | 591 | 814.329 MW |
| seed_26092603 | Verified within tolerance | 559 | 821.329 MW |

Fractionality means distance from the nearest integer exceeds 1e-5. The mean
changes compare these particular continuous vectors with the original network
witness's complete mean vector. They are descriptive differences, not optimized
repair distances. The cap is active within numerical roundoff in these returned
vectors; no minimum-fossil-energy optimization or threshold search was performed.

## Scientific interpretation

The four original LP rejections **do not persist in this aggregate-budget LP
sensitivity**. Their exact certificates remain valid for the original complete
41-unit energy targets. The result shows that relaxing those allocations to this
single fossil-generation budget changes the LP verdict. A conclusion that the
ordinary-twin examples already demonstrate impossibility under the same aggregate
service budget would therefore be unsupported.

These positive vectors are fractional, so the permuted cases have not acquired
full binary unit-commitment or network feasibility witnesses. The separately
verified original identity network witness remains a positive control. No
conclusion about field operation, economic cost, actual carbon emissions or
general temporal-summary sufficiency follows from this sensitivity.

The sum used here is fossil generation in MWh, with equal coefficient one for
oil, coal and gas generation. It is not a carbon estimate. The native generator
CSV has emissions and heat-rate field headers; this experiment does not validate
or use those conversions. Say that emissions factors were not used or validated
for this sensitivity, rather than claiming that such source fields are absent.

The synthetic theorem candidate with a specified thermal-energy/carbon cap is
a separate construction. This RTS sensitivity does not itself demonstrate that
theoretical cap-feasibility obstruction on the selected real-data cases. Likewise,
the sparse original certificates remain conditioned on the complete mean vector.
