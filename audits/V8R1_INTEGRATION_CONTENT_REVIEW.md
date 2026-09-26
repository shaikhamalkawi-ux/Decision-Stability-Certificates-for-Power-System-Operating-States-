# Independent V8R1 integration content review

Date: 2026-09-26. Read-only review of the integrated candidate `main_core.tex` and `supplement.tex` against `results/v8r1`, the residence-certificate implementation, and both bibliography files. This review edits no manuscript source or result. Findings were reported to the integration owner as they were identified; the owner is applying fixes in parallel. Line references below identify the integrated source initially inspected and can shift during those fixes.

## Decision

The new numerical claims inspected are supported by the supplied artifacts. In particular, the eight-week rejection, seven independent residence obstructions, hourly ramp redundancy, and eight-day Elexon ranges are consistent with their result files. No new numerical contradiction or demonstrated failure of the residence-count argument was found.

The initially integrated text had stale interpretation/sample wording and needed explicit hour-to-energy units. Its availability statement also implied that new local candidate files were already in the public repository. The integration owner corrected these points, and the affected final text was independently re-read as recorded below. **The reported content findings are resolved, with public availability of the candidate branch still pending its push.** This report does not certify PDF layout, public deposition, or a new full optimization replay.

## Final affected-text reread

After the owner applied the fixes, the following source changes were verified directly:

- Main Elexon limitations now say eight Wednesdays. The added statement that all eight dates have only DF rows agrees with `daily_diagnostics.csv` for both complete raw files and classified rows.
- Main discussion now covers the eight-week extension and explains the unit-energy/residence obstruction. It explicitly treats hourly on/on ramps as redundant. Both the main ladder and the supplementary original two-week table label their ramp rows redundant.
- Main and supplementary energy-count expressions now include `Delta t=1 h`, and the thermal-unit restriction `Pmin>0` is explicit. The supplementary ceil/floor denominators contain the same time factor.
- The main first LP use is expanded; supplementary `r_g`, constant thermal `Pmax`, CCGT, OCGT, and EIC are defined. The supplementary W1 wording now unambiguously refers to the empirical operating laws.
- Main reproducibility text labels the 26 checks as baseline numerical claims. The supplementary verification paragraph enumerates the baseline quantities actually checked; its ledger's shorter “central numerical claims” phrase does not add a new verification claim.
- The supplementary unsupported numerical PGLib stress section is replaced by a benchmark-semantics limitation stating why those historical calculations are not candidate evidence.
- Main availability now distinguishes the candidate branch link from the original baseline Zenodo release, explicitly says the baseline lacks the new analyses, and preserves the raw-upstream-data exclusion. The owner plans to push the validated branch; the branch URL must not be represented as accessible until that succeeds. This is the only outstanding external-state dependency from this content review.
- Citation/bibliography order was rechecked after these edits: main 36/36 and supplement 12/12 remain in identical first-use order.

No further full numerical repetition or manuscript edits were performed for this closure check. The remaining task of validating final PDF layout belongs to the designated final-review owner.

## Findings sent for correction

