# Loop 4 proofs: what decides the next doubling

Notation as in loops 1 and 3. `ε_k ∈ {0,1}` says whether the period doubles at offset `k`
(TL: `P_k = P_{k-1}(1+ε_k)` for `k ≥ 3`). `ones_j` is the number of ones of `y_j` in one least
period. Loop 3 reduced the whole period table to the 0/1 sequence `ε_3, ε_4, …`. This loop
finds the rule for `ε` right after a doubling.

## TM. After a doubling, the next doubling is the parity of the grandparent's ones

**Statement.** For `k ≥ 4`, if `ε_{k-1} = 1` then `ε_k ≡ ones_{k-2} (mod 2)`.

**Proof.** Put `R = P_{k-1}`. Since `k-1 ≥ 3` and `ε_{k-1} = 1`, TL gives `R = 2 P_{k-2}`.
TA with `ε_{k-1} = 1` and `Q_{k-1} = R/2` gives `y_{k-1}(t + R/2) = 1 - y_{k-1}(t)` for all `t`.
`y_{k-2}` has period `P_{k-2} = R/2`, so `y_{k-2}(t + R/2) = y_{k-2}(t)`.

By TK, `Q_k = max(P_{k-1}, P_{k-2}) = R`, so `ε_k` is the parity of `Σ_{t<R} q_k(t)`. Pair each
`t < R/2` with `t + R/2`, writing `a = y_{k-1}(t)` and `b = y_{k-2}(t)`:

    q_k(t) + q_k(t + R/2) = (a OR b) + ((1-a) OR b) = 1 + b.

Summing over `t < R/2` gives `Σ_{t<R} q_k(t) = R/2 + ones_{k-2} = P_{k-2} + ones_{k-2}`.
`P_{k-2}` is even, because `k-2 ≥ 2` and `P_2 = 2` with periods nondecreasing (TK).
Hence `ε_k ≡ ones_{k-2} (mod 2)`. ∎

## TN. Never three doublings in a row

**Statement.** For `k ≥ 5`, if `ε_{k-2} = ε_{k-1} = 1` then `ε_k = 0`.

**Proof.** `ε_{k-2} = 1` gives `y_{k-2}(t + P_{k-2}/2) = 1 - y_{k-2}(t)` (TA). So exactly half of
one period is ones: `ones_{k-2} = P_{k-2}/2`. Since `k-2 ≥ 3`, `P_{k-2} ≥ P_3 = 4`, so
`ones_{k-2}` is even. TM gives `ε_k = 0`. ∎

**Corollary.** Among any three consecutive offsets `≥ 3` at most two double. So for `k ≥ k0 ≥ 3`,
`log2 P_k ≤ log2 P_{k0} + ceil(2(k - k0)/3)`. TB gives the lower bound `P_k > ceil(k/2)`.
The observed growth (`log2 P_64 = 27`) sits far inside both bounds. Neither bound reaches the
center column.

## H16 (falsified). The rule does not hold without the doubling

The naive extension "`ε_k ≡ ones_{k-2} (mod 2)` for every `k ≥ 4`" fails at `k = 6`:
`ε_5 = 0`, `ones_4 = 4` (even), but `ε_6 = 1`. The pairing in TM needs `y_{k-1}` to be
antiperiodic, which is exactly `ε_{k-1} = 1`. When the parent plateaus, the parity of `q_k`
also depends on the overlap `Σ y_{k-1} y_{k-2}`, and no rule for that case is known.

---

### Status after this loop

| Claim | Status | Depends on |
|---|---|---|
| H15 | OPEN → PROVED_HUMAN_READABLE (it is TM, tested first on k = 4..64) | TM |
| H16 | OPEN → FALSIFIED at k = 6 | — |
| TM | PROVED_HUMAN_READABLE | TA, TK, TL |
| TN | PROVED_HUMAN_READABLE | TM, TA, TK |
