"""Loop 22: TX, B9, and the seeded (left-consistent) relaxation. See PROOFS.md and docs/p1-frontier.md."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-13-top-down'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt
from left_cone import primitive_words
from seeded import grow, tail_death

HERE = Path(__file__).resolve().parent
TMAX2, TMAX34, Wd = 46, 32, 3
RESULT = {}


def compute():
    t0 = time.time()
    words = {'01': TMAX2, '10': TMAX2}
    for p in (3, 4):
        for a in primitive_words(p):
            words[a] = TMAX34
    rows, sizes = [], {}
    for t, B in grow(TMAX2 - 1, Wd, cap=1 << 27):
        T = t + 1
        sizes[str(t)] = int(B.shape[0])
        if T < 4:
            continue
        for a, tm in words.items():
            if T > tm:
                continue
            d, alive = tail_death(B, T, a, 2 * T + 8, Wd)
            ex = d[d >= 0] - T
            rows.append({'a': a, 'p': len(a), 'T': T, 'prefixes': int(B.shape[0]), 'survivors': int(alive.sum()),
                         'excess_max': int(ex.max()) if ex.size else None, 'excess_mean': round(float(ex.mean()), 2) if ex.size else None,
                         'death_before_2T_minus_1': bool(alive.sum() == 0 and d.max() < 2 * T - 1),
                         'excess_hist': {str(k): int(v) for k, v in zip(*np.unique(ex, return_counts=True))}})
        print(f'T={T} prefixes={B.shape[0]} ({time.time() - t0:.0f}s)', flush=True)
    two = [r for r in rows if r['p'] == 2]
    other = [r for r in rows if r['p'] > 2]
    out = {'TMAX2': TMAX2, 'TMAX34': TMAX34, 'seconds': round(time.time() - t0, 1), 'tree_sizes': sizes,
           'growth_ratio_last10': round((sizes[str(TMAX2 - 1)] / sizes[str(TMAX2 - 11)]) ** 0.1, 4),
           'H35_holds': all(r['death_before_2T_minus_1'] for r in two),
           'H36_holds': all(r['death_before_2T_minus_1'] for r in other),
           'H35_failures': [{k: r[k] for k in ('a', 'T', 'survivors', 'excess_max')} for r in two if not r['death_before_2T_minus_1']],
           'H36_failures': [{k: r[k] for k in ('a', 'T', 'survivors', 'excess_max')} for r in other if not r['death_before_2T_minus_1']],
           'period2_excess_max_by_T': {a: {str(r['T']): r['excess_max'] for r in two if r['a'] == a} for a in ('01', '10')},
           'period34_excess_max_overall': max((r['excess_max'] for r in other if r['excess_max'] is not None), default=None),
           'period34_excess_max_by_T': {str(T): max(r['excess_max'] for r in other if r['T'] == T) for T in range(4, TMAX34 + 1)},
           'rows': rows}
    (HERE / 'seeded.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TX', 'B9', 'H35', 'H36', 'F21', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-22-left-consistent/PROOFS.md'
    lt.add_assertion(book, 'TX', 'The left half x(i,t), i<=-1, is a function of c(0..t-1) and the seed, and whenever c(t)=1 the forward rule forces c(t+1)=NOT x(-1,t): the center is left-consistent.', 'PROVED_HUMAN_READABLE', ps + ' §TX', deps=['D0', 'T0'])
    lt.add_assertion(book, 'B9', 'No left-consistent sequence (c(0)=1, and c(t+1)=NOT x(-1,t) whenever c(t)=1, with x the left half it generates from the seed) ends in a periodic tail with a nonconstant word.', 'OPEN', deps=['TX'])
    lt.add_dependency(book, 'B9', 'B5'); lt.add_dependency(book, 'B9', 'TU')
    lt.set_status(book, 'B9', 'PROVED_HUMAN_READABLE', 'Derived from B5 and TU (PROOFS.md §B9): a left-consistent sequence with a periodic tail from T gives a row at T satisfying every relaxation constraint, which B5 forbids. B9 is weaker than B5; a direct proof would replace this premise. Compiles BLOCKED while B5 is.')
    lt.add_dependency(book, 'B1', 'B9'); lt.add_dependency(book, 'B1', 'TX')
    lt.row(book, 'Assertions', 'B1')['ProofSection'] = ps + ' §B9 (B1 from B9 and TX); earlier route research/loop-13-top-down/PROOFS.md §Route L'
    lt.add_assertion(book, 'H35', f'For the words 01 and 10 and every onset 4<=T<={TMAX2}, every left-consistent prefix c(0..T-1) is killed by the 2-periodic tail before time 2T-1, inside the zone where the free-row relaxation provably cannot kill (TW).', 'OPEN', deps=['TX', 'TW'])
    lt.add_assertion(book, 'H36', f'For every nonconstant primitive word of period 3 or 4 and every onset 4<=T<={TMAX34}, every left-consistent prefix is killed by the periodic tail before time 2T-1.', 'OPEN', deps=['TX', 'TW'])
    lt.add_assertion(book, 'F21', f'Seeded relaxation table: for the words 01, 10 (onsets 4..{TMAX2}) and every primitive word of period 3 and 4 (onsets 4..{TMAX34}), the number of left-consistent prefixes, survivors, and the largest and mean death excess t*-T with its histogram; tree growth ratio {r["growth_ratio_last10"]} per step.', 'FINITE_VERIFIED', '', deps=['TX'])
    for h, key in (('H35', 'H35'), ('H36', 'H36')):
        if r[f'{key}_holds']:
            detail = json.dumps(r['period2_excess_max_by_T']) if h == 'H35' else json.dumps(r['period34_excess_max_by_T'])
            lt.set_status(book, h, 'FINITE_VERIFIED', f'All prefixes die before 2T-1; max excess by onset {detail} (E48). Finite only.')
        else:
            lt.set_status(book, h, 'FALSIFIED', f'{len(r[key + "_failures"])} failures, first {json.dumps(r[key + "_failures"][0])} (E48).', replacement='TX')
    lt.add_evidence(book, 'E48', 'research/loop-22-left-consistent/seeded.json', supports=['H35', 'H36', 'F21', 'B9'])
    lt.add_evidence(book, 'E49', ps, supports=['TX', 'B9', 'B1'])
    lt.add_evidence(book, 'E50', 'docs/p1-frontier.md', supports=['B1', 'B7', 'B8', 'B9'])
    return (f'Consolidated the P1 frontier (docs/p1-frontier.md: chain, reductions, 7 ruled-out mechanisms; dyadic wall corrected). TX proved; B9 (no left-consistent sequence has a nonconstant periodic tail) inserted under B1. '
            f'H35 {"held" if r["H35_holds"] else "FALSIFIED"}: period-2 max excess by onset {json.dumps(r["period2_excess_max_by_T"])}. '
            f'H36 {"held" if r["H36_holds"] else "FALSIFIED"}: period 3-4 max excess {r["period34_excess_max_overall"]}.')


consumed = lt.run_loop('effortless-22', f'Consolidate the P1 frontier; TX (the center is left-consistent) and B9 under B1. H35: every left-consistent prefix is killed by a 2-periodic tail before time 2T-1, onsets 4..{TMAX2}; H36: the same for periods 3-4, onsets 4..{TMAX34}.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'growth_ratio_last10', 'H35_holds', 'H36_holds', 'H35_failures', 'H36_failures', 'period2_excess_max_by_T', 'period34_excess_max_overall')}, indent=1))
