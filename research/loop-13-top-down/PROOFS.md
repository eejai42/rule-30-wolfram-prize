# Loop 13: start from the finish. Decomposing P1.

Loops 1 to 12 grew the ledger upward from the definition. None of their 33 claims has P1, P2 or
P3 downstream, and the one obligation blocking P1, `B1`, had never been split. This loop works
the other way, as the Fermat ledger did: take the open node under the prize problem, write down
what it would follow from, mark the parent as derived, and leave the open child as the next
target. The build keeps the parent `BLOCKED` until the child is discharged.

Notation. `c(t) = x(0,t)` is the center. For a shift `p ≥ 1`, `d_i(t) = x(i,t) XOR x(i,t+p)` is
the discrepancy of column `i`; "column `i` p-agrees at `t`" means `d_i(t) = 0`. The inverse rule
is `x(i-1,t) = x(i,t+1) XOR (x(i,t) OR x(i+1,t))`.

## TS. Under center agreement, column -1 is column 1 read at the center's zero-times

**Statement.** If `d_0(t) = d_0(t+1) = 0` then

* `d_{-1}(t) = 0` when `c(t) = 1`;
* `d_{-1}(t) = d_1(t)` when `c(t) = 0`.

Hence inside any center agreement run, the agreement pattern of column -1 is the agreement
pattern of column 1 restricted to the times where the center is 0, and is automatic elsewhere.

**Proof.** The forward rule at `(0, t+1)` and at `(0, t+p+1)`, XORed, gives

    d_0(t+1) = d_{-1}(t) XOR [ (c(t) OR x(1,t)) XOR (c(t+p) OR x(1,t+p)) ].

With `d_0(t+1) = 0` and `c(t) = c(t+p) = b`: if `b = 1` both ORs equal 1, the bracket is 0 and
`d_{-1}(t) = 0`. If `b = 0` the bracket is `x(1,t) XOR x(1,t+p) = d_1(t)`, so
`d_{-1}(t) = d_1(t)`. ∎

Consequence for any relaxation that fixes the center to a periodic word and frees column 1:
the free bit `r'(t)` enters only through `x(-1,t) = c'(t+1) XOR (c'(t) OR r'(t))`, so it is
irrelevant at one-times of the word. The effective freedom is the zero-times.

## The left-cone relaxation (H26, F12)

Fix an onset `T ≥ 1`, a word `a` of least period `p`, and a window length `L`. Put
`c'(t) = a[(t-T) mod p]` on `[T, T+L]` and let `r'(t)` be free on `[T, T+L-1]`. The inverse rule
determines the triangle `x(-s,t)`, `1 ≤ s ≤ L`, `T ≤ t ≤ T+L-s`. The single seed forces, by T0,
`x(-s,t) = 0` for `s > t`, `x(-s,s) = 1`, and `x(1,1) = 1`. The true lattice satisfies all of
this with the true `(c, r)`; `research/loop-13-top-down/left_cone.py` checks that.

`count(T,a,L)` is the number of compatible `r'` on the zero-times of the window. If it reaches 0
the left cone alone excludes a p-periodic center of word `a` from onset `T`: a TC-type
certificate that never looks at the right side. TC is the special case in which `r'` is also
periodic. TD's proof for a constant-one center is the case `a = 1`: no zero-times, no freedom,
dead by `L = T+2`. TD's constant-zero case needs the right side (monotone column 1), and the
relaxation is expected to keep a few bits of slack for `a = 0`.

**H26 (stated before computing).** For every onset `1 ≤ T ≤ 10` and every nonconstant primitive
word `a` of period `p ≤ 4`, `count(T,a,L) = 0` for some `L ≤ 4T + 4p + 8`.

**F12.** The full table: for every `T ≤ 10` and every primitive word of period `≤ 4`, including
the constants, the first `L` with no solution, or the surviving count at `L_max`.
Output: `research/loop-13-top-down/left_cone_table.json`.

## B1 derived, two routes

`B1`: a center that is eventually periodic with least period `p ≥ 2` contradicts seed-compatible
neighbouring columns. The ledger adopts one of the following traces, chosen by F12; the other
stays here as the recorded alternative.

### Route L (adopted if H26 holds). B1 ⇐ B5, T0

**B5 (open).** For every onset `T`, every `p ≥ 2` and every nonconstant word `a` of least period
`p`, the left-cone relaxation is unsatisfiable at some finite `L(T,a)`.

**Derivation of B1 from B5.** Suppose the center is eventually periodic with least period
`p ≥ 2` from onset `T`, with word `a`. Then `a` is nonconstant. The true columns `(c, r)` on
`[T, T+L]` satisfy every constraint of the relaxation for every `L`, because the true lattice
has the cone of T0 and obeys the inverse rule. For `L = L(T,a)`, B5 says no such pair exists.
Contradiction. ∎ (The case `p = 1` is K1, already a premise of P1.)

### Route R (adopted if H26 fails). B1 ⇐ TC, B4

**B4 (open).** If the center is eventually p-periodic from onset `T`, then for some `T' ≥ T`
column 1 p-agrees on the whole window `[T', 2T'+p]`.

**Derivation of B1 from B4.** With the center p-periodic from `T`, `d_0 = 0` on `[T', 2T'+p]`;
with B4, `d_1 = 0` there too. TC says some mismatch occurs in column 0 or 1 on that window.
Contradiction. ∎

By TS, B4 can be weakened to "column 1 agrees at the center's zero-times of the window",
equivalently "column -1 agrees on `[T', 2T'+p-1]`", if TC is restated for columns -1 and 0
(the v05 report proves that form with the window `[T, 2T+p-1]`).

## What this changes in the ledger

* `B1` becomes `PROVED_HUMAN_READABLE` *given its premises* and compiles to `BLOCKED`, with
  `IsAtRisk = 1`, because its new child is `OPEN`. That is the intended reading: the edge is
  closed, the obligation moved one level down. P1's blocking ancestor is now the child, not `B1`.
* Every new node in this loop has P1 downstream. The next target is the open child.
