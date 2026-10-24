# Loop 17: the free bits of the relaxation, and how nonlinear the kill is

Joint work with a second session on this repo, which read the loop 14 to 16 tables and
proposed the lemma TW below and the observation that the live set of the search is exactly
2^Z. Both were re-derived and re-checked here before use.

## TW. Exactly 2^Z rows survive to time 2T-2, parametrised by the zero-times

Let `Z` be the number of zero-times of `c'` in `[T, 2T-2]`.

**Statement.** In the forward form (TU), the one-time constraints at `T ≤ t ≤ 2T-2` fix the
row bit at position `-(t-T+1)` as a function of the row bits to its right; the bits at the
positions `-(t-T+1)` of zero-times `t` are unconstrained. Hence exactly `2^Z` rows satisfy every
constraint up to `2T-2`, in bijection with the assignments of those `Z` bits, and every
constraint at a one-time `t ≥ 2T-1` is a Boolean function of those `Z` bits alone.

**Proof.** By TV with `j = t-T`, `x(-1,t) = R(-(t-T+1)) XOR P_t` where `P_t` is the parity of
`x(-i,t-i) OR x(-i+1,t-i)` over `i = 1..t-T`. The cell `(-i, t-i)` is `t-T-i` steps after
time `T`, so it depends only on row positions in `[-i-(t-T-i), -i+(t-T-i)] = [-(t-T), t-T-2i]`,
and its neighbour `(-i+1, t-i)` on positions `≥ -(t-T)+1`. So `P_t` depends only on positions
`-1 .. -(t-T)`, strictly right of `-(t-T+1)`, and the constraint `x(-1,t) = NOT c'(t+1)` reads
`R(-(t-T+1)) = P_t XOR NOT c'(t+1)`: one bit fixed by the bits to its right. Running `t` from
`T` to `2T-2` covers positions `-1 .. -(T-1)`, the whole free row; zero-times leave their bit
free. For `t ≥ 2T-1` the leading term of TV is the edge (1) or outside the cone (0), so the
constraint is a function of the row, hence of the `Z` free bits. ∎

The search's live set equals `2^Z` exactly in 3,837 of the 3,841 completed cases of loop 14
(the other four die before the window reaches `2T`), as TW predicts.

## B6 and the derivation of B5

**B6 (open).** For every `T ≥ 2` and every nonconstant periodic word, each of the `2^Z` rows
of TW violates `x(-1,t) = NOT c'(t+1)` at some one-time `t ≥ 2T-1`.

**Derivation of B5 from TU, TW and B6.** By TU the relaxation at window `L` is the set of rows
satisfying the one-time constraints with `t ≤ T+L-1`. By TW the rows satisfying those with
`t ≤ 2T-2` are the `2^Z` parametrised rows. By B6 each of them fails some later one-time, and
there are finitely many of them, so some `L` excludes them all. For `T = 1` the window starting
at onset 2 is contained in the one starting at onset 1, so the `T = 2` case covers it. ∎

B6 is B5 with the free data named: `Z` bits, and constraints that begin at `2T-1`. The ledger
moves the open child of B1 from B5 to B6; B5 compiles `BLOCKED` by B6.

## H30 and F16: how nonlinear are the killing constraints?

Each constraint at `t ≥ 2T-1` is a Boolean function `f_t` of the `Z` bits. If these were affine
over GF(2), B6 would be linear algebra: an inconsistent affine system in `Z` unknowns. A kill of
many survivors at one step means `f_t` is constant (and wrong) on the surviving set, which is
compatible with both pictures.

**H30 (stated before the full computation; a four-case smoke test showed degrees near Z).**
For every nonconstant primitive word of period `p ≤ 5` and every onset `4 ≤ T ≤ 18`, the killing
constraints are maximally nonlinear: the largest algebraic degree among the `f_t` applied before
death is at least `Z-1`. If this holds, no proof of B6 can go through linear algebra over the
free bits; the argument has to be combinatorial.

**F16.** For each `(T,a)`: `Z`, the TW check, and for each later one-time constraint until death
its algebraic degree, the live counts before and after, and whether it was constant on the live
set (a mass kill). Output: `research/loop-17-affine/affine.json`.
