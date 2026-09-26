# Post-pilot extraction on the existing rejection corpus

Recorded after the frozen paired-order experiment: its one-unit screen found
zero rejections across 16 permutations, while the first four complete MILPs
terminated infeasible. No compact explanations were produced for those new
negative cases. These results are retained unchanged.

This separate software-validation exercise applies the already implemented
greedy explanation extractor to the eight **previously inspected** original
weekly targets. Seven have existing necessary-condition rejections and June
does not. This is a known-result development set, not a new validation sample.
Use the same interval propagation and unit-order selection, no parameter tuning,
and check expected rejection identities against the archived results.

For each of the seven rejected weeks, select the first failing unit, remove
forced-status atoms in increasing hour order whenever the rejection remains,
and independently recheck every final core and every single-atom deletion with
the age-based checker. Report inclusion-minimal atom counts. No minimum-memory,
minimum-cardinality, new rejection-coverage or unseen-data accuracy claim follows.

All 168 hours and all 41 energy targets can still be needed to derive the
necessary bounds. Independent checking here concerns the residence/count
contradiction, not an independently implemented proof of the propagation stage.
