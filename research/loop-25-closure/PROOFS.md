# Loop 25: an inductive invariant for period 2? (H40)

Loop 23 showed the finite half of a route to B9 for period 2: every near-center window of width 25
that a left-consistent sequence shows at any time 19 to 45 dies within 23 steps under both period-2
tails (H38). The uniform half needs a set of windows that provably contains every window shown at
*every* time and still dies. This loop builds the simplest such set and tests it.

## The closure

A window at time `t` is `w = (c(t), x(-1,t), …, x(-24,t))` of a left-consistent sequence
(`c(0) = 1`; `c(t+1) = NOT x(-1,t)` whenever `c(t) = 1`; TX). Let `B` be every window shown at
`t0 = 19` by every left-consistent prefix `c(0..19)` (40 windows, loop 23). The step `w → w'` is

* `w'_j = w_{j+1} XOR (w_j OR w_{j-1})` for `1 ≤ j ≤ 23`;
* `w'_24` either value (it needs `x(-25,t)`, which the window does not hold);
* `w'_0 = NOT w_1` if `w_0 = 1`, either value if `w_0 = 0`.

`A` is the least superset of `B` closed under the step.

**Lemma (closure contains every window).** Every window shown by any left-consistent sequence at any
`t ≥ 19` lies in `A`. *Proof.* At `t = 19` by definition of `B`. If the window at `t` is in `A`, the
window at `t+1` is one of its step successors: its bits 1..23 are given by the rule from the
window, its bit 24 is one of the two values allowed, and its bit 0 obeys TX. ∎

**H40 (stated before computing; sent to the other session working on this repo at the time).**
For each tail `a ∈ {01, 10}`, every `w ∈ A` fails one of the 24 one-time checks `j = 0..23` when run
forward with `c(t) = w_0` and `c(t+1+j) = a[j mod 2]`.

**H40 implies B9 for period 2, at every onset.** A tail of word `a` from onset `T` is also a tail of
the same word from `T+2`, so every 2-periodic left-consistent sequence has an onset `T ≥ 20`. Its
window at `T-1 ≥ 19` lies in `A` by the lemma, and H40 makes one of the next 24 one-time checks fail,
which a left-consistent sequence cannot do. ∎

Code validation (done before stating H40, at width 11 only): the closure contains every window seen
at `t = 19..45`, and the kill check agrees with loop 23. At width 11 the closure is already all 2,048
windows, so the over-approximation is lossy at small widths. Width 25 was not computed before H40
was stated.

## Outcome

**H40 is falsified.** The closure of the 40 base windows reaches every one of the 2^25 windows in 20
rounds. Freeing the outer bit at every step, and the next center bit after every 0, lets the step
reach everything. Among all windows, 12,288 survive the 24 checks under `01` and 6,144 under `10`.
None of the windows actually shown at `t = 19..45` survives, as H38 found. So the reachable language
is a thin, killing set, but the simplest inductive description of it is the whole space. A local
invariant has to keep information this one throws away: the far-left cells beyond the window, or a
correlation between the outer bit and the bits inside.
