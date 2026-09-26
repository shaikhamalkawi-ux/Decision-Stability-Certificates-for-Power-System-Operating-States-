# Frozen all-on network restriction: unsuccessful

The one prescribed identity-week LP returned **Infeasible** in 0.472056 seconds
(HiGHS 1.12.0; one thread; simplex; presolve off; one 60-second limit). No second
solve, commitment adaptation, or permutation replay was performed.

This outcome concerns only the restriction that all 24 thermal units remain ON
throughout the week. Its hourly minimum generation, including fixed hydro,
exceeds net load by as much as 273.571153 MW. Thus there is already an aggregate
obstruction to this restriction, independently of transmission congestion or the
fossil-energy cap. The result is not evidence of infeasibility of unrestricted
unit commitment under the aggregate service specification.

The model has 10,920 columns, 10,417 rows and 38,976 nonzeros. It contains the
24-bus, 38-branch DC network, native power/availability bounds, fixed hourly hydro,
and the unchanged fossil-energy cap of 180555.9189139999 MWh. The cap includes
the 23 fossil units and excludes `121_NUCLEAR_1`. There are no individual mean
constraints, and the objective is identically zero. All 24 native hourly ramp
limits exceed their thermal output ranges; the smallest redundancy margin is
30 MW. Constant ON commitment satisfies the stated mature initial-history and
minimum up/down semantics.

As a formulation check, the existing network reference dispatch passed the
assembled network and cap rows when paired with its own archived commitment
bounds: the largest violation was 7.96e-12. This does not make that reference an
all-on witness. HiGHS returned a vector flagged `value_valid`, but direct matrix
and bound verification failed; that vector is retained as `returned_vector.npz`
and is not a feasible witness. No binary positive witness was obtained here.

All 25 source, protocol, native-input, reference-witness, budget, and permutation
files still match the pre-solve manifest in bytes and SHA-256, as recorded in
`final_input_hash_check.json`. The prospective protocol and executable source
were not edited after the run. Matrix and bound hashes are recorded in
`result.json`; the solver log and failed returned vector remain archived.

This test leaves the unrestricted full-network service problem unresolved. The
earlier five verified positive continuous no-network service LPs and the four
original negative certificates under individual generator mean constraints
retain their respective, different scopes.
