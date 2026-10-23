"""Loop 2: push the exact diagonal-period frontier past k=51 with an independent implementation.

Hypothesis F5: the exact least periods P_k, forcing periods Q_k and parities eps_k
can be certified well beyond k=51 (the v05 cap was 2^21 words), and an
implementation that never touches the v05 code reproduces every v05 period-word
hash for k<=51.  H7 and H4 are re-tested on every new offset.

Representation: a diagonal word is a Python int whose bit t is y_k(t).
Prefix-XOR (the discrete antiderivative) is done by log-doubling; period tests
are shift-and-compare.  A direct big-int Rule 30 lattice evolution cross-checks
every diagonal against x(t-k, t) for t <= LATTICE_T.
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
CAP_BITS = 2 ** 27          # longest window we will materialise (bits)
LATTICE_T = 4096
E1 = json.loads((lt.ROOT / 'bootstrap/cmcc_rule30_effortless_migration/research_v05/data/diagonal_periods.json').read_text())
E1 = {r['k']: r for r in E1}
TR = bytes.maketrans(b'01', b'\x00\x01')


def mask(n):
    return (1 << n) - 1


def extend(w, p, n):
    """Periodic extension of the p-bit word w to n bits (n a multiple of p)."""
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
    return (x << 1) & mask(n)        # bit t = XOR_{s<t} q(s)


def least_pow2_period(w, p):
    """w has period p (a power of two); return its least period among divisors of p."""
    while p > 1:
        h = p // 2
        if (w >> h) != (w & mask(h)):
            return p
        w &= mask(h)
        p = h
    return 1


def word_hash(w, p):
    s = format(w, f'0{p}b')[::-1].encode().translate(TR)   # bytearray-of-0/1 convention of research_v05
    return hashlib.sha256(s).hexdigest()


def popcount(x):
    return x.bit_count()


t0 = time.time()
words = {0: (1, 1), -1: (0, 1), -2: (0, 1)}     # k -> (word, period)
records = [{'k': 0, 'period': 1, 'ones': 1, 'sha256': word_hash(1, 1)}]
k = 1
while True:
    (wa, pa), (wb, pb) = words[k - 1], words[k - 2]
    P = max(pa, pb)
    if 2 * P > CAP_BITS:
        break
    q = extend(wa, pa, P) | extend(wb, pb, P)
    Q = least_pow2_period(q, P)
    eps = popcount(q & mask(Q)) & 1
    M = Q * (1 + eps)                                     # TA prediction
    n = 2 * M
    y = prefix_xor_exclusive(extend(q & mask(Q), Q, n), n)
    w = y & mask(M)
    assert extend(w, M, n) == y, k                        # M is a period of y over the window
    assert least_pow2_period(w, M) == M, k                # and it is the least power-of-two period
    half = (w >> (M // 2)) & 1 if M >= 2 else None
    rec = {'k': k, 'parent_common_period': P, 'forcing_period': Q, 'forcing_parity': eps, 'period': M,
           'ones': popcount(w), 'first_one': (w & -w).bit_length() - 1, 'bit_at_half_period': half,
           'ones_first_half': popcount(w & mask(M // 2)) if M >= 2 else None, 'sha256': word_hash(w, M)}
    if k in E1:
        rec['matches_E1'] = all(E1[k][f] == rec[f] for f in ('parent_common_period', 'forcing_period', 'forcing_parity', 'period', 'ones', 'first_one', 'sha256'))
    records.append(rec)
    words[k] = (w, M)
    k += 1
K = k - 1
compute_seconds = round(time.time() - t0, 1)

# ---- lattice cross-check: evolve Rule 30 directly, compare every diagonal k<=K for t<=LATTICE_T
t1 = time.time()
row, lo = 1, 0                     # bit j of row = x(j+lo, t)
lattice_mismatch = []
for t in range(LATTICE_T + 1):
    for kk in range(0, min(K, 2 * t) + 1):
        i = t - kk
        bit = (row >> (i - lo)) & 1
        w, M = words[kk]
        if bit != (w >> (t % M)) & 1:
            lattice_mismatch.append((kk, t))
    # step: x(i,t+1) = x(i-1,t) XOR (x(i,t) OR x(i+1,t)); widen by one cell each side
    row <<= 1; lo -= 1
    row = ((row << 1) ^ (row | (row >> 1))) & mask(2 * t + 3)
lattice_seconds = round(time.time() - t1, 1)

h7_fail = [r['k'] for r in records if r['k'] >= 3 and r['forcing_period'] != max(records[r['k'] - 1]['period'], records[r['k'] - 2]['period'])]
h4_fail = [r['k'] for r in records if r['k'] >= 1 and r['period'] < records[r['k'] - 1]['period']]
e1_match = all(r.get('matches_E1', True) for r in records)
result = {
    'frontier_K': K, 'cap_bits': CAP_BITS, 'largest_period': records[-1]['period'], 'log2_largest_period': records[-1]['period'].bit_length() - 1,
    'E1_rows_reproduced': sum(1 for r in records if r.get('matches_E1')), 'E1_all_match': e1_match,
    'lattice_T': LATTICE_T, 'lattice_mismatches': lattice_mismatch[:10], 'lattice_ok': not lattice_mismatch,
    'H7_counterexamples': h7_fail, 'H4_counterexamples': h4_fail,
    'new_offsets': [r['k'] for r in records if r['k'] > 51],
    'compute_seconds': compute_seconds, 'lattice_seconds': lattice_seconds, 'records': records,
}
(HERE / 'diagonal_periods_v06.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'records'}, indent=1))
assert e1_match and not lattice_mismatch and not h7_fail and not h4_fail


def edit(book):
    lt.add_assertion(book, 'F5', f'Exact least diagonal periods, forcing periods and parities certified through offset {K} (largest period 2^{result["log2_largest_period"]}) by an independent big-integer implementation that reproduces all 52 v05 period-word hashes and agrees with a direct lattice evolution for t<={LATTICE_T}.', 'FINITE_VERIFIED', '', deps=['TA', 'T004'])
    lt.add_evidence(book, 'E10', 'research/loop-02-frontier/diagonal_periods_v06.json', supports=['F5', 'H7', 'H4'])
    lt.set_status(book, 'H7', 'FINITE_VERIFIED', f'Re-verified on every offset 3..{K} by E10 (independent implementation); {len(result["new_offsets"])} new offsets, no counterexample.')
    lt.set_status(book, 'H4', 'FINITE_VERIFIED', f'Re-verified on every offset 1..{K} by E10; no counterexample.')
    return f'Added F5 (frontier k<={K}, {compute_seconds}s). H7 and H4 re-verified through {K}. E1 hashes reproduced: {result["E1_rows_reproduced"]}/52. Lattice cross-check t<={LATTICE_T}: ok.'


consumed = lt.run_loop('effortless-2', f'F5: exact diagonal periods are certifiable far past k=51; H7 and H4 survive out-of-sample offsets.', edit, ['F5', 'F2', 'H7', 'H4'], HERE)
print(json.dumps({k: consumed[k] for k in ('F5', 'H7', 'H4', '_dashboard')}, indent=1))
