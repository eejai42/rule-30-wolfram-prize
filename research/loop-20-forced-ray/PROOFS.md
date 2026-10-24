# Loop 20: what the 64-wall is not, and where TW says it must end

Loops 18 and 19 established that for the period-2 words the left-cone relaxation dies at window
exactly 64 (65 for `10`) for every onset `37 ≤ T ≤ 50`, after an early-kill regime below `T = 37`.
Three probes on the surviving windows at the wall (word `01`, onsets 40 and 44) rule out the
three simplest explanations; this loop records them as finite facts and tests the one
prediction the theory makes about the wall.

## Three things the wall is not (F19)

1. **Not a cellwise forcing.** On the death ray (the two final diagonals), every cell strictly
   inside the cone and off column -1 takes both values across the survivors. Only the
   one-time cell `x(-1,t)` and the cone-edge diagonals `w_0, w_1, w_2` are forced.
2. **Not a linear conservation law.** Over all `2^(T-1)` rows (`T ≤ 18`), the 33 one-time values
   `x(-1, T+d)`, `d = 1, 3, …, 65`, together with the constant, are linearly independent over
   GF(2). So no XOR of earlier constraints equals the wall constraint as functions on rows.
3. **Not a local cascade.** Tying cells by equality or complement across all survivors, columns
   -1, -2, -3 are fully tied (the hand analysis: column -1 is 1 at one-times, column -2 is
   constant across each (odd, even) pair, column -3 is tied to column -2), columns -4 and -5 are
   about half tied, and from column -6 to the cone zone essentially nothing is tied. The
   constraints do not propagate cell by cell to the edge.

So the wall is a global, nonlinear property of the 63-step evolution with alternating boundary:
the parity of ORs along the ray of length 63 is constant on the solution set of the 31 earlier
ray parities, while no sub-structure of the ray is.

## Where the wall must end

By TW, a one-time constraint at `t ≤ 2T-2` is absorbed by a free row bit and cannot kill. The
window-`W` constraint sits at `t = T+W-1`, so a wall at window `W` can kill only while
`T+W-1 ≥ 2T-1`, that is `T ≤ W`. For `W = 64` the wall must stop killing at `T = 65` at the
latest, and the data of loop 14 already show `L(64) = 90` for `0111`. The dyadic story of loop
19 ("a wall at every `2^(k+1)`") is also not supported for `k ≤ 4`: for `01`, `L(20) = 38 > 32`.
Only the 64-wall is established, and only for `T ≤ 50` (period 2) or `T ≤ 60` (`0111`).

**H33 (stated before computing).** The 64-wall is exactly the TW boundary phenomenon. For the
words `011, 101, 110, 0111, 1011, 1101, 1110` and every onset from the first pinned onset through
`T = 63`, the death window stays at its pinned value (66 for the period-3 words, 64 for the
period-4 words, as loop 14 recorded at onsets 50 to 60); at `T = 64, 65, 66` it exceeds that
value. For `01` and `10` at onsets 51 and 52 (cap 2^26) it stays at 64 and 65.

**F19.** The three structural records above for `01` at onsets 37 to 46 (survivors rebuilt from
their column-1 windows), the GF(2) rank table for `T ≤ 18`, and the `L(T)` table of H33.

## What this leaves for a proof of B7

A proof of the wall for `T ≤ 63` would prove B7 for those onsets but not beyond; past `T = 64`
the kill must come from constraints at `t ≥ 2T-1`, which the data put at about `1.1 T` to
`1.8 T` with no sharp structure found yet. The honest statement is that B7 is open at every onset
above 50, and the next loop should either find the mechanism of the early kill or prove the
64-wall as a self-contained theorem about 63 steps of Rule 30 with alternating boundary.
