# Loop 18: the exact killing cell for the period-2 word

P1 ← B1 ← B5 ← B6. B6 says each of the 2^Z rows of TW violates some one-time constraint at or
after 2T-1; by TV those constraints are the cone cells read through the inverse rule. This loop
asks, for the simplest words `01` and `10` and every onset the exact search reaches, *which*
cone cell finally kills everyone, so that the induction on T has a concrete target.

At the death step the search holds the last surviving windows and the newly computed diagonal
of cells `x(-s, T+L-s)`; the constrained ones are the cone exterior (must be 0) and the edge
`x(-s,s)` (must be 1). For each survivor the violated cells are recorded; a *common killing cell*
is one violated by every survivor.

**H31 (stated before computing).** For `a ∈ {01, 10}` and every onset `4 ≤ T ≤ 46`: (i) a
common killing cell exists; (ii) its time `t*(T)` is non-decreasing in `T` with
`t*(T+1) - t*(T) ∈ {0, 1}`.

**F17.** For each `(T,a)`: the death window, the number of survivors, the histogram of violated
cells (column, time), the set of common killing cells, whether the edge cell is among them, and
`t*(T)`.

If (i) and (ii) hold, B6 for these words reduces to: for every T the reconstructed cone cell at
`(-s*(T), t*(T))` has the wrong value for all 2^Z rows, with `t*` a staircase in T. That is a
statement about one cell per onset, which is what an induction can carry.
