# Novelty decision: fixed-window statistics under a global resource cap

Drafted 26 September 2026, approximately 20:12 UTC. This is one theorem candidate with a complete elementary construction, not a novelty certification. No root experiment was rerun and no implementation was added by this reviewer. Independent enumeration and dynamic-programming checks are assigned to the checker agent.

## Decision

Pursue the following narrow statement:

> A fixed minimum-up time does not imply that any fixed-length histogram of complete exogenous time windows is sufficient to decide chronological feasibility under a cumulative emissions or energy cap.

The quantifier is the useful part: **for every finite window length**, an indistinguishable feasible/infeasible pair exists while the physical minimum-up time remains two hours. This is substantially sharper than equal means or equal first-order transition counts. It also avoids dependence on an exact named-generator energy equality: the separating requirement can be an ordinary common upper bound on total emissions.

This is a statement about information discarded by a particular observation map. It is not a claim that UC needs unbounded sequential state, that no compact exact representation exists, or that the underlying combinatorics or Farkas proof technique is new. Its value as an original energy-systems result remains to be established against the sources below.

## Precise model and observation

Use one bus, one thermal generator, one curtailable renewable source and one-hour intervals. Thermal dispatch is \(p_t=u_t\), with \(u_t\in\{0,1\}\): the thermal unit produces exactly 1 MW when on. Its minimum-up time is two hours and minimum-down time is one hour. Ramps, reserves and network restrictions are absent or nonbinding. The initial unit is mature off. Inputs include forced-off periods at both ends, so no truncated on-run or terminal convention is used to create the difference.

Renewable dispatch satisfies \(0\le v_t\le a_t\), and balance is
\[
u_t+v_t=d_t.
\]
No load shedding, dumping or storage is allowed. The complete varying hourly input package is \((d_t,a_t)\), drawn from a fixed alphabet:

| Symbol | Demand \(d_t\) | Renewable upper bound \(a_t\) | Thermal implication |
|---|---:|---:|---|
| \(Z\) | 0 | 0 | Forced off |
| \(F\) | 1 | 0 | Forced on |
| \(O\) | 1 | 1 | Either off or on |

The thermal emissions rate is one normalized unit per MWh and renewable emissions are zero. Impose the common cumulative cap
\[
\sum_t u_t\le B.
\]
An energy cap or a unit generation-cost cap gives the identical mathematics. This is an operational service requirement with a resource budget; it is not an unconstrained adequacy result.

For fixed \(k\ge1\), define \(\Phi_k(w)\) as the counts of **every complete input word of every length \(1,\ldots,k\)** occurring contiguously in \(w\), together with its first and last \(k\) input symbols. Also supply the same \(T,B\) and plant data to the decision procedure. These counts retain complete joint packages; no independent shuffling of load and renewable variables is involved.

