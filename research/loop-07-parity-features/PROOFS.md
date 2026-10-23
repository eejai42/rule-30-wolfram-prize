# Loop 7: the parity of a diagonal, and whether parities decide the doublings

Notation as in loops 1 to 6. `ones_k` is the number of ones of `y_k` in one least period
`P_k`; `o_k = ones_k mod 2`. TM (loop 4) says: after a doubling at `k-1`, `ε_k = o_{k-2}`.
So the parities `o_j` matter. This loop computes them.

## TO. The parity of a diagonal is read off its forcing word

**Statement.** Let `k ≥ 3`.
1. If `ε_k = 1`, then `o_k = 0`.
2. If `ε_k = 0`, then `o_k ≡ #{ t ∈ [0, P_k) : t odd and q_k(t) = 1 } (mod 2)`.

**Proof.** (1) TA gives `y_k(t + P_k/2) = 1 - y_k(t)`, so exactly half of one period is ones:
`ones_k = P_k/2`, which is even because `P_k ≥ P_3 = 4`.

(2) Here `P_k = Q_k = P` (TA) and the parity of `q_k` over one period is 0, so `q_k` has an even
number `m` of ones in `[0, P)`, at positions `s_1 < s_2 < … < s_m`. Since `y_k(0) = 0` (T0) and
`y_k(t) = XOR_{s<t} q_k(s)`, for `0 ≤ t < P` we have `y_k(t) = 1` exactly when an odd number of the
`s_i` are below `t`, that is for `t` in the disjoint intervals `[s_1+1, s_2], [s_3+1, s_4], …,
[s_{m-1}+1, s_m]`. Hence

    ones_k = Σ_{i=1}^{m/2} (s_{2i} - s_{2i-1}) ≡ Σ_{i=1}^{m} s_i  (mod 2),

because `-1 ≡ 1`. The right side counts, mod 2, the `s_i` that are odd. ∎

**Corollary (with TM).** If `ε_{k-1} = 1` and `ε_{k-2} = 0` (`k ≥ 5`), then `ε_k` is the parity of
the number of ones of `q_{k-2}` at odd positions in one period. If `ε_{k-1} = ε_{k-2} = 1`, then
`ε_k = 0` (this is TN again).

## H19 (hypothesis, tested in this loop)

`ε_k` is a function of the four parities `(ε_{k-1}, ε_{k-2}, o_{k-1}, o_{k-2})` for every `k ≥ 5`.
TM and TO decide `ε_k` whenever `ε_{k-1} = 1`. H19 asks whether the same four bits also decide
the case `ε_{k-1} = 0`. Tested on `k = 5..72` by looking for two offsets with the same four bits
and different `ε`.
