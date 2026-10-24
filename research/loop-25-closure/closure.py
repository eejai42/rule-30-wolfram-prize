"""Loop 25 (H40): an inductive over-approximation of the near-center windows of left-consistent sequences.

A window of width E+1 at time t is (c(t), x(-1,t), ..., x(-E,t)), encoded as in loop 23 (bit 0 =
c(t), bit j = x(-j,t)). One step of the left half gives bits 1..E-1 of the next window from the
current one; bit E needs x(-(E+1),t), which the window does not hold, so the step allows both
values. The next center bit is forced to NOT x(-1,t) after a 1 (TX) and free after a 0.
closure(E, base) is the smallest set containing `base` and closed under that step. By induction
on t it contains every window a left-consistent sequence shows at every time t >= t0 when `base`
holds every window shown at t0.
"""
from __future__ import annotations
import numpy as np

U = np.uint64


def successors(w: np.ndarray, E: int) -> np.ndarray:
    """All successor windows of the windows w (uint64 array)."""
    full = U((1 << (E + 1)) - 1)
    core = ((w >> U(1)) ^ (w | (w << U(1)))) & full      # bits 1..E-1 valid, bit E is a guess
    core &= ~U(1)                                        # clear bit 0 (the next c)
    core &= ~(U(1) << U(E))                              # clear bit E (unknown)
    hiE = [core, core | (U(1) << U(E))]
    c = w & U(1)
    xm1 = (w >> U(1)) & U(1)
    out = []
    for base in hiE:
        forced = c == U(1)
        out.append(base[forced] | (xm1[forced] ^ U(1)))  # after a 1: forced
        free = ~forced
        out.append(base[free])                           # after a 0: next bit 0
        out.append(base[free] | U(1))                    # after a 0: next bit 1
    return np.concatenate(out)


def closure(E: int, base: np.ndarray, max_states: int = 1 << 27):
    """Smallest superset of base closed under successors(). Returns sorted unique uint64 array."""
    seen = np.zeros(1 << (E + 1), dtype=bool)
    frontier = np.unique(base)
    seen[frontier.astype(np.int64)] = True
    rounds = 0
    while frontier.size:
        nxt = np.unique(successors(frontier, E))
        new = nxt[~seen[nxt.astype(np.int64)]]
        seen[new.astype(np.int64)] = True
        frontier = new
        rounds += 1
        if seen.sum() > max_states:
            raise MemoryError
    return np.flatnonzero(seen).astype(U), rounds


def survivors(win: np.ndarray, E: int, a: str) -> np.ndarray:
    """Boolean mask: windows that pass all E checks (times t..t+E-1) under the tail a from t+1."""
    w = win.copy()
    alive = np.ones(len(w), dtype=bool)
    p = len(a)
    for j in range(E):
        c = w & U(1)
        nxt = U(int(a[j % p]))
        xm1 = (w >> U(1)) & U(1)
        alive &= ~((c == U(1)) & ((xm1 ^ U(1)) != nxt))
        new = ((w >> U(1)) ^ (w | (w << U(1)))) & ~U(1)
        new |= nxt
        valid = E - j - 1
        w = new & ((U(1) << U(valid + 1)) - U(1))
    return alive
