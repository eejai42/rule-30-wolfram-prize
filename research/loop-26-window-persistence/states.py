"""Loop 26: the reachable states of left-consistent sequences, merged.

A left-consistent prefix c(0..t) acts on its future only through its row at time t (c(t) and the
left half x(-1..,t), loop 22 encoding: bit 0 = c(t), bit j = x(-j,t)): the next rows and every later
one-time check are functions of that row and the next center bits. So prefixes with equal rows can
be merged. grow_states yields, for each t, the distinct rows of all left-consistent prefixes; it is
loop 22's grow() followed by np.unique at every step.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-22-left-consistent'))
from seeded import step_left, x_m1, U64


def grow_states(Tmax: int, Wd: int | None = None, cap: int = 1 << 26):
    """Yield (t, S) for t = 0..Tmax: the distinct rows at time t over all left-consistent prefixes.
    Wd (64-bit words per row) defaults to the Tmax + 2 bits the rows need; pass more to run tails on."""
    Wd = Wd or (Tmax + 2 + 63) // 64
    S = np.zeros((1, Wd), dtype=U64)
    S[:, 0] = U64(1)
    yield 0, S
    for t in range(Tmax):
        c = S[:, 0] & U64(1)
        xm1 = x_m1(S)
        L = step_left(S, t, Wd)
        one = c == U64(1)
        F = L[one].copy(); F[:, 0] |= (xm1[one] ^ U64(1))
        Z = L[~one]
        Z1 = Z.copy(); Z1[:, 0] |= U64(1)
        S = np.unique(np.concatenate([F, Z, Z1], axis=0), axis=0)
        if S.shape[0] > cap:
            raise MemoryError(f'{S.shape[0]} states at t={t + 1}')
        yield t + 1, S
