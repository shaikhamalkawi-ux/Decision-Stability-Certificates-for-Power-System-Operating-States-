# Full-unit MIP extension: four unresolved cases

All four fixed cases reached the configured 60-second limit without a verified
integer incumbent. None is labeled admitted or rejected. The original Markov LP
results and their UNKNOWN operational verdicts remain unchanged.

| Seed | Solver termination | Operational verdict | Observed solve call time |
|---|---|---|---:|
| 260926100 | Time limit reached | UNKNOWN | 62.531 s |
| 260926101 | Time limit reached | UNKNOWN | 60.625 s |
| 260926102 | Time limit reached | UNKNOWN | 62.829 s |
| 260926103 | Time limit reached | UNKNOWN | 60.766 s |

The configuration allocated four 60-second limits, totaling 240 seconds. Actual
measured solve calls totaled 246.751 seconds because termination checks overran
the configured limits slightly; that observed time is not rewritten as 240.
There was one solve per case and no retry or tuning.

The reference dispatch passed the physical chronology and native on/on ramp
checks. For each permutation, reconstructed continuous matrices and bounds
matched the archived Markov model exactly before integer solving. The MIPs
retained all physical units, all 41 target means, native availability, fixed
hydro and minimum up/down constraints with the established free-edge conventions.
They omitted the network. Every solve log and paired-input/hash record is saved.
No new positive dispatch or commitment witness was obtained.

The distinction matters: first-order commitment counts can accompany an invalid
direct replay, while the existence of a different feasible schedule remains
undetermined here. These time limits neither prove an operational counterexample
to the preserved summary nor show that the summary is sufficient. The earlier
continuous witnesses prove only feasibility of the LP relaxation.

The boundary-pair wording correction and independent preservation checks are in
`docs/research8h/MARKOV_TWINS_REVIEW.md`. The separate prospective MIP design is
`docs/research8h/MARKOV_MIP_PROTOCOL.md`; its executable is
`src/research8h_markov_mip.py`.
