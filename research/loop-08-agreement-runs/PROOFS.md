# Loop 8: agreement runs of the center column

`c(t) = x(0,t)` is the center column. For a shift `p ≥ 1`, an **agreement run** is a maximal
interval of consecutive `t` with `c(t) = c(t+p)`.

## TQ. Problem 1 is the finiteness of agreement runs

**Statement.** The center column is eventually periodic with period `p` if and only if some
agreement run for shift `p` is infinite. Consequently, if for every `p ≥ 1` there is a finite
bound `L_p` on the length of the agreement runs for shift `p`, then the center is not eventually
periodic (Problem 1, P1).

**Proof.** "Eventually periodic with period `p` from onset `T`" means `c(t) = c(t+p)` for all
`t ≥ T`, which is an infinite agreement run starting at or before `T`. Conversely an infinite
agreement run starting at `T` is exactly that statement. If every run for shift `p` has length
at most `L_p`, none is infinite, so no onset works for `p`; if this holds for every `p`, the
center is not eventually periodic. ∎

TQ is a reformulation, not progress on P1 by itself. It says which finite statistic a proof
would have to control, and it lets finite data be stated in that currency. TC (loop 0, the v05
report) is the two-column version: every agreement run of the pair (column 0, column 1) with
shift `p` starting at `T` ends by `2T + p`. That bound grows with `T`; a uniform `L_p` would not.

## H21 (hypothesis, tested in this loop)

On the first `N = 2^20` center bits, for every shift `1 ≤ p ≤ 4096`, every agreement run has
length at most `2·log2(N) + 4 = 44`.

The bound was fixed before computing. For comparison, a uniformly random sequence of this
length would have a longest run near `log2(N) = 20` per shift, and about `20 + log2(4096) = 32`
for the worst of 4096 shifts. `p = 1` runs are the constant runs of H13 (longest 22).
