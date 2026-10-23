# Loop 3 proofs: the plateau case, and H7 / H4 become theorems

Notation as in loop 1 (`research/loop-01-forcing-period/PROOFS.md`): `y_k(t) = x(t-k,t)`,
`y_k(t+1) = y_k(t) XOR q_k(t)`, `q_k = y_{k-1} OR y_{k-2}`, `P_k` the least period of `y_k`,
`Q_k` the least period of `q_k`, `ε_k` the parity of `q_k` over one period, `a_j = ceil(j/2)`
the first time `y_j` is 1 (TB), and `y_j(t) = 0` for `t < a_j` (T0).

Loop 1 proved **TH**: when a parent attaining `P = max(P_{k-1},P_{k-2})` doubles (`ε = 1`), `Q_k = P`.
The open case was a parent that merely repeats. The natural guess, **H14: `y_j(P_j/2) = 1` for every
`j ≥ 1`**, would have closed it through TF at `t = 0`. H14 is **false**: `y_5` has period 8 and
`y_5(4) = 0` (period word `00010101`); 17 further offsets through 64 fail (E11). So the witness for
the open case cannot sit at `t = 0`. The witness comes from an ancestor instead.

---

## TJ. A cascade lemma: any ancestor that is 1 at `P/2` forces `Q_k = P`

**Statement.** Let `k ≥ 4` and `P = max(P_{k-1}, P_{k-2})`. If `y_j(P/2) = 1` for some `j` with
`2 ≤ j ≤ k-1`, then `Q_k = P`.

**Proof.** `Q_k | P` as in TF. Suppose, for contradiction, that `P/2` is a period of `q_k`.

*Step 1 (both parents restart from zero at `P/2`).* Let `a = a_{k-2} = ceil((k-2)/2) ≥ 1`. Since
`a_{k-1} ≥ a_{k-2}`, both parents vanish on `[0, a)`, so `q_k(t) = 0` for `t < a`. Periodicity with
period `P/2` gives `q_k(P/2 + t) = 0` for `t < a`, i.e. `y_{k-1}` and `y_{k-2}` both vanish on the window
`[P/2, P/2 + a)`.

*Step 2 (a zero window of a diagonal passes to its parents, one shorter).* If `y_j` vanishes on
`[s, s+m)` with `m ≥ 2`, then for `s ≤ u < s+m-1`: `q_j(u) = y_j(u) XOR y_j(u+1) = 0`, hence
`y_{j-1}(u) = y_{j-2}(u) = 0`. So `y_{j-1}` and `y_{j-2}` vanish on `[s, s+m-1)`.

*Step 3 (cascade).* Write `W_j` for the length of the longest zero window of `y_j` starting at
`P/2`. Step 1 gives `W_{k-1} ≥ a` and `W_{k-2} ≥ a`. Step 2 gives `W_{j-1} ≥ W_j - 1` and
`W_{j-2} ≥ W_j - 1`. By induction on `i`, `W_{k-1-2i} ≥ a - i` and `W_{k-2-2i} ≥ a - i`:
the case `i = 0` is Step 1, and from the case `i` the two parents of `y_{k-1-2i}` and of
`y_{k-2-2i}` are `y_{k-3-2i}` and `y_{k-4-2i}`, each of which inherits `≥ a - i - 1`.

*Step 4 (every offset from `k-2a` to `k-1` is 0 at `P/2`).* `W_j ≥ 1` means `y_j(P/2) = 0`. From
Step 3 this holds for `j = k-1-2i` and `j = k-2-2i` whenever `i ≤ a-1`, i.e. for every
`j ∈ [k-2a, k-1]`. For even `k`, `a = (k-2)/2` and `k-2a = 2`; for odd `k`, `a = (k-1)/2` and
`k-2a = 1`. Either way `[2, k-1] ⊆ [k-2a, k-1]`.