| ID / priority | Location at initial inspection | Finding and specific correction |
|---|---|---|
| I1 / required consistency | Main 406, Elexon limitations | The integrated eight-day extension was still described as “two matched weekdays,” followed by “both selected days.” Change the overall sample to eight Wednesdays. Restrict statements about the original two-day PN comparison or original DF evidence to that illustrative pair, or use the eight-day diagnostics where appropriate. |
| I2 / required interpretation | Main 388 and figure ramp row 255 | Discussion still emphasized March/July surviving ramp constraints as the distinguishing result without mentioning that those constraints are redundant. Update to all eight weeks and make the redundancy explicit. Label the figure's native-ramp row a redundant control; retaining March/July in the figure is legitimate because that figure also compares their repair/AC results. The integration owner reported correcting the discussion and planned the figure clarification. |
| I3 / required dimensional clarity | Main 156; supplement 302–305 | `E_g=168 mu_{T,g}` and `Pmin*n_g <= E_g <= Pmax*n_g` suppress the time unit while `E_g` is explicitly MWh and `n_g` is a dimensionless count. Define `Delta t=1 h`, write `E_g=T Delta t mu_{T,g}` (or `Delta t sum_t p_target`), and include `Delta t` in count-energy bounds and ceil/floor denominators. State that the count test concerns thermal units with `Pmin>0`. The computation at one-hour resolution is numerically consistent; this is a written-unit issue. |
| I4 / required availability accuracy | Main 416 | “The current candidate adds ... in the repository” appears inside a public GitHub availability paragraph. At review time the new V8R1 code/results were still local untracked files and the branch had no upstream. Describe the additions as candidate/local artifacts until a public release actually contains them. Also change “the corresponding versioned archive” to “the original baseline archive” so the Zenodo DOI cannot be read as covering the new results. The explicit statement that the earlier Zenodo snapshot lacks the additions is useful and should remain. |
| I5 / first-use definition | Main 86 | LP lost its earlier expansion when the introduction was rewritten. The first remaining use is now “is an LP.” Change it to “is a linear program (LP).” |
| I6 / mathematical wording | Supplement GB mean/shape definitions, around 234 | “W1 for their empirical first Wasserstein distance” grammatically points back to the mean vectors. Use “the first Wasserstein distance between the empirical operating laws with full-coordinate L1 ground cost.” The actual implementation compares laws, not just their means. |
| I7 / evidence-version scope | Main 385; supplement numerical-verification section and ledger | Label the 26-claim arithmetic checker as checking **baseline** numerical claims. Its count does not include the newly added eight-week, residence, and eight-day claims. Those have their separate result checks, including 32 transport-program comparisons and 1125 short-horizon recurrence checks. The existing warning that arithmetic checking is not a complete optimization replay is correct. |
| I8 / source completeness | Supplement new sections, around 273, 300, 312 | Define `r_g` and constant thermal `Pmax` locally in the new supplementary ramp paragraph. Expand CCGT/OCGT and EIC at first supplementary use, or use their full names. These are small remaining first-use issues introduced by integration. |
| I9 / consistency with removed evidence | Supplement “PGLib-UC stress benchmark” section | After the integration owner reported removing unsupported/unpinned numerical PGLib stress claims from the main paper, the supplementary section still asserted the March/July numerical rejection pattern. Apply the same evidence boundary to the supplement: remove those numerical claims or supply their specific retained evidence. Background methodological comparison and bibliography references can remain. |

The integration owner was promptly informed of I1–I9. This record does not silently mark a notified item resolved without a subsequent check of the final source.

## Evidence checks that passed

### Eight-week chronology

`results/v8r1/rts_seasonal/summary.csv` contains January, February, March, April, May, June, July, and October. Every minimum-up/down model has status `Infeasible`, with elapsed solver time under 60 seconds; the largest listed elapsed value is approximately 3.094 seconds. The May ramp-only optimization reaches its time limit and is correctly distinguished from infeasibility. Original schedules provide the separate direct witnesses.

`results/v8r1/rts_archived_ramp` and the residence summary report all eight archived schedules passing their bound, balance, hydro, and native online-to-online ramp checks. Thus the expanded table's binary/ramp admission counts are supported without relying on the unresolved May optimization search.

The analytic redundancy table has exactly 24 thermal rows, all with `on_on_ramp_redundant=True`; its smallest `redundancy_margin_MW` is 30. The implication is mathematically valid for constant thermal bounds and the chosen on/on-only one-hour convention: any two online outputs differ by at most `Pmax-Pmin <= 60*r_g`. It does not prove anything about tighter ramps, startup/shutdown envelopes, or a finer time grid. The revised abstract and conclusion state that boundary correctly.

### Independent residence explanation

The summary labels seven months `INFEASIBLE_NECESSARY_CONDITION`; June alone is `NOT_ESTABLISHED`. The candidate correctly retains the full mixed-integer result for June instead of interpreting lack of a single-unit certificate as admission.

The implementation in `src/v8r1_rts_residence_certificate.py` propagates conservative necessary bounds from balance and fixed coordinate energy, obtains forced thermal statuses, and enumerates reachable online-hour counts with a finite-state recurrence. Its initial statuses have no pre-week dwell obligation, and terminal dwell is not extended beyond the observed horizon. The count test uses outward power/energy tolerances. Inspection did not reveal an inconsistency with the declared weak-boundary model.

For January, `failure_margins.csv` supports the cited `123_STEAM_3` example: target energy `3228.521078000018 MWh`, energy-compatible online count at most 23, and smallest residence-compatible count 100. With the 140-MW minimum output, this represents a large gap rather than a rounding artifact.

