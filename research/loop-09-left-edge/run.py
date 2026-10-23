"""Loop 9: left-edge diagonals w_k(t) = x(-t+k, t).

Hypothesis H22 (stated before computing): for every k >= 1, log2(left period of w_k) <= log2(P_k)/2,
with P_k the right-edge period from E19. Offsets 1..8 were inspected first; the test is k >= 9.
Exact certification per PROOFS.md (simulate (L) to T0 + 3P, then minimise period and onset).
Cross-checked against a direct big-int lattice for t <= 4096.
"""
import json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
KMAX, CAP = 72, 1 << 24
LATTICE_T = 4096
RESULT = {}


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


def certify(k, a: Seq, b: Seq):
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
    # shrink the period
    while L > 1 and w[onset:onset + L // 2] == w[onset + L // 2:onset + L]:
        L //= 2
    # shrink the onset
    while onset > 0 and w[onset - 1] == w[onset - 1 + L]:
        onset -= 1
    # verify periodicity on the whole simulated window
    assert all(w[t] == w[t + L] for t in range(onset, n - L)), k
    return Seq(bytearray(w[:onset + L]), onset, L)


def compute():
    right = {r['k']: r for r in json.loads((lt.ROOT / 'research/loop-06-plateau-bound/plateau_check.json').read_text())['records']}
    t0 = time.time()
    W = {-2: Seq(bytearray([0]), 0, 1), -1: Seq(bytearray([0]), 0, 1), 0: Seq(bytearray([1]), 0, 1)}
    rows = [{'k': 0, 'period': 1, 'onset': 0}]
    k = 1
    while k <= KMAX:
        if max(W[k - 1].p, W[k - 2].p) * 2 > CAP:
            break
        s = certify(k, W[k - 1], W[k - 2])
        W[k] = s
        Pk = right[k]['P'] if k in right else None
        rows.append({'k': k, 'period': s.p, 'log2_period': s.p.bit_length() - 1, 'onset': s.o,
                     'right_log2_P': (Pk.bit_length() - 1) if Pk else None,
                     'ones_per_period': sum(s.d[s.o:s.o + s.p])})
        k += 1
    K = k - 1
    secs = round(time.time() - t0, 1)

    # lattice cross-check
    row, bad = 1, []
    for t in range(LATTICE_T + 1):
        for kk in range(0, min(K, 2 * t) + 1):
            if ((row >> kk) & 1) != W[kk].at(t):
                bad.append((kk, t))
        row = ((row << 2) ^ ((row << 1) | row)) & ((1 << (2 * t + 3)) - 1)

    h22 = [r for r in rows if r['k'] >= 1 and r['right_log2_P'] is not None and r['log2_period'] > r['right_log2_P'] / 2]
    tested = [r['k'] for r in rows if r['k'] >= 9 and r['right_log2_P'] is not None]
    out = {
        'K': K, 'cap_steps': CAP, 'seconds': secs, 'lattice_T': LATTICE_T, 'lattice_mismatches': bad[:10],
        'H22_tested_k': [min(tested), max(tested)] if tested else None,
        'H22_counterexamples': h22,
        'H22_counterexamples_in_test_range': [r for r in h22 if r['k'] >= 9],
        'max_onset': max(r['onset'] for r in rows), 'max_log2_period': max(r.get('log2_period', 0) for r in rows),
        'rows': rows,
    }
    (HERE / 'left_edge.json').write_text(json.dumps(out, indent=1) + '\n')
    assert not bad, bad[:5]
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-09-left-edge/PROOFS.md'
    lt.add_assertion(book, 'TR', 'Every left-edge diagonal w_k(t)=x(-t+k,t) is eventually periodic, with least eventual period a power of two dividing 2^k.', 'PROVED_HUMAN_READABLE', ps + ' §TR', deps=['D0', 'T0'])
    lt.add_assertion(book, 'F8', f'Exact least eventual periods and onsets of the left-edge diagonals certified for k<={r["K"]} (largest period 2^{r["max_log2_period"]}, latest onset {r["max_onset"]}); agrees with a direct lattice for t<={LATTICE_T}.', 'FINITE_VERIFIED', '', deps=['TR'])
    lt.add_assertion(book, 'H22', 'The left edge grows at most half as fast as the right: log2(left-edge period of w_k) <= log2(P_k)/2 for every k>=1.', 'OPEN', deps=['TR', 'T004'])
    bad = r['H22_counterexamples_in_test_range']
    if bad:
        b0 = bad[0]
        lt.set_status(book, 'H22', 'FALSIFIED', f'k={b0["k"]}: left period 2^{b0["log2_period"]} but right period 2^{b0["right_log2_P"]} (E25).', replacement='TR')
    else:
        lt.set_status(book, 'H22', 'FINITE_VERIFIED', f'Holds for every k in {r["H22_tested_k"]} (and for k=1..8, inspected before stating it). Finite only.')
    lt.add_evidence(book, 'E25', 'research/loop-09-left-edge/left_edge.json', supports=['TR', 'F8', 'H22'])
    lt.add_evidence(book, 'E26', ps, supports=['TR'])
    return (f'TR proved: left-edge diagonals are eventually periodic with power-of-two periods. Certified exactly for k<={r["K"]} '
            f'(largest period 2^{r["max_log2_period"]}, latest onset {r["max_onset"]}). H22 {"FALSIFIED" if bad else "held"} on {r["H22_tested_k"]}.')


consumed = lt.run_loop('effortless-9', 'H22: the left edge grows at most half as fast as the right (log2 left period <= log2 P_k / 2).', edit, ['TR', 'F8', 'H22', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('TR', 'F8', 'H22', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('K', 'seconds', 'H22_tested_k', 'H22_counterexamples', 'max_onset', 'max_log2_period')}, indent=1))
print(' '.join(f"{r['k']}:{r.get('log2_period',0)}/{r.get('right_log2_P')}@{r['onset']}" for r in RESULT['rows']))
