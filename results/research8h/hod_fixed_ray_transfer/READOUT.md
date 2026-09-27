# Fixed-ray explanation reuse: complete null result

Exactly six prescribed arithmetic candidates were checked once after the 2026-09-27 00:24:34 UTC freeze. All six are valid signed-row combinations but fail to separate even the strict model. There were zero optimizer calls, zero adaptive projections or coefficient changes, and zero accepted transferred certificates. All 106 frozen input bindings remained unchanged. Runtime for the six candidate checks was 5.037 s.

| Target seed | Fixed candidate | Retained / original nonzero multipliers | Nonzero dwell multipliers | Expanded separation gap |
|---|---|---:|---:|---:|
| 26093200 | old_january_locality | 1268 / 1268 | 211 | -58340203.203434 |
| 26093200 | own_full_to_two_cc | 866 / 1442 | 27 | -538161.240790 |
| 26093200 | own_full_to_locality48 | 1326 / 1442 | 112 | -827764.088384 |
| 26093201 | old_january_locality | 1268 / 1268 | 211 | -51125713.782195 |
| 26093201 | own_full_to_two_cc | 1002 / 1706 | 37 | -574395.174643 |
| 26093201 | own_full_to_locality48 | 1551 / 1706 | 155 | -763128.960573 |

These gaps have the arbitrary scale of each source multiplier vector; they are not MWh and are not comparable as operational deficits. Exact rational values and independently matching widened-endpoint/norm computations are in summary.json and each candidate's exact_check.json.

The old January locality ray remains a valid, independently replayed certificate for its own original model. It does not transfer to either HOD target under the unchanged coefficient vector. Dropping coefficients from the HOD full-model certificates according to the fixed two-CC or locality48 rules also fails to certify their respective restricted models. This is a null result about these six proof vectors, not evidence of feasibility, absence of another sparse certificate, or impossibility of finding a smaller explanation. The known full-model HOD negatives remain unchanged.

The two-CC rule retains all temporal families only for 107_CC_1 and 118_CC_1; it is not a dwell-only deletion. The locality48 rule retains global transitions/exclusivity and only complete dwell rows whose state-column support lies in hours 60–107. Both retain full static/network/cap background and column boxes. Retained model rows, nonzero dual support and dropped source entries are recorded separately. Existing identity/class full positive controls imply positivity of their own archived subset models through the checked row-inclusion mappings; they are not positive points for the two ordinary targets.

This is post-label, same-week explanation reuse. No new temporal replication, IIS minimality, minimum-information claim, or raw-data acquisition result follows. Source certificate mathematical validity was replayed separately from its historical source-manifest provenance.

Reproducibility: source SHA256 a8138ee89545d25e4f35e6f52cfcb49ec697b7467ce0c5c71f911fbed80207e4; protocol SHA256 2f90ae2c16907a32136c491d9b2ba2ae93a59e23ddbf8eb212d0175173915fd5; manifest SHA256 3753fdcd4bb9d4f04c45f538631f019e54ff17d5c834266d0807a1353b89366a. Run commands: python -B -I -S src/research8h_hod_fixed_ray_transfer.py --prepare-only, then --check-prepared. Preparation and checks are separate; no outcomes were computed before freeze. Root completed the final source/protocol review before the target checks.
