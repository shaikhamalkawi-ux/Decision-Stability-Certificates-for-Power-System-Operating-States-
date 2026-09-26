# Day-block source/protocol preflight

Review date: 2026-09-26 UTC. **Verdict: no remaining blocker in the final
reviewed source and protocol.** No preparation or solver was launched by this
reviewer. This is a pre-preparation code review; generated model and witness
replay remains a separate check after the archive exists.

Reviewed SHA-256 values:

- `src/research8h_day_blocks.py`:
  `43441ca2da48c6d8acc2574461502f6f74a4f0f4a3b32ad653c5fd794a5f6a8b`
- `docs/research8h/DAY_BLOCK_PROTOCOL.md`:
  `b557ac53749616f13c600ddf2b02712e3fbd307083659dea05e65c108a659933`

The complete initial source and inherited archive, candidate, transition,
LP-certificate and exact-point helper contracts were read. The root corrected
the issues below before preparation; the final relevant code was reread.

## Corrected preflight findings

1. The static control initially excluded nonexistent min_up/min_down labels.
   It now excludes the actual minimum_up/minimum_down families, with a
   nonempty-deletion assertion.
2. The certificate helper needs matrix.npz and bounds.npz beside its output.
   Preparation now copies matrix, bounds, original integrality and row
   metadata into every lp/ directory before the manifest is frozen. Execution
   uses those existing files without overwriting them. The inherited helper's
   experiment-manifest binding is correctly redirected by transfer.OUTPUT.
3. Early constructive admission initially depended only on exact expanded
   matrix membership. It now also requires the complete native/numerical
   binary-network check, and an exact/native discrepancy stops preparation.
4. Source unit/thermal ordering and native Coal/Oil/NG membership are now
   asserted against the loaded model, with nuclear explicitly excluded from
   the 23-unit fossil sum. The MIP relative gap is explicitly 1e-8 in both
   code and protocol.
5. New certificate output corrects the inherited mixed-UID support label and
   target-mean wording. It separates temporal-generator support, uses the
   actual exclusive_transition family, and states the global cap's all-hour
   dependency. No existing certificate or inherited source is rewritten.

## Validated execution logic

The five lexicographic orders are generated once, with first/last 48 hours
fixed and within-day order/hour-of-day alignment checked. Native inputs and
reference P/U/theta share a bijective mapping; Y/Z are recomputed across the
whole sequence. Native nodal reconstruction and exact fossil preservation
are checked. Identity and the existing U-class positive control receive
exact expanded-model checks; the latter remains outside the five-case set.
Every target has an exact static control and an attempted full constructive
check. Failure of that copied schedule does not become a negative label.

Skipping both LP and MIP when a constructive point already answers the case
is valid. This differs from the earlier design suggestion of uniform LP
coverage, but the change is explicitly fixed before new outcomes and retains
all five cases in the denominator. Unresolved cases receive LP30 first, then
conditional MIP300; all LPs precede the MIPs. No cap, order, warm-start, retry,
or budget tuning is introduced. The 2,100-second phase and 305-second start
guard are implemented; unstarted MIPs remain UNKNOWN with their route saved.

U-only integrality is subject to the actual sparse projection audit. Returned
MIP vectors are retained raw; near-binary U is rounded, canonical Y/Z is
recovered, and P/theta is unchanged. Admission requires raw/recovered matrix
checks, the native physical check, and exact membership in the expanded
full-binary model. Strict exact membership is recorded separately. The exact
fossil sum is saved. Numerical-only candidates and unproved MIP infeasibility
remain distinct from accepted positives and exact negatives.

The inherited LP helper certifies only a fully recomputed rational ray that
survives the declared outward bound expansion. It does not promote a floating
infeasible status alone. The certificate files bind the copied matrices and
metadata, and the prepared manifest is checked before and after execution.
Preparation/run modes and the exclusive execution marker prevent accidental
reruns. The protocol correctly calls this an outcome-informed follow-up
with prospective settings, not blind seasonal replication or a new method.

One reporting detail: changed_adjacent_pairs_after_hours counts locations
where consecutive destination packages are nonconsecutive source hours
(diff(order) != 1). It is a source-continuity diagnostic, not a count of every
pair whose absolute time position differs from identity. Preserve that
interpretation when describing the saved count.

Successful preparation, immutable hashes, independent archive checks, and
post-run witness/certificate replay are still needed before publishing an
outcome. This review asserts no generated-case feasibility or novelty result.
