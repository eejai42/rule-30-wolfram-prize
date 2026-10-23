"""Loop 12: when does the left edge reach period 32?

Left-edge periods first appear at k = 3 (2), 8 (4), 29 (8), 400 (16); none above 16 through
k = 5000 (loop 11). Hypothesis H25 (stated before computing): some left-edge diagonal with
k < 20000 has least eventual period 32.

Also recorded as a finite claim: onset_k > k for every 20 <= k < 20000 (the center c(t) = w_t(t)
is always read before its left-edge diagonal settles), checked on the same exact data.
Exact, with research/left_edge.py; reproduces loop 11 for k <= 5000.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
from left_edge import BASE, certify

HERE = Path(__file__).resolve().parent
KMAX = 19999
RESULT = {}


def compute():
    f10 = json.loads((lt.ROOT / 'research/loop-11-front-speed/front_speed.json').read_text())
    check = {r['k']: r for r in f10['rows_every_100']}
    t0 = time.time()
    W = dict(BASE)
    first_period, onset_le_k, ratio_by_1000 = {1: 0}, [], {}
    for k in range(1, KMAX + 1):
        s = certify(k, W[k - 1], W[k - 2])
        W[k] = s
        W.pop(k - 3, None) if k >= 3 else None
        first_period.setdefault(s.p, k)
        if k >= 20 and s.o <= k:
            onset_le_k.append(k)
        if k in check:
            assert (s.p, s.o) == (check[k]['period'], check[k]['onset']), k
        if k % 1000 == 0:
            ratio_by_1000[k] = {'onset': s.o, 'ratio': round(s.o / k, 4), 'period': s.p}
            print(f'k={k} onset={s.o} ratio={s.o / k:.4f} period={s.p} {time.time() - t0:.0f}s', flush=True)
    out = {
        'KMAX': KMAX, 'seconds': round(time.time() - t0, 1), 'loop11_rows_checked': len(check),
        'first_k_with_period': {str(p): k for p, k in sorted(first_period.items())},
        'H25_period_32_found': 32 in first_period, 'first_k_period_32': first_period.get(32),
        'max_period': max(first_period),
        'onset_le_k_for_k_ge_20': onset_le_k[:20], 'onset_gt_k_all': not onset_le_k,
        'onset_ratio_every_1000': ratio_by_1000,
    }
    (HERE / 'period_32.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    lt.add_assertion(book, 'H25', f'Some left-edge diagonal with k < {KMAX + 1} has least eventual period 32.', 'OPEN', deps=['TR'])
    lt.add_assertion(book, 'F11', f'Exact left-edge periods and onsets certified for k<={KMAX}; for every 20<=k<={KMAX} the onset exceeds k, so the center c(t)=w_t(t) is read before its left-edge diagonal settles.', 'FINITE_VERIFIED' if r['onset_gt_k_all'] else 'FALSIFIED', '', deps=['TR'])
    if r['H25_period_32_found']:
        lt.set_status(book, 'H25', 'FINITE_VERIFIED', f'First period-32 left-edge diagonal at k={r["first_k_period_32"]} (E29).')
    else:
        lt.set_status(book, 'H25', 'FALSIFIED', f'No left-edge period above {r["max_period"]} for k<={KMAX}; first k per period {r["first_k_with_period"]} (E29).', replacement='TR')
    lt.add_evidence(book, 'E29', 'research/loop-12-period-32/period_32.json', supports=['H25', 'F11'])
    return (f'Left edge certified to k={KMAX} in {r["seconds"]}s. H25 {"held: period 32 first at k=" + str(r["first_k_period_32"]) if r["H25_period_32_found"] else "FALSIFIED: max period " + str(r["max_period"])}. '
            f'Onset > k for every 20<=k<={KMAX}: {r["onset_gt_k_all"]}. Onset/k at k=19000: {r["onset_ratio_every_1000"].get(19000)}.')


consumed = lt.run_loop('effortless-12', f'H25: a left-edge diagonal with k < {KMAX + 1} has period 32.', edit, ['H25', 'F11', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H25', 'F11', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'first_k_with_period', 'H25_period_32_found', 'first_k_period_32', 'onset_gt_k_all')}, indent=1))
