"""Loop 6: are plateaus of the doubling sequence bounded?

Hypothesis H18 (stated before computing): every plateau (maximal run of eps_k = 0, k >= 3)
has length at most 7.  Tested by pushing the exact diagonal frontier past k = 64.

The computation runs inside the loop, so the explorer shows the loop RUNNING meanwhile.
Streaming version of research/diagonals.py: only the last two words are kept in memory.
Checks: every period-word hash for k <= 64 reproduces E10 (loop 2), the TA/TK/TL identities
hold at every k, and a direct big-int lattice agrees with every new diagonal for t <= 4096.
New words are hashed as sha256 of w.to_bytes(ceil(P/8), 'little') (bit t of the int is y_k(t)).
"""
import hashlib, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
from diagonals import mask, extend, prefix_xor_exclusive, least_pow2_period

HERE = Path(__file__).resolve().parent
CAP_BITS = 2 ** 31          # stop before a word would need more than 2^31 bits per period window
LATTICE_T = 4096
E10 = {r['k']: r for r in json.loads((lt.ROOT / 'research/loop-02-frontier/diagonal_periods_v06.json').read_text())['records']}
TR = bytes.maketrans(b'01', b'\x00\x01')


def legacy_hash(w, p):
    return hashlib.sha256(format(w, f'0{p}b')[::-1].encode().translate(TR)).hexdigest()


