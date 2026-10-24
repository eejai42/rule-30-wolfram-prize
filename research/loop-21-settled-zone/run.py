"""Loop 21: settled-zone relaxation, exact and periodic-only, words 01 and 10, onsets 8..160. See PROOFS.md."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt
from settled import counts_settled, frontier, check_true_window

HERE = Path(__file__).resolve().parent
CAP, BOUND = 1 << 25, {'exact': 8, 'periodic': 16}
RESULT = {}


def onsets():
    T = 8
    while T <= 160:
        yield T
        T += 4 if T < 64 else 16


def compute():
    t0 = time.time()
    for T, L in [(12, 30), (40, 80), (80, 120)]:
        assert check_true_window(T, L), (T, L)
    rows = []
    for a in ('01', '10'):
        for mode in ('exact', 'periodic'):
            for T in onsets():
                d = {}; t1 = time.time()
                cs, fz, cap = counts_settled(T, a, 3 * T + 16, cap=CAP, death=d, mode=mode)
                sf = frontier(T)
                rows.append({'a': a, 'mode': mode, 'T': T, 'frontier': sf, 'L': fz, 'excess': (fz - sf) if fz else None, 'capped': cap,
                             'peak_live': max(x for x in cs if x is not None), 'survivors': d.get('live_before'),
                             'fail_cols': [d.get('fail_col_min'), d.get('fail_col_max')], 'seconds': round(time.time() - t1, 1)})
                print(f'{a} {mode} T={T} frontier={sf} L={fz} excess={rows[-1]["excess"]} capped={cap} {time.time() - t0:.0f}s', flush=True)
                if cap or (mode == 'periodic' and T >= 128):
                    break
    done = [r for r in rows if not r['capped']]
    viol = [r for r in done if r['excess'] is None or r['excess'] > BOUND[r['mode']]]
    out = {'CAP_live': CAP, 'BOUND': BOUND, 'seconds': round(time.time() - t0, 1), 'cases_completed': len(done), 'H34_holds': not viol,
           'violations': [{k: r[k] for k in ('a', 'mode', 'T', 'frontier', 'L', 'excess')} for r in viol],
           'excess_by_T': {f'{r["a"]}:{r["mode"]}': {} for r in done}, 'rows': rows}
    for r in done:
        out['excess_by_T'][f'{r["a"]}:{r["mode"]}'][str(r['T'])] = r['excess']
    (HERE / 'settled_zone.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H34', 'F20', 'B5', 'B7', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-21-settled-zone/PROOFS.md'
    lt.add_assertion(book, 'H34', 'With every settled left-edge diagonal imposed on the periodic-center relaxation (exact values, or periodicity only), the death window exceeds the settled frontier by at most 8 (exact) or 16 (periodic only) for the words 01 and 10 at every onset 8<=T<=160 the search completes: the clash with the settled zone is local.', 'OPEN', deps=['T0', 'TR', 'TU', 'F11'])
    lt.add_assertion(book, 'F20', 'Settled-zone relaxation table for the words 01 and 10, exact and periodicity-only modes, onsets 8..160: frontier, death window, excess, peak live set, failing columns; the true lattice satisfies every imposed constraint to time 400.', 'FINITE_VERIFIED', '', deps=['T0', 'TR', 'TU', 'F11'])
    ex = r['excess_by_T']
    if r['H34_holds']:
        lt.set_status(book, 'H34', 'FINITE_VERIFIED', f'{r["cases_completed"]} cases; excess by onset {json.dumps(ex)} (E46). Finite only.')
    else:
        v = r['violations'][0]
        lt.set_status(book, 'H34', 'FALSIFIED', f'{len(r["violations"])} of {r["cases_completed"]} cases exceed the bound, first {json.dumps(v)}; excess by onset {json.dumps(ex)} (E46).', replacement='TR')
    lt.add_evidence(book, 'E46', 'research/loop-21-settled-zone/settled_zone.json', supports=['H34', 'F20', 'B5'])
    lt.add_evidence(book, 'E47', ps, supports=['H34'])
    return (f'Settled-zone relaxation: H34 {"held" if r["H34_holds"] else "FALSIFIED"}; excess past the settled frontier by onset {json.dumps(ex)}. '
            + ('The clash is local: next loop states B9/B10 and rewires B1.' if r['H34_holds'] else 'The clash is not local even against the settled zone; the relaxation programme has reached its natural end for P1.'))


consumed = lt.run_loop('effortless-21', 'H34: with the settled left-edge diagonals imposed, the periodic-center relaxation dies within 8 (exact) / 16 (periodic-only) windows past the settled frontier for 01 and 10, onsets 8..160.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'cases_completed', 'H34_holds', 'excess_by_T')}, indent=1))
