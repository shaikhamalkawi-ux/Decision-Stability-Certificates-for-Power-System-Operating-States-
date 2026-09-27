# Strict nominal witnesses: bounded design assessment

Status: design and read-only structural inspection only. No new shortest-path bounds, separating candidates, rational repair, optimizer calls or model changes have been performed. The closed expanded-model evidence remains unchanged.

## What the existing audit settles

The completed `nominal_balance_audit` considered all 672 hours across the original January, April, July and October references. Every aggregate-minus-sum-of-nodal balance combination has 15 nonzero angle coefficients when stored binary64 coefficients are interpreted exactly. None separated against the original column box in either orientation, strictly or after uniform finite-bound expansion. Its independent integer-arithmetic replay passed. This is a null diagnostic: it proves neither strict feasibility nor strict infeasibility.

The nonredundancy matters to attempted strict repair. A residual of order roundoff in a nearly redundant equality can impose a substantial extra restriction on the angle pattern after division by its small coefficients. It is therefore unsafe to assume that rounding a saved point more carefully will make all original equalities exact.

## Actual archived branch structure

A read-only inspection of the four already audited model archives verified the 15 existing frozen input bindings and inspected their sparse branch rows and column bounds. Each week has 6,384 branch rows: 38 per hour. Each branch row has exactly two nonzero, exactly opposite coefficients, on angle columns within the same hour, with symmetric positive finite row limits. All hours and all four months share the same branch coefficient/limit block.

Every hour has one angle column pinned exactly to zero: **bus index 12, bus ID 113**. It is not index zero. The first inspection stopped at an over-specific index-zero assertion; the corrected read-only inspection discovers the pinned coordinate from bounds and confirms it across all four archives. No new certificate or model computation occurred in either inspection. Future source must discover and validate the pin rather than inherit a guessed index.

## Recommended first diagnostic: original-row path certificates

This is a cheaper and more interpretable next step than a full rational fixed-commitment LP. A prospective protocol can retain all original 672 hour/week cases and both existing signed balance combinations. It must archive all null outcomes and distinguish strict from uniformly expanded results. A separating result would describe an inconsistency of the exact archived representation, not physical network infeasibility.

Write an original branch row as `b_e (theta_u - theta_v)` with limits `[-R_e, R_e]`. Interpret every coefficient and endpoint as its exact binary64 rational value. A path from the reference bus to bus j supplies rational row multipliers `p_je` whose combined coefficients equal `theta_j - theta_ref`. Its strict difference bound is the sum of `R_e / |b_e|`. Under uniform expansion the edge contribution is `(R_e + tau) / |b_e|`; the reference column itself lies in `[-tau, tau]`.

For a simple finite design, select one path per bus using exact strict weights `R_e / |b_e|`, deterministic row-ID tie breaking, and no outcome-based choice. Reuse those paths for both strict and expanded checks. Strict weights target the unresolved strict question; checking the same paths at tau is still sound without asserting they minimize expanded path length. A second path metric would be a distinct candidate family and should only be added prospectively, not after a null result. The common 38-edge block permits one tree to be reused after exact per-archive block equality checks.

Let the signed original aggregate-minus-nodal combination be `q^T theta = beta`, with original multiplier vector y0. For every non-reference coordinate add the branch combination `-q_j p_j`. The resulting original-row multiplier vector has angle coefficients zero away from the reference and reference coefficient `s = sum_j q_j`. This is an exact cancellation identity that must be verified against the original sparse matrix. All newly introduced multipliers must be stored as numerator/denominator pairs; generally they cannot be encoded without loss as binary64 `value_hex` entries.

With merged branch multiplier `z_e = -sum_j q_j p_je`, its strict gap is

```text
g0 = beta - sum_e R_e |z_e| - max_ref(s theta_ref).
```

For these archives the strict reference maximum is zero. The expanded gap, computed directly on original rows and the original expanded reference-column box, is

```text
g_tau = beta - tau ||y0||_1
        - sum_e (R_e + tau) |z_e| - tau |s|.
```

This is exactly the ordinary signed-row/finite-box Farkas calculation for the assembled rational multiplier vector. The remaining column coefficients must all be checked as zero, not dropped by a numerical threshold. If graph construction or exact cancellation fails, classify that diagnostic as unsupported/invalid rather than silently altering the matrix.

There is a useful comparison with a path bound that already retains the shared reference coefficient `s`, but the equality needs care. Combining paths can cancel shared-edge multipliers. Thus the assembled gap equals that conservative sum-of-paths gap plus the explicit nonnegative improvement

```text
sum_e (R_e + tau) [sum_j |q_j p_je| - |sum_j q_j p_je|].
```

Use `R_e` for the strict version. This comparison already keeps one correlated reference-angle term. A comparison against independently bounded individual angles has an additional reference cancellation gain, given below. A direct equality between the assembled gap and the uncorrected path-box gap is generally false. Archive the unmerged contributions, merged exact multipliers, cancellation gains and final original-matrix arithmetic, so a second implementation can verify both representations independently. For ordinary derived individual angle boxes, intersecting path bounds with existing boxes is sound, but do not substitute those tighter boxes into a certificate without their derivation.

### General identity with the reference term and original-box choices

For any interval `[l,u]`, define its support function `h(a) = a*u` when `a >= 0`, and `h(a) = a*l` otherwise. Let `h_e` use the branch row's strict or expanded endpoints, `h_j` the corresponding original angle-column endpoints, and `h_r` those of the discovered reference column. These are the actual archived intervals, not invented equality rows. In the expanded model the reference column has support `h_r(a) = tau*|a|`; strictly it has support zero.

