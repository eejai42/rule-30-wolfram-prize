"""Loop 11: the speed of the left-edge front.

Loop 10 saw the onset of the left-edge diagonal w_k grow like ~1.25 k (least-squares slope 1.2529
on k = 300..600). Hypothesis H24 (stated, with its tolerance, before computing):

    for every 1000 <= k <= 5000:  | onset_k / k - 5/4 | <= 0.02

i.e. the settled zone at the left edge spreads inward at 4/5 of a diagonal per step, which puts
its boundary at position about -t/5 at time t.

Observation recorded alongside: whether onset_k > k for every k >= 20 (the center c(t) = w_t(t)
is always read before its left-edge diagonal settles), and where each new period first appears.
Exact, with research/left_edge.py; direct lattice cross-check for t <= 1600.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
from left_edge import BASE, certify

HERE = Path(__file__).resolve().parent
KMAX, LATTICE_T, TOL = 5000, 1600, 0.02
RESULT = {}


def compute():
    loop10 = {r['k']: r for r in json.loads((lt.ROOT / 'research/loop-10-left-zone/left_zone.json').read_text())['rows']}
    t0 = time.time()
    W = dict(BASE)
    rows = [{'k': 0, 'period': 1, 'onset': 0}]
    for k in range(1, KMAX + 1):
        s = certify(k, W[k - 1], W[k - 2])
        W[k] = s
        if k - 3 > 2 * LATTICE_T:      # older words are only needed for the lattice check
            W.pop(k - 3, None)
        rows.append({'k': k, 'period': s.p, 'onset': s.o})
        if k in loop10:
            assert (s.p, s.o) == (loop10[k]['period'], loop10[k]['onset']), k
    secs = round(time.time() - t0, 2)

    row, bad = 1, []
    kmax_l = min(KMAX, 2 * LATTICE_T)
    for t in range(LATTICE_T + 1):
        for kk in range(0, min(kmax_l, 2 * t) + 1):
            if ((row >> kk) & 1) != W[kk].at(t):
                bad.append((kk, t))
        row = ((row << 2) ^ ((row << 1) | row)) & ((1 << (2 * t + 3)) - 1)

    h24 = [r for r in rows if 1000 <= r['k'] <= KMAX and abs(r['onset'] / r['k'] - 1.25) > TOL]
    dev = [(r['k'], r['onset'] - 1.25 * r['k']) for r in rows if r['k'] >= 1000]
    first_period = {}
    for r in rows:
        first_period.setdefault(r['period'], r['k'])
    not_after = [r['k'] for r in rows if r['k'] >= 20 and r['onset'] <= r['k']]
    window = [r for r in rows if r['k'] >= KMAX // 2]
    mx = sum(r['k'] for r in window) / len(window)
    my = sum(r['onset'] for r in window) / len(window)
    slope = sum((r['k'] - mx) * (r['onset'] - my) for r in window) / sum((r['k'] - mx) ** 2 for r in window)
    out = {
        'KMAX': KMAX, 'seconds': secs, 'tolerance': TOL, 'loop10_rows_reproduced': len(loop10),
        'lattice_T': LATTICE_T, 'lattice_checked_k_max': kmax_l, 'lattice_mismatches': bad[:10],
        'H24_counterexamples': h24[:10], 'H24_counterexample_count': len(h24),
        'onset_minus_5k_over_4': {'min': round(min(d for _, d in dev), 2), 'max': round(max(d for _, d in dev), 2),
                                  'at_KMAX': round(dev[-1][1], 2)},
        'least_squares_slope_k_ge_2500': round(slope, 5),
        'first_k_with_period': {str(p): k for p, k in sorted(first_period.items())},
        'onset_le_k_for_k_ge_20': not_after[:20], 'onset_gt_k_for_all_k_ge_20': not not_after,
        'rows_every_100': [r for r in rows if r['k'] % 100 == 0],
    }
    (HERE / 'front_speed.json').write_text(json.dumps(out, indent=1) + '\n')
    assert not bad, bad[:5]
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    lt.add_assertion(book, 'H24', f'The left-edge front moves at 5/4: |onset_k/k - 5/4| <= {TOL} for every 1000 <= k <= {KMAX}.', 'OPEN', deps=['TR'])
    lt.add_assertion(book, 'F10', f'Exact left-edge periods and onsets certified for k<={KMAX}; reproduces loop 10 for k<=600 and a direct lattice for t<={LATTICE_T}.', 'FINITE_VERIFIED', '', deps=['TR'])
    if r['H24_counterexamples']:
        c = r['H24_counterexamples'][0]
        lt.set_status(book, 'H24', 'FALSIFIED', f'k={c["k"]}: onset {c["onset"]}, ratio {c["onset"] / c["k"]:.4f} (E28). {r["H24_counterexample_count"]} offsets outside the band.', replacement='TR')
    else:
        d = r['onset_minus_5k_over_4']
        lt.set_status(book, 'H24', 'FINITE_VERIFIED', f'onset_k - 5k/4 stays in [{d["min"]}, {d["max"]}] for k in 1000..{KMAX}; slope {r["least_squares_slope_k_ge_2500"]}. Finite only.')
    lt.add_evidence(book, 'E28', 'research/loop-11-front-speed/front_speed.json', supports=['H24', 'F10'])
    return (f'Left edge certified to k={KMAX} in {r["seconds"]}s. H24 {"FALSIFIED (" + str(r["H24_counterexample_count"]) + " offsets outside the band)" if r["H24_counterexamples"] else "held"}; '
            f'slope {r["least_squares_slope_k_ge_2500"]}; onset - 5k/4 in [{r["onset_minus_5k_over_4"]["min"]}, {r["onset_minus_5k_over_4"]["max"]}]. '
            f'First k per period: {r["first_k_with_period"]}. Onset > k for all k>=20: {r["onset_gt_k_for_all_k_ge_20"]}.')


consumed = lt.run_loop('effortless-11', f'H24: the left-edge front moves at 5/4 (|onset_k/k - 5/4| <= {TOL} for 1000<=k<={KMAX}).', edit, ['H24', 'F10', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H24', 'F10', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H24_counterexample_count', 'H24_counterexamples', 'onset_minus_5k_over_4', 'least_squares_slope_k_ge_2500', 'first_k_with_period', 'onset_gt_k_for_all_k_ge_20')}, indent=1))