def compute():
    t0 = time.time()
    a, b = (1, 1), (0, 1)        # (word, period) of y_{k-1}, y_{k-2}; starts at k = 1
    rec, low = [], {}
    k = 1
    while True:
        (wa, pa), (wb, pb) = a, b
        P = max(pa, pb)
        if 2 * P > CAP_BITS:
            break
        ts = time.time()
        q = extend(wa, pa, P) | extend(wb, pb, P)
        Q = least_pow2_period(q, P)
        eps = (q & mask(Q)).bit_count() & 1
        M = Q * (1 + eps)
        n = 2 * M
        y = prefix_xor_exclusive(extend(q & mask(Q), Q, n), n)
        w = y & mask(M)
        assert extend(w, M, n) == y and least_pow2_period(w, M) == M, k
        if k >= 3:
            assert Q == P, f'TK fails at {k}'
            assert M == pa * (1 + eps), f'TL fails at {k}'
        ones = w.bit_count()
        r = {'k': k, 'P_parent': P, 'Q': Q, 'eps': eps, 'P': M, 'log2_P': M.bit_length() - 1, 'ones': ones,
             'dev_from_half': ones - M // 2, 'seconds': round(time.time() - ts, 2)}
        if k in E10:
            r['matches_E10'] = legacy_hash(w, M) == E10[k]['sha256'] and M == E10[k]['period'] and ones == E10[k]['ones']
            assert r['matches_E10'], k
        else:
            r['sha256_le_bytes'] = hashlib.sha256(w.to_bytes((M + 7) // 8, 'little')).hexdigest()
            low[k] = w & mask(LATTICE_T + 1) if M > LATTICE_T else None
        rec.append(r)
        print(f"k={k} log2P={r['log2_P']} eps={eps} {r['seconds']}s", flush=True)
        a, b = (w, M), a
        k += 1
    K = k - 1

    # lattice cross-check of the new offsets
    t1 = time.time()
    row, lo, bad = 1, 0, []
    new = [kk for kk in low if low[kk] is not None]
    for t in range(LATTICE_T + 1):
        for kk in new:
            if kk <= 2 * t:
                bit = (row >> (t - kk - lo)) & 1
                if bit != (low[kk] >> t) & 1:
                    bad.append((kk, t))
        row <<= 1; lo -= 1
        row = ((row << 1) ^ (row | (row >> 1))) & mask(2 * t + 3)

    eps_seq = {r['k']: r['eps'] for r in rec if r['k'] >= 3}
    runs, start = [], None
    for kk in range(3, K + 2):
        z = eps_seq.get(kk) == 0
        if z and start is None:
            start = kk
        if not z and start is not None:
            runs.append({'from': start, 'to': kk - 1, 'length': kk - start, 'complete': kk <= K})
            start = None
    complete = [r for r in runs if r['complete']]
    h18_fail = [r for r in complete if r['length'] > 7]
    trailing = [r for r in runs if not r['complete']]
    tp_ok = all(r['log2_P'] >= 2 + (r['k'] - 3) // 8 for r in rec if r['k'] >= 3)
    out = {
        'frontier_K': K, 'cap_bits': CAP_BITS, 'largest_period_log2': rec[-1]['log2_P'],
        'E10_rows_reproduced': sum(1 for r in rec if r.get('matches_E10')),
        'new_offsets': [r['k'] for r in rec if r['k'] > 64],
        'lattice_T': LATTICE_T, 'lattice_checked_offsets': new, 'lattice_mismatches': bad[:10], 'lattice_seconds': round(time.time() - t1, 1),
        'eps_sequence_3_to_K': ''.join(str(eps_seq[kk]) for kk in range(3, K + 1)),
        'plateaus': runs, 'longest_complete_plateau': max(r['length'] for r in complete),
        'H18_counterexamples': h18_fail, 'trailing_open_plateau': trailing,
        'TP_bound_with_L7_holds_on_data': tp_ok,
        'growth_bits_per_offset_3_to_K': round((rec[-1]['log2_P'] - 2) / (K - 3), 4),
        'compute_seconds': round(t1 - t0, 1), 'records': rec,
    }
    (HERE / 'plateau_check.json').write_text(json.dumps(out, indent=1) + '\n')
    assert not bad, bad[:5]
    return out


RESULT = {}


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-06-plateau-bound/PROOFS.md'
    K, lp = r['frontier_K'], r['longest_complete_plateau']
    lt.add_assertion(book, 'H18', 'Every plateau of the doubling sequence (maximal run of eps_k=0, k>=3) has length at most 7.', 'OPEN', deps=['TL'])
    lt.add_assertion(book, 'TP', 'If every plateau has length at most L, then log2 P_k >= 2 + floor((k-3)/(L+1)) for all k>=3; a plateau bound forces exponential growth of the diagonal periods.', 'PROVED_HUMAN_READABLE', ps + ' §TP', deps=['TL', 'TK'])
    lt.add_assertion(book, 'F7', f'Exact diagonal periods certified through offset {K} (largest period 2^{r["largest_period_log2"]}); all 64 E10 period-word hashes reproduced; new diagonals agree with a direct lattice for t<={LATTICE_T}.', 'FINITE_VERIFIED', '', deps=['TA', 'T004'])
    if r['H18_counterexamples']:
        c = r['H18_counterexamples'][0]
        lt.set_status(book, 'H18', 'FALSIFIED', f'Plateau of length {c["length"]} at k={c["from"]}..{c["to"]} (E19).', replacement='TP')
    else:
        lt.set_status(book, 'H18', 'FINITE_VERIFIED', f'All complete plateaus through k={K} have length <= 7 (longest {lp}). Finite only; would give log2 P_k >= 2 + floor((k-3)/8) by TP.')
    lt.add_evidence(book, 'E19', 'research/loop-06-plateau-bound/plateau_check.json', supports=['H18', 'F7', 'TP'])
    lt.add_evidence(book, 'E20', ps, supports=['TP', 'H18'])
    return (f'Frontier pushed from k=64 to k={K} (period 2^{r["largest_period_log2"]}, {r["compute_seconds"]}s). '
            f'H18 {"FALSIFIED" if r["H18_counterexamples"] else "held"}: longest complete plateau {lp}. '
            f'Growth {r["growth_bits_per_offset_3_to_K"]} bits per offset. TP proved (plateau bound implies exponential growth).')


consumed = lt.run_loop('effortless-6', 'H18: every plateau of the doubling sequence has length at most 7.', edit, ['H18', 'TP', 'F7', 'TL', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H18', 'TP', 'F7', '_dashboard')}, indent=1))
print(json.dumps({k: v for k, v in RESULT.items() if k not in ('records', 'plateaus')}, indent=1))
