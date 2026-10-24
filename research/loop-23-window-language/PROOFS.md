# Loop 23: the near-center language of left-consistent sequences

Loop 22 found that, for period 2, every left-consistent start at onsets 20 to 46 dies within 22
steps of the tail, flat in the onset. Over `j` steps the cell `x(-1, t+j)` depends only on the
center bits and on the *window* `(c(t), x(-1,t), …, x(-(j+1),t))` of the row at time `t`. So a
bounded kill means a finite neighbourhood decides it, and B9 for period 2 would follow from two
statements:

* **Finite part, K(E).** Every width-`E+1` window that a left-consistent sequence can show at a
  time `t ≥ 19` dies within `E-1` steps under the tail `01` and under the tail `10`.
* **Uniform part, L(E).** The set of windows a left-consistent sequence can show is, for every
  `t`, contained in an explicit finite set `W_E` (for example, all windows avoiding a list of
  forbidden patterns that one step of the dynamics never creates: an inductive invariant).

K(E) and L(E) together give B9 for period 2 at every onset `T ≥ 20` (onsets below 20 are F21).
This loop measures the language and tests the finite part.

Windows are encoded as in `research/loop-22-left-consistent/seeded.py`: bit 0 is `c(t)`, bit `j`
is `x(-j,t)`. `W_E(t)` is the set of width-`E+1` windows over all left-consistent prefixes
`c(0..t)`. A window is run forward on its own: each step shortens its valid width by one, so
`E-1` steps of the one-time check can be decided from the window alone.

**H37 (stated before computing).** For some `E ≥ 12`, the language at `t = 45` misses at least half
of the `2^(E+1)` windows.

**H38 (stated before computing).** There is an `E ≤ 30` for which K(E) holds at every `t` from 19
to 45.

**F22.** For `E = 4, 6, …, 30` and `t = 19 … 45`: `|W_E(t)|`, whether `W_E(t) = W_E(t-1)` (for
`E ≤ 22`), the smallest missing windows at the smallest non-full width, and for each `E` the number
of windows in `W_E(t)` that survive `E-1` steps under each period-2 tail.

If H37 and H38 both hold, loop 24 looks for the forbidden patterns of L(E) and tests whether one
step of the left-consistent dynamics preserves their absence.
