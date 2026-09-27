# Independent root review of six fixed-ray candidates

Status: PASS_COMPLETE, 27 September 2026. Source/protocol were reviewed before target arithmetic. The separate root replay checks all 106 frozen bindings, reconstructs the fixed row subsets from actual sparse state-column support, checks complete retained and dropped source coefficient ledgers and unchanged semantic row/column maps, and recomputes all six exact gaps through the standalone standard-library checker. It imports no producer subset or candidate-construction routine and invokes no optimizer.

All six prescribed candidate vectors are valid but fail to separate either the strict or expanded target model. Their exact reports agree with the producer. This is a null for those vectors, not proof of restricted feasibility, absence of another sparse certificate, minimum information or a new temporal replication. Source proof provenance remains a separate archived audit.

Reproduction: python -I -S results/research8h/hod_fixed_ray_transfer_root_review.py. The completed result is results/research8h/hod_fixed_ray_transfer/root_independent_review.json. The reviewer refuses to overwrite that result on a repeated run; use a clean checkout or a separately named review destination for a later independent execution.
