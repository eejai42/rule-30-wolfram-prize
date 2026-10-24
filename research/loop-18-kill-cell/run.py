"""Loop 18: common killing cell for words 01 and 10, onsets 4..46. See PROOFS.md."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
import loop_tools as lt
from left_cone_fast import counts

HERE = Path(__file__).resolve().parent
WORDS, TMIN, TMAX, CAP = ('01', '10'), 4, 46, 1 << 24
RESULT = {}


def compute():
    t0 = time.time()
    rows = []
    for a in WORDS:
        for T in range(TMIN, TMAX + 1):
            d = {}
            cs, fz, cap = counts(T, a, 4 * T + 16, cap=CAP, death=d)
            hist = {int(s): n for s, n in d['fail_hist_by_column'].items()} if d else {}
            lb = d.get('live_before', 0)
            common = sorted(s for s, n in hist.items() if n == lb)
            L = d.get('window_L')
            cells = [{'column': s, 'time': T + L - s, 'is_edge': s == T + L - s} for s in common] if common else []
            rows.append({'T': T, 'a': a, 'L': fz, 'death_time_window_end': T + fz if fz else None, 'capped': cap, 'survivors': lb,
                         'violated_cells': {str(s): {'n': n, 'time': T + L - s, 'is_edge': s == T + L - s} for s, n in sorted(hist.items())},
                         'common_killing_cells': cells, 't_star': min(c['time'] for c in cells) if cells else None,
                         's_star': [c['column'] for c in cells if c['time'] == min(c['time'] for c in cells)][0] if cells else None,
                         'edge_is_common': any(c['is_edge'] for c in cells)})
        print(f'{a} done ({time.time() - t0:.0f}s)', flush=True)
    out = {'WORDS': WORDS, 'TMIN': TMIN, 'TMAX': TMAX, 'seconds': round(time.time() - t0, 1)}
    for a in WORDS:
        rs = [r for r in rows if r['a'] == a and not r['capped']]
        ts = [r['t_star'] for r in rs]
        steps = [ts[i + 1] - ts[i] if (ts[i] is not None and ts[i + 1] is not None) else None for i in range(len(ts) - 1)]
        out[a] = {'cases': len(rs), 'common_cell_always': all(r['common_killing_cells'] for r in rs),
                  'cases_without_common_cell': [r['T'] for r in rs if not r['common_killing_cells']],
                  't_star_by_T': {str(r['T']): r['t_star'] for r in rs}, 'steps': steps,
                  'staircase': all(s in (0, 1) for s in steps if s is not None) and all(s is not None for s in steps),
                  'edge_is_common_count': sum(1 for r in rs if r['edge_is_common']),
                  'excess_t_star_minus_T': {str(r['T']): (r['t_star'] - r['T']) if r['t_star'] is not None else None for r in rs},
                  'multiple_common_cells': [r['T'] for r in rs if len(r['common_killing_cells']) > 1]}
    out['H31_holds'] = all(out[a]['common_cell_always'] and out[a]['staircase'] for a in WORDS)
    out['rows'] = rows
    (HERE / 'kill_cell.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H31', 'F17', 'B6', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-18-kill-cell/PROOFS.md'
    lt.add_assertion(book, 'H31', f'For the words 01 and 10 and every onset {TMIN}<=T<={TMAX}, a cone cell violated by every surviving window exists at the death step, and its time t*(T) is non-decreasing in T with steps 0 or 1.', 'OPEN', deps=['T0', 'TU', 'TV', 'TW'])
    lt.add_assertion(book, 'F17', f'For the words 01 and 10 at onsets {TMIN}..{TMAX}: the death window, survivors, the violated cone cells with counts, the common killing cells, whether the edge cell is among them, and t*(T).', 'FINITE_VERIFIED', '', deps=['T0', 'TU', 'TV'])
    summ = {a: {k: r[a][k] for k in ('cases', 'common_cell_always', 'cases_without_common_cell', 'staircase', 'edge_is_common_count')} for a in WORDS}
    if r['H31_holds']:
        lt.set_status(book, 'H31', 'FINITE_VERIFIED', f'{json.dumps(summ)}; t* staircase recorded (E40). Finite only.')
    else:
        lt.set_status(book, 'H31', 'FALSIFIED', f'{json.dumps(summ)} (E40).', replacement='TW')
    lt.add_evidence(book, 'E40', 'research/loop-18-kill-cell/kill_cell.json', supports=['H31', 'F17', 'B6'])
    lt.add_evidence(book, 'E41', ps, supports=['H31'])
    return f'H31 {"held" if r["H31_holds"] else "FALSIFIED"}: {json.dumps(summ)}. t*-T for 01: {json.dumps(r["01"]["excess_t_star_minus_T"])}.'


consumed = lt.run_loop('effortless-18', f'H31: for words 01 and 10 at onsets {TMIN}..{TMAX} a common killing cone cell exists at death and its time t*(T) is a staircase in T (steps 0 or 1).', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H31_holds', '01', '10')}, indent=1)[:6000])
