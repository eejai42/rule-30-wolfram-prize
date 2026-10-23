"""Exact left-edge diagonal certifier (shared from loop 10 on; loop 9 keeps its own copy).

w_k(t) = x(-t+k, t) obeys w_k(t+1) = w_{k-2}(t) XOR (w_{k-1}(t) OR w_k(t)), w_{-1}=w_{-2}=0,
w_k(0) = [k=0]. Given parents periodic from T0 with period P, simulating to T0+3P decides
w_k's eventual period (P or 2P) and onset exactly (research/loop-09-left-edge/PROOFS.md).
"""


class Seq:
    """Eventually periodic 0/1 sequence: explicit bytes up to onset+period, then periodic."""
    def __init__(self, data: bytearray, onset: int, period: int):
        self.d, self.o, self.p = data, onset, period

    def at(self, t):
        return self.d[t] if t < self.o + self.p else self.d[self.o + (t - self.o) % self.p]

    def block(self, n):
        out = bytearray(self.d[:min(n, self.o + self.p)])
        while len(out) < n:
            out += self.d[self.o:self.o + self.p]
        return out[:n]


BASE = {-2: Seq(bytearray([0]), 0, 1), -1: Seq(bytearray([0]), 0, 1), 0: Seq(bytearray([1]), 0, 1)}


def certify(k, a: Seq, b: Seq) -> Seq:
    """w_k from parents a = w_{k-1}, b = w_{k-2}."""
    T0 = max(a.o, b.o)
    P = max(a.p, b.p)
    n = T0 + 3 * P + 1
    A, B = a.block(n), b.block(n)
    w = bytearray(n)
    w[0] = 1 if k == 0 else 0
    for t in range(n - 1):
        w[t + 1] = B[t] ^ (A[t] | w[t])
    if w[T0 + P] == w[T0 + 2 * P]:
        onset, L = T0 + P, P
    else:
        onset, L = T0, 2 * P
    while L > 1 and w[onset:onset + L // 2] == w[onset + L // 2:onset + L]:
        L //= 2
    while onset > 0 and w[onset - 1] == w[onset - 1 + L]:
        onset -= 1
    assert all(w[t] == w[t + L] for t in range(onset, n - L)), k
    return Seq(bytearray(w[:onset + L]), onset, L)
