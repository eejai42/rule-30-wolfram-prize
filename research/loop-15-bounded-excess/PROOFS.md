# Loop 15: the contradiction arrives a bounded distance past the cone

Loop 14 measured the exclusion length `L(T,a)` of the left-cone relaxation to onset 144. The
excess `L(T,a) - T`, the number of steps past the first cone column, did not grow with `T`:
at most 54 for `T ≥ 8`, at most 34 for `T ≥ 40`. This loop states that as the hypothesis, tests
it out of sample on the 366 primitive words of periods 7 and 8, and records exactly which cone
cells the last surviving windows violate. It also proves the lemma that says why the death
time sits just past `2T`.

Notation as in loops 13 and 14: `c'(t) = a[(t-T) mod p]` on the window, the inverse-rule
triangle `x(-s,t)`, the relaxation's free data (TU) the row at time `T`.

## TV. Past time 2T the one-time constraint is a parity along a light ray

**Statement.** In any Rule 30 patch, for `t ≥ T` and `0 ≤ j ≤ t-T`,

    x(-1,t) = x(-j-1, t-j) XOR XOR_{i=1}^{j} ( x(-i, t-i) OR x(-i+1, t-i) ).

In the relaxation take `j = t-T`. The leading term is the row-`T` cell at position `-(t-T+1)`:
a free bit while `t ≤ 2T-2`, the edge value 1 at `t = 2T-1`, and 0 (outside the cone) for
`t ≥ 2T`. Hence for every one-time `t ≥ 2T` the constraint `x(-1,t) = NOT c'(t+1)` reads

    XOR_{i=1}^{t-T} ( x(-i, t-i) OR x(-i+1, t-i) ) = NOT c'(t+1),

a parity of ORs of adjacent cells along the ray from `(-1, t-1)` down-left to `(-(t-T), T)`,
with no free-row term.

**Proof.** The rule at `(-i, t-i+1)` says `x(-i, t-i+1) = x(-i-1, t-i) XOR (x(-i,t-i) OR x(-i+1,t-i))`.
Substituting for `i = 1, …, j` in turn telescopes the first terms. The cases of the leading
term follow from T0: position `-(t-T+1)` at time `T` is inside the cone iff `t-T+1 < T`. ∎

TV is the same mechanism as TE (the n-step output is XOR-affine in its extreme-left input)
applied to the left half of the relaxation. It explains the shape of the loop 14 data: before
time `2T-1` every one-time constraint can be absorbed by a free row bit, so the live set grows
like 2^(zero-times); from `2T` on the constraints are parities of the patch itself, and the
measured death time is `2T + e` with `e` small.

## H28 and F14

**H28 (stated before computing).** For every primitive nonconstant word `a` of period 7 or 8
and every onset `T ≥ 8` that exact enumeration completes (live-set cap 2^23), the excess
`L(T,a) - T` is at most 64. Equivalently the relaxation dies by time `2T + 64`. Periods 2 to 6
(loop 14) satisfy this in sample with maximum 54.

**F14.** For each `(T,a)`: `L(T,a)`, the death time, and the histogram of the cone cells that
the last surviving windows violate, as (column offset past the first cone column, time offset
past `T`), with the share that fails the edge cell `x(-s,s)=1` rather than a zero cell.

## What a bounded excess would mean

If `L(T,a) - T ≤ C` for all `T`, then for each word the contradiction is produced by the rays
of TV for the one-times in `[2T, 2T+C]`, which involve the patch only in a strip of width about
`C` next to the cone edge together with the near-center cells they pass through. A proof of B5
for a fixed word then has a bounded "shape" independent of `T`, and the remaining work is to
show the shape recurs as `T` grows: an induction on `T` with a fixed finite case analysis, or a
periodicity of the death pattern in `T`. The pinned values `L = 64` seen in loop 14 across ranges
of `T` suggest that periodicity is tied to the power-of-two periods of the left-edge diagonals
(TR). Nothing in this section is proved.
