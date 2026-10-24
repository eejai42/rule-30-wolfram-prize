"""Loop 19: split B6 into B7 (period 2) and B8 (period >= 3); test the exact wall for 01/10 at T=47..50."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
import loop_tools as lt
from left_cone_fast import counts

HERE = Path(__file__).resolve().parent
CAP = 1 << 26
RESULT = {}


def compute():
    t0 = time.time()
    prev = {r['a']: r for r in []}
    old = json.load(open(HERE.parent / 'loop-18-kill-cell' / 'kill_cell.json'))['rows']
    rows = [{'T': r['T'], 'a': r['a'], 'L': r['L'], 'survivors': r['survivors'], 'source': 'loop18'} for r in old if not r['capped']]
    for a in ('01', '10'):
        for T in (2, 3):
            cs, fz, cap = counts(T, a, 4 * T + 16, cap=CAP)
            rows.append({'T': T, 'a': a, 'L': fz, 'survivors': None, 'source': 'loop19'})
        for T in range(47, 51):
            d = {}
            t1 = time.time()
            cs, fz, cap = counts(T, a, 70, cap=CAP, death=d)
            rows.append({'T': T, 'a': a, 'L': fz, 'capped': cap, 'survivors': d.get('live_before'), 'peak_live': max(x for x in cs if x is not None),
                         'seconds': round(time.time() - t1, 1), 'source': 'loop19'})
            print(f'{a} T={T} L={fz} capped={cap} surv={d.get("live_before")} {time.time() - t0:.0f}s', flush=True)
    rows.sort(key=lambda r: (r['a'], r['T']))
    new = [r for r in rows if r['source'] == 'loop19' and r['T'] >= 47]
    want = {'01': 64, '10': 65}
    holds = all((not r.get('capped')) and r['L'] == want[r['a']] for r in new)
    out = {'CAP_live': CAP, 'seconds': round(time.time() - t0, 1), 'H32_holds': holds,
           'new_cases': [{k: r.get(k) for k in ('a', 'T', 'L', 'capped', 'survivors', 'peak_live', 'seconds')} for r in new],
           'L_by_T': {a: {str(r['T']): r['L'] for r in rows if r['a'] == a} for a in ('01', '10')},
           'rows': rows}
    (HERE / 'period2.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['B6', 'B7', 'B8', 'H32', 'F18', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-19-period-2/PROOFS.md'
    lt.add_assertion(book, 'B7', 'B6 for the period-2 words 01 and 10: for every onset T>=2, each TW row for a 2-periodic center violates a one-time constraint at or after 2T-1 (equivalently, the Rule 30 center is not eventually 2-periodic).', 'OPEN', deps=['T0', 'TU', 'TW'])
    lt.add_assertion(book, 'B8', 'B6 for every nonconstant word of least period p>=3.', 'OPEN', deps=['T0', 'TU', 'TW'])
    lt.add_dependency(book, 'B6', 'B7'); lt.add_dependency(book, 'B6', 'B8')
    lt.row(book, 'Assertions', 'B6')['ProofSection'] = ps + ' §Why period 2 first'
    lt.set_status(book, 'B6', 'PROVED_HUMAN_READABLE', 'Case split: every nonconstant word has least period 2 (B7) or at least 3 (B8). Compiles BLOCKED until both are discharged.')
    lt.add_assertion(book, 'H32', 'The dyadic wall is exact for period 2 past onset 36: for a=01 and every onset 47<=T<=50 the left-cone relaxation dies at window exactly 64, and for a=10 at exactly 65.', 'OPEN', deps=['T0', 'TU', 'TV', 'TW'])
    lt.add_assertion(book, 'F18', 'L(T) for the words 01 and 10 at every onset 2<=T<=50 (loop 18 data plus onsets 2, 3 and 47..50 computed here with cap 2^26), with survivors at the death step.', 'FINITE_VERIFIED', '', deps=['T0', 'TU'])
    nc = json.dumps([(c['a'], c['T'], c['L']) for c in r['new_cases']])
    if r['H32_holds']:
        lt.set_status(book, 'H32', 'FINITE_VERIFIED', f'New cases {nc} (E42). Finite only.')
    else:
        lt.set_status(book, 'H32', 'FALSIFIED', f'New cases {nc} (E42).', replacement='TW')
    lt.add_evidence(book, 'E42', 'research/loop-19-period-2/period2.json', supports=['H32', 'F18', 'B7'])
    lt.add_evidence(book, 'E43', ps, supports=['B6', 'B7', 'B8', 'H32'])
    return f'B6 split into B7 (period 2) and B8 (period>=3); focus on B7. H32 {"held" if r["H32_holds"] else "FALSIFIED"}: {nc}. Wall at 64/65 for 01/10 now {"confirmed" if r["H32_holds"] else "broken"} on 37<=T<=50.'


consumed = lt.run_loop('effortless-19', 'Split B6 into B7 (period 2) and B8 (period>=3). H32: for a=01 the left-cone relaxation dies at window exactly 64 for every 47<=T<=50 (65 for a=10).', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H32_holds', 'new_cases')}, indent=1))