This contradicts the hypothesis `y_j(P/2) = 1` for some `j ∈ [2, k-1]`. So `P/2` is not a period
of `q_k`; as in TF, `Q_k` is a power of two dividing `P` but not `P/2`, hence `Q_k = P`. ∎

## TK. H7 is a theorem: `Q_k = max(P_{k-1}, P_{k-2})` for every `k ≥ 3`, and H4 with it

**Statement.** For every `k ≥ 3`, `Q_k = max(P_{k-1}, P_{k-2})`; and `P_0 ≤ P_1 ≤ P_2 ≤ …`.

**Proof.** Induction on `k`, proving both statements together.

*Base.* `y_0 ≡ 1`, so `P_0 = 1`. `q_1 = y_0 OR y_{-1} ≡ 1`, so `y_1 = 0,1,0,1,…` and `P_1 = 2`.
`q_2 = y_1 OR y_0 ≡ 1`, so `y_2 = 0,1,0,1,…` and `P_2 = 2`. `q_3 = y_2 OR y_1 = 0,1,0,1,…`, so
`Q_3 = 2 = max(P_2, P_1)`, `ε_3 = 1`, `P_3 = 4`. Thus H7 holds at `k = 3` and `P_0 ≤ P_1 ≤ P_2 ≤ P_3`.

*Step.* Let `k ≥ 4` and assume H7 for `3 ≤ j ≤ k-1` and `P_0 ≤ … ≤ P_{k-1}`. Put `P = P_{k-1}`
(the maximum, by monotonicity); `P ≥ P_3 = 4`. Let `j0` be the least index with `P_{j0} = P`.
Then `j0 ≥ 3` (because `P ≥ 4 > P_2`), `j0 ≤ k-1`, and by minimality and monotonicity
`P_{j0-1} < P`. By H7 at `j0`, `Q_{j0} = max(P_{j0-1}, P_{j0-2}) = P_{j0-1} < P = P_{j0}`.
By TA, `P_{j0} ∈ {Q_{j0}, 2Q_{j0}}`, so `P_{j0} = 2Q_{j0}` and `ε_{j0} = 1`. By TG,
`y_{j0}(P_{j0}/2) = y_{j0}(P/2) = 1`. Since `2 ≤ j0 ≤ k-1`, TJ gives `Q_k = P = max(P_{k-1}, P_{k-2})`,
which is H7 at `k`. Finally TA gives `P_k ≥ Q_k = P_{k-1}`, extending monotonicity to `k`. ∎

H4 ("least diagonal periods never decrease") is the second half of TK; TI (loop 1) gives it from
H7 as well.

## TL. The period sequence repeats or doubles, and doubles infinitely often

**Statement.** For every `k ≥ 3`, `P_k = P_{k-1} · (1 + ε_k)`. Consequently `ε_k = 1` for
infinitely many `k`.

**Proof.** By TK and TA, `P_k = Q_k (1 + ε_k) = P_{k-1} (1 + ε_k)`. If `ε_k = 1` only finitely
often, `P_k` would be eventually constant, contradicting TB (`P_k > ceil(k/2)`). ∎

So the whole period table is encoded by the 0/1 sequence `ε_3, ε_4, …` (data: E10). What
governs `ε` (why plateaus of length 7 occur at `k = 17..23`, for instance) is open.

---

### Status after this loop

| Claim | Status | Depends on |
|---|---|---|
| H14 | FALSIFIED at k = 5 (E11) | — |
| TJ | PROVED_HUMAN_READABLE | D0, T0, TB, T004, TA |
| TK | PROVED_HUMAN_READABLE | TJ, TG, TA, T004, TB |
| H7 | FINITE_VERIFIED → PROVED_HUMAN_READABLE | TK |
| H4 | FINITE_VERIFIED → PROVED_HUMAN_READABLE | TI, H7 |
| TL | PROVED_HUMAN_READABLE | H7, TA, TB |

Nothing here speaks to the center column `c(t) = y_t(t)`; Problem 1 remains exactly as open as before.
