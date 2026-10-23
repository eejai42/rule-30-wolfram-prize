# Loop 14: how far does the left cone reach, and what a proof of B5 must do

Loop 13 left P1 blocked by one node, `B5`: for every onset `T` and every nonconstant periodic
word `a`, the left-cone relaxation (periodic center, free column 1, inverse rule, cone of T0) is
unsatisfiable at some finite window `L(T,a)`. It held in all 200 cases with `T ≤ 10`, `p ≤ 4`.
This loop measures `L(T,a)` as far as exact enumeration reaches, and rewrites the relaxation
in the form an induction would use.

## TU. The relaxation is a driven left half with `T-1` free bits

**Statement.** Fix `T ≥ 2`, a word `a` and `L ≥ T`. The following are in bijection:

1. column-1 windows `r'` on the zero-times of `[T, T+L-1]` whose inverse-rule triangle from
   `(c', r')` agrees with the cone (the loop 13 relaxation);
2. rows `R` at time `T` on positions `-T+1 .. -1` such that the Rule 30 evolution of the left
   half (positions `≤ -1`) from `R`, with `x(-T,T)=1`, zeros further left, and the center
   prescribed as the boundary `x(0,t) = c'(t)`, satisfies `x(-1,t) = NOT c'(t+1)` at every
   one-time `t` (`c'(t)=1`) with `T ≤ t ≤ T+L-1`.

In particular `count(T,a,L) ≤ 2^(T-1)`, with equality for the all-zero word, and column 1 is
not free data at all: at a zero-time it is `r'(t) = x(-1,t) XOR c'(t+1)`, at a one-time it is
irrelevant.

**Proof.** The inverse rule and the forward rule are the same equation
`x(i,t+1) = x(i-1,t) XOR (x(i,t) OR x(i+1,t))` solved for different unknowns, so a triangle
built by the inverse rule from `(c', r')` satisfies the forward rule at every cell whose stencil
lies inside it. Given (1), read off `R` as the triangle's row at time `T` on `-T+1..-1`; the
triangle's row at `T` is cone-shaped because the cone constraints at `s ≥ T`, `t = T` are
part of (1) when `L ≥ T`. Evolving `R` forward with boundary `c'` reproduces the triangle where
both are defined, and at a one-time the forward rule at `(0,t+1)` reads
`c'(t+1) = x(-1,t) XOR (1 OR r'(t)) = NOT x(-1,t)`, which is the constraint in (2).
Given (2), define `r'(t) = x(-1,t) XOR c'(t+1)` at zero-times (and anything at one-times);
then the forward rule holds at `(0,t+1)` for every `t`, so the evolved left half together with
columns 0 and 1 is a valid patch, and the inverse rule from `(c', r')` rebuilds exactly it; its
cone constraints hold because a cone-shaped row evolves to a cone-shaped row (T0). The two maps
are inverse to each other because each recovers the other's data from the same patch. ∎

**Why this matters for a proof.** B5 is now a statement about a *deterministic* system with a
periodic boundary drive and finitely many initial conditions: no initial row of the left half
can keep answering `x(-1,t) = NOT c'(t+1)` at every one-time forever. The data below say the
answer fails within a window linear in `T` for every nonconstant word tried.

## H27 and F13

**H27 (stated before computing).** For every primitive nonconstant word `a` of period `p ≤ 6`
and every onset `2 ≤ T ≤ T_max(a)` that exact enumeration completes under a live-set cap, the
left cone excludes the periodic center with `L(T,a) ≤ 4T + 4p + 8`, the bound of loop 13.

**F13.** The table of `L(T,a)` from `research/loop-14-left-cone-growth/left_cone_fast.py`,
a vectorised breadth-first version of the loop 13 search validated bit for bit against the
loop 13 table and against an independent SAT encoding of the forward form (TU) at `T ≤ 20`.
For each word the onset is pushed until the live set exceeds the cap. The record keeps, per
onset band, the largest ratio `L(T,a)/T`.

## What a proof of B5 must do (open; the next target)

In the forward form the left half is a closed system in diagonal coordinates,
`w_k(t) = x(-t+k, t)`, `w_k(t) = w_{k-2}(t-1) XOR (w_{k-1}(t-1) OR w_k(t-1))`, with
`w_0 ≡ 1`, `w_1 ≡ 1`, `w_2 ≡ 0` after the first steps, `w_k(k) = c'(k)` for `k ≥ T`, and the
free row supplying `w_k(T)` for `k < T`. The one-time constraint reads `w_{t-1}(t) = NOT c'(t+1)`.
When `w_{k-1}(t-1) = 1` the diagonal `k` is reset to `NOT w_{k-2}(t-1)` regardless of its past;
when it is 0 the diagonal accumulates `w_{k-2}`. An induction would show that a periodic drive
forces, column by column leftward, a pattern that the reset/accumulate dynamics cannot sustain
once it meets the fixed diagonals `w_1, w_2`. For `a = 01` the first steps are explicit:
column -1 is 1 at every one-time, column -2 is constant across each (one-time, next time)
pair, column -3 across the complementary pairs, and so on; the measured `L(T, 01)` says the
conflict with the cone arrives about `0.6 T` columns in, not at the first cone column.
Nothing here is proved beyond TU.
