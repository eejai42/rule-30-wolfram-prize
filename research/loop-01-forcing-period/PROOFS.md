# Loop 1 proofs: the forcing word of a diagonal

Notation (from research_v05/REPORT.md §3). `x(i,t)` is Rule 30 from the single seed,
`x(i,t+1) = x(i-1,t) XOR (x(i,t) OR x(i+1,t))`. For k ≥ 0 the **diagonal** is
`y_k(t) = x(t-k, t)`, with `y_{-1} = y_{-2} = 0`. Then

    y_k(t+1) = y_k(t) XOR q_k(t),     q_k = y_{k-1} OR y_{k-2}      (R)

`q_k` is the **forcing word** of diagonal k. Known inputs:

- **T0** (cone support, boundaries): `y_0 ≡ 1`; `y_j(t) = 0` for `t < ceil(j/2)`, so `y_j(0) = 0` for every `j ≥ 1`.
- **T004**: `y_k` is purely periodic with least period `P_k` dividing `2^k`.
- **TA**: if `q` is purely periodic with least period `Q` and `y(t+1) = y(t) XOR q(t)`, then `y(t+Q) = y(t) XOR ε` where `ε` is the XOR of `q` over one period, and the least period of `y` is `Q` if `ε = 0`, `2Q` if `ε = 1`. Its proof also shows: every period of a purely periodic sequence is a multiple of its least period.

Write `Q_k` for the least period of `q_k` and `ε_k` for the XOR of `q_k` over one period, so `P_k = Q_k (1 + ε_k)`.

---

## TF. If `q_k(P/2) = 1` then `Q_k = P`

**Statement.** Let `k ≥ 3` and `P = max(P_{k-1}, P_{k-2})`. If `q_k(P/2) = 1`, then the least period of `q_k` is exactly `P`.

**Proof.** `P_{k-1}` and `P_{k-2}` are powers of two (T004), so the larger is a multiple of the smaller and `P` is a common period of `y_{k-1}` and `y_{k-2}`, hence a period of `q_k`. By TA's divisibility remark, `Q_k | P`.

`P ≥ 2`: `y_{k-1}` is not constant, because `y_{k-1}(0) = 0` (T0, `k-1 ≥ 1`) while `y_{k-1}(ceil((k-1)/2)) = 1` (Theorem B of the report, which only uses T0). So `P_{k-1} ≥ 2` and `P/2` is an integer.

`q_k(0) = y_{k-1}(0) OR y_{k-2}(0) = 0` because `k-2 ≥ 1` (T0). By hypothesis `q_k(P/2) = 1 ≠ q_k(0)`, so `P/2` is **not** a period of `q_k`.

If `Q_k ≠ P`, then `Q_k` is a power of two properly dividing `P`, so `Q_k | P/2`, and `P/2` would be a period of `q_k` (a multiple of its least period). Contradiction. Hence `Q_k = P`. ∎

## TG. A doubling diagonal is 1 at its half period

**Statement.** If `j ≥ 1` and `ε_j = 1`, then `y_j(P_j / 2) = 1`.

**Proof.** By TA, `P_j = 2 Q_j` and `y_j(t + Q_j) = y_j(t) XOR 1` for all `t`. Take `t = 0`: `y_j(Q_j) = NOT y_j(0) = NOT 0 = 1` (T0). And `Q_j = P_j / 2`. ∎

## TH. A doubling parent forces the full period

**Statement.** Let `k ≥ 3`, `P = max(P_{k-1}, P_{k-2})`. If some `j ∈ {k-1, k-2}` has `P_j = P` and `ε_j = 1`, then `Q_k = P`.

**Proof.** By TG, `y_j(P/2) = y_j(P_j/2) = 1`. Then `q_k(P/2) = y_{k-1}(P/2) OR y_{k-2}(P/2) ≥ y_j(P/2) = 1`. Apply TF. ∎

**What TH does not cover.** The case where every parent attaining `P` has `ε = 0` (a plateau feeding the next step). That case is hypothesis **H7** below, tested finitely in this loop and attacked in a later loop.

## TI. H7 implies H4

**H7 (hypothesis).** For all `k ≥ 3`, `Q_k = max(P_{k-1}, P_{k-2})`.

**H4 (hypothesis).** `P_k` is nondecreasing in `k`.

**Statement.** H7 implies H4.

**Proof.** For `k ≥ 3`, TA gives `P_k ≥ Q_k`, and H7 gives `Q_k ≥ P_{k-1}`. For the first values: `P_0 = 1` (`y_0 ≡ 1`); `q_1 = y_0 OR y_{-1} ≡ 1` so `y_1` alternates from `y_1(0)=0`, `P_1 = 2`; `q_2 = y_1 OR y_0 ≡ 1` so `y_2` alternates, `P_2 = 2`. Thus `P_0 ≤ P_1 ≤ P_2 ≤ P_3 ≤ …`. ∎

**Corollary (under H7).** `P_k = P_{k-1} (1 + ε_k)` for all `k ≥ 3`: the period either repeats or doubles, and never does anything else.

---

### Status after this loop

| Claim | Status | Depends on |
|---|---|---|
| TF | PROVED_HUMAN_READABLE | D0, T0, T004, TA, TB |
| TG | PROVED_HUMAN_READABLE | T0, TA |
| TH | PROVED_HUMAN_READABLE | TF, TG |
| TI | PROVED_HUMAN_READABLE | T004, TA |
| H7 | FINITE_VERIFIED through k = 51 (data E1, check E8) | T004 |
| H4 | FINITE_VERIFIED through k = 51, and reduced to H7 by TI | TI, H7 |

None of this touches the center column; it only sharpens the diagonal-period machinery that Problem 1 would eventually have to use.
