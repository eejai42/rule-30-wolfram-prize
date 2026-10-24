# Loop 21: the settled-zone relaxation. Does the clash become local?

## The strengthening

Loops 9 to 12 certified that the left-edge diagonal `w_k(t) = x(-t+k, t)` is eventually periodic
(TR, proved) with onset `o_k` and period `p_k ≤ 16` (finite, to `k = 20000`). So at time `t` every
cell on a diagonal `k ≤ t - s` with `t ≥ o_k` is *settled*: its value is the periodic value. The
true lattice satisfies all of this, so imposing it on the periodic-center relaxation of loop 13
is a legitimate strengthening of B5: a periodic center that contradicts the settled zone is
still refuted. Two versions are run:

* **S1, exact**: settled cells take their certified values (uses the certified words).
* **S2, periodic only**: cells on diagonals `k ≤ 2` take their values (T0); a settled cell on a
  diagonal `k ≥ 3` must equal the cell one period earlier on the same diagonal when that one is
  settled and inside the window. S2 uses only TR-type periodicity plus the onsets and periods,
  never the words, so a proof built on it would owe only an onset law and a period bound.

`research/loop-21-settled-zone/settled.py`; the true lattice satisfies every S1 and S2
constraint to time 400 (checked cellwise), and the true `(c, r)` windows pass the S1 checker.

## The question

The cone of T0 sits `T` columns from the center and carries no information but zeros and a line of
ones; against it the exclusion excess grew with `T` (loops 15, 16, 20). The settled zone begins at
the frontier `s_f(T)` (the first settled cell on the row at time `T`), about `0.25 T` columns out
for large `T`, and carries periodic structure. If a periodic center clashed with it *locally*, the
death window `L` would exceed the frontier by a bounded amount, and B5 would reduce to a finite
case analysis per phase plus the onset and period laws. That is the pivot proposed after loop 20.

**H34 (stated before the full computation; probes at six onsets were run while debugging the
checker and are included in the table).** For the words `01` and `10` and every onset
`8 ≤ T ≤ 160` that the search completes (cap 2^25), the excess `L(T) - s_f(T)` is at most 8 in
S1 and at most 16 in S2.

**F20.** The table of frontier, `L`, excess, peak live set and failing columns for both words and
both modes.

## Reading the outcome

If H34 holds, the next loop states B9 (periodic center is incompatible with periodic left-edge
diagonals within a bounded window past the frontier) and B10 (onset law and period bound for
the closed left-edge system), and rewires B1 to them. If H34 fails with an excess that grows with
`T`, the clash is not local even against the richest known left-side structure, and the
relaxation programme has reached its natural end: P1's difficulty is global, and further loops
on relaxations are not expected to narrow it. The ledger should then say so.
