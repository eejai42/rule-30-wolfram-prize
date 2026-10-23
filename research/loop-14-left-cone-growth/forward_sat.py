"""Forward form of the left-cone relaxation (loop 14), solved by SAT.

TU (PROOFS.md): the left-cone relaxation of loop 13 is equivalent to
  * a free row at time T on positions -T+1..-1 (x(-T,T)=1, zeros further left),
  * the left half (positions <= -1) evolving by Rule 30 with the center column prescribed,
    x(0,t) = c'(t) = a[(t-T) mod p], acting as a boundary input,
  * the constraint x(-1,t) = NOT c'(t+1) at every one-time t (c'(t)=1).
Column 1 is then determined at zero-times and irrelevant at one-times, so the relaxation
has 2^(T-1) candidates, not 2^(zero-times), and it is UNSAT at window L iff
count(T,a,L) = 0 in loop 13 (for L >= T).

first_zero(T, a) = least L such that the constraints at one-times t <= T+L-1 are UNSAT.
"""
from __future__ import annotations
from pysat.solvers import Cadical153


class Enc:
    def __init__(self):
        # variable 1 is forced true, so the integer 1 can serve as the constant 'true' literal
        # and -1 as 'false'; 0 is also 'false'. Real variables start at 2.
        self.n = 1
        self.clauses = [[1]]

    def var(self):
        self.n += 1
        return self.n

    def OR(self, b, c):
        if b == 1 or c == 1:
            return 1
        if b in (0, -1):
            return c
        if c in (0, -1):
            return b
        o = self.var()
        self.clauses += [[-b, o], [-c, o], [-o, b, c]]
        return o

    def XOR(self, a, o):
        if a in (0, -1):
            return o
        if o in (0, -1):
            return a
        if a == 1:
            return self.NOT(o)
        if o == 1:
            return self.NOT(a)
        x = self.var()
        self.clauses += [[-x, a, o], [-x, -a, -o], [x, -a, o], [x, a, -o]]
        return x

    def NOT(self, a):
        if a == 0:
            return 1
        return -a


class Forward:
    """Incremental: rows T..; call step() to add the next row and its one-time constraint."""

    def __init__(self, T: int, a: str):
        self.T, self.a, self.p = T, a, len(a)
        self.enc = Enc()
        self.solver = Cadical153()
        self.t = T
        # row T: dict position -> literal/const, positions -T..-1
        self.row = {-T: 1}
        for i in range(-T + 1, 0):
            self.row[i] = self.enc.var()
        self.free = list(range(2, self.enc.n + 1))
        self.flushed = 0
        self.L = 0          # window length covered: constraints at one-times t <= T+L-1
        self.contradiction = False

    def c(self, t):
        return int(self.a[(t - self.T) % self.p])

    def _flush(self):
        for cl in self.enc.clauses[self.flushed:]:
            self.solver.add_clause(cl)
        self.flushed = len(self.enc.clauses)

    def step(self):
        """Add the one-time constraint at time t (if c'(t)=1), then build row t+1. L += 1."""
        t, e = self.t, self.enc
        if self.c(t) == 1:
            lit = self.row[-1]
            want = 1 - self.c(t + 1)
            if lit in (0, 1, -1):
                if (lit == 1) != (want == 1):
                    self.contradiction = True
            else:
                e.clauses.append([lit] if want == 1 else [-lit])
        get = lambda i: self.row.get(i, 0) if i < 0 else self.c(t)
        new = {}
        for i in range(-(t + 1), 0):
            new[i] = e.XOR(get(i - 1), e.OR(get(i), get(i + 1)))
        self.row = new
        self.t = t + 1
        self.L += 1
        self._flush()

    def sat(self):
        if self.contradiction:
            return False
        return self.solver.solve()

    def count_models(self, cap=1 << 16):
        """Number of satisfying free rows (small cases only)."""
        if self.contradiction:
            return 0
        n = 0
        while self.solver.solve():
            n += 1
            m = self.solver.get_model()
            self.solver.add_clause([-l for l in m if abs(l) in set(self.free)])
            if n >= cap:
                return None
        return n


def first_zero(T: int, a: str, Lmax: int, check_every: int = 1):
    """Least L <= Lmax with UNSAT, or None. Checks SAT every `check_every` steps, then refines."""
    f = Forward(T, a)
    last_sat_L = 0
    while f.L < Lmax:
        for _ in range(check_every):
            if f.L >= Lmax:
                break
            f.step()
        if not f.sat():
            if check_every == 1:
                return f.L, f
            # refine between last_sat_L and f.L
            g = Forward(T, a)
            for _ in range(last_sat_L):
                g.step()
            while True:
                g.step()
                if not g.sat():
                    return g.L, g
        last_sat_L = f.L
    return None, f
