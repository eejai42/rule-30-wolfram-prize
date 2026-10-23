"""Loop 10: the settled zone at the left edge.

Hypothesis H23 (stated before computing): every left-edge diagonal w_k has least eventual period
at most 8.  Loop 9 saw this for k <= 72; here it is tested on k = 73..600, exactly, with the
loop-9 certifier (simulate the left-edge recurrence to T0 + 3P, then minimise period and onset).

Observations recorded alongside (not hypotheses):
  * whether the settled pattern is periodic in k as well (a doubly periodic background), and
  * the front: onset_k / k.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
from left_edge import BASE, Seq, certify

HERE = Path(__file__).resolve().parent
KMAX, LATTICE_T = 600, 1600
RESULT = {}


def compute():
    loop9 = {r['k']: r for r in json.loads((lt.ROOT / 'research/loop-09-left-edge/left_edge.json').read_text())['rows']}
    t0 = time.time()
    W = dict(BASE)
    rows = [{'k': 0, 'period': 1, 'onset': 0}]
    for k in range(1, KMAX + 1):
        s = certify(k, W[k - 1], W[k - 2])
        W[k] = s
        rows.append({'k': k, 'period': s.p, 'onset': s.o})
        if k in loop9:
            assert (s.p, s.o) == (loop9[k]['period'], loop9[k]['onset']), k
    secs = round(time.time() - t0, 1)

    # direct lattice cross-check
    row, bad = 1, []
    for t in range(LATTICE_T + 1):
        for kk in range(0, min(KMAX, 2 * t) + 1):
            if ((row >> kk) & 1) != W[kk].at(t):
                bad.append((kk, t))
        row = ((row << 2) ^ ((row << 1) | row)) & ((1 << (2 * t + 3)) - 1)

    h23 = [r for r in rows if r['period'] > 8]
    # background: phase-aligned settled pattern (8 bits, t = 8j + phase, j large)
    def cycle(k):
        s = W[k]
        base = ((s.o + 7) // 8) * 8
        return ''.join(str(s.at(base + i)) for i in range(8))
    cyc = {k: cycle(k) for k in range(0, KMAX + 1)}
    spatial = None
    for m in range(1, 129):
        k0 = next((k0 for k0 in range(0, KMAX - 2 * m) if all(cyc[k] == cyc[k + m] for k in range(k0, KMAX - m + 1))), None)
        if k0 is not None and k0 < KMAX - 4 * m:
            spatial = {'m': m, 'from_k': k0, 'pattern': [cyc[k] for k in range(k0, k0 + m)]}
            break
    ratios = [(r['k'], r['onset'] / r['k']) for r in rows if r['k'] >= 50]
    fit_window = [x for x in rows if x['k'] >= KMAX // 2]
    n = len(fit_window)
    mx = sum(r['k'] for r in fit_window) / n
    my = sum(r['onset'] for r in fit_window) / n
    slope = sum((r['k'] - mx) * (r['onset'] - my) for r in fit_window) / sum((r['k'] - mx) ** 2 for r in fit_window)
    out = {
        'KMAX': KMAX, 'seconds': secs, 'loop9_rows_reproduced': len(loop9), 'lattice_T': LATTICE_T, 'lattice_mismatches': bad[:10],
        'H23_counterexamples': h23[:10], 'H23_counterexample_count': len(h23),
        'period_histogram': {str(p): sum(1 for r in rows if r['period'] == p) for p in sorted({r['period'] for r in rows})},
        'background': spatial,
        'front': {'onset_over_k_min_k_ge_50': round(min(x[1] for x in ratios), 4), 'onset_over_k_max_k_ge_50': round(max(x[1] for x in ratios), 4),
                  'least_squares_slope_k_ge_300': round(slope, 4), 'onset_at_KMAX': rows[-1]['onset'],
                  'first_k_with_onset_gt_k': next((r['k'] for r in rows if r['k'] >= 1 and r['onset'] > r['k'] and all(x['onset'] > x['k'] for x in rows if x['k'] >= r['k'])), None)},
        'rows': rows,
    }
    (HERE / 'left_zone.json').write_text(json.dumps(out, indent=1) + '\n')
    assert not bad, bad[:5]
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    lt.add_assertion(book, 'H23', 'Every left-edge diagonal w_k has least eventual period at most 8.', 'OPEN', deps=['TR'])
    lt.add_assertion(book, 'F9', f'Exact left-edge periods and onsets certified for k<={KMAX}; reproduces loop 9 for k<=72 and a direct lattice for t<={LATTICE_T}.', 'FINITE_VERIFIED', '', deps=['TR'])
    if r['H23_counterexamples']:
        c = r['H23_counterexamples'][0]
        lt.set_status(book, 'H23', 'FALSIFIED', f'w_{c["k"]} has least eventual period {c["period"]} (E27).', replacement='TR')
    else:
        lt.set_status(book, 'H23', 'FINITE_VERIFIED', f'All k<={KMAX}: periods {r["period_histogram"]}. Finite only.')
    lt.add_evidence(book, 'E27', 'research/loop-10-left-zone/left_zone.json', supports=['H23', 'F9'])
    bg = r['background']
    fr = r['front']
    return (f'Left edge certified to k={KMAX}. H23 {"FALSIFIED" if r["H23_counterexamples"] else "held"} (periods {r["period_histogram"]}). '
            f'Background: {"periodic in k with spatial period " + str(bg["m"]) + " from k=" + str(bg["from_k"]) if bg else "no spatial period <= 128 found"}. '
            f'Front: onset/k between {fr["onset_over_k_min_k_ge_50"]} and {fr["onset_over_k_max_k_ge_50"]} for k>=50, slope {fr["least_squares_slope_k_ge_300"]}.')


consumed = lt.run_loop('effortless-10', 'H23: every left-edge diagonal has least eventual period at most 8.', edit, ['H23', 'F9', 'TR', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H23', 'F9', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H23_counterexample_count', 'H23_counterexamples', 'period_histogram', 'background', 'front')}, indent=1))
