# Independent fresh January reference review

PASS for both completed reference witnesses, with no optimizer calls by the reviewer. The separate replays are results/research8h/fresh_reference_postrun_review/week_2.json and week_3.json; replay source SHA256 ee35dbe4878252c33381fe5a0202844601e14f1350df36fdf66f55632a8f5183. All 48 frozen bindings match before and after each replay.

For each vector, all 12,096 original binary coordinates are exact integers; P and theta bytes remain identical to the raw incumbent; U rounding is within the declared tolerance; Y/Z equal canonical transitions including zero initial auxiliaries. Every row and box bound was independently evaluated using scaled-integer exact arithmetic. Both points belong to the uniformly widened binary64 model at exact Fraction.from_float(1e-5); both fail strict nominal membership. Stored producer native no-cap checks pass; the independent preparation audit had reconstructed the native hourly arrays, while this replay does not rerun the producer physical assembler.

| Reference | Fossil MWh of verified incumbent | Solver seconds | Numerical relative gap |
|---|---:|---:|---:|
| January week 2 | 26269.05353649975 | 600.3705777 | 1.47857% |
| January week 3 | 47840.28339873613 | 600.3401202 | 0.77593% |

Exact energies are respectively 16259756583482128080663775801439 / 618970019642690137449562112 and 1683230331936304381 / 35184372088832. Each accepted point is an upper bound for its expanded-model optimum, not proof of optimality. Both calls ended at a time limit. Actual solver time is 1200.7106979 s, 0.7106979 s above the sum of nominal solver limits; reference phase time was 1213.7337655 s, within its 1800 s soft allocation.

These are native, newly selected week references. They establish eligibility for the separately frozen target stage, not successful replication of an order-induced infeasibility effect. That question remains to be tested with the four prespecified targets; their cap formula must use the exact accepted incumbent energy without outcome-adaptive adjustment.
