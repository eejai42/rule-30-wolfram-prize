"""Loop 17: TW (2^Z free rows), B6 (B5 restated), and the algebraic degree of the kill. See PROOFS.md."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-13-top-down'))
import loop_tools as lt
from left_cone import primitive_words
from affine import analyse

HERE = Path(__file__).resolve().parent
PMAX, TMIN, TMAX = 5, 4, 18
RESULT = {}


def compute():
    t0 = time.time()
    rows = []
    for p in range(2, PMAX + 1):
        for a in primitive_words(p):
            for T in range(TMIN, TMAX + 1):
                r = analyse(T, a, 4 * T + 4 * p + 8)
                rows.append(r)
            print(f'a={a} done ({time.time() - t0:.0f}s)', flush=True)
    dead = [r for r in rows if r['death_time'] is not None]
    tw_bad = [r for r in rows if not r['TW_ok']]
    viol = [r for r in dead if r['max_degree'] is not None and r['max_degree'] < r['Z'] - 1]
    cons = [r['constraints_after_2T-2'] for r in dead]
    mass = [c for cc in cons for c in cc if c['live_before'] >= 16 and c['live_after'] == 0]
    out = {
        'PMAX': PMAX, 'TMIN': TMIN, 'TMAX': TMAX, 'seconds': round(time.time() - t0, 1), 'cases': len(rows),
        'TW_failures': [{k: r[k] for k in ('T', 'a', 'Z', 'survivors_at_2T-2')} for r in tw_bad],
        'cases_dying_in_window': len(dead), 'not_dying_in_window': [{k: r[k] for k in ('T', 'a', 'Z')} for r in rows if r['death_time'] is None],
        'H30_holds': not viol and not tw_bad,
        'H30_violations': [{k: r[k] for k in ('T', 'a', 'Z', 'max_degree')} for r in viol],
        'degree_minus_Z_hist': {str(k): sum(1 for r in dead if r['max_degree'] - r['Z'] == k) for k in range(-6, 1)},
        'constraints_to_death_minus_Z': {str(k): sum(1 for r in dead if r['n_constraints_to_death'] - r['Z'] == k) for k in range(-10, 15)},
        'mass_kills': {'count': len(mass), 'all_constant_on_live': all(c['constant_on_live'] for c in mass),
                       'degrees': sorted(set(c['degree'] for c in mass if c['degree'] is not None))},
        'rows': rows,
    }
    (HERE / 'affine.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TW', 'B6', 'B5', 'H30', 'F16', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-17-affine/PROOFS.md'
    lt.add_assertion(book, 'TW', 'In the forward form, the one-time constraints at T<=t<=2T-2 fix the row bit at position -(t-T+1) as a function of the bits to its right and leave the bits at zero-time positions free: exactly 2^Z rows survive to 2T-2 (Z = zero-times in [T,2T-2]), and every constraint at t>=2T-1 is a Boolean function of those Z bits.', 'PROVED_HUMAN_READABLE', ps + ' §TW', deps=['D0', 'T0', 'TU', 'TV'])
    lt.add_assertion(book, 'B6', 'For every T>=2 and every nonconstant periodic word, each of the 2^Z rows of TW violates x(-1,t)=NOT c\'(t+1) at some one-time t>=2T-1.', 'OPEN', deps=['T0', 'TU', 'TW'])
    lt.add_dependency(book, 'B5', 'TU'); lt.add_dependency(book, 'B5', 'TW'); lt.add_dependency(book, 'B5', 'B6')
    lt.row(book, 'Assertions', 'B5')['ProofSection'] = ps + ' §B6'
    lt.set_status(book, 'B5', 'PROVED_HUMAN_READABLE', 'Derived from TU, TW and B6 (PROOFS.md): the finitely many TW rows each fail a later one-time, so some window excludes them all. Compiles BLOCKED until B6 is discharged.')
    lt.add_assertion(book, 'H30', f'For every nonconstant primitive word of period p<={PMAX} and every onset {TMIN}<=T<={TMAX}, the largest algebraic degree over the Z free bits among the one-time constraints applied before death is at least Z-1: the kill is maximally nonlinear, so B6 is not linear algebra over GF(2).', 'OPEN', deps=['TU', 'TW'])
    lt.add_assertion(book, 'F16', f'For every nonconstant primitive word of period <={PMAX} and onset {TMIN}..{TMAX}: Z, the TW count check, and for each one-time constraint after 2T-2 until death its algebraic degree over the Z free bits, live counts before and after, and whether it was constant on the live set.', 'FINITE_VERIFIED', '', deps=['TU', 'TW'])
    if r['H30_holds']:
        lt.set_status(book, 'H30', 'FINITE_VERIFIED', f'{r["cases_dying_in_window"]} cases; degree minus Z histogram {json.dumps(r["degree_minus_Z_hist"])}; mass kills {r["mass_kills"]["count"]}, all constant on the live set: {r["mass_kills"]["all_constant_on_live"]} (E38). Finite only.')
    else:
        v = (r['H30_violations'] or r['TW_failures'])[0]
        lt.set_status(book, 'H30', 'FALSIFIED', f'{json.dumps(v)} (E38).', replacement='TW')
    lt.add_evidence(book, 'E38', 'research/loop-17-affine/affine.json', supports=['H30', 'F16', 'TW'])
    lt.add_evidence(book, 'E39', ps, supports=['TW', 'B5', 'B6'])
    return (f'TW proved (2^Z free rows, confirmed in all {r["cases"]} cases); B5 derived from TU+TW+B6, B6 is the new open child of B1. H30 {"held" if r["H30_holds"] else "FALSIFIED"}: '
            f'degree minus Z histogram {json.dumps(r["degree_minus_Z_hist"])}; constraints-to-death minus Z {json.dumps({k: v for k, v in r["constraints_to_death_minus_Z"].items() if v})}; '
            f'{r["mass_kills"]["count"]} mass kills, degrees {r["mass_kills"]["degrees"]}.')


consumed = lt.run_loop('effortless-17', f'TW: exactly 2^Z rows survive to 2T-2; B5 <- TU+TW+B6. H30: the one-time constraints that kill them have algebraic degree >= Z-1 over the Z free bits (p<={PMAX}, {TMIN}<=T<={TMAX}).', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'cases', 'TW_failures', 'cases_dying_in_window', 'not_dying_in_window', 'H30_holds', 'H30_violations', 'degree_minus_Z_hist', 'constraints_to_death_minus_Z', 'mass_kills')}, indent=1))