Equal factor counts through length \(k\) are already called *k-abelian equivalence* in combinatorics on words. The explicit endpoint data here is included for clarity and is stronger than necessary for sufficiently long words. This definition is not proposed as new. See Karhumäki, Saarela and Zamboni, Section 2, [primary article](https://cyber.bibl.u-szeged.hu/index.php/actcybern/article/download/3921/3905), DOI [10.14232/actacyb.23.1.2017.11](https://doi.org/10.14232/actacyb.23.1.2017.11).

## Candidate theorem

For every \(k\ge1\), choose \(r=k\), define
\[
A_m=O(FO)^m,
\]
and construct
\[
x_k=Z^k A_{2r}Z^k A_{2r}Z^k,
\qquad
y_k=Z^k A_{2r-1}Z^k A_{2r+1}Z^k.
\]
Both instances have
\[
T=8r+3k+2,\qquad
B=6r+\tfrac12,
\]
and exactly the same physical parameters.

Then:

1. \(\Phi_k(x_k)=\Phi_k(y_k)\).
2. \(x_k\) is feasible.
3. \(y_k\) is infeasible.
4. Their minimum possible thermal energies are exactly \(6r\) and \(6r+1\), respectively.

Therefore there is no classifier depending only on \(\Phi_k,T,B\) and these fixed plant parameters that is correct on all horizons. In particular, no finite window length chosen solely as a function of the maximum native dwell time can guarantee sufficiency for this model class. A randomized classifier receiving these identical observations cannot have error below one half on both members of a uniformly chosen pair.

The safe family \(r=k\) is sufficient for the theorem. The tighter range \(k\le4r\) appears valid by the counting argument below and is being checked separately; the general claim does not depend on that improvement.

## Proof

### A. Observational equivalence

Both words have \(4r\) occurrences of \(F\), \(4r+2\) of \(O\), and \(3k\) of \(Z\). Their first and last \(k\) symbols are \(Z^k\).

Consider a window of length \(\ell\le k\). A window internal to \(A_m\) is alternating. For \(\ell=2s\), each of the two alternating patterns occurs \(m-s+1\) times. For \(\ell=2s+1\), the pattern beginning with \(O\) occurs \(m-s+1\) times and the one beginning with \(F\) occurs \(m-s\) times. These formulas are nonnegative for the safe parameter family.

Consequently, all internal counts depend affinely on \(m\). Summing over two blocks with total index \(4r\) gives identical counts for the even/even and odd/odd constructions.

All block prefixes and suffixes of length at most \(k-1\) are the same alternating strings. A window meeting a \(Z\)/alternating boundary therefore contributes the same pattern counts on both sides. No window of length at most \(k\) spans two boundaries: the \(Z\) separators have length \(k\), and the shortest alternating block has length \(4r-1\ge k\). Windows internal to the three \(Z^k\) blocks are identical. These cases exhaust all windows and establish equality of every count in \(\Phi_k\).

### B. Minimum energy of one block

Within \(A_m\), all \(m\) positions labeled \(F\) must have thermal status one. Let \(b_0,\ldots,b_m\) be thermal statuses at the \(m+1\) positions labeled \(O\), ordered from left to right. These are not renewable dispatch variables.

To avoid an isolated thermal on-hour at the \(j\)-th forced-on position, minimum-up time two requires
\[
b_{j-1}+b_j\ge1,\qquad j=1,\ldots,m.
\]
Select the inequalities for odd \(j\). Their left sides involve disjoint pairs of \(O\) positions, giving
\[
\sum_{i=0}^{m}b_i\ge\lceil m/2\rceil.
\]
Thus every valid schedule consumes at least \(m+\lceil m/2\rceil\) thermal MWh.

The bound is attained. For \(m=2s\), turn on the \(O\) positions between forced-on pairs \((F_1,F_2),(F_3,F_4),\ldots\). This creates on-runs of length three, separated by off-runs of length one. For \(m=2s+1\), do the same for the first \(2s\) forced-on positions and turn on the last \(O\) after the final \(F\), creating one final on-run of length two. All other optional positions stay off and use renewable output one.

The \(Z\) blocks force separation and satisfy the one-hour minimum-down rule. They also prevent inherited or terminal states from changing this bound.

### C. Separation by the shared cap

Apply the block formula:
\[
E_{\min}(x_k)=2(2r+r)=6r,
\]
while
\[
E_{\min}(y_k)
=(2r-1+r)+(2r+1+r+1)=6r+1.
\]
The common cap \(B=6r+1/2\) lies strictly between them. The exhibited schedule makes \(x_k\) feasible, and the lower bound rules out every schedule for \(y_k\).

This is not merely a failed replay of a particular commitment. It is an all-schedules lower bound.

### D. Numerical and LP interpretation

All coefficients are integers and the cap is a half-integer, giving a half-unit separating margin. That does not establish robustness to arbitrary perturbations of hourly inputs or thermal minimum output. Only cap perturbations of magnitude strictly below one half preserve both conclusions.

The block lower bound sums valid linear inequalities on disjoint optional positions; it does not use rounding of a fractional sum. In the usual startup formulation, \(s_t\ge u_t-u_{t-1}\) and \(u_{t+1}\ge s_t\) imply \(u_{t-1}+u_{t+1}\ge u_t\). At a forced-on hour this gives the displayed covering inequality. The argument can therefore produce an LP infeasibility certificate for a relaxation containing these implications. An arbitrary weaker UC relaxation need not expose that proof. Verify the actual row formulation before claiming this extension.

## Small decisive executable falsification

Use the following 19-hour pair, \(k=3,r=1\), which fits the tighter counting range. This deliberately preserves windows longer than the two-hour minimum-up time:

\[
x=ZZZ\;OFOFO\;ZZZ\;OFOFO\;ZZZ,
\]
\[
y=ZZZ\;OFO\;ZZZ\;OFOFOFO\;ZZZ,
\qquad B=6.5.
\]

Their common trigrams and counts are:

| Trigram | Count |
|---|---:|
| ZZZ | 3 |
| ZZO | 2 |
| ZOF | 2 |
| OFO | 4 |
| FOF | 2 |
| FOZ | 2 |
| OZZ | 2 |

Counts total 17 as required; both have \(F=4,O=6,Z=9\). The common endpoints and trigram counts imply all shorter counts also agree, but the checker should verify them directly.

A decisive independent check needs no large MILP: enumerate the binary choices at the six optional positions, enforce all complete on-runs of length at least two, and calculate exact minimum thermal energy. The expected values are 6 and 7. A second small dynamic program should agree. Check the simple family for several \(k\), preferably including 1,2,3,4,8,16, and directly hash all window-count dictionaries. For the general safe family, use \(r=k\); use the small 19-hour example to test the tightened range separately.

Mandatory controls: with minimum-up time reduced to one, both minima become \(4r\); with the cap removed, both instances are feasible. If either control fails, the implementation is not testing the stated mechanism.

This is a small decisive test, not a claim that 19 hours is the globally smallest counterexample.

## Dispatchable-unit extension and resolution-versus-error bound

The fixed-output assumption is unnecessary. Fix any \(a\in(0,1)\) and replace \(p_t=u_t\) by \(a u_t\le p_t\le u_t\). Keep the same hourly packages and use \(p_t+v_t=d_t\). Forced-on positions have output exactly one, while a selected optional position can operate at \(a\), with renewable generation covering the remainder. Hence
\[
E_{\min}(A_m)=m+a\lceil m/2\rceil,
\]
and the pair has minima
\[
E_x=4r+2ra,\qquad E_y=4r+(2r+1)a.
\]
A common **emissions or thermal-energy upper cap** \(B=4r+2ra+a/2\) separates them. This does not impose exact named-unit targets. Startup/shutdown ramps must permit the displayed changes. At \(a=1/2,k=3,r=1\), the genuinely dispatchable operating range is [0.5,1] MW, the exact minima are 5 and 5.5 MWh, and the common cap is 5.25 MWh. The same covering inequalities, combined with \(p_O\ge a u_O\), give the weighted lower bound.

For the tighter construction \(r=\lceil k/4\rceil\), the window-count argument remains valid: no length-\(k\) window can include both boundaries of the shortest alternating block, since that would require length \(4r+1>k\). The affine internal counts remain nonnegative through length \(4r\). Thus
\[
T=8\lceil k/4\rceil+3k+2\le5k+8.
\]
Every estimator of optimal thermal energy that uses only the specified summary receives identical observations for the pair. By the triangle inequality, its worst-case absolute error is at least \(a/2\). For normalized energy per hour, the worst-case error is at least
\[
\frac{a}{2T}\ge\frac{a}{10k+16}=\Omega(1/k).
\]
This is a lower bound on attainable error for the restricted observation class, not an upper bound or a new generic estimation theorem. To guarantee normalized error at most \(\varepsilon\) on this class, a necessary condition is \(k\ge(a/\varepsilon-16)/10\) when the right side is positive. Other observations, an ordered scan or a full optimization oracle may avoid this restriction.

Repeat an entire pair \(J\) times: the identical zero endpoints make all seam counts match, and forced-off separators make block minima additive. Scale demand, renewable capacity and both thermal output bounds by \(C>0\), if desired. The absolute optimal-energy difference becomes \(JCa\); the intermediate-cap violation is \(JCa/2\). This shows that the absolute deficit can scale with system size or duration.

However, repetition and capacity scaling do **not** improve the relative gap. Relative to the feasible minimum it remains \(a/(4r+2ra)\); the cap deficit relative to the cap is \((a/2)/(4r+2ra+a/2)\), both \(O(1/k)\). With \(a=1/2,k=48,r=12\), these are approximately 0.833% and 0.415%. These are arithmetic properties of the construction, not measured operational impacts. A substantial practical claim still needs appropriate-scale independent cases or a stronger construction.

The independent checker reports that the small fixed-output construction passes, including the 19-hour case with minima 6 and 7. At the time this addendum was written, its dispatchable-extension checks were still being added. Keep that extension's mathematical derivation separate from the status of executed tests.

## Adversarial novelty and scope

The proposed contribution, if retained, is the explicit resource-constrained UC separation with fixed two-hour dwell and arbitrary input-window order. The proof is elementary. The currently inspected literature does not establish priority for it, and lack of a matching search result is not evidence of originality.

- **Known observation mathematics.** k-Abelian equivalence and its endpoint/factor-count characterization are established. The candidate must cite that literature and must not rename the concept as an invented information measure. The cited 2017 primary paper was read through its definitions and relevant preliminary results.
- **Known sequential solution.** Demassey, Pesant and Rousseau already combine finite-state sequencing with cumulative costs using weighted layered graphs. Their Sections 3-3.1 explicitly describe shortest-path filtering. A small weighted dynamic program can solve this example; the theorem does not contradict that. [Primary paper](https://hanalog.ca/wp-content/uploads/2016/09/DPR_CostReg.pdf), *Constraints* 11:315-333 (2006), DOI [10.1007/s10601-006-9003-7](https://doi.org/10.1007/s10601-006-9003-7).
- **Known temporal approximations.** Auer et al.'s 2026 revision addresses expected predecessor values across representative periods and relaxes boundary binaries. Our theorem concerns exact classification from exogenous factor histograms and does not refute their approximate method or its reported performance. [Primary preprint](https://arxiv.org/html/2510.18555v2).
- **Known certificate selection.** Fischetti et al. and existing IIS/Farkas literature already cover small conditional infeasible supports. The covering inequality is an explanation of the obstruction, not a new certificate-generation method. See the earlier literature audit.
- **Not the same Markov experiment.** The empirical pilot preserves transition counts of a reference witness's full commitment vector, an endogenous object. This construction preserves exogenous input windows. No implication in either direction should be asserted without an explicit mapping.

An unrestricted notion of “minimum information” would be vacuous here: the feasibility answer itself is one bit. A meaningful lower bound must restrict the observation/query class and account for how its values are obtained. The theorem restricts that class to unordered finite-window input statistics. It does not bound bits, distinguish every possible compression, or rule out an ordered scan with a small number of cost accumulators.

For adaptive refinement, the valid corollary is only this: a procedure that terminates using exclusively aggregate factor counts bounded by one horizon-independent maximum \(K\) still cannot classify both members of the corresponding indistinguishable pair. Positioned queries, block-parity information, unbounded window growth, ordered automata or a full feasibility oracle are outside that restricted observation class and may resolve it. IIS row selection after loading the full chronology is not evidence of a minimal data-acquisition procedure.

## Kill criteria and next decision

1. **Mathematical kill:** an independent exact schedule gives \(E_{\min}(y)\le6r\), a window-count mismatch occurs in the safe family, or the exhibited positive schedule violates a stated boundary/dwell rule. Repair the theorem or abandon it before manuscript use.
2. **Model kill for transfer:** the intended application excludes cumulative resource caps or hour-dependent renewable availability, or adds constraints that invalidate the exhibited positive schedule. Then this remains an illustrative mathematical example, not a theorem about that narrower application. The dispatchable-unit extension above removes any dependence on equal minimum and maximum thermal output. Do not silently alter assumptions to force transfer.
3. **Novelty kill:** a prior primary result already gives this UC/resource-budget construction or makes it an immediate, explicitly discussed specialization. Retain it as an attributed explanatory lemma, not the paper's central novelty.
4. **Scope kill:** any draft claim expands this result to all temporal summaries, all finite-state models, the endogenous Markov twins, or field operation. Such a claim is false or unsupported even if the theorem passes.
5. **Significance kill:** if the result remains only this simple artificial construction and adds no insight to held-out operational cases or summary design, it is unlikely to justify a major standalone novelty claim. A theorem plus reproducible benchmark evidence can be more useful, but neither guarantees publication.

Recommended immediate action: let the independent checker finish the exact tiny-instance tests, freeze the statement and proof if they agree, and present it as a candidate *limitation theorem for unordered local summaries under global resource constraints*. Decide the paper's novelty only after a targeted comparison with weighted-automaton and aggregation theory. Do not spend the remaining research session polishing a “minimum memory” claim that this construction does not support.