Let S be the non-reference coordinates for which the proposed diagnostic chooses a path-derived bound, and T the other non-reference coordinates left with their original column boxes. A simple all-path design has S equal to every non-reference coordinate. If a design intersects with original boxes, it must archive each selected side/choice and the resulting S and T; it cannot continue using an all-path formula. Set

```text
w_e = sum_{j in S} q_j p_je,
s_S = q_ref + sum_{j in S} q_j,
beta_tau = beta - tau ||y0||_1.
```

The branch multipliers added to the original row combination are `-w_e`. Its remaining column coefficients are exactly `s_S` at the reference and `q_j` for j in T. The original-row assembled gap is

```text
G_assembled = beta_tau - sum_e h_e(w_e)
              - h_r(s_S) - sum_{j in T} h_j(q_j).
```

The conservative gap obtained by separately bounding each chosen variable is

```text
G_independent = beta_tau - h_r(q_ref)
                - sum_{j in S} [h_r(q_j) + sum_e h_e(q_j p_je)]
                - sum_{j in T} h_j(q_j).
```

Their exact difference is

```text
G_assembled - G_independent
  = sum_e [sum_{j in S} h_e(q_j p_je) - h_e(w_e)]
    + h_r(q_ref) + sum_{j in S} h_r(q_j) - h_r(s_S).
```

Both bracketed edge terms and the reference term are nonnegative by subadditivity of interval support functions. For the actual symmetric expanded intervals this becomes

```text
sum_e (R_e + tau) [sum_{j in S}|q_j p_je| - |w_e|]
  + tau [|q_ref| + sum_{j in S}|q_j| - |s_S|].
```

This includes the original reference coefficient `q_ref`. The reference gain vanishes at the strict zero pin. For S containing all non-reference coordinates, its expanded form is `tau*(sum_j|q_j| - |sum_j q_j|)`. Keeping this term avoids a second false equality even when paths share no edges.

For these symmetric branch bounds, adding `-w_e` to a signed lower-row combination contributes exactly `-h_e(w_e)`. The same support-function argument also handles asymmetric finite branch bounds without assuming symmetry. A standalone exact replay must evaluate the combined original row multipliers and remaining original column coefficients directly, and then compare that result with these identities. Reference-column support may equivalently be written as explicit bound inequalities, but no nonexistent reference row should be claimed as an archived matrix row.

The existing exact expanded positive references also provide a consistency check: a valid expanded negative for the identical full model would contradict a verified positive and must trigger a hard review stop. It would not be a publishable new physical finding. Strict-only separation can coexist with expanded feasibility.

This diagnostic needs no numerical optimizer. On a 24-node, 38-edge graph, exact path construction and the fixed small row combinations should be modest compared with a rational full-week LP; rational numerator growth and repeated certificate serialization should still be bounded and reported. Source/protocol review and a finite frozen input/case list should precede execution. No implementation or execution is authorized by this assessment.

## If the path diagnostic is null

A null result would leave strict feasibility unresolved. The next meaningful positive route is a separately frozen **fixed original binary schedule** feasibility problem with the original matrices and endpoints interpreted rationally. Fixing U/Y/Z eliminates integer search, but retains every physical row, hydro/availability bound and any original global fossil cap. Hourly DC blocks can help construct rational candidates, while their combined energy must still satisfy the complete weekly cap. Native on/on ramp redundancy must remain proved or its constraints retained.

A rational reconstruction can hold selected free dispatch coordinates at rational values and solve exact equality systems for the remaining coordinates, or use an exact LP method with rational primal/dual evidence. Either approach must handle the additional nonredundant aggregate relation explicitly, finite bounds and active constraints; simply dropping the aggregate equality, projecting onto the nodal system or changing a right-hand side changes the model. Numerical bases may be useful proposals, but a successful numerical solve is not a strict certificate. Denominator growth and ill conditioning can make exact reconstruction expensive or leave the selected schedule infeasible.

The decisive positive evidence is a rational vector satisfying **all** unchanged nominal rows and boxes exactly, with the original binary states unchanged, plus an independent rational membership replay. Such a vector may have non-dyadic denominators and cannot generally be stored losslessly as a float64 NPZ point. It needs a new explicitly rational point format and a separately reviewed checker path; the frozen existing kernel and historical witnesses should not be edited. A failed reconstruction is not nominal infeasibility. A fixed-schedule exact negative would exclude only that schedule unless its proof also applies without the fixing constraints.

## Physically consistent assembly is a separate research arm

If strict feasibility of the existing representation cannot be established, a principled new assembly can derive nodal balance and aggregate balance from one exact incidence/branch construction and one exact nodal load vector. For example, build the rational susceptance Laplacian from shared branch coefficients so row/column conservation identities hold algebraically, and define any redundant aggregate right-hand side as the exact sum of nodal quantities. The declared meaning of native decimal inputs and of divisions must be fixed in advance.

That would be a new model, even if its numeric changes are tiny. It requires new hashes, a transparent coefficient/RHS difference inventory, new positive and negative evidence, and explicit comparison with the old results. It must not replace the old archive or retroactively relabel expanded witnesses as strict. The current evidence does not establish that this alternative will preserve every negative case, every cap threshold or every energy interval.

The recommended order is therefore: frozen solver-free path refinement; if still unresolved, one bounded fixed-schedule rational feasibility attempt with exact acceptance; separately evaluate a physically consistent assembly only as a new arm. The decisive missing fact remains strict membership or a valid strict infeasibility certificate for the relevant unchanged model.
