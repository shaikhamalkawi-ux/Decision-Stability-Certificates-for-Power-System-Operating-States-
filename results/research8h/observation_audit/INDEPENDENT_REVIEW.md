# Independent numerical and implementation review

Verdict: **PASS; no defect identified.** A separate reviewing agent independently reconstructed native arrays, checked the implementation and protocol, and compared the emitted arrays and all 16 archived Markov permutations. The reviewer made no edits and ran no optimization.

The independently reconstructed full exogenous array (168 x 106) matches the emitted array exactly; its contiguous little-endian binary64 array-byte SHA256 is `20a4e4c6bee167af4c27e3e732d718b23c270e9fe42c0ae1d039d6d1dcdcf643`. The corresponding aggregate array (168 x 83) hash is `44d438fe9bc9e701904d840332846d4905aeb59df9945456b3730970446ef256`. These are array-byte hashes, not compressed NPZ-file hashes.

For both exogenous definitions the reviewer reproduced 168 distinct states, zero repeats, 167 distinct bigrams, zero predecessor/successor branching, and zero self-loops. No negative zeros occur; exact numerical and byte class counts agree. Exogenous keys exclude timestamps, source-hour/native-row identifiers, dispatch P and commitment U. Sorting state IDs by byte keys avoids leaking original chronology through first-occurrence numbering. Reconstruction follows sole outgoing edges from the endpoint and consumes all edges, so the stated uniqueness proof is valid.

The reviewer reproduced the endogenous-U results: 48 states, 20 repeated classes, 140 observations in repeated classes, 120 repetitions beyond first occurrences, 92 distinct bigrams, 20 predecessor and 20 successor branching states, maximum distinct successor/predecessor degree 8, and 79 self-loop transitions. All 16 archived Markov orders preserve U bigrams and endpoints while changing the U sequence; none preserves either exogenous bigram multiset. No Euler-trail count is inferred.

Interpretive boundary: injectivity of this particular raw-data week makes exact labelled bigrams lossless here. It does not refute a worst-case finite-alphabet theorem, because repeated numeric vectors can encode finite symbols within a real-valued domain. Endogenous-U ambiguity is distinct from input-only observational ambiguity and by itself proves no operational infeasibility.
