# Closed observation audit: six existing HOD pairs

The single authorized run completed all six ordinary pairs, three class controls and three identity self-controls, with no errors or phase skips. All six ordinary pairs have identical hour-of-day joint snapshot multisets and ordered 48-hour edges. Every ordinary pair differs in both its whole-day multiset and its raw directed-hour-transition observation. These pairs therefore do not demonstrate information loss for either of those two stronger observations.

This is a post-label audit of explicit unclustered observations. It is not an execution or evaluation of Auer TAG, TSAM or another published representative-period method. `PUBLISHED_COMPARATOR_NOT_EXECUTED` remains the status in every case. Existing UC labels are inherited context, not checked again here; seed26093211 remains UNKNOWN.

## Fixed six ordinary comparisons

Each day multiset has seven occurrences. Each noncyclic directed transition multiset has167occurrences. Removed and added counts below are multiplicities, not changed chronological positions. Every ordinary pair has three changed chronological day positions and four matched day occurrences.

| Week | Target | HOD+edges equal | Day multiset equal | Day removed/added | Transition equal | Transition matched | Transition removed/added | Changed physical rows | Inherited binary label |
|---|---|---|---|---|---|---|---|---|---|
|1|26093200|yes|no|3/3|no|121|46/46|46|certified expanded negative|
|1|26093201|yes|no|3/3|no|126|41/41|56|certified expanded negative|
|2|26093210|yes|no|3/3|no|110|57/57|46|certified expanded negative|
|2|26093211|yes|no|3/3|no|123|44/44|51|UNKNOWN|
|3|26093220|yes|no|3/3|no|121|46/46|44|certified expanded negative|
|3|26093221|yes|no|3/3|no|123|44/44|48|certified expanded negative|

The corresponding numbers of changed chronological adjacent-value pairs are61,69,65,65,61and63. They differ from the transition multiset changes because a pair can move to another chronological position without being removed from the multiset. Full records separately retain source continuity breaks and literal changed adjacent source-index pairs; neither substitutes for physical-value comparisons.

## Controls and conditional reconstruction

| Control | HOD+edges equal | Day matched; removed/added | Transition matched; removed/added | Changed physical rows |
|---|---|---|---|---|
|26100200|yes|5;2/2|151;16/16|14|
|26100210|yes|4;3/3|142;25/25|25|
|26100220|yes|5;2/2|163;4/4|2|

All three identity self-controls agree under every observation, with7matched days,167matched transitions and zero changes. All twelve input roles have168distinct complete107-coordinate rows. Their directed noncyclic transition multisets plus endpoints consume all167edges and reconstruct their exact sequences. This conditional, instance-specific losslessness of the raw observation does not extend to clustered transition representations or inputs with repeated rows, nor does it establish a useful compression or runtime advantage.

## What was checked

All107coordinates were retained:41pmin,41pmax,one independently archived aggregate net and24nodal values. Exact numeric equality normalizes signed zero only. Package forward and inverse maps were checked bitwise. HOD membership,48-hour boundaries, native row ranges, CSV/source indices, coordinate order, common coefficient matrices, all row/column-bound mappings and the full12096binary-coordinate mask passed. Canonical full-content dictionaries and complete observations are in `run01/`.

Preparation admitted108selected case artifacts against two pinned historical manifests and added9source/context bindings,117total. Entry and close rehashes passed. This selected-input audit is not a new reconstruction from raw native CSVs and does not repeat native physical feasibility or primal/dual proofs. Those older checks remain inherited evidence. Source IDs, commitment states and UC labels are not observation features.

## Execution and immutable bindings

Exactly one hash-only preparation (session43970,exit0) and one audit (session51607,exit0) ran under ordinary cached CPython with `-I -S`. Ten invented-data fixtures passed before source review; no old tests were rerun. The measured audit phase was55.77552329999162seconds against its300-second soft limit; initial validation/import was12.026345000020228seconds. Final input rehash and summary serialization are outside that phase measurement. Zero optimizer, clustering or UC mathematical replay calls occurred.

| Artifact | SHA256 |
|---|---|
|`src/researchnext_observation_audit.py`|`7a0bf951b4fc0c500d35c3f4729bf9a6b74bb6bb7f48ece673225c0eea991432`|
|`docs/research_next/OBSERVATION_AUDIT_PROTOCOL.md`|`22a5241efa5887fc7720e95b6e965d2e2bf8bbb54dcfeb28f4cec4717a2487f2`|
|`prepared/input_freeze.json`|`9ba6a4b70cc5572ec53493597c693092e6877aad8127d711dc3922900a075636`|
|`run01/summary.json`|`86045c0827ae1bb16fe856cd65dccf383f0f12be5d45de17cd26a183ae7fd39f`|
|`implementation_fixtures.json`|`400fc78132d2311e1b90350ef2e107a51aa28e06cb6f9f418b80f94de7665e5a`|

The summary retains the complete12-role ledger. Its referenced twelve case JSONs include all observations, comparisons, conditional reconstruction and provenance. Three `week_*_dictionary.json` files provide lossless canonical numeric content. Preparation and run start markers are retained. No historical source, results, labels or deliveries were modified.

Portability limitation: this reviewed version's preparation maps historical absolute paths by the current worktree prefix. It is a valid audit in this original workspace, not an independently relocated replay. A copied repository at a different path would need a separately reviewed, explicit old-prefix mapping before preparation; no such relocation or second-machine claim is made. The frozen source was not modified after this limitation was noticed.
