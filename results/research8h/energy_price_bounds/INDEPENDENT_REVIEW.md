# Independent energy-bound review

**PASS COMPLETE.** The proof and source were reviewed before output inspection. This follow-up made no optimization calls and did not rerun the full point-row checks. It bound those archived exact point checks and independently verified binary coordinates, objective sums, source models, bounds, lower-bound derivations, and interval arithmetic.

All 49 audit input hashes/byte counts and all 55 uncapped-preparation hashes pass. Both target matrices equal their capped parents with exactly the fossil cap removed; all other bounds, native arrays and original binary masks match. The objective covers exactly 23 native Coal/Oil/NG units and excludes nuclear.

The 168 identity aggregate-row supports and equality bounds were checked directly. Every hourly maximum of the fossil-box and balance/nonfossil-box bounds was recomputed exactly. The resulting identity lower bound is 22,114.0856691 MWh; the exact chosen-reference energy is approximately 22,964.941239556443 MWh.

For both targets, the noncap ray multipliers, row terms, reduced-objective box terms, tau corrections, and both cap-removal identities match exactly. The final +tau after removal of the cap is correct.

Outward six-decimal brackets for target optimum minus identity optimum:

| Case | Lower MWh | Upper MWh |
|---|---:|---:|
| seed_26093100 | 681.629680 | 3048.533304 |
| seed_26093101 | 782.406864 | 3579.201241 |

These use [L_target - E_reference, U_target - L_identity]. The separately reported chosen-reference brackets use [L_target - E_reference, U_target - E_reference]; they were checked separately and are not substituted for optimum-to-optimum bounds. All saved rational endpoints and all 543 outward decimal display records pass.

Every conclusion concerns the explicitly tau-expanded, original-binary uncapped models. Full exact point feasibility was established by the bound, reviewed audit rather than repeated here; solver incumbent bounds/gaps are not used as exact proof. This is one January week and one network, with fossil electrical MWh as objective. No exact nominal optimum, economic-cost, emissions, or multiseason claim follows.

Detailed review SHA-256: `d70d955763a5aa7aa7c6a3ac0f889a2786e112939493452ad2bf51e6030bfd1d`.

Reporting check: both `summary.csv` rows and all three interval columns in `READOUT.md` match the exact outward endpoints. The optimum-difference and chosen-reference-excess columns are correctly distinguished. Their final file hashes are recorded in the detailed review. Both cases were complete at the original availability freeze.
