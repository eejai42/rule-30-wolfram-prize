"""Shared big-integer diagonal machinery (same algorithm as loop-02-frontier/run.py).

A diagonal word is an int whose bit t is y_k(t) = x(t-k, t); words(K) returns
{k: (word, least_period)} for 0 <= k <= K using only the recurrence
y_k(t+1) = y_k(t) XOR (y_{k-1}(t) OR y_{k-2}(t)).
"""


def mask(n):
    return (1 << n) - 1


def extend(w, p, n):
    x, L = w, p
    while L < n:
        x |= x << L
        L *= 2
    return x & mask(n)


def prefix_xor_exclusive(q, n):
    x, s = q, 1
    while s < n:
        x ^= (x << s) & mask(n)
        s *= 2
    return (x << 1) & mask(n)


def least_pow2_period(w, p):
    while p > 1:
        h = p // 2
        if (w >> h) != (w & mask(h)):
            return p
        w &= mask(h)
        p = h
    return 1


def bit(w, p, t):
    return (w >> (t % p)) & 1


def words(K):
    out = {0: (1, 1), -1: (0, 1), -2: (0, 1)}
    info = {}
    for k in range(1, K + 1):
        (wa, pa), (wb, pb) = out[k - 1], out[k - 2]
        P = max(pa, pb)
        q = extend(wa, pa, P) | extend(wb, pb, P)
        Q = least_pow2_period(q, P)
        eps = (q & mask(Q)).bit_count() & 1
        M = Q * (1 + eps)
        n = 2 * M
        y = prefix_xor_exclusive(extend(q & mask(Q), Q, n), n)
        w = y & mask(M)
        assert extend(w, M, n) == y and least_pow2_period(w, M) == M
        out[k] = (w, M)
        info[k] = {'P_parent': P, 'Q': Q, 'eps': eps, 'P': M, 'q': q & mask(P)}
    return out, info
