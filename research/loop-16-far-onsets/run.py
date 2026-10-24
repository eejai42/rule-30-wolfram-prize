"""Loop 16: single-zero words to onsets near 25p with a 2^25 live-set cap. See PROOFS.md."""
import json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
import loop_tools as lt
from left_cone_fast import counts

HERE = Path(__file__).resolve().parent
PERIODS, CAP, BOUND, RUN_BUDGET_S = (8, 10, 12, 16), 1 << 25, 64, 1800.0
RESULT = {}


def onsets(p):
    T = 32
    while T <= 40 * p:
        yield T
        T += 16 if T < 128 else 32


def fit(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx, 4) if sxx else None


def compute():
    t0 = time.time()
    rows = []
    for p in PERIODS:
        a = '0' + '1' * (p - 1)
        for T in onsets(p):
            Lmax = T + BOUND + 8
            death = {}
            t1 = time.time()
            cs, fz, cap = counts(T, a, Lmax, cap=CAP, death=death)
            dt = round(time.time() - t1, 1)
            rows.append({'T': T, 'p': p, 'a': a, 'Lmax': Lmax, 'first_zero_L': fz, 'excess': (fz - T) if fz else None, 'capped': cap,
                         'peak_live': max(x for x in cs if x is not None), 'seconds': dt, 'count_at_Lmax': cs[-1], 'death': death})
            print(f'p={p} T={T} L={fz} excess={(fz - T) if fz else None} capped={cap} peak={rows[-1]["peak_live"]} {dt}s ({time.time() - t0:.0f}s)', flush=True)
            if cap or dt > RUN_BUDGET_S:
                break
    done = [r for r in rows if not r['capped']]
    viol = [r for r in done if r['first_zero_L'] is None or r['excess'] > BOUND]
    far = [r for r in done if r['T'] >= 64 and r['excess'] is not None]
    out = {
        'PERIODS': PERIODS, 'CAP_live': CAP, 'BOUND': BOUND, 'seconds': round(time.time() - t0, 1),
        'cases_completed': len(done), 'largest_T_completed': max(r['T'] for r in done), 'H29_holds': not viol,
        'violations': [{k: r[k] for k in ('T', 'p', 'a', 'first_zero_L', 'excess', 'count_at_Lmax')} for r in viol],
        'excess_by_T': {f'{r["p"]}:{r["T"]}': r['excess'] for r in done},
        'excess_max': max(r['excess'] for r in done if r['excess'] is not None),
        'fit_excess_vs_T_slope_T>=64': fit([r['T'] for r in far], [r['excess'] for r in far]),
        'fit_excess_vs_log2T_slope_T>=64': fit([math.log2(r['T']) for r in far], [r['excess'] for r in far]),
        'rows': rows,
    }
    (HERE / 'far_onsets.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H29', 'F15', 'B5', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-16-far-onsets/PROOFS.md'
    lt.add_assertion(book, 'H29', f'For the single-zero words a=0 1^(p-1), p in {list(PERIODS)}, and every onset T>=32 that exact enumeration completes (cap 2^25), the left-cone exclusion excess L(T,a)-T is at most {BOUND}.', 'OPEN', deps=['T0', 'TU', 'TV'])
    lt.add_assertion(book, 'F15', f'Exclusion lengths, excess and death cells of the left-cone relaxation for the single-zero words of periods {list(PERIODS)} at onsets from 32 to the enumeration limit (largest completed {r["largest_T_completed"]}), with the excess fitted against T and log2 T.', 'FINITE_VERIFIED', '', deps=['T0', 'TU', 'TV'])
    if r['H29_holds']:
        lt.set_status(book, 'H29', 'FINITE_VERIFIED', f'{r["cases_completed"]} cases to onset {r["largest_T_completed"]}, max excess {r["excess_max"]}; excess slope vs T {r["fit_excess_vs_T_slope_T>=64"]}, vs log2 T {r["fit_excess_vs_log2T_slope_T>=64"]} (E36). Finite only.')
    else:
        v = r['violations'][0]
        lt.set_status(book, 'H29', 'FALSIFIED', f'p={v["p"]} T={v["T"]}: L={v["first_zero_L"]}, excess {v["excess"]} (E36).', replacement='B5')
    lt.add_evidence(book, 'E36', 'research/loop-16-far-onsets/far_onsets.json', supports=['H29', 'F15', 'B5'])
    lt.add_evidence(book, 'E37', ps, supports=['H29'])
    return (f'H29 {"held" if r["H29_holds"] else "FALSIFIED"}: single-zero words p={list(PERIODS)} to onset {r["largest_T_completed"]}, max excess {r["excess_max"]}; '
            f'excess slope vs T {r["fit_excess_vs_T_slope_T>=64"]}, vs log2 T {r["fit_excess_vs_log2T_slope_T>=64"]}. B5 remains the open child of B1.')


consumed = lt.run_loop('effortless-16', f'H29: for the single-zero words of periods {list(PERIODS)} the left-cone exclusion excess stays at most {BOUND} at every onset T>=32 the enumeration completes (cap 2^25).', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H29_holds', 'cases_completed', 'largest_T_completed', 'excess_max', 'excess_by_T', 'fit_excess_vs_T_slope_T>=64', 'fit_excess_vs_log2T_slope_T>=64', 'violations')}, indent=1))
