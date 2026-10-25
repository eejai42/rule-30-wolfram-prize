# The P1 frontier

Where the attack on Problem 1 (the Rule 30 center is not eventually periodic) stands, what is
proved, what is ruled out, and what the next loops aim at. The rulebook is the source of truth
for every status below; this page is the map that explains how the nodes fit. Update it when a
loop changes the chain under P1.

Last updated: loop 27 (2026-10-25).

## Measured against the challenge (loop 27)

The prize is graded in Lean, and the kit (WolframInstitute/Rule30PrizeKit) holds the official
statements, a catalog of partial results and 100+ equivalent forms, all kernel-checked. Loop 27
loaded all of it into the model (claims `L-...`, `KC1`..`KC7`, `Q-...`, routes `B10`, `B11`). The
kit's own split of P1 by the least period:

| Case | Kit status | Claim |
|---|---|---|
| Period 1 | proved for every column | KC1 (our K1 is kernel-checked against it) |
| Small periods | proved: no eventual period P <= 4096 with transient T <= 8192 | KC2 |
| Any period | proved: T + P >= 16359 | KC3 |
| Period 2 | reduced to Q01 (zero-boundary left half; open, proved to width 52) | KC4 <- Q-Q01 |
| Least period 3 | reduced to four open statements | KC5 <- Q-Q001, Q-C3w011 |
| Least period 4 | reduced to Absorption (open) | KC6 <- Q-Absorption |
| Longer periods | open; many words excluded | KC7 |

What this changes for the chain below:

- **Our diagonal results are known.** T004, H4, TL, TN, TK, H7, TB, TR and K1 are kit theorems
  (`Rule30Diagonals`, `Rule30RightPeriods`); `Assertions.IsKnownInKit` marks them. They stay usable
  premises, and none of them is new against the catalog.
- **The kernel now checks six of our claims** (K1, T0, TX, D0, TS, T004) and proves our formal
  P1 equivalent to the official `Problem1`. Its term tree used to say "no onset" in its inner binder,
  the shape of the negation; Lean's alignment check is what decides it now.
- **B7 and Q01 are the same frontier from two sides.** Q01 asks the zero-boundary left half from
  any finite start; B9 asks the left half the real seed produces (TX). The kit proves that no finite
  abstraction, local ranking or edge-DFA ranking can prove Q01 over all finite starts
  (`Rule30ZeroBoundaryBarriers`), but its witnesses are never real left halves
  (`trunc_not_left_half`). That gap is the only room our route has, and the planned automaton loop
  (loop 28) has to live in it.

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
| TY | a free outer cell steers any window to any window within 2E+1 steps (a lemma that rules out, not a reduction) | 26 |

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

8. **A local invariant with a free outer bit.** The closure of the width-25 near-center windows under
   one step, with the outer cell and the post-0 center bit free, is every window, and 18,432 of
   them survive a period-2 tail (H40, loop 25). The real windows all die (H38), so the reachable
   set is thin, but this description of it is not.
9. **Any closure with a free outer cell, at any width.** Rule 30 is left-permutive, so the free
   outer cell steers every window to every window within 2E+1 steps (TY, proved, loop 26). Widening
   the window cannot rescue mechanism 8.
10. **A fixed-width finite kill of the reachable windows.** H38 (every width-25 window dies within 24
   checks) held only because loop 23 stopped at t = 45. At t = 46 a reachable state survives 30
   checks of `01` (H41, loop 26), and the longest survival keeps growing: 46 and 47 checks by t = 111.
   Every state through t = 160 still dies within 120 checks.

## Certified, finite

Every nonconstant periodic center tested is excluded: periods 2 to 16, onsets to 384, about 6,000
cases (F12 to F18, F20). These are not progress on P1 by themselves: F6 already excludes every
period below 2^17 from every onset below 917,498 for the real center. A proof needs an argument
uniform in the onset.

## Current target

B9 for period 2, by whole rows. Loop 26 closed the near-center window route (mechanisms 9 and 10):
no fixed-width window description works, because the kill time grows with t. What it found
instead: left-consistent prefixes with the same row have the same future, and merged by row they
are few (631 states at t = 45, 4.6 million at t = 160, against an extrapolated 10^28 prefixes). Every
one of them dies under both period-2 tails (F23). A proof needs a description of the reachable rows
that is closed under the step and contains only rows that die. The next candidate is an automaton
that reads the row from the left edge inward, where the settled diagonals make the rows periodic;
loop 28 tests whether the reachable rows at t <= 160 fit an automaton whose size stops growing. The
kit's barrier B6 (`no_edge_dfa_ranking`) says no such automaton works over all finite starts; it can
only work because the real left halves exclude the barrier's truncated stripes.

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
