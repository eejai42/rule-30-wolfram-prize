# Loop 9: the left edge of the light cone

Every claim so far concerns the **right-edge** diagonals `y_k(t) = x(t-k, t)`, at distance `k`
from the right boundary `x(t,t) = 1`. The **left-edge** diagonals are

    w_k(t) = x(-t+k, t),    k ≥ 0,

at distance `k` from the left boundary `x(-t,t) = 1`. With `w_{-1} = w_{-2} = 0` and
`w_k(0) = [k = 0]`, Rule 30 gives, for every `t ≥ 0`,

    w_k(t+1) = w_{k-2}(t) XOR ( w_{k-1}(t) OR w_k(t) ).          (L)

(Cells outside the cone are 0, so (L) also holds before the diagonal enters the cone.)
Unlike the right edge, (L) is not linear in `w_k`: if `w_{k-1}(t) = 1` then
`w_k(t+1) = 1 - w_{k-2}(t)`, otherwise `w_k(t+1) = w_k(t) XOR w_{k-2}(t)`.

## TR. Left-edge diagonals are eventually periodic, with power-of-two periods

**Statement.** For every `k ≥ 0`, `w_k` is eventually periodic, and its least eventual period
is a power of two that divides `2^k`.

**Proof.** Induction on `k`. `w_0 ≡ 1` (left boundary, T0) has period 1; `w_{-1}, w_{-2} ≡ 0`.
Suppose `w_{k-1}` and `w_{k-2}` are periodic from some time `T0` with least periods `2^a` and
`2^b`, both dividing `2^{k-1}`. Then the input pair `(w_{k-1}(t), w_{k-2}(t))` is periodic from
`T0` with period `P = 2^{max(a,b)}`. For `t ≥ T0` put `σ(t) = (t mod P, w_k(t))`. By (L), `σ(t+1)`
is a function of `σ(t)`, and there are only `2P` states, so `σ` is eventually periodic. The first
component cycles with period exactly `P`, so the cycle length of `σ` is a multiple of `P` and at
most `2P`: it is `P` or `2P`. Hence `w_k` is eventually periodic with period `P` or `2P`, which
divides `2^k`, and its least eventual period divides that, so it is a power of two dividing `2^k`. ∎

TR is the left-edge counterpart of T004. It is no closer to the center: the center is
`c(t) = y_t(t) = w_t(t)`, the diagonal whose offset grows with `t`.

**Computing the periods exactly.** In the proof, the state at times `T0, T0+P, T0+2P` decides
everything: if `w_k(T0+P) = w_k(T0+2P)` the period is `P` from `T0+P`; otherwise it is `2P` from
`T0`. So each `w_k` is certified by simulating (L) to `T0 + 3P`, then shrinking the period and the
onset to their least values by direct comparison. No sampling or extrapolation is involved.

## H22 (hypothesis, tested in this loop)

The left edge grows at most half as fast as the right edge: for every `k ≥ 1`,
`log2(least eventual period of w_k) ≤ (1/2) log2 P_k`, where `P_k` is the right-edge period
(E19). Offsets 1 to 8 were looked at before stating it; the test covers `k = 9` upward.
