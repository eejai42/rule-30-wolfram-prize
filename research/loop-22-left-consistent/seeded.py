"""Left-consistent sequences (loop 22).

TX: the left half x(i,t), i <= -1, is a causal function of the center c(0..t-1) and the seed, and
the forward rule at column 0 reads c(t+1) = x(-1,t) XOR (c(t) OR x(1,t)). So whenever c(t) = 1,
    c(t+1) = NOT x(-1,t)                                                          (*)
with x(-1,t) computed from c's own past. A sequence obeying (*) is *left-consistent*. The true
center is one. This module grows the tree S of left-consistent prefixes from the seed: after a 1
the next bit is forced, after a 0 it branches.

Row encoding: bit 0 = c(t) (position 0), bit j = x(-j, t) for j >= 1. One step of the left half:
    new bit j = old bit (j+1) XOR (old bit j OR old bit (j-1)),   j >= 1
(left neighbour of position -j is -(j+1), right neighbour is -(j-1)); bit 0 then gets c(t+1).
"""
from __future__ import annotations
import numpy as np

U64 = np.uint64


def shl(a, k=1):
    out = a << U64(k)
    out[:, 1:] |= a[:, :-1] >> U64(64 - k)
    return out


def shr(a, k=1):
    out = a >> U64(k)
    out[:, :-1] |= a[:, 1:] << U64(64 - k)
    return out


def step_left(B, t, Wd):
    """Rows at time t -> left half at time t+1 with bit 0 cleared. Keeps bits 1..t+1."""
    N = (B >> U64(1)) if False else None
    new = shr(B) ^ (B | shl(B))
    new[:, 0] &= ~U64(1)
    # mask to bits 1..t+1 (cone): positions beyond -(t+1) are zero anyway by construction
    return new


def x_m1(B):
    return (B[:, 0] >> U64(1)) & U64(1)


def grow(Tmax, Wd, cap=1 << 27):
    """Yield (t, B) for t = 0..Tmax: all left-consistent prefixes c(0..t) with their rows at time t."""
    B = np.zeros((1, Wd), dtype=U64)
    B[:, 0] = U64(1)                       # c(0) = 1, nothing on the left
    yield 0, B
    for t in range(Tmax):
        c = B[:, 0] & U64(1)
        xm1 = x_m1(B)
        L = step_left(B, t, Wd)
        one = c == U64(1)
        # forced children
        F = L[one].copy(); F[:, 0] |= (xm1[one] ^ U64(1))
        # branching children of zeros
        Z = L[~one]
        Z0 = Z.copy(); Z1 = Z.copy(); Z1[:, 0] |= U64(1)
        B = np.concatenate([F, Z0, Z1], axis=0)
        if B.shape[0] > cap:
            raise MemoryError(f'live set {B.shape[0]} at t={t + 1}')
        yield t + 1, B


def tail_death(B, T, a, Lmax, Wd, bit=None):
    """B: rows at time T-1 for prefixes c(0..T-1). Tail c(T+j) = a[j mod p].
    Returns, per prefix, the first t >= T-1 at which (*) fails (or -1 if none within Lmax)."""
    p = len(a)
    N = B.shape[0]
    death = np.full(N, -1, dtype=np.int64)
    alive = np.ones(N, dtype=bool)
    cur = B.copy()
    t = T - 1
    for j in range(Lmax):
        c = cur[:, 0] & U64(1)
        nxt_c = U64(int(a[j % p])) if bit is None else U64(bit(j))
        viol = (c == U64(1)) & ((x_m1(cur) ^ U64(1)) != nxt_c)
        newly = alive & viol
        death[newly] = t
        alive &= ~viol
        if not alive.any():
            break
        cur = step_left(cur, t, Wd)
        cur[:, 0] |= nxt_c
        t += 1
    return death, alive
