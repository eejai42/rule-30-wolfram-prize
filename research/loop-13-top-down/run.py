"""Loop 13: start from the finish. Decompose P1's one blocking obligation, B1.

Loops 1-12 added 33 claims; none has P1 downstream, and B1 (the only blocked ancestor of P1)
was a root. This loop (a) proves TS, the identity that moves column-1 agreement to column -1
under center agreement; (b) tests H26, that the left cone and the inverse rule alone exclude
every nonconstant periodic center word (p <= 4, onsets T <= 10) within L <= 4T+4p+8;
(c) marks B1 as derived from a stated open child (B5 if H26 holds, otherwise B4), so the
build compiles B1 as BLOCKED by that child and P1's blocking ancestor moves down one level.
Hypothesis stated before computing; see PROOFS.md.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.setrecursionlimit(20000)
import loop_tools as lt
from left_cone import counts, check_true_window, primitive_words

HERE = Path(__file__).resolve().parent
TMAX, PMAX = 10, 4
RESULT = {}


def compute():
    t0 = time.time()
    for T, L in [(1, 8), (4, 20), (10, 48)]:
        assert check_true_window(T, L), (T, L)
    rows, survivors, capped = [], [], []
    for p in range(1, PMAX + 1):
        for a in primitive_words(p):
            for T in range(1, TMAX + 1):
                Lmax = 4 * T + 4 * p + 8
                cs, fz, cap = counts(T, a, Lmax)
                row = {'T': T, 'p': p, 'a': a, 'Lmax': Lmax, 'first_zero_L': fz, 'capped': cap,
                       'count_at_Lmax': cs[-1], 'counts': cs}
                rows.append(row)
                nonconst = p >= 2
                if cap:
                    capped.append(row)
                if nonconst and fz is None:
                    survivors.append(row)
    excluded = [r for r in rows if r['p'] >= 2 and r['first_zero_L'] is not None]
    ratio = [r['first_zero_L'] / r['T'] for r in excluded]
    out = {
        'TMAX': TMAX, 'PMAX': PMAX, 'seconds': round(time.time() - t0, 1),
        'true_windows_checked': [[1, 8], [4, 20], [10, 48]],
        'words': {str(p): list(primitive_words(p)) for p in range(1, PMAX + 1)},
        'H26_holds': not survivors and not capped,
        'nonconstant_cases': sum(1 for r in rows if r['p'] >= 2),
        'nonconstant_excluded': len(excluded),
        'nonconstant_survivors': [{k: r[k] for k in ('T', 'p', 'a', 'Lmax', 'count_at_Lmax')} for r in survivors],
        'capped': [{k: r[k] for k in ('T', 'p', 'a')} for r in capped],
        'first_zero_over_T_min_max': [round(min(ratio), 3), round(max(ratio), 3)] if ratio else None,
        'first_zero_L_by_T_max_over_words': {str(T): max((r['first_zero_L'] for r in excluded if r['T'] == T), default=None) for T in range(1, TMAX + 1)},
        'constants': [{k: r[k] for k in ('T', 'a', 'first_zero_L', 'count_at_Lmax')} for r in rows if r['p'] == 1],
        'rows': rows,
    }
    (HERE / 'left_cone_table.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TS', 'H26', 'F12', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-13-top-down/PROOFS.md'
    lt.add_assertion(book, 'TS', 'If the center p-agrees at t and t+1 then column -1 p-agrees at t when c(t)=1, and column -1 p-agrees at t iff column 1 does when c(t)=0: under center agreement, column -1 is column 1 read at the center\'s zero-times.', 'PROVED_HUMAN_READABLE', ps + ' §TS', deps=['D0'])
    lt.add_assertion(book, 'H26', f'For every onset 1<=T<={TMAX} and every nonconstant primitive word a of period p<={PMAX}, the left cone and the inverse rule alone exclude a p-periodic center of word a from onset T: no column-1 window is compatible once L reaches some L<=4T+4p+8.', 'OPEN', deps=['T0', 'TC', 'TS'])
    lt.add_assertion(book, 'F12', f'Left-cone relaxation table for every onset T<={TMAX} and every primitive word of period <={PMAX}: the number of column-1 windows (on the zero-times) compatible with a periodic center and the single-seed cone, for L<=4T+4p+8, with the first L that has none; the true (c,r) windows pass the same checker.', 'FINITE_VERIFIED', '', deps=['T0', 'TS'])
    if r['H26_holds']:
        lo, hi = r['first_zero_over_T_min_max']
        lt.set_status(book, 'H26', 'FINITE_VERIFIED', f'All {r["nonconstant_excluded"]} nonconstant cases (T<={TMAX}, p<={PMAX}) excluded; first_zero_L/T in [{lo}, {hi}] (E30). Finite only.')
        lt.add_assertion(book, 'B5', 'For every onset T, every p>=2 and every nonconstant word a of least period p, the left-cone relaxation (periodic center word a from T, free column 1, inverse rule, cone of T0) is unsatisfiable at some finite L(T,a).', 'OPEN', deps=['T0', 'TS'])
        lt.add_dependency(book, 'B1', 'B5')
        lt.add_dependency(book, 'B1', 'T0')
        lt.row(book, 'Assertions', 'B1')['ProofSection'] = ps + ' §Route L'
        lt.set_status(book, 'B1', 'PROVED_HUMAN_READABLE', 'Derived from B5 and T0 (PROOFS.md §Route L): a least-period-p>=2 center is nonconstant, the true (c,r) satisfies every left-cone constraint, B5 says none can. Compiles BLOCKED until B5 is discharged.')
        child = 'B5'
    else:
        s = r['nonconstant_survivors'][0] if r['nonconstant_survivors'] else r['capped'][0]
        lt.set_status(book, 'H26', 'FALSIFIED', f'Left cone alone leaves slack: T={s["T"]}, a={s["a"]} has {s.get("count_at_Lmax")} compatible column-1 windows at L={s.get("Lmax")} (E30); {len(r["nonconstant_survivors"])} nonconstant survivors, {len(r["capped"])} capped.', replacement='TC')
        lt.add_assertion(book, 'B4', 'If the center is eventually p-periodic from onset T, then for some T\'>=T column 1 p-agrees on the whole window [T\', 2T\'+p]; by TS it suffices that column 1 agree at the center\'s zero-times there.', 'OPEN', deps=['D0', 'TS'])
        lt.add_dependency(book, 'B1', 'TC')
        lt.add_dependency(book, 'B1', 'B4')
        lt.row(book, 'Assertions', 'B1')['ProofSection'] = ps + ' §Route R'
        lt.set_status(book, 'B1', 'PROVED_HUMAN_READABLE', 'Derived from TC and B4 (PROOFS.md §Route R): center and column 1 both p-agree on [T\', 2T\'+p], which TC forbids. Compiles BLOCKED until B4 is discharged.')
        child = 'B4'
    CONSUME.append(child)
    lt.add_evidence(book, 'E30', 'research/loop-13-top-down/left_cone_table.json', supports=['H26', 'F12'])
    lt.add_evidence(book, 'E31', ps, supports=['TS', 'B1', child])
    RESULT['child'] = child
    fzT = r['first_zero_L_by_T_max_over_words']
    return (f'Top-down: B1 derived from {child} (new open child), TS proved. H26 '
            f'{"held" if r["H26_holds"] else "FALSIFIED"}: {r["nonconstant_excluded"]}/{r["nonconstant_cases"]} nonconstant (T<={TMAX}, p<={PMAX}) cases excluded by the left cone alone'
            f'{"; worst first_zero_L per T: " + json.dumps(fzT) if r["H26_holds"] else ""}. '
            f'Constants: a=1 dies by T+2 (TD), a=0 keeps slack ({[c["count_at_Lmax"] for c in r["constants"] if c["a"] == "0"][-1]} windows at T={TMAX}). '
            f'P1\'s blocking ancestor is now {child}.')


consumed = lt.run_loop('effortless-13', f'Top-down decomposition of P1: B1 <- TC+B4 or <- B5. H26: for every onset 1<=T<={TMAX} and every nonconstant primitive word of period p<={PMAX}, the left cone and the inverse rule alone exclude a p-periodic center by L<=4T+4p+8.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H26_holds', 'nonconstant_cases', 'nonconstant_excluded', 'nonconstant_survivors', 'capped', 'first_zero_over_T_min_max', 'first_zero_L_by_T_max_over_words', 'child')}, indent=1))
