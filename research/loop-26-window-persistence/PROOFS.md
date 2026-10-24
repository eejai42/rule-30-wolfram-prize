# Loop 26: does the finite kill hold past t = 45? (H41, TY)

Serves B7 (period 2) through B9. Loop 23 found that every near-center window of width 25 shown by
a left-consistent sequence at times 19 to 45 dies within 24 checks under both period-2 tails (H38).
Loop 25 found that the closure of those windows with a free outer cell is every window (H40). Two
questions were open: is the closure result special to width 25, and does H38 itself survive past
t = 45? The reachable windows were still growing at t = 45 (40 windows at t = 19, 631 at t = 45),
and loop 22's longest survival past the onset was already 22 steps against a window of 24 checks.

## TY: a free outer cell floods the closure at every width

Windows and the step are loop 25's (`closure.py`): a window is `w = (w_0, ..., w_E)` with
`w_0 = c(t)` and `w_j = x(-j, t)`; the step gives

* `w'_j = w_{j+1} XOR (w_j OR w_{j-1})` for `1 <= j <= E-1` (Rule 30 is left-permutive);
* `w'_E` either value (the outer cell);
* `w'_0 = NOT w_1` if `w_0 = 1` (TX), either value if `w_0 = 0`.

**TY.** For every `E >= 1`, every window reaches every window in at most `2E + 1` steps. Hence the
closure of any nonempty set of windows is all `2^(E+1)` windows, at every width.

*Proof.* Write `b_k` for the value given to the outer cell at step `k + 1`, so cell `E` at step `s`
is `b_{s-1}`. By induction on steps, cell `j` at step `s` depends on `b_k` only for
`k <= s - 1 - (E - j)`: the outer cell moves inward one cell per step and no faster. Following the
rule down the leftmost chain, cell `j` at step `s` equals `b_{s-1-(E-j)}` XOR terms in cells `j`
and `j - 1` one step earlier, and those depend only on `b_k` with smaller `k`. So, with the center
choices fixed,

    cell j at step s = b_{s-1-(E-j)} XOR g_{j,s}(b_k for k < s-1-(E-j), the start window, the center choices).   (1)

*Phase 1: make the center 0.* Whenever the center is 0 the next center is free; choose 0, and it
stays 0. While the center is 1, the next center is `NOT` cell 1, so it stays 1 only while cell 1 is
0. Cell 1 at step `s < E` and the centers up to step `E` involve no `b_k`. By (1), cell 1 at step `E`
is `b_0 XOR g`; choose `b_0` to make it 1. If the center at step `E` is still 1, the center at step
`E + 1` is 0. So after at most `E + 1` steps the center is 0.

*Phase 2: steer.* From a window with center 0 at step `m`, hold the center at 0 and solve (1) at step
`m + E` for `j = 1, ..., E` in turn: cell `j` is `b_{m+j-1}` XOR a function of earlier choices, so
choose `b_{m+j-1}` to make it the target bit. At the last step the center was 0 one step earlier, so
the last center bit is free: give it the target value; it does not affect cells `1..E` at that
step. Total at most `(E + 1) + E = 2E + 1` steps. ∎

`flood.py` checks this exhaustively: for `E = 1..16` the step graph on all `2^(E+1)` windows has one
strongly connected component, and for `E <= 10` its diameter is `E + 1`, inside the bound. So H40's
outcome was not special to width 25: a closure with a free outer cell is the whole space at every
width, and widening the window cannot rescue it. Any invariant has to constrain the outer cell.

## Merging prefixes by their row

A left-consistent prefix `c(0..t)` affects its future only through its row at time `t` (`c(t)` and
the left half): the next rows and every later one-time check are functions of that row and of the
next center bits. So prefixes with equal rows can be merged. `states.py` grows the distinct rows
directly (loop 22's tree, then `np.unique` at every step). It matches loop 22's tree, with
duplicates removed, at every `t <= 36`. The merge is large: 43,951,920 prefixes at `t = 45` are 631
states, and `t = 160` has about 4.6 million states.

Exactness of the window test: under a tail, check `j` (at time `t + j`) reads `x(-1, t + j)`, which
depends on cells `-1 .. -(j + 1)` at time `t`. For `j <= 23` these lie inside the width-25 window,
so a state passes the first 24 checks exactly when its window does, that is, when its window is one
of loop 25's survivors (12,288 under `01`, 6,144 under `10`).

## H41 (stated before computing; no kill was computed past t = 45 before this)

**H41.** For every time `19 <= t <= 160` and each tail `a in {01, 10}`, every width-25 near-center
window shown at time `t` by a left-consistent prefix fails one of the next 24 one-time checks when the
center continues `c(t + 1 + j) = a[j mod 2]`. (H38 at `E = 24`, extended from `t <= 45` to `t <= 160`.)

Equivalently: no reachable state at `19 <= t <= 160` survives 24 checks of a period-2 tail.

Reading. If H41 fails, the kill window must grow with `t` and the fixed-width route to B9 for
period 2 is closed. If it holds and the longest survival stays flat, a fixed-width kill is likely
real, and the target set is explicit: the reachable states must avoid the 18,432 survivors.

`run.py` also records, at every `t <= 160`, the number of states, the number of distinct width-25
windows, and the longest survival of a full state under each tail (up to 120 checks), and checks
these against loop 22 (onsets 4..46) and loop 23 (`t = 19..45`).

## Outcome

**H41 is falsified, at the first time past loop 23's range.** At `t = 46` one reachable state
survives 30 checks of the tail `01`; at `t = 47` one survives 29 checks of `10`. H38 held only
because loop 23 stopped at `t = 45`. Past that, the number of reachable windows among loop 25's
survivors grows with `t` (`01`: 1 at `t = 46`, 15 at `t = 85`, 1,538 at `t = 160`; `10`: 1 at
`t = 47`, 682 at `t = 160`).

Every state still dies. No state at any `t <= 160` passes 120 checks of either tail, so B9 for period
2 holds on every reachable state tested. But the kill time grows with `t`. Record longest survivals
(first `t` reaching each new maximum):

| tail | (t, checks survived) |
|---|---|
| 01 | (15, 20), (26, 22), (46, 30), (89, 36), (111, 38), (112, 46) |
| 10 | (16, 19), (27, 21), (29, 23), (47, 29), (90, 35), (97, 37), (111, 47) |

Through `t = 160` the maximum is 46 (`01`) and 47 (`10`), both first reached near `t = 111`. That is
too few points to fit a growth law; the maximum is not bounded by a constant.

Cross-checks, all passed: merged states equal loop 22's tree without duplicates (`t <= 36`); the
longest survival at `t = T - 1` equals loop 22's max excess plus one at every onset 4..46; the
width-25 window counts equal loop 23's for `t = 19..45`; at every `t` a window is among the loop 25
survivors exactly when its state survives 24 checks.

**What this closes.** A fixed-width finite kill does not exist at width 25, and the growth of the
kill time with `t` makes it unlikely at any fixed width. Together with TY (a free outer cell floods
the closure at every width), the near-center window route to B9 for period 2 is closed. Merging
prefixes by their row is the useful by-product: 4,575,350 states at `t = 160` against an extrapolated 10^28
prefixes (loop 22's growth ratio 1.498 per step), so whole-row properties of the reachable set can be tested far past where loop 22 stopped.
A proof along B9 now needs a description of whole reachable rows, closed under the step, every member
of which dies.
