# Temporal-information pilot: frozen protocol

Recorded 2026-09-26 before running the paired-order experiment. This is a
bounded exploratory pilot, not a claim of novelty or a replacement manuscript.
Baseline source commit: `1c32c5f65a7aba51c721f61a7fe9bb3b1a280dcd`.

## Question and falsifiable outcomes

Can two orderings of the same complete set of hourly operating conditions have
opposite chronological feasibility verdicts for the same full generator energy
vector? If yes, how many forced-status observations suffice to explain a
rejection? A sparse explanation is not automatically a small sufficient input
summary or a globally minimum certificate.

## Fixed design

1. Use the existing July 168-hour network repair witness in
   `results/v8/network_repair`. Independently recheck dispatch, status, nodal DC
   balance, branch limits, native on/on ramps and minimum residence times.
   The target is this witness's complete 41-generator mean, not the infeasible
   original static mean. No optimization is used to create the positive case.
2. Keep hours 0--23 and 144--167 fixed. Permute the interior 120 complete hourly
   packages using NumPy PCG64 seeds 26092600 through 26092615. Each package
   contains native row ID, nodal load and embedded PV, generation availability,
   and witness dispatch. Preserve a full permutation map. Use identity as the
   positive control. The exact multiset identity is checked by undoing each
   permutation, not merely by comparing rounded descriptive statistics.
3. All cases retain one-hour steps, native minimum up/down times, and the
   existing free initial history and truncated terminal dwell conventions.
   Every generator remains a separate physical unit. First and last days being
   fixed strengthens boundary control but does not impose a new initial state.
4. Apply the existing solver-free necessary-condition method: balance/energy
   interval propagation, then individual-unit residence/count reachability.
   Absence of a rejection is UNKNOWN. A violation by the permuted seed schedule
   alone is never an infeasibility proof.
5. For each rejected case, choose the first rejecting unit in the locked native
   order and greedily remove forced-status observations in increasing hour
   order while preserving rejection. Recheck every retained observation's
   necessity in the final subset. Report this as an inclusion-minimal
   explanation, not minimum cardinality. Keep all underlying bound evidence.
6. Cross-check the first four permuted cases, irrespective of their outcomes,
   with the unchanged 60-second full unit-level no-network minimum-up/down
   feasibility model and the same complete target means. A verified incumbent
   proves only relaxed feasibility; an explicit infeasible status rejects the
   stronger network model. Time limits without a verified witness are UNKNOWN.
   Certificate rejection and a valid incumbent together constitute a failure
   requiring investigation, never a favorable result.
7. Seeds 00--07 are the development half and 08--15 are a held-out application
   of the frozen procedure; all derive from one week and are dependent. No
   population accuracy, out-of-season generalization, or speedup over full UC
   is inferred from this small sample. Time preprocessing, reachability,
   explanation extraction and solver runs separately.

## Numerical and information accounting

Power tolerance is 1e-5 MW and coordinate weekly-energy tolerance is
168e-5 MWh, with outward relaxed bounds/count limits. This is a numerically
checked necessary-condition certificate, not a formal exact-arithmetic proof.
Recheck the existing finite-state method against exhaustive short sequences.
Check a second dynamic program independently for the compact explanations.

Count the retained unit/time/status atoms and archive their numeric forced
bounds and physical parameters. Explicitly report that deriving those bounds
can use all 168 hours and all generators. Do not equate explanation sparsity
with input-data compression or prove a general minimum-memory theorem from it.

## Interpretation rules

- A verified positive control plus a rejected permutation establishes a paired
  counterexample in this model. It does not establish field performance.
- If no permutation is rejected, report the pilot as inconclusive or negative;
  do not change seeds/horizon/means silently.
- Strict equivalent-unit weekly-energy pooling is audited separately over the
  eight original weeks. Its relaxed positive results must not be described as
  network feasibility. If pooling removes rejections, revise the interpretation
  of coordinate-specific targets rather than hide that outcome.
- This pilot must precede any claim about reliable compact summaries. The
  existing candidate manuscript and published release remain reference outputs.
