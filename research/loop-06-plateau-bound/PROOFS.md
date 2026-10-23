# Loop 6: plateau lengths and the growth of the diagonal periods

Notation as in loops 1 to 4. By TL, `P_k = P_{k-1}(1+ε_k)` for `k ≥ 3`, so the period table is
the 0/1 sequence `ε_3, ε_4, …`. A **plateau** is a maximal run of consecutive `k ≥ 3` with
`ε_k = 0`; its length is the number of offsets in the run.

Known bounds before this loop: TB gives `P_k > ceil(k/2)` (logarithmic in `k`); TN gives
`log2 P_k ≤ log2 P_{k0} + ceil(2(k-k0)/3)`. Nothing forces exponential growth.

## H18 (hypothesis, tested in this loop)

Every plateau has length at most 7.

Through `k = 64` the plateau lengths are 1, 1, 5, 7, 1, 1, 4, 1, 1, 1, 1, 4, 1, 2, 2, 1, 2
(E13). This loop recomputes the diagonals past `k = 64` and checks every new plateau.

## TP. A plateau bound gives exponential growth

**Statement.** If every plateau has length at most `L`, then for every `k ≥ 3`,
`log2 P_k ≥ 2 + floor((k-3)/(L+1))`.

**Proof.** `P_3 = 4` (TK base case). Split `4, 5, …, k` into `floor((k-3)/(L+1))` disjoint
blocks of `L+1` consecutive offsets, plus a remainder. A block with no doubling would contain
a run of `L+1` zeros of `ε`, which lies inside some plateau longer than `L`; so each block has
at least one doubling. Each doubling multiplies the period by 2 and no step lowers it (TL).
Hence `log2 P_k ≥ log2 P_3 + floor((k-3)/(L+1))`. ∎

So H18 with `L = 7` would give `log2 P_k ≥ 2 + floor((k-3)/8)`. Together with TN's upper bound,
the diagonal periods would grow exponentially in `k`, at a rate between 1/8 and 2/3 bits per
offset. Observed through `k = 64`: about 0.42.

H18 is only ever checked finitely here. TP is unconditional as an implication.
