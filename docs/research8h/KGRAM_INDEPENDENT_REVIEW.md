# Independent review: finite-window histogram theorem candidate

Status: **theorem candidate with an independently checked proof argument**.
This review assesses internal validity under the assumptions below. It does not
establish novelty, publication priority, or implications for every temporal
aggregation method. The initial construction was supplied by the research agent;
the parent requested the dispatchable thermal extension.

## Precise claim and assumptions

Fix any positive integer k. There are two equal-length sequences of exogenous
hourly load/renewable-availability packages with identical counts of every
contiguous word of lengths 1 through k, identical length-k prefixes and suffixes,
and identical plant parameters and aggregate carbon/thermal-energy budget, yet
one admits a schedule and the other does not.

The model has one thermal unit with binary status u, output a*u <= p <= u for
any fixed 0 < a <= 1, minimum up time two hours, minimum down time one hour,
and nonbinding ramps. Its history is initially mature OFF. A second generator
is curtailable renewable, with 0 <= q <= availability. Balance is p+q=load.
There is no storage, network, load shedding, target slack or demand adjustment.
Thermal emissions have coefficient one and renewable emissions coefficient zero,
so the shared carbon budget is a cap on total thermal generation. All time steps
have unit duration. The final zero-load suffix forces the thermal unit off, so
the result does not exploit a truncated final ON run.

The claim concerns **unordered exogenous k-gram counts**, not sequential access
to the input, exact representative-period boundary variables, unique timestamp
labels, or arbitrary sufficient statistics. The horizon grows with k. It does
not assert failure of all summaries on an already fixed short horizon.

## Construction and word-count proof

Use the alphabet Z=(load 0, renewable limit 0), F=(1,0), O=(1,1).
Write B_m=O(FO)^m. For positive integers r and k with k <= 4r, set

    x = Z^k B_(2r)   Z^k B_(2r)   Z^k
    y = Z^k B_(2r-1) Z^k B_(2r+1) Z^k.

Both horizons are T=8r+2+3k, with 4r occurrences of F, 4r+2 of O and 3k of Z.
The conservative choice r=k works for every k. The tighter choice
r=ceil(k/4) also works and reduces the necessary horizon.

For a word length j <= k, a window cannot touch two distinct nonzero blocks,
because the separating Z run already has length k. It cannot span both sides
of the shortest nonzero block either: that block has length 4r-1, so a window
including a Z on both sides would require length 4r+1. Thus every relevant
window is internal to a Z run, internal to one alternating block, or crosses
one boundary. Boundary prefixes and suffixes of the alternating blocks agree
to the needed length and their counts do not depend on m.

For internal windows of length 2s in B_m, the two alternating words each occur
m-s+1 times. For length 2s+1, the O-starting and F-starting words occur m-s+1
and m-s times. These expressions are nonnegative for all four blocks when
j <= 4r, including the zero counts at the shortest-block endpoint. Their sums
depend only on the combined m=4r. This proves all required histogram equalities.

The first differing order for this family is 4r+1: the word Z B_(2r-1) Z
occurs in y and cannot occur in x. This sharpness statement describes this
construction, not a universal smallest sufficient window length.

## Operational lower bound and constructive witness

At F, balance and zero renewable availability force p=1 and u=1. At Z, balance
and a>0 force p=u=0. At O, an ON unit can use p=a, with renewable q=1-a;
an OFF unit uses p=0 and q=1.

Each forced F must have an ON neighboring O, or it would be an isolated ON
hour and violate minimum up time two. In B_m, select the first, third, fifth,
and subsequent odd-indexed F occurrences. Their neighboring O pairs are
disjoint. They force at least ceil(m/2) units of optional commitment. Therefore

    E_min(B_m) >= m + a*ceil(m/2).

This bound is attained: pair consecutive F occurrences using their shared O;
if one F remains, turn on its final neighboring O. The resulting ON runs have
length three or two. Every separating OFF interval has at least one hour.
Dispatch the selected O hours at a. Hence the lower bound is the exact minimum.

