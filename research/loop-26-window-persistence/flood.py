"""Loop 26 (TY): the free-outer-cell window step is strongly connected at every width checked.

The step is loop 25's (closure.successors): bits 1..E-1 of the next window from the rule, bit E
free, the next center bit NOT x(-1) after a 1 and free after a 0. TY (PROOFS.md) proves that every
window reaches every window within 2E+2 steps, so the closure of any nonempty set is everything.
This module checks the statement exhaustively for small E: the step graph on all 2^(E+1) windows
has one strongly connected component, and the largest shortest-path distance is at most 2E+2.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-25-closure'))
from closure import U

DIAMETER_UPTO = 10                                    # all-pairs distances are 4^(E+1) entries


def edges(E: int):
    """(source, target) pairs of the step graph, one per successor (duplicates harmless)."""
    n = 1 << (E + 1)
    w = np.arange(n, dtype=U)
    full = U(n - 1)
    core = ((w >> U(1)) ^ (w | (w << U(1)))) & full & ~U(1) & ~(U(1) << U(E))
    c = w & U(1)
    xm1 = (w >> U(1)) & U(1)
    src, dst = [], []
    for hi in (U(0), U(1) << U(E)):
        base = core | hi
        forced = c == U(1)
        src.append(w[forced]); dst.append(base[forced] | (xm1[forced] ^ U(1)))
        src.append(w[~forced]); dst.append(base[~forced])
        src.append(w[~forced]); dst.append(base[~forced] | U(1))
    return np.concatenate(src).astype(np.int64), np.concatenate(dst).astype(np.int64), n


def check(E: int) -> dict:
    s, d, n = edges(E)
    G = csr_matrix((np.ones(len(s), dtype=np.int8), (s, d)), shape=(n, n))
    ncomp, _ = connected_components(G, directed=True, connection='strong')
    out = {'E': E, 'windows': n, 'strong_components': int(ncomp)}
    if E <= DIAMETER_UPTO:
        D = shortest_path(G, method='D', unweighted=True)
        out['diameter'] = int(D.max())
        out['bound_2E_plus_2'] = 2 * E + 2
    return out


def check_all(Emax: int = 16) -> list[dict]:
    return [check(E) for E in range(1, Emax + 1)]


if __name__ == '__main__':
    for r in check_all():
        print(r, flush=True)
