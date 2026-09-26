# Finite post-pilot sparse Farkas extraction

Frozen before these runs, from baseline commit
`7300129ce9bc4d7d4b6a9911eabe000b1789295e`.

The four cases are the archived LP models for seeds 26092600 through 26092603.
Seed 00 is the development example. The same method below is already fixed for
the other three, which are post-pilot coverage cases, not unseen generalization.
The baseline exact certificates and model files remain unchanged.

The purpose is a smaller exact infeasibility proof, especially fewer nonzero
chronological rows and the hours they reference. This is distinct from reducing
the source data needed to calculate the full-week target means or model bounds.

1. Independently replay each existing certificate against its hash-bound matrix
   and bounds. Count all row support, chronological row support, row-anchor hours,
   chronological variable-reference hours, global target-mean dependencies, and
   exact nonzero combined-column coefficients requiring box bounds.
2. Try the finite coefficient-pruning grid: relative thresholds 0, 1e-14, 1e-12,
   1e-10, 1e-8, 1e-6, 1e-4, 1e-3 and 1e-2, relative to the largest absolute row
   multiplier. Every candidate is a newly constructed vector and is fully checked
   with exact rational arithmetic. No deleted coefficient is assumed zero.
3. Start with every original static row and all 41 target-mean equalities, all
   variable bounds, and only the chronological rows used by the best verified
   candidate. Chronological families are transition, exclusive_transition,
   minimum_up and minimum_down. This only removes constraints.
4. Attempt further chronological group deletions in this fixed order: whole units
   in ascending UID order; contiguous 24-hour row-anchor blocks; contiguous
   8-hour blocks; then individual row-anchor hours in ascending order. A group
   already absent is skipped. Each proposal solves the continuous relaxed model.
   An accepted deletion needs an exactly verified, sign-admissible Farkas vector
   whose support is a subset of the retained rows and whose separation survives
   outward 1e-5 relaxation of every finite row and column bound. Solver status
   alone does not accept a deletion. Positive continuous vectors are checked
   and saved; timeouts, invalid rays and other failures remain explicit.
5. For each new solver ray, test both orientations after explicit projection to
   admissible row signs, and test relative thresholds 0 and 1e-10. Exact checking
   recomputes the complete weighted matrix, including numerical residual columns.
   After acceptance, retain only nonzero chronological rows of the new proof,
   together with all the unchanged static rows, means and variable bounds.

Candidate ordering minimizes chronological variable-reference hour count, then
nonzero chronological row count, then total nonzero row count; ties keep the first
candidate. Deletion acceptance always removes at least one retained chronological
row. No minimal-cardinality or irreducibility claim follows from this finite
greedy search, particularly when a budget cap stops it.

The initial cap is 840 seconds of total script wall time, 195 seconds per case,
64 LP deletion attempts per case, and 12 seconds per LP solve (further reduced by
remaining case/global time). One thread, simplex, presolve off, deterministic
random seed zero. All cases retain their original independently checked proof
even if the cap prevents improvement. The final certificate replay may add a few
seconds and requires no optimizer. Solver attempts and failed candidates are
archived. A null result is acceptable if no verified improvement is obtained.

All calculations concern the exact rational values of archived binary64 model
coefficients, not exact physical measurements. Full-week energy information and
variable bounds remain dependencies even when only a few chronological rows
appear in a proof. Report proof support and those dependencies separately.
