# Independent theory review: selected dwell plus capacity cover

Status: **PASS_THEORY_AND_ASSEMBLY_SOURCE_CORRESPONDENCE; actual new prepared archive and implementation not yet admitted.** Reviewed proposal SHA256 `b6491923aec0912079afceae3e4d82e08574aafb9266a60302d99df1fce8b676`. This is source/theory review only: no scientific cover table, threshold, state recurrence, model construction, Julia import, solver or bound evaluation was performed. Producer files were not edited.

## Boundary correspondence

The inspected original assembly (`src/temporal_lp_certificate.py`, SHA256 `6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4`, lines32–86) uses exact binary U/Y/Z under the original mask, nominal boxes0..1, and initial Y0/Z0 upper boxes0. It skips temporal rows at hour0. At later hours the rows are

- U_t − U_(t−1) − Y_t + Z_t = 0;
- Y_t + Z_t ≤ 1;
- sum(Y_s, s=max(1,t−D_up+1)..t) − U_t ≤ 0;
- sum(Z_s, s=max(1,t−D_down+1)..t) + U_t ≤ 1.

All left-hand sides are integers when the original state coordinates are exact binaries. Since0≤tau<1, expanding each finite row endpoint bytau leaves these discrete relations unchanged. Expanded initial zero upper boxes still force binary Y0=Z0=0. Transition plus exclusion makes Y/Z the unique indicators of changes in U; they are not independent permissive labels.

A start at s≥1 appears in every up-window row through min(T−1,s+D_up−1), forcing U=1 there. A stop analogously forces U=0 through min(T−1,s+D_down−1). There is no represented start/stop before the horizon and no hour0 temporal row. Thus either U0 is mature; imposing an initial lock would incorrectly narrow this relaxation. There are no future rows beyond T−1, so any final residual lock must be accepted. Imposing completion of that lock would also incorrectly narrow the relaxation.

With the state interpreted **after serving the current hour**, a switch sets remaining lock toD_new−1. A positive lock allows only continuation and decrements byone; lockzero permits continuation or switching. This yields the exact selected-unit binary residence convention of the inspected assembly. Current-hour cost must be charged once at initialization and once for each later arrival state; the final state receives no extra tail cost. The layered recurrence remains valid even if a relaxed hourly cost is negative; it must not assume nonnegative arcs.

Source/raw metadata inspection confirms the retained labels separately:115_STEAM_3 and116_STEAM_1 each have up/down8/8 and PMin/PMax62/155MW;118_CC_1 has8/5 in the archived native specification and170/355MW. Its source CSV downtime is4.5; assembly applies ceil, so5 is the required archived convention. The coal units are at buses115 and116; no full-network interchangeability follows.

This correspondence is not a substitute for checking the actual frozen matrices. The new admission must establish exactly4×167×3=2004 selected temporal rows per world with the stated supports/endpoints, no extra selected hour0 temporal row, every selected state column's original mask and box, and the original-to-joint maps identifying all selected U/Y/Z in both worlds. Rows must be checked as exact CSR coefficients, not merely trusted labels or helper names. Dwell/native mismatch must yield UNSUPPORTED, not a changed automaton.

## Capacity and sum proof

Write F_it for fossil output in worldi/hourt. The previously admitted aggregate and nonfossil/fossil box premises give F_it≥d_it. The23 fossil upper rows give F_it≤sum_j b_j U_tj+23tau. Therefore the actual common remaining20-unit vector satisfies

b_R U_R ≥ max_i d_it −23tau−b_S s.

Its capacity is a nonnegative integer, so the stated exact rational ceiling followed by clipping below atzero is a necessary threshold. Its minimum-output sum is at least the complete exact cover-table optimum M_R at that threshold. The23 fossil lower rows separately give F_it≥a_Ss+a_RU_R−23tau. Conditioning three binary U values does not remove their three upper-row or lower-row tolerances: **both23tau terms are retained**. No20tau substitution is valid from conditioning alone.

Consequently F_it≥g_it(s)=max(d_it,a_Ss+M_R(h_t(s))−23tau) for both worlds and the same selected pattern. Each full common solution projects to a path in the selected residence relaxation. Summing its two hourly floors, then minimizing over all such paths, yields E0+E1≥L. Each original cap is one expanded row, so E0+E1≤2×23195+2tau. A strict excess L>that sum rejects every original common binary solution. Equality/nonexcess is a null. In particular, this does not imply a separate E_i≥L/2 bound.

An empty complete state graph is also a rejection only after every unreachable label and admissible transition has been verified; a timed-out/partial recurrence cannot establish emptiness or a minimum. Integer dyadic scaling must be exact. A stored minimizing path alone establishes only a candidate cost in the relaxation, not a universal minimum. All state labels/transitions, including unreachable states, must support independent recurrence replay.

## Scope and remaining gate

The three labels are explicitly post-hoc from closed evidence, fixed before the new bound. Other commitments remain free binary hourly cover decisions; none is fixed to a fractional/union/LP value. Their residence, all ramps/network restrictions and nuclear chronology are relaxed using the inherited safe premises. A low-cost selected path is neither a common dispatch nor a full feasible commitment. A strict bound, if obtained, would not by itself identify the selected residence rules as a unique physical cause, prove minimal information, or introduce a new algorithm. No choice of a different subset, scalarization or longer budget may be hidden after a null.

The capacity algebra received a separate source-only review from delegated agent `/root/find_deposit/gb_docs`; it found no blocker and performed no recurrence, numerical bound, model, import, solver or edits. Its review did not cover the automaton; the latter is independently addressed above. Producer implementation/invented controls and actual prepared archive are still separate gates. No scientific rejection or new bound value is asserted here.

## Reviewed bindings

- Original assembly:6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4.
- Common-commitment source:039af59750b4c165d877b9878ac14af02a202700b46739ba96a8914075ae3284.
- Closed capacity-cover source:b0e07f9cba7ea91696ef5884f94666592263003f610fd7104a23ff4760f42ab8.
- Closed capacity-cover protocol:157b910ec99e5f0f42a9f80bb5eee42a25382cf16555722d52949c3022b3060f.
- Existing identity native specification:9a2c78233792adb44a3a50ba7510769185457660551f92892941eeda1bacffd3.
- Existing source gen.csv:988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068.
