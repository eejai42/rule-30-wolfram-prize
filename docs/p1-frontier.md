# The P1 frontier

Where the attack on Problem 1 (the Rule 30 center is not eventually periodic) stands, what is
proved, what is ruled out, and what the next loops aim at. The rulebook is the source of truth
for every status below; this page is the map that explains how the nodes fit. Update it when a
loop changes the chain under P1.

Last updated: loop 22 (2026-10-23).

## The chain under P1

```
P1  <- B1, K1                       K1: not eventually constant (known result)
B1  <- B9, TX                       periodic center of period >= 2 is impossible
B9  <- B5, TU                       no left-consistent sequence has a nonconstant periodic tail
B5  <- B6, TU, TW                   the free-row left-cone relaxation excludes it
B6  <- B7, B8                       split by period
B7  OPEN                            period 2
B8  OPEN                            period >= 3
```

B1 also keeps its older edge to B5, which B9 makes redundant.

## The problem in one line (TX, loop 22)

The left half of the lattice is a causal function of the center's own past. Whenever `c(t) = 1`
the forward rule at column 0 forces `c(t+1) = NOT x(-1,t)`. So the center is a sequence that,
after every 1, must take the next bit that its own history dictates through the left half. Call
such a sequence *left-consistent*. After a 0 the left half says nothing; only the right side does.
B9 asks: can a left-consistent sequence end in a periodic tail with a nonconstant word?

## Proved reductions (each a short argument from the definition and the cone)

| Node | Content | Loop |
|---|---|---|
| TS | under center agreement, column -1 is column 1 read at the zero-times | 13 |
| TU | the free-row relaxation is a left half driven by the periodic center, T-1 free bits | 14 |
| TV | from time 2T each one-time constraint is a parity along a light ray, no free bits | 15 |
| TW | exactly 2^Z rows survive to 2T-2; later constraints are functions of Z bits | 17 |
| TX | the center is left-consistent | 22 |

## Ruled out: mechanisms a proof cannot use

Each line is a falsified hypothesis or a finite check in the rulebook. Do not retry these without a
new idea about why they would work.

1. **Bounded excess past the cone.** The free-row relaxation dies at an excess over the first
   cone column that grows with the onset (H28, H29 held only for the stated bound; the growth is
   about 0.055 per onset, loop 16).
2. **Linear algebra over the free bits.** The killing constraints have algebraic degree Z or Z-1
   in 731 of 750 cases (H30, loop 17).
3. **Cellwise forcing.** At the 64-wall the cells of the death ray take both values across
   survivors (F19, loop 20).
4. **A GF(2) conservation law.** The 33 one-time functions are linearly independent with the
   constant over all rows for T <= 18 (F19, loop 20).
5. **A local cascade.** Columns 1 to 3 are tied by the constraints, 4 and 5 partly, 6 onward not
   at all (F19, loop 20).
6. **A dyadic wall at every level.** Only the 64-wall exists (windows 64 to 67, onsets about 37 to
   63, every short word tested; H32, H33). At k = 3 and k = 4 the period-2 words die past window
   2^(k+1) at most onsets (loop 22 check of the loop 19 table). An induction on k has no base.
7. **Bounded excess past the settled left-edge zone.** Imposing every settled left-edge diagonal,
   exactly or by periodicity only, still leaves an excess that grows with the onset (H34, loop 21).

## Certified, finite

Every nonconstant periodic center tested is excluded: periods 2 to 16, onsets to 384, about 6,000
cases (F12 to F18, F20). These are not progress on P1 by themselves: F6 already excludes every
period below 2^17 from every onset below 917,498 for the real center. A proof needs an argument
uniform in the onset.

## Current target

B9, attacked directly with the seeded relaxation of loop 22: grow every left-consistent prefix
from the seed, attach a periodic tail, and see how soon the left half contradicts it. It uses the
whole left-side information, not a relaxation of it, and is strictly sharper than B5.

## What the model computes (loop 24 on)

The chain above is now also in the rulebook as predicates with term-tree statements
(`Predicates`, `Terms`), and these nodes have instances the build decides from Rule 30 itself:

| Node | Instances (depth 64) | Verdict |
|---|---|---|
| TX | every center step t < 64 (`LeftConsistencyChecks`) | holds on all |
| B9, B1 | the real prefix with every primitive tail of length <= 3 spliced on at onsets 1..10, each with its own left-half lattice (`TailCandidates`, `TailCells`, `TailChecks`) | every one is killed; the longest survival is 10 steps (010 at onset 10) |
| H39 (loop 24) | the same 80 tails: killed within 3 x period | FALSIFIED by the build (010 at onset 10) |
| TC | every window (T, p) inside the horizon (`MismatchWindows`) | holds; column 0 alone has the mismatch in all 492 |
| P1, K1 | every candidate (p, T), p <= 24, with its refuting witness (`PeriodicityCandidates`) | every onset in the bounded form is refuted |

TU, TV, TW and B5 to B8 have formal statements but use operators the model does not compute yet
(`RelaxationSatisfiable`, `TWRowCount`, `IsTWRow`, `RowViolates`, ...; `Operators.IsModeled` = 0).
Modeling the free-row relaxation as tables (rows R as data, their left-half lattices, the one-time
checks) is what would let the build decide B6 to B8 on small onsets.
