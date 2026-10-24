# Loop 22: consolidate, then attack B9 with the whole left side

The consolidation is `docs/p1-frontier.md`: the chain under P1, the proved reductions, and seven
ruled-out mechanisms. It corrects one claim made in conversation after loop 21: the dyadic wall
is not exact at k = 4. The period-2 words die past window 32 at most onsets 18 to 31, so only the
64-wall exists and an induction on k has no base.

## TX. The center is left-consistent

**Statement.** For `i ≤ -1` and `t ≥ 0`, `x(i,t)` is a function of `c(0), …, c(t-1)` alone, given
the single seed. Whenever `c(t) = 1`, `c(t+1) = NOT x(-1,t)`.

**Proof.** At time 0 the left half is all zero. The rule at `(i, t+1)` with `i ≤ -1` reads
`x(i-1,t)`, `x(i,t)`, `x(i+1,t)`, all left of column 1, and the only column-0 input is
`x(0,t) = c(t)` (for `i = -1`). Induction on `t`. The forward rule at `(0, t+1)` is
`c(t+1) = x(-1,t) XOR (c(t) OR x(1,t))`, which is `NOT x(-1,t)` when `c(t) = 1`. ∎

A binary sequence with `c(0) = 1` that satisfies `c(t+1) = NOT x(-1,t)` at every `t` with `c(t) = 1`,
where `x` is the left half it generates, is *left-consistent*. The left-consistent prefixes form a
tree: after a 1 the next bit is forced, after a 0 it branches. Its size grows like `1.50^t`
(a 0 has two children, a 1 has one, and the forced child is a 0 or a 1 about equally often).

## B9 and its place in the chain

**B9 (open).** No left-consistent sequence ends in a periodic tail with a nonconstant word.

**B1 from B9 and TX.** A center that is eventually periodic with least period `p ≥ 2` has a
nonconstant word and is left-consistent by TX. ∎

**B9 from B5 and TU.** A left-consistent sequence with a tail of word `a` from onset `T ≥ 2`
gives, at time `T`, a row of the left half for which every one-time constraint of the
relaxation holds forever; B5 says no row does. ∎

So B9 is weaker than B5, which only bounds rows from above; it is the statement B1 actually
needs. The ledger cannot express "proved by B5 or directly", so B9 is marked derived from B5 and a
direct proof of B9 would replace that premise.

## The seeded relaxation (H35, H36, F21)

For onset `T`, take every left-consistent prefix `c(0..T-1)`, attach the tail `c(T+j) = a[j mod p]`,
evolve the left half, and record the first time `t*` at which `(*)` fails. Unlike the free-row
relaxation there is no free data after `T`: every one-time from `T-1` on is a real constraint.

Two checks before the run: the true center, given its true continuation, never violates `(*)`
through `T+100` for `T = 5, 10, 15, 20`; and for the period-2 words at every onset 4 to 20 the
seeded death time is never later than the free-row window end of loop 19, as containment
requires. A smoke test at onsets 6 to 12 gave deaths 2 to 6 steps after `T`, against windows of 10
to 30 in the free-row relaxation.

**H35 (stated after the smoke test, before the full run).** For `a ∈ {01, 10}` and every onset
`4 ≤ T ≤ 46`, every left-consistent prefix is killed by the 2-periodic tail before time `2T-1`:
inside the zone where TW proves the free-row relaxation cannot kill at all.

**H36.** The same for every nonconstant primitive word of period 3 or 4 at onsets `4 ≤ T ≤ 32`.

**F21.** For each word and onset: the number of prefixes, the largest and mean death excess
`t* - T`, and the excess histogram.

If H35 holds with a small excess, the information that kills a periodic tail lives in the left
half's memory of the center's own recent past, not in the cone, and B9 for period 2 becomes the
next target in its own right.
