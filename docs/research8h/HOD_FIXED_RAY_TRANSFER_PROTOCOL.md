# Fixed-ray transfer to two known HOD negatives: zero-optimizer protocol

This post-label, same-week explanatory arm uses exactly six deterministic arithmetic candidates. It adds no LP/MIP, new permutation, window/unit selection, replication or optimization. The full HOD labels are already known. All old files remain read-only. Root reviews this source/protocol before new target arithmetic. Separate prepare-only and check-prepared modes preserve a complete freeze before candidate evaluation.

## Models and fixed candidates

The targets are the archived full-network capped HOD models seed26093200 and seed26093201, with cap23195 MWh, no unit means, full168 hours and unchanged finite column boxes. Apply only the two existing rules from TRANSFER_PROTOCOL.md and SEASONAL_RULE_TRANSFER_PROTOCOL.md:

- two_cc keeps the four temporal families only for107_CC_1 and118_CC_1; all static/network/cap rows survive. Other units' transitions and exclusivity are removed too, so this is not a dwell-only restriction. Expected rows19985, columns23016.
- locality48 keeps transitions/exclusivity globally; a dwell row survives iff all its nonzero U/Y/Z variable hours lie in[60,107]. No truncated sum, endpoint-only test or moved window. Expected rows28689, including1023minimum_up and1001minimum_down rows, columns23016.

For each target, in this order, evaluate:

1. old_january_locality: map the accepted seed26093101/locality48 certificate from seasonal_rule_transfer onto the target locality48 model, preserving every multiplier bit/value.
2. own_full_to_two_cc: keep the target's own accepted full HOD ray entries only on two_cc rows; set every excluded entry to zero.
3. own_full_to_locality48: the analogous restriction to locality48.

Visit seed26093200 before seed26093201. No sign reversal, rescaling, thresholding, sign-cone repair, support search, alternative candidate or retry is permitted. Existing accepted source rays were sign-projected in their original experiments; this arm neither repeats nor adapts that projection. Exactly six target candidates stay in the ledger, including zero/nonseparating/invalid candidates.

## Preparation and provenance

Use the stdlib-only archived matrix/ray reader; no NumPy/SciPy/HiGHS or producer solver module is imported. Check the full parent matrix dimensions, finite coefficients/bounds, original full-binary mask, physical unit/bus ordering and P/U/Y/Z/theta offsets. Construct the row subsets directly from actual nonzero columns. Freeze all inputs, old rule/source protocol bindings, current source/protocol, four new subset matrices/bounds/original masks, selected parent rows, semantic row metadata, candidates and mapping tables before checking targets. Rehash all inputs after preparation and after target arithmetic. Source proof validation is separate from the six target checks: independently replay the one old January locality proof and two accepted full HOD proofs against their original bound models, matching archived exact fractions.

For the old certificate, prove its stored retained-parent map and each original_row label identify the same actual parent row. Map semantic family/hour/UID keys into the HOD parent, verify column identities and exact sparse coefficient equality, then into the target subset. Row bounds and boxes may differ between old and new hourly order; target arithmetic must use the new bounds. Save a coordinate mapping for every nonzero source multiplier. For target-full restrictions, save kept and zeroed original entries separately, retaining exact hexadecimal values. Never infer a valid target proof solely from an old label or matching row number.

The HOD identity and class control26100200 have independently verified original-binary full feasibility under uniform finite-bound expansion. Bind their full models/vectors, the completed independent post-run review and its frozen parent manifest. Prove each new control rule is an exact indexed row subset with all columns/boxes unchanged; deleting rows preserves those same witnesses. No control solve or repeated point/native replay is required. The inherited claim is expanded membership, not nominal strict membership.

## Exact checker and interpretation

Interpret every archived binary64 value as its exact rational. For a supplied signed row multiplier d, select each finite lower row endpoint when d>0 and upper endpoint when d<0. Let beta be the signed endpoint sum and q=A^T d. Separation is beta-max_box(q^T x). The uniform-expanded separation at tau=Fraction.from_float(1e-5) is the strict gap minus tau times(||d||1+||q||1); independently evaluate widened endpoints too. Reject inadmissible finite-endpoint signs explicitly, without repair. Invalid input models/bindings/mappings halt; a correctly loaded but inadmissible target candidate is retained as INVALID_CANDIDATE.

Keep distinct statuses: CERTIFIED_EXPANDED_INFEASIBLE, strict-only separation, valid nonseparating candidate, and invalid candidate. Only the first transfers the original expanded-model negative claim. No failed candidate, negative gap or zero vector proves restricted feasibility; no solver is called to resolve a null. Gaps depend on multiplier scale and are not MWh penalties.

Report retained model row counts separately from candidate nonzero row counts, dwell/other temporal support, global/background rows, distinct generator support and dropped source multiplier counts. These are sufficient proof candidates, not minimum supports or IISs. Locality refers only to retained dwell-row support: global transitions, DC/static data and the cap still depend on the full horizon. Two_cc does not identify two uniquely necessary generators. Preserve all six outcomes and existing prior transfer failures. No publication occurs until root review and any required independent replay are complete.
