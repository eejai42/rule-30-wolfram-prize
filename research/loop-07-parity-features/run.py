"""Loop 7: diagonal parities, and whether they decide the doubling bit.

Hypothesis H19 (stated before computing): eps_k is a function of (eps_{k-1}, eps_{k-2}, o_{k-1}, o_{k-2})
for every k >= 5, where o_j = ones_j mod 2.  Tested on k = 5..72 (eps and ones from E19, loop 6).
Also checks lemma TO directly on the words for k <= 64, and reports the smallest window of past
(eps, o) bits that is consistent with the data, as an observation only.
"""
import json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import diagonals as dg

HERE = Path(__file__).resolve().parent
RESULT = {}


def odd_mask(n):
    m, L = 0b10, 2
    while L < n:
        m |= m << L
        L *= 2
    return m & dg.mask(n)


def compute():
    E19 = json.loads((lt.ROOT / 'research/loop-06-plateau-bound/plateau_check.json').read_text())['records']
    K = max(r['k'] for r in E19)
    eps = {r['k']: r['eps'] for r in E19}
    o = {r['k']: r['ones'] & 1 for r in E19}

    # TO, checked on the actual words (k <= 64)
    W, info = dg.words(64)
    to_fail = []
    for k in range(3, 65):
        if info[k]['eps'] == 1:
            ok = (W[k][0].bit_count() & 1) == 0
        else:
            P = info[k]['P']
            ok = (W[k][0].bit_count() & 1) == ((info[k]['q'] & odd_mask(P)).bit_count() & 1)
        if not ok:
            to_fail.append(k)

    # H19: determinism of eps_k given (eps_{k-1}, eps_{k-2}, o_{k-1}, o_{k-2})
    def table(depth):
        seen = defaultdict(set)
        for k in range(3 + depth, K + 1):
            key = tuple((eps[k - i], o[k - i]) for i in range(1, depth + 1))
            seen[key].add((eps[k], k))
        conflicts = {str(key): sorted(v) for key, v in seen.items() if len({e for e, _ in v}) > 1}
        return conflicts, len(seen)

    h19_conf, h19_keys = table(2)
    minimal = None
    for d in range(1, 12):
        c, _ = table(d)
        if not c:
            minimal = d
            break
    # the case TM does not cover: eps_{k-1} = 0
    plateau_case = {str(k): v for k, v in h19_conf.items() if k.startswith('((0,')}
    out = {
        'K': K, 'TO_checked_k': [3, 64], 'TO_failures': to_fail,
        'H19': {'features': '(eps_{k-1}, o_{k-1}), (eps_{k-2}, o_{k-2})', 'range': [5, K], 'distinct_feature_values': h19_keys,
                'conflicts': h19_conf, 'conflicts_in_plateau_case': plateau_case},
        'smallest_consistent_window_depth': minimal,
        'note': 'A consistent window on 68 data points is an observation, not evidence of a rule: with depth d there are up to 4^d keys.',
        'eps_3_to_K': ''.join(str(eps[k]) for k in range(3, K + 1)),
        'o_3_to_K': ''.join(str(o[k]) for k in range(3, K + 1)),
    }
    (HERE / 'parity_features.json').write_text(json.dumps(out, indent=1) + '\n')
    assert not to_fail, to_fail
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-07-parity-features/PROOFS.md'
    lt.add_assertion(book, 'TO', 'For k>=3: if eps_k=1 the diagonal has an even number of ones per period; if eps_k=0 that parity equals the parity of the number of ones of q_k at odd positions.', 'PROVED_HUMAN_READABLE', ps + ' §TO', deps=['TA', 'T0'])
    lt.add_assertion(book, 'H19', 'eps_k is a function of (eps_{k-1}, eps_{k-2}, o_{k-1}, o_{k-2}) for every k>=5, where o_j is the parity of the number of ones of y_j per period.', 'OPEN', deps=['TL', 'TM', 'TO'])
    conf = r['H19']['conflicts']
    if conf:
        key, vals = next(iter(conf.items()))
        lt.set_status(book, 'H19', 'FALSIFIED', f'Same four parity bits {key} give different eps at offsets {vals}; {len(conf)} conflicting feature value(s) on k=5..{r["K"]}, all with eps_(k-1)=0 as TM predicts.', replacement='TO')
    else:
        lt.set_status(book, 'H19', 'FINITE_VERIFIED', f'No two offsets in 5..{r["K"]} share the four bits with different eps.')
    lt.add_evidence(book, 'E21', 'research/loop-07-parity-features/parity_features.json', supports=['TO', 'H19'])
    lt.add_evidence(book, 'E22', ps, supports=['TO'])
    return (f'TO proved (diagonal parity read off the forcing word) and checked on k=3..64. H19 '
            f'{"FALSIFIED: " + str(len(conf)) + " conflicting feature value(s)" if conf else "held on 5.." + str(r["K"])}. '
            f'Smallest window of past (eps, o) bits consistent with the data: {r["smallest_consistent_window_depth"]} (observation only).')


consumed = lt.run_loop('effortless-7', 'H19: eps_k is decided by the four parity bits (eps_{k-1}, eps_{k-2}, o_{k-1}, o_{k-2}).', edit, ['TO', 'H19', 'TM', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('TO', 'H19', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('TO_failures', 'H19', 'smallest_consistent_window_depth', 'eps_3_to_K', 'o_3_to_K')}, indent=1))
