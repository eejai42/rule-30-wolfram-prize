# Loop 19: split B6 by period and take period 2 as the first target

## What loop 18 showed for the period-2 words

For `a = 01` the death window `L(T)` is exactly 64 for every onset `37 ≤ T ≤ 46` (65 for `10`,
whose first one-time at or after window 64 is one step later). Below `T = 37` the relaxation
dies earlier, at a window that grows with `T`. Across all data (loops 14 to 16) the same shape
appears for every word: a dyadic *wall* at window `2^(k+1)` for onsets `2^k ≤ T < 2^(k+1)`, at
which almost everything that survived dies; 176 of 193 cases with `T ≥ 1.6·2^k` die within
`2p` of the wall at 64, 41 of 61 at the wall 128. But the wall is not a law: three cases
(`T=60, 111001, L=80`; `T=60, 111011, L=71`; `T=124, 101111, L=144`) die past it. For the
period-2 words no exception has been seen.

## Why period 2 first

B6 quantifies over every nonconstant word. The period-2 words are the smallest case, their
left-cone relaxation shows the cleanest wall, and "the center is not eventually 2-periodic"
would already be a theorem beyond the known period-1 result (K1). So B6 is split:

* **B7 (open).** B6 for the words `01` and `10`: for every `T ≥ 2`, each TW row for a period-2
  center violates a one-time constraint at or after `2T-1`.
* **B8 (open).** B6 for every nonconstant word of least period `p ≥ 3`.

B6 follows from B7 and B8 (every nonconstant word has least period 2 or at least 3), so B6 is
marked derived and compiles `BLOCKED` by both. The chain under P1 is now
`P1 ← B1 ← B5 ← B6 ← {B7, B8}`, and the loops concentrate on B7.

## H32 and F18

**H32 (stated before computing).** The wall is exact for period 2 past onset 36: for `a = 01`
and every onset `47 ≤ T ≤ 50`, `L(T) = 64`; for `a = 10`, `L(T) = 65`. These onsets were not
reachable in loop 18 (its cap was 2^24); this loop uses 2^26.

**F18.** `L(T)` for `01` and `10` at every onset `2 ≤ T ≤ 50`, with the survivors at the death
step and the killing one-time, in one table, so the two regimes (early kill, wall) can be read
off directly.

## The conjectured law for period 2 (not proved)

Writing `k` for `⌊log2 T⌋` and `W = 2^(k+1)`: `L(T) = W` (`W+1` for `10`) once `T ≥ c·2^k` with
`c ≈ 1.15`, and `L(T) < W` below that, where the early kill grows roughly like `1.5 T` to
`1.8 T`. In forward form (TU, TV) the wall says: no row satisfying the one-time constraints for
`t ≤ T+W-3` satisfies the one at `t = T+W-1` (the ray of length `W-1 = 2^(k+1)-1` from
`(-1, T+W-2)` to the cone). The ray length one less than a power of two is where additive
cellular automata collapse (Lucas), and the alternating drive is the period of the left-edge
diagonal `w_3`. The next loop should try to prove the wall for `01` by induction on `k`.
