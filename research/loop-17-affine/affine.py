"""Loop 17: the surviving rows after 2T-2 and the algebraic degree of the later constraints.

TW: for a one-time t in [T, 2T-2] the constraint x(-1,t) = NOT c'(t+1) fixes the row bit at
position -(t-T+1) as a function of the bits to its right; at zero-times that bit is free. So
exactly 2^Z rows survive to 2T-2, parametrised by the bits at the zero-time positions.
Every later constraint (t >= 2T-1) is a Boolean function of those Z bits. This module
enumerates all 2^(T-1) rows, confirms TW, and computes the algebraic normal form degree of each
later constraint over the Z parameters until the set dies.
"""
from __future__ import annotations
import numpy as np


def evolve_left(rows: np.ndarray, T: int, cprime, steps: int):
    """rows: (N, T) uint8, column j = position -(T-j) at time T (so column 0 is the edge).
    Returns list of x(-1, t) arrays for t = T..T+steps, evolving the left half with x(0,t)=c'(t)."""
    N = rows.shape[0]
    cur = rows.astype(np.uint8)          # positions -T..-1
    outs = [cur[:, -1].copy()]
    for k in range(steps):
        t = T + k
        W = cur.shape[1]                 # positions -(T+k)..-1
        ext = np.zeros((N, W + 3), dtype=np.uint8)   # pad: two zeros on the left, c'(t) on the right
        ext[:, 2:W + 2] = cur
        ext[:, W + 2] = cprime(t)
        nxt = ext[:, 0:W + 1] ^ (ext[:, 1:W + 2] | ext[:, 2:W + 3])   # positions -(T+k+1)..-1
        cur = nxt
        outs.append(cur[:, -1].copy())
    return outs


def anf_degree(truth: np.ndarray, Z: int) -> int:
    """Algebraic degree of a Boolean function given as a truth table over Z bits (index = bits)."""
    f = truth.astype(np.uint8).copy()
    for i in range(Z):
        step = 1 << i
        idx = np.arange(len(f))
        hi = (idx & step) != 0
        f[hi] ^= f[idx[hi] ^ step]
    nz = np.flatnonzero(f)
    return int(max((bin(int(i)).count('1') for i in nz), default=-1))   # -1 = zero function


def analyse(T: int, a: str, Lmax: int):
    p = len(a)
    c = lambda t: int(a[(t - T) % p])
    n = T - 1
    N = 1 << n
    rows = np.zeros((N, T), dtype=np.uint8)
    rows[:, 0] = 1                                   # edge x(-T,T)=1
    idx = np.arange(N, dtype=np.uint64)
    for j in range(n):                               # bit j of idx -> position -(j+1) (column T-1-j)
        rows[:, T - 1 - j] = (idx >> np.uint64(j)) & np.uint64(1)
    col1 = evolve_left(rows, T, c, Lmax)             # col1[k] = x(-1, T+k)
    alive = np.ones(N, dtype=bool)
    one_times = [t for t in range(T, T + Lmax) if c(t) == 1]
    # phase 1: constraints up to 2T-2
    for t in one_times:
        if t > 2 * T - 2:
            break
        alive &= col1[t - T] == (1 - c(t + 1))
    zero_pos = [t - T for t in range(T, 2 * T - 1) if c(t) == 0]   # bit j <-> position -(j+1) <-> time T+j
    Z = len(zero_pos)
    surv = np.flatnonzero(alive)
    tw_ok = len(surv) == (1 << Z)
    # parameter index of each survivor: its bits at the zero-time positions
    par = np.zeros(len(surv), dtype=np.int64)
    for b, j in enumerate(zero_pos):
        par |= (((surv >> j) & 1) << b).astype(np.int64)
    tw_ok = tw_ok and len(np.unique(par)) == len(surv)
    order = np.argsort(par)
    surv = surv[order]
    # phase 2: later one-times
    rec = []
    live = np.ones(len(surv), dtype=bool)
    rank_rows = []
    for t in one_times:
        if t <= 2 * T - 2:
            continue
        f = col1[t - T][surv]                        # truth table over Z bits (index = parameter)
        want = 1 - c(t + 1)
        deg = anf_degree(f, Z) if Z <= 22 else None
        before = int(live.sum())
        vals = np.unique(f[live_prev]) if (live_prev := live.copy()).any() else np.array([])
        live &= f == want
        after = int(live.sum())
        rec.append({'t': t, 'time_past_2T': t - 2 * T, 'degree': deg, 'live_before': before, 'live_after': after,
                    'constant_on_live': bool(len(vals) == 1)})
        if after == 0:
            break
    return {'T': T, 'a': a, 'p': p, 'Z': Z, 'TW_ok': bool(tw_ok), 'survivors_at_2T-2': int(len(surv)),
            'constraints_after_2T-2': rec, 'death_time': rec[-1]['t'] if rec and rec[-1]['live_after'] == 0 else None,
            'max_degree': max((r['degree'] for r in rec if r['degree'] is not None), default=None),
            'n_constraints_to_death': len(rec) if rec and rec[-1]['live_after'] == 0 else None}