For July, `month_07_certificate.json` lists `115_STEAM_3` forced on at hour 2, off at hour 3, and on again at hour 7, with an eight-hour minimum downtime. A shutdown at hour 3 forbids the forced on-state at hour 7 under that rule. This is a valid concrete obstruction.

`dp_exhaustive_validation.json` reports 1125 passing short-horizon forced-status cases. The implementation independently enumerates all binary sequences for each selected case and compares reachable counts. The manuscript does not claim that those 1125 cases exhaust every possible full 168-hour instance, which is appropriate.

### Elexon signed state and sensitivity

The integrated methods explicitly retain signed B1610 average-MW coordinates and explain that acquisition-date production classification includes pumped-storage-coded units and station-demand names. No text reviewed interprets negative values as automatically erroneous or clips them. The current registry is explicitly not represented as a historical 2023 registry.

`sensitivity_summary.json`, `pair_metrics.csv`, and `verification.json` support the new primary table:

| January / July dates | Pairwise coordinates | Shape share, rounded | Same-period premium, rounded |
|---|---:|---:|---:|
| 4 / 5 | 259 | 6.49% | 1.56% |
| 11 / 12 | 260 | 5.89% | 1.15% |
| 18 / 19 | 260 | 6.59% | 1.77% |
| 25 / 26 | 260 | 13.56% | 2.47% |

The pairwise-primary shape range is `5.8872756–13.5601185%`, matching the abstract's `5.89–13.56%`. The 16 pairwise cross-pair ranges are `3.4607684–13.5601185%` for shape and `0.7463374–9.3549348%` for the same-period premium. The fixed-259-coordinate primary shape range is `5.8912978–13.5662752%`, matching the manuscript's `5.89–13.57%`.

All 32 assignment/transport-program comparisons pass; the maximum recorded absolute difference is `1.0913936421275139e-11 MW`, below the stated `1.1e-11 MW`. The text explicitly treats cross-pairs that reuse days as nonindependent and descriptive, not independent statistical replications. It also distinguishes a protocol fixed before additional acquisition from an unsupported claim that the original illustrative pair was selected independently of outcomes.

`baseline_and_provider_revisions.json` supports the reacquisition statement: original-date raw hashes changed, while BMU/period keys, quantities, and settlement-run values were unchanged. The registry duplicate diagnostic supports one duplicated BMU identifier being collapsed to one coordinate with two aliases retained.

### Great Britain interpretation and baseline quantities

`pypsa_gb_chronology_gate.json` is consistent with the revised prose: inactive/null chronology fields in frozen LP extracts do not prove that upstream UC parameters are absent. Recovered optional overlay parameters do not establish native matched-network chronology without missing eligibility/time-dependent model information. No new GB chronological rejection is claimed.

The original July repair values and outward-rounded inequalities remain consistent. Main's strict six-decimal interval `[8.020508,11.926297] MW` and the supplementary ten-decimal endpoints enclose the archived relaxed/witness values. The March lower bound remains clearly distinguished from an exact integer repair. The 48 AC witnesses are still restricted to the specified March/July hours, and returned local witness costs remain distinguished from globally minimal distances.

### References and cross-references

A source-order comparison of every first `cite` occurrence against the `bibitem` lists returned:

| Document | Unique cited keys | Bibliography entries | Missing keys | Uncited entries | First-use order mismatches |
|---|---:|---:|---:|---:|---:|
| Main | 36 | 36 | 0 | 0 | 0 |
| Supplement | 12 | 12 | 0 | 0 | 0 |

This confirms first-use bibliography ordering in the reviewed source. It is not a fresh per-DOI metadata verification; that is covered by the separate reference correction workstream. The new Elexon sensitivity table has an explicit callout and unique label. Existing main/supplement labels and calls were already repaired before integration; final compilation and PDF verification remain with the final-review owner.

## Limits of this review

Read-only source/artifact inspection and simple independent counting/arithmetic were performed. The review did not edit scientific sources, rerun the full mixed-integer or nonlinear optimizations, validate a new public release remotely, or certify final PDF layout. It distinguishes currently available baseline artifacts from candidate additions and does not treat a repository or Zenodo deposit as peer review.
