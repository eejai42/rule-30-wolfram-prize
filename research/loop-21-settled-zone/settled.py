"""Settled-zone relaxation (loop 21): the left-cone relaxation with every settled left-edge
diagonal imposed, not only the cone.

Diagonal w_k(t) = x(-t+k, t) is eventually periodic (TR) with certified onset o_k and period word
(research/left_edge.py, loops 9-12). A cell (-s, t) lies on diagonal k = t - s; it is *settled*
when t >= o_k, and then its value is the known periodic value. The true lattice satisfies all of
these, so imposing them on the periodic-center relaxation is a legitimate strengthening of
B5/B6 (it still refutes a periodic center). The cone of T0 is the special case k <= 2.

counts_settled(T, a, Lmax): live-set sizes per window, as left_cone_fast.counts, but each new
diagonal cell on a settled diagonal must equal w_k(t).
"""
from __future__ import annotations
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
from left_edge import BASE, certify, Seq
from left_cone_fast import shl, prefix_xor, bit_mask, U64

_W: dict[int, Seq] = dict(BASE)


def wseq(k: int) -> Seq:
    if k < 0:
        return BASE[-1]
    while max(_W) < k:
        j = max(_W) + 1
        _W[j] = certify(j, _W[j - 1], _W[j - 2])
    return _W[k]


def settled_value(s: int, t: int):
    """Known value of x(-s,t) if the cell is settled (or outside the cone), else None."""
    k = t - s
    if k < 0:
        return 0
    w = wseq(k)
    return w.at(t) if t >= w.o else None


def frontier(T: int) -> int:
    """Smallest s >= 1 such that the row-T cell (-s, T) is settled."""
    s = 1
    while settled_value(s, T) is None:
        s += 1
    return s


def counts_settled(T: int, a: str, Lmax: int, cap: int = 1 << 24, death: dict | None = None, mode: str = 'exact'):
    """mode 'exact': settled cells take their certified values (S1).
    mode 'periodic': cells on diagonals k<=2 take their values (T0); a settled cell on a diagonal
    k>=3 must equal the cell one period earlier on the same diagonal when that cell is settled
    too (S2: uses only TR-type periodicity plus the certified onsets and periods, never the words)."""
    assert T >= 2 and mode in ('exact', 'periodic')
    p = len(a)
    c = lambda t: int(a[(t - T) % p])
    W = (Lmax + 3 + 63) // 64
    Dm1 = np.zeros((1, W), dtype=U64); Dm2 = np.zeros((1, W), dtype=U64); Dm1[:, 0] = U64(c(T))
    out = []
    hist_d = {}                       # past diagonals (periodic mode), hist_d[m] = D_m after filtering
    for m in range(Lmax):
        N = Dm1.shape[0]
        c0, c1 = c(T + m), c(T + m + 1)
        if c0 == 0:
            Dm1 = np.repeat(Dm1, 2, axis=0); Dm2 = np.repeat(Dm2, 2, axis=0)
            if mode == 'periodic':
                hist_d = {j: np.repeat(h, 2, axis=0) for j, h in hist_d.items()}
            r = np.tile(np.array([0, 1], dtype=U64), N)
            b1 = U64(c1) ^ (U64(c0) | r)
        else:
            b1 = np.full(N, c1 ^ 1, dtype=U64)
        G = shl(Dm1, 1) | shl(Dm2, 2); G[:, 0] &= ~U64(3)
        P = prefix_xor(G)
        D = P ^ ((U64(0) - b1)[:, None] & np.tile(~U64(1), W))
        D[:, 0] = (D[:, 0] & ~U64(1)) | U64(c1)
        D &= bit_mask(0, m + 1, W)
        mask = np.zeros(W, dtype=U64); want = np.zeros(W, dtype=U64)
        fails = np.zeros_like(D)
        for s in range(1, m + 2):
            t = T + m - s + 1; k = t - s
            if mode == 'exact' or k <= 2:
                v = settled_value(s, t)
                if v is not None:
                    mask[s >> 6] |= U64(1) << U64(s & 63)
                    if v:
                        want[s >> 6] |= U64(1) << U64(s & 63)
            else:
                w = wseq(k)
                if t >= w.o and t - w.p >= max(w.o, T) and s - w.p >= 0:
                    cur = (D[:, s >> 6] >> U64(s & 63)) & U64(1)
                    s2, m2 = s - w.p, m - 2 * w.p
                    if s2 == 0:
                        prev = np.full(D.shape[0], c(t - w.p), dtype=U64)
                    else:
                        prev = (hist_d[m2][:, s2 >> 6] >> U64(s2 & 63)) & U64(1)
                    fails[:, s >> 6] |= (cur ^ prev) << U64(s & 63)
        fails |= (D & mask) ^ want
        ok = ~np.any(fails, axis=1)
        if death is not None and not ok.any():
            hist = {}
            for s in range(1, m + 2):
                n = int(((fails[:, s >> 6] >> U64(s & 63)) & U64(1)).sum())
                if n:
                    hist[s] = n
            death.update({'window_L': m + 1, 'live_before': int(D.shape[0]), 'fail_hist_by_column': {str(s): n for s, n in hist.items()},
                          'fail_col_min': min(hist), 'fail_col_max': max(hist)})
        Dm2, Dm1 = Dm1[ok], D[ok]
        if mode == 'periodic':
            hist_d = {j: h[ok] for j, h in hist_d.items() if j >= m - 40}
            hist_d[m] = Dm1
        out.append(int(Dm1.shape[0]))
        if Dm1.shape[0] == 0:
            return out + [0] * (Lmax - m - 1), m + 1, False
        if Dm1.shape[0] > cap:
            return out + [None] * (Lmax - m - 1), None, True
    return out, None, False


def check_true_window(T: int, L: int) -> bool:
    """The true (c, r) must satisfy every settled constraint: run the same incremental checker
    on the true columns (no branching)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-13-top-down'))
    from left_cone import true_lattice, LeftCone
    x = true_lattice(T + L + 3)
    chk = LeftCone(T, lambda t: x(0, t), L)
    for m in range(L):
        assert chk.choose(m, x(1, T + m)), (T, m)
        for s in range(1, m + 2):
            v = settled_value(s, T + m - s + 1)
            if v is not None and chk.col[s][m - s + 1] != v:
                return False
            if chk.col[s][m - s + 1] != x(-s, T + m - s + 1):
                return False
    return True
