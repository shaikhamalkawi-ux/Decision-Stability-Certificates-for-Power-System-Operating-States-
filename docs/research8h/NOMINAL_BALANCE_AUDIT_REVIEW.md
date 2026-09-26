# Nominal balance audit: independent preflight

Verdict: PASS for the proposed read-only arithmetic audit; no mathematical or implementation blocker found. This review precedes execution and makes no claim about the as-yet uncomputed outcomes. No optimizer was launched by this reviewer and no archived model was changed.

Reviewed bindings:

| Input | SHA-256 |
|---|---|
| `src/research8h_nominal_balance_audit.py` | `956232a675ff9446e652753395a723a5e1823e600f7563cfa224e7a56b938db8` |
| `docs/research8h/NOMINAL_BALANCE_AUDIT_PROTOCOL.md` | `918a28a4fc07c7f65b890fe3c9aa85323bb0e3f73438dc29600332015706e4df` |
| `src/research8h_standalone_verify.py` | `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f` |

The code fixes January, April, July and October and all 168 hours in advance. Independent parsing of each original row-metadata archive found 34,680 sequential, unique row indices, integer hour labels and, for every hour, exactly one aggregate-balance row and 24 nodal-balance rows with distinct bus identifiers. Therefore the multiplier dictionary cannot silently collapse duplicate selected row indices in these supplied inputs. The runner additionally checks the selected rows are equalities and validates the complete finite-column-box CSR model through the standalone reader.

For each hour the exact binary64-rational combination is `c = A_aggregate - sum(A_nodal)` and `b = lower_aggregate - sum(lower_nodal)`. The sign-dependent column endpoints correctly compute the minimum and maximum of `c*x` over the nominal box. The equality is impossible within that box exactly when `b` lies outside this closed interval. The two original-row multiplier orientations test its two strict-separation directions, and the runner asserts agreement between the interval test and the independent ray calculation.

The expanded check retains the original 25 nonzero row multipliers. It therefore subtracts `tau * (25 + ||c||_1)` from the nominal ray gap; it does not incorrectly expand only the already-combined equality. The standalone checker also obtains the same result directly from widened row and column endpoints. Its single call at the exact binary64 value of `1e-5` reports both the unexpanded and expanded gaps, fulfilling the protocol's two model comparisons without a second redundant call.

The audit binds its source, protocol, checker and all twelve matrix/bounds/metadata inputs before calculating results, creates outputs exclusively, and rechecks every frozen input at completion. It does not overwrite original reference files. These are fresh input bindings, not an additional validation against the historical reference manifest; historical provenance is covered by the earlier prepared-archive reviews.

A nonzero coefficient or right-hand-side difference establishes failure of exact algebraic redundancy, not infeasibility by itself. A strict-only separating combination establishes an exact encoding obstruction in the nominal binary64 model, not a physical temporal obstruction and not failure of the uniformly expanded model. Conversely, nonseparation of these selected combinations is not a feasibility proof. Any expanded separation for a model with a verified expanded positive point would require diagnosis before reporting either claim; the script preserves all per-hour evidence and does not automatically repair such a discrepancy. The exhaustive arithmetic audit supplies evidence for this selected balance identity only, not a general numerical-conditioning guarantee.

Review procedure note: an initial read-only Node scan timed out and a shell one-line read probe failed at command parsing. Neither produced audit results or ran an optimizer. The successful independent roster check used one-pass parsing; these exploratory review failures are not audit executions or experimental retries.