It follows that

    E_min(x) = 4r + 2r*a,
    E_min(y) = 4r + (2r+1)*a.

The common cap C=4r+(2r+1/2)*a admits x and rejects y, with an exact gap a/2
on either side. This cap avoids relying on a fragile named-unit equality.
Alternatively, an exact thermal-energy target E_min(x), together with the
renewable energy determined by common total demand, gives the same rejection.

The lower bound also holds in the usual continuous startup relaxation. At a
forced F hour t, the transition identity and nonnegative shutdown imply
y_t >= 1-u_(t-1). Minimum up time two implies
u_(t+1) >= y_t+y_(t+1) >= y_t. Thus u_(t-1)+u_(t+1) >= 1.
Summing the disjoint odd-F inequalities and p_O >= a*u_O produces the same
energy bound without integrality. The checker cancels the corresponding
linear coefficients and checks the negative right-hand side using exact
rational arithmetic. Symbols y and z in that algebra denote startup and
shutdown, not the two words; the renewable dispatch is q. Expressing the cover
inequality as q_left+q_right >= 1 would have the wrong sign for renewable q.

## Small decisive example

Take k=3 and r=1, so T=19:

    x = ZZZ OFOFO ZZZ OFOFO   ZZZ
    y = ZZZ OFO   ZZZ OFOFOFO ZZZ.

The shared trigrams are ZZZ:3, ZZO:2, ZOF:2, OFO:4, FOF:2, FOZ:2, OZZ:2.
With a=1, minimum thermal energy is 6 versus 7, and cap 6.5 separates them.
With genuinely dispatchable a=1/2, it is 5 versus 5.5, and cap 5.25 separates
them. Thus the input window can already be longer than the local two-hour
dwell rule and still miss the aggregate feasibility distinction.

## Independent checking and limits

The executable is `src/research8h_kgram_check.py`; it uses only Python's standard
library. A run-age dynamic program is checked against independent forward-dwell
enumeration. The base run passed 9,841 complete words of lengths 0 through 8,
enumerating 87,381 instantaneously admissible binary schedules; 41 block-size
formula checks; six exhaustive paired examples totaling 35,328 schedules;
64 conservative-family cases; 132 tighter parameter cases; and 16 checks of the
first distinguishing order. Initial and terminal conventions are explicit.

The base run's exact original source is preserved at
`results/research8h/kgram_check/base_source_snapshot.py`, with its original frozen
SHA256. The dispatchable extension has a separate prospective freeze and results
under `results/research8h/kgram_check/dispatchable/`; its costs are integer-scaled,
so a=1/2 uses cost 2 on F and 1 on an ON O, without floating-point comparisons.
That extension passed all 9,841 weighted generic words and 87,381 enumerated
schedules, 256 parameter cases covering a=1/4, 1/2, 2/3 and 1 with k through 64,
and six exhaustive paired examples totaling 35,328 schedules. Every constructed
positive dispatch and negative rational lower-bound calculation passed. The
19-hour a=1/2 witness, dispatch, shared trigrams and exact coefficient-cancellation
certificate are in `dispatchable/example_k3_r1_a_half.json`. Reported checking
times were 25.479 seconds for the base run and 8.111 seconds for the extension.

No counterexample to the proof was found under the stated assumptions. Essential
conditions include a>0, the separating zero-load hours, and the global budget.
At a=0 the OFF separators and positive energy gap disappear. With minimum up
time one both words require only the common forced-F energy. Without the cap,
both words are feasible. The unbounded-horizon quantifier also matters.

This is not an impossibility result for bounded sequential state: a small
weighted finite-state dynamic program computes these minima. It is specifically
the loss of order in finite window histograms that creates indistinguishability.
The elementary counting/cover proof and finite-state viewpoint require a prior-
art assessment before any novelty claim. A theorem candidate on this synthetic
model is also not evidence of field performance or direct failure of Auer et
al.'s representative-period formulation.
