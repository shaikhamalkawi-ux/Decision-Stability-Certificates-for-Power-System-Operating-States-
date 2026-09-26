# Cap bands and order-blind error: independent review

**Verdict: PASS for the arithmetic consequences and stated scope.** This review adds no optimizer call, full matrix/point replay or experimental case. It relies on the separately completed January exact lower-bound and binary upper-witness audits, checks the exact rational quantities against that independent review, and independently reproduces endpoint arithmetic.

Replay source: results/research8h/cap_band_independent_review.py, SHA-256 bff145ec85dfdfb19788e4a1111c7c70e9d103e9769adc7b4ff13cf7aadef0de. Evidence: results/research8h/cap_band/independent_arithmetic_review.json. One execution completed successfully in 0.224 seconds. All four frozen input bindings match before and after. Manifest SHA-256: 686d407ff94eb2e198656a5edc43aef115492e5ef618a7be1c4f0a0128c92806.

## Cap theorem and endpoints

Let U_I be the exact energy of a verified identity binary witness and L_T a valid target lower bound for the uncapped model with every finite noncap bound expanded by tau = Fraction.from_float(1e-5). The added nominal cap B expands to B + tau. Thus U_I - tau <= B guarantees identity membership, while B < L_T - tau implies target infeasibility, even in the continuous relaxation used to derive L_T. The upper endpoint is excluded: equality does not give a contradiction. This band is sufficient, not an exact feasibility threshold or a maximal band.

The replay reproduces both rational endpoints, width L_T-U_I, the exact half-width, inward six-decimal display rounding, first/last integer membership and neighboring-integer exclusion. The displayed endpoints, when parsed as actual binary64 values, also remain inside the band in these two cases.

| Original January target | Safe closed decimal cap interval (MWh) | Integer caps | Count | Half-gap lower bound (MWh, rounded down) |
|---|---|---|---:|---:|
| seed_26093100 | [22964.941230, 24507.776959] | 22965 through 24507 | 1543 | 771.417865 |
| seed_26093101 | [22964.941230, 25104.092367] | 22965 through 25104 | 2140 | 1069.575568 |

The original cap 23195 lies inside both. These many admissible caps are arithmetic consequences for the same two pairs, not separately executed tests or additional replication. Exact fractions remain authoritative; the displayed interval is a deliberately smaller closed subset. Because the declared tau is the exact binary64 interpretation of 1e-5, it is slightly greater than the decimal rational 0.000010; its six-decimal upper enclosure 0.000011 is therefore mathematically correct, although visually surprising.

## Estimation consequence

The identical observations used here are the complete joint hourly multiset, fixed first/last 48 packages, unchanged physical model and common cap. They refer to the original two January permutations, not automatically to the later hour-of-day experiment. A deterministic classifier restricted to these observations gives the same output on each pair and cannot be correct for both opposite feasibility labels; it can abstain. This is a pairwise worst-case obstruction, not a population error rate.

The existing uncapped binary witness upper bounds are finite: approximately 25162.618973 and 25693.286910 MWh for the two targets, and 22964.941240 for the identity. Their exact fractions and inheritance bindings match the completed independent energy review. Together with finite expanded dispatch boxes, existence of these witnesses ensures finite attained optimum values. The true target-minus-identity optimal difference is at least L_T-U_I, despite the identity incumbent not being proved optimal. For any common finite numerical estimate v, the triangle inequality gives max(|v-E_I*|, |v-E_T*|) >= (L_T-U_I)/2. Thus the reported half-gaps are defensible even without optimality of the incumbent witnesses.

The calculation does not rerun the upper-point checks and must retain those provenance links. It is not a bound on a specific algorithm's observed error, a minimum-information theorem, a bit complexity statement, an emissions quantity or a new information-theoretic method. Fossil electric energy has units MWh; conversion to fuel use or emissions requires additional data. No claim about methods retaining more chronology follows.
