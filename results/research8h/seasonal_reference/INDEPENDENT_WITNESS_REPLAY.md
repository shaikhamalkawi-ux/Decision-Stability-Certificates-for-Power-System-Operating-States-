# Independent archived witness replay

## January: PASS

A separate reviewer independently loaded the saved January CSV candidates and native inputs without optimization or file edits. The CSV coordinates matched the archived returned-vector NPZ exactly. The maximum checked residual was 2.5510e-11 MW in provided-angle nodal balance, below the declared 1e-5 tolerance. All fixed-hydro, availability, rounded-commitment coupling, native on/on ramps, nodal balances, branch ratings, angle-domain and reference-angle checks passed.

The reviewer checked 300 changed-status runs and found zero minimum-residence violations. Derived startup/shutdown indicators matched the saved values within 3.7896e-14. Maximum branch loading was 1.0 and maximum absolute angle was 0.8000712033 radians.

The independently summed 23-unit fossil electrical energy was 22964.941239556443 MWh, exactly matching the reported value. The exact rational sum of the binary64 dispatch values is `1654798412944827657145 / 72057594037927936` MWh. This rational energy sum is an audit of saved values, not an exact feasibility proof for all floating-point network equations.

January is a verified feasible reference. The solver's 1.5158345894% remaining MIP gap leaves optimality unresolved. Results for any other month must be read from its own archived status and verification; this January replay makes no claim about other months.
