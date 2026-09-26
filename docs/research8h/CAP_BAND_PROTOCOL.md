# Arithmetic cap bands and order blind error lower bounds

This solver-free addendum is derived after the completed and independently replayed January energy bounds. It reuses exactly those two cases and adds no empirical sample or new optimization. The claims are elementary consequences of existing witnesses and lower bounds, not a new information-theoretic method.

Let tau = Fraction.from_float(1e-5). For each fixed target let U_I be the exact fossil energy of the verified identity witness, and L_T the certified lower bound for the target's uncapped model with all finite bounds expanded by tau. Adding the nominal cap row c^T x <= B makes its expanded version c^T x <= B + tau. Hence for every cap B satisfying

    U_I - tau <= B < L_T - tau,

the identity is feasible and the target is infeasible in their respective expanded original-binary models. All noncap bounds remain unchanged. The interval has width L_T-U_I; the original integer cap23195 must lie inside it. This is valid for any representable binary64 cap value in the interval; the mathematical parameterized family can also be defined for exact rational caps. A binary64 implementation must compare the actual stored cap fraction, not the decimal string alone.

The program records authoritative rational endpoints and a CLOSED six-decimal subinterval lying inside this left-closed/right-open band. The lower displayed endpoint is rounded upward. The upper displayed endpoint is rounded downward and, if exactly equal to the excluded endpoint, reduced by one display unit. This is inward rounding for an admissible-cap range, not outward rounding of an uncertainty enclosure. It also reports the exact first and last integer caps and counts, without running any of them.

The observation supplied to an order-blind rule consists of the complete joint hourly multiset, the fixed first/last48 input packages, the unchanged physical model and the common cap. These observations are identical for each identity/target pair. A deterministic binary classifier restricted to that observation must give one answer to both and is wrong on at least one; it may instead report unresolved. This is a worst-case statement on the declared pair, not a population error rate or a claim about methods retaining additional chronology.

For uncapped optimal fossil energies E_I* and E_T*, the verified bounds establish E_T* - E_I* >= L_T-U_I > 0. Any common deterministic numerical estimate v based only on those identical observations has

    max(|v-E_I*|, |v-E_T*|) >= (L_T-U_I)/2.

This follows from the triangle inequality. Both optimum values are finite because uncapped binary witnesses exist and all dispatch coordinates have finite bounds; a finite union of closed bounded feasible polytopes attains its optimum. The lower bound concerns absolute error in fossil electric generation, not computational cost, raw-information bits, emissions, or out-of-sample generalization. It does not measure the observed error of a particular deployed method.

Freeze and rehash the source, protocol, refined rational bounds and independent review before/after arithmetic. Check the interval endpoints symbolically, integer endpoint membership and immediately adjacent integer exclusion, the preserved cap23195, and the exact half-gap. Preserve all prior evidence without edits.
