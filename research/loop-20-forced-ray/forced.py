"""Rebuild the inverse-rule triangle of every window that dies at the wall and find the forced cells."""
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
from left_cone_fast import counts, shl, prefix_xor, bit_mask, U64


def rebuild(T, a, Lmax, rbits):
    """Diagonals D_m (m = 0..death_step) for each window given its r' bits. Returns array (N, M, W)."""
    p = len(a); c = lambda t: int(a[(t - T) % p])
    N, W = rbits.shape
    Dm1 = np.zeros((N, W), dtype=U64); Dm2 = np.zeros((N, W), dtype=U64); Dm1[:, 0] = U64(c(T))
    diags = []
    for m in range(Lmax):
        c0, c1 = c(T + m), c(T + m + 1)
        r = (rbits[:, m >> 6] >> U64(m & 63)) & U64(1)
        b1 = U64(c1) ^ (U64(c0) | r)
        G = shl(Dm1, 1) | shl(Dm2, 2); G[:, 0] &= ~U64(3)
        P = prefix_xor(G)
        D = P ^ ((U64(0) - b1)[:, None] & np.tile(~U64(1), W))
        D[:, 0] = (D[:, 0] & ~U64(1)) | U64(c1)
        D &= bit_mask(0, m + 1, W)
        diags.append(D)
        Dm2, Dm1 = Dm1, D
    return np.stack(diags, axis=1)          # (N, M, W)


def forced_map(T, a, Lmax=80):
    keep = {}
    cs, fz, cap = counts(T, a, Lmax, cap=1 << 24, track=keep)
    R = keep['live_r_bits']; md = keep['death_step']          # windows alive before step md, all die at md
    diags = rebuild(T, a, md + 1, R)                          # includes the death diagonal m = md
    N, M, W = diags.shape
    cells = {}                                                # (m, s) -> 'forced0' | 'forced1' | 'free'
    for m in range(M):
        for s in range(1, m + 2):
            bits = (diags[:, m, s >> 6] >> U64(s & 63)) & U64(1)
            v = int(bits[0]); same = bool(np.all(bits == bits[0]))
            cells[(m, s)] = ('forced%d' % v) if same else 'free'
    return {'survivors': int(N), 'death_step': md, 'first_zero_L': fz, 'cells': cells}
