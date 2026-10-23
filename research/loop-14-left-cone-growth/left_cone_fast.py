"""Vectorised breadth-first version of loop 13's left-cone relaxation (loop 14).

Same semantics as research/loop-13-top-down/left_cone.py (validated against it bit for bit):
count(T, a, L) = number of column-1 windows on the zero-times of the periodic center word a
(onset T) whose inverse-rule triangle agrees with the single-seed cone. Here the live set of
partial windows is kept as a numpy array of bit-packed diagonals, so the search reaches onsets
where the plain DFS cannot.

Diagonal of step m: bit s = x(-s, T+m-s+1) for 1 <= s <= m+1, bit 0 = c'(T+m+1).
  bit 1 = c'(T+m+1) XOR (c'(T+m) OR r'(T+m))
  bit s = bit s-1 XOR (D_{m-1}[s-1] OR D_{m-2}[s-2])          (s >= 2)
Cone constraints at step m: bits s >= ceil((T+m+2)/2) must be 0, except s = (T+m+1)/2 (the
edge), which must be 1. Requires T >= 2 (loop 13 covers T = 1).
"""
from __future__ import annotations
import numpy as np

U64 = np.uint64
ALL = U64(0xFFFFFFFFFFFFFFFF)


def shl(a: np.ndarray, k: int) -> np.ndarray:
    out = a << U64(k)
    if a.shape[1] > 1:
        out[:, 1:] |= a[:, :-1] >> U64(64 - k)
    return out


def prefix_xor(a: np.ndarray) -> np.ndarray:
    x = a.copy()
    for k in (1, 2, 4, 8, 16, 32):
        x ^= x << U64(k)
    # carry the parity of each word into all higher words
    W = a.shape[1]
    if W > 1:
        par = (x >> U64(63)) & U64(1)           # parity of each word = top bit of its prefix
        cum = np.zeros_like(par[:, 0])
        for w in range(1, W):
            cum ^= par[:, w - 1]
            x[:, w] ^= (U64(0) - cum)           # 0 or all-ones
    return x


def bit_mask(lo: int, hi: int, W: int) -> np.ndarray:
    """Mask with bits lo..hi (inclusive) set, as a (W,) uint64 vector."""
    m = np.zeros(W, dtype=U64)
    for s in range(max(lo, 0), hi + 1):
        m[s >> 6] |= U64(1) << U64(s & 63)
    return m


def counts(T: int, a: str, Lmax: int, cap: int = 1 << 22):
    """Live-set sizes per window length L=1..Lmax. Returns (counts, first_zero_L, capped)."""
    assert T >= 2
    p = len(a)
    c = lambda t: int(a[(t - T) % p])
    W = (Lmax + 3 + 63) // 64
    Dm1 = np.zeros((1, W), dtype=U64)     # D_{-1}: only bit 0 matters: c'(T)
    Dm2 = np.zeros((1, W), dtype=U64)     # D_{-2}: bit 0 = c'(T-1), never used for s>=2 at m=0? (D_{m-2}[0] at m=0 -> s=2 > m+1, masked)
    Dm1[:, 0] = U64(c(T))
    out = []
    for m in range(Lmax):
        N = Dm1.shape[0]
        c0, c1 = c(T + m), c(T + m + 1)
        # branch on r'(T+m) only at zero-times
        if c0 == 0:
            Dm1 = np.repeat(Dm1, 2, axis=0)
            Dm2 = np.repeat(Dm2, 2, axis=0)
            r = np.tile(np.array([0, 1], dtype=U64), N)
            b1 = U64(c1) ^ (U64(c0) | r)
        else:
            b1 = np.full(N, c1 ^ 1, dtype=U64)
        G = shl(Dm1, 1) | shl(Dm2, 2)
        G[:, 0] &= ~U64(3)                       # clear bits 0,1
        P = prefix_xor(G)
        D = P ^ ((U64(0) - b1)[:, None] & np.tile(~U64(1), W))   # XOR seed b1 into every bit >= 1
        D[:, 0] = (D[:, 0] & ~U64(1)) | U64(c1)                  # bit 0 = c'(T+m+1)
        keep = bit_mask(0, m + 1, W)
        D &= keep
        # constraints
        lo = -(-(T + m + 2) // 2)                 # ceil((T+m+2)/2)
        zero_mask = bit_mask(lo, m + 1, W)
        want = np.zeros(W, dtype=U64)
        if (T + m + 1) % 2 == 0:
            e = (T + m + 1) // 2
            if 1 <= e <= m + 1:
                zero_mask[e >> 6] |= U64(1) << U64(e & 63)
                want[e >> 6] |= U64(1) << U64(e & 63)
        ok = np.all((D & zero_mask) == want, axis=1)
        Dm2, Dm1 = Dm1[ok], D[ok]
        out.append(int(Dm1.shape[0]))
        if Dm1.shape[0] == 0:
            return out + [0] * (Lmax - m - 1), m + 1, False
        if Dm1.shape[0] > cap:
            return out + [None] * (Lmax - m - 1), None, True
    return out, None, False
