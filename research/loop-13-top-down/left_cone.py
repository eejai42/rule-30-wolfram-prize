"""The left-cone relaxation of a periodic center (loop 13).

Suppose the center column c(t)=x(0,t) were p-periodic on a window [T, T+L] with word a:
c'(t) = a[(t-T) mod p]. Column 1 on [T, T+L-1] is free: r'(t). The inverse rule

    x(i-1,t) = x(i,t+1) XOR (x(i,t) OR x(i+1,t))

then determines every cell x(-s,t) for 1 <= s <= L, T <= t <= T+L-s (a triangle). The single
seed forces zeros outside the cone and ones on its edge: x(-s,t)=0 for s>t, x(-s,s)=1, and on
the right x(1,1)=1, x(1,t)=0 for t<1 (relevant only for T<=1). The true lattice satisfies all of
this with the true (c, r); the relaxation asks whether ANY (periodic c', free r') does.

count(T, a, L) = number of r' words on [T, T+L-1] compatible with the cone.
If count reaches 0 for some L, the left cone alone excludes a p-periodic center of word a
from onset T: a TC-type certificate that never looks at the right side.

By TS, r'(t) only matters at zero-times of c' (col -1 at a one-time is c'(t+1) XOR 1), so the
effective free bits are the zero-times of a in the window.
"""
from __future__ import annotations
import itertools


def true_lattice(tmax: int):
    """x[t][i+tmax] for -tmax<=i<=tmax, 0<=t<=tmax (zeros outside the cone)."""
    W = 2 * tmax + 3
    rows = [[0] * W for _ in range(tmax + 1)]
    rows[0][tmax + 1] = 1
    for t in range(tmax):
        prev, cur = rows[t], rows[t + 1]
        for j in range(1, W - 1):
            cur[j] = prev[j - 1] ^ (prev[j] | prev[j + 1])
    return lambda i, t: rows[t][i + tmax + 1]


def cone_value(i: int, t: int):
    """Value forced by the single seed, or None when (i,t) is strictly inside the cone."""
    if abs(i) > t:
        return 0
    if abs(i) == t:
        return 1
    return None


class LeftCone:
    """Incremental checker: choose r'(T), r'(T+1), ... and verify newly computable cells."""

    def __init__(self, T: int, cprime, L: int):
        self.T, self.L = T, L
        # col[s][t-T] = x(-s, t); col[0] = c', col[-1] stored at index 'r'
        self.c = [cprime(t) for t in range(T, T + L + 2)]
        self.r = [None] * (L + 1)
        self.col = [[None] * (L + 2) for _ in range(L + 2)]  # col[s][k] = x(-s, T+k), s>=1
        self.ok_c = all(cone_value(0, t) in (None, cprime(t)) for t in range(T, T + L + 1))

    def cell(self, s, k):
        if s == 0:
            return self.c[k]
        if s == -1:
            return self.r[k]
        return self.col[s][k]

    def choose(self, m: int, bit: int) -> bool:
        """Set r'(T+m)=bit; compute the diagonal of cells x(-s, T+m-s+1), s=1..m+1; check them."""
        T = self.T
        if cone_value(1, T + m) not in (None, bit):
            return False
        self.r[m] = bit
        for s in range(1, m + 2):
            k = m - s + 1                      # time index t-T of the new cell in column -s
            v = self.cell(s - 1, k + 1) ^ (self.cell(s - 1, k) | self.cell(s - 2, k))
            self.col[s][k] = v
            forced = cone_value(-s, T + k)
            if forced is not None and forced != v:
                return False
        return True


class _Cap(Exception):
    pass


def counts(T: int, a: str, Lmax: int, cap: int = 1 << 15):
    """count(L) for L=1..Lmax: the number of compatible column-1 windows r' on [T, T+L-1],
    counted on the zero-times of c' only (TS: r' at a one-time changes nothing, so it is fixed
    to 0 unless the cone forces it). Returns (counts, first_zero_L, capped)."""
    p = len(a)
    cprime = lambda t: int(a[(t - T) % p])
    chk = LeftCone(T, cprime, Lmax)
    if not chk.ok_c:
        return [0] * Lmax, 1, False
    per_depth = [0] * Lmax

    def dfs(m):
        if m == Lmax:
            return
        forced = cone_value(1, T + m)
        bits = (forced,) if forced is not None else ((0,) if cprime(T + m) == 1 else (0, 1))
        for bit in bits:
            if chk.choose(m, bit):
                per_depth[m] += 1
                if per_depth[m] > cap:
                    raise _Cap()
                dfs(m + 1)

    try:
        dfs(0)
    except _Cap:
        k = next(i for i, v in enumerate(per_depth) if v > cap)
        return per_depth[:k] + [None] * (Lmax - k), None, True
    fz = next((i + 1 for i, v in enumerate(per_depth) if v == 0), None)
    return per_depth, fz, False


def check_true_window(T: int, L: int) -> bool:
    """The true (c, r) on [T, T+L] must pass the checker: validates the constraint code."""
    x = true_lattice(T + L + 3)
    chk = LeftCone(T, lambda t: x(0, t), L)
    assert chk.ok_c
    return all(chk.choose(m, x(1, T + m)) for m in range(L))


def primitive_words(p: int):
    for bits in itertools.product('01', repeat=p):
        w = ''.join(bits)
        if all(w != w[d:] + w[:d] for d in range(1, p)) or p == 1:
            # least period exactly p: no proper rotation equals w  <=>  no proper divisor period
            if p == 1 or not any(p % d == 0 and w == w[:d] * (p // d) for d in range(1, p)):
                yield w
