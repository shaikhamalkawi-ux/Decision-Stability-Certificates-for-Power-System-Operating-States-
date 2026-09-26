# Independent preflight review of the fixed-reference service arm

Review scope: read-only inspection before this arm's first solve. The reviewed
source was `src/research8h_fixed_reference_service.py`, initially SHA-256
`59b8f7a07a8faaf433e19ae189f277f64ef5f907e82114406080604f0d1695c2`, together
with `FIXED_REFERENCE_SERVICE_PROTOCOL.md` and the already frozen full-network
service-model assembly. This review does not launch or alter the experiment.

The variable mapping is correct. Each archived network model orders its columns
as P, U, Y, Z, theta. There are 6,888 dispatch columns, followed by 4,032 columns
in each of U, Y and Z, then 4,032 bus angles. Thus the half-open interval
[6888,18984) contains precisely the 12,096 integer columns. The runner asserts
that its archive integrality mask equals this interval, constructs U/Y/Z in the
same hour-major order, and fixes both bounds of every such coordinate. Startup
and shutdown follow the actual unpermuted reference changes; their first-hour
entries are zero. It does not inadvertently fix angles or permute the reference
commitments.

With those bounds, declaring the remaining optimization continuous is valid:
every formerly integer coordinate already has an exact binary value forced by
its lower and upper bound. Any passing point therefore belongs to the original
binary-network feasible set. The matrix is unchanged, including minimum dwell,
nodal DC equations, branch limits, output coupling and the shared fossil cap.
The fixed schedule is a restriction, so failure cannot reject the unrestricted
service model. Positive witnesses still require raw/rounded binary coupling,
observed residence and transitions, native ramp checks, reconstructed network
checks and the unchanged fossil cap, as implemented by the imported direct
checker. No generator-mean equality enters that checker.

All four fixed bound files and input hashes are written before any optimization
call. The zero objective and separate 30-second calls match the prospective
protocol. The use of the original chronological reference, without permuting its
U/Y/Z sequence, is explicit. This is a new prospective feasibility restriction,
not a retry or amendment of the four earlier MIP calls.

One implementation issue was reported to the parent before launch: the initial
runner asserted exact equality between every returned U/Y/Z coordinate and the
fixed values immediately after `solution.value_valid`. That flag does not imply
feasibility; the preceding all-on run supplied an invalid vector with that flag
set. Therefore a failed or infeasible vector could abort the remaining cases.
The requested correction is to retain a failed fixed-coordinate check and
continue, or gate the strict assertion on a passing matrix check. This concerns
failure handling, not the feasible-set mapping. No runner edit was made by this
reviewer.

The parent corrected this before execution. The revised source, SHA-256
`c28ae08e6542d55e87fe69498ca42efad66ae405ca029b015fb42eb1de853fca`, records
`fixed_schedule_exact` as a Boolean and uses it as an admission gate, without
asserting it for failed vectors. This reviewer inspected the changed lines and
confirmed the correction. The preflight is now clear for the stated bounded
experiment; no remaining formulation or verdict-scope defect was identified.

No fixed-reference optimization result had been inspected in writing this
preflight. Outcome verification and final source-hash binding remain separate
post-run checks.

## Post-run outcome and archive review

All four fixed-reference LPs returned numerical `Infeasible`, with verdict
`FIXED_SCHEDULE_INFEASIBLE_ONLY`. Actual call times were 0.0919695, 0.0832535,
0.1023640 and 0.0712995 seconds, respectively (0.3488865 seconds total). No
returned feasible point or binary-network admission was claimed. This reviewer
performed no optimization in checking these records.

All 42 manifest entries match their stored byte counts and SHA-256 hashes, and
the manifest itself matches `models_frozen_before_first_solve.json`. The final
runner hash is the corrected preflight hash above. In every case the source
matrix, original bounds and fixed bounds match their model-binding hashes.
Exactly the 12,096 integer coordinates are fixed to the original U/Y/Z sequence;
every other column bound and every row bound is unchanged. New lower bounds
are nowhere weaker than the source lower bounds, and new upper bounds are
nowhere weaker than the source upper bounds. This is an exact bound restriction
of the archived full service model, with its fossil cap preserved.

The quick failures have a direct fixed-schedule explanation: native available
capacity under the unpermuted commitment is below permuted net demand by up to
765.028253, 676.336665, 920.028253 and 765.028253 MW for seeds 00 through 03,
respectively. The corresponding zero-based hours are 79, 49, 104 and 119. These
are read-only floating-point diagnostics, not newly generated exact negative
certificates. They concern this particular unpermuted commitment sequence.

The protocol and recorded verdicts correctly restrict the conclusion to that
fixed sequence. They do not turn these four LP outcomes into an infeasibility
claim about unrestricted binary commitment or the shared service specification.
The earlier four unrestricted MIP timeouts remain UNKNOWN.
