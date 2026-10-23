"""Loop 14: push the left-cone exclusion (B5) as far as exact enumeration reaches.

TU (PROOFS.md) rewrites the relaxation as a driven left half with T-1 free bits. H27: the
loop 13 bound L(T,a) <= 4T+4p+8 keeps holding for every primitive nonconstant word of period
p <= 6 at every onset the enumeration completes. F13 is the table. Hypothesis stated before
computing; see PROOFS.md.
"""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-13-top-down'))
import loop_tools as lt
from left_cone import primitive_words
from left_cone_fast import counts

HERE = Path(__file__).resolve().parent
PMAX, TSTART, TMAX_HARD = 6, 2, 160
MEM = int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout or 0)
CAP = 1 << (23 if MEM >= 16 << 30 else 22)
RUN_BUDGET_S = 90.0
RESULT = {}


def onsets():
    T = TSTART
    while T <= TMAX_HARD:
        yield T
        T += 1 if T < 24 else (2 if T < 60 else 4)


def compute():
    t0 = time.time()
    rows, log = [], []
    for p in range(1, PMAX + 1):
        for a in primitive_words(p):
            tmax_done = None
            for T in onsets():
                Lmax = 4 * T + 4 * p + 8
                t1 = time.time()
                cs, fz, cap = counts(T, a, Lmax, cap=CAP)
                dt = round(time.time() - t1, 2)
                peak = max(x for x in cs if x is not None)
                rows.append({'T': T, 'p': p, 'a': a, 'Lmax': Lmax, 'first_zero_L': fz, 'capped': cap, 'peak_live': peak, 'seconds': dt,
                             'count_at_Lmax': cs[-1]})
                if cap or dt > RUN_BUDGET_S:
                    break
                tmax_done = T
            log.append({'a': a, 'p': p, 'T_max_completed': tmax_done})
            print(f'a={a} done to T={tmax_done} ({time.time() - t0:.0f}s)', flush=True)
    done = [r for r in rows if not r['capped']]
    nonconst = [r for r in done if r['p'] >= 2]
    survivors = [r for r in nonconst if r['first_zero_L'] is None]
    bands = {}
    for r in nonconst:
        if r['first_zero_L'] is not None:
            b = str((r['T'] // 10) * 10)
            bands.setdefault(b, []).append(r['first_zero_L'] / r['T'])
    out = {
        'PMAX': PMAX, 'TSTART': TSTART, 'CAP_live': CAP, 'seconds': round(time.time() - t0, 1),
        'words': {str(p): list(primitive_words(p)) for p in range(1, PMAX + 1)},
        'cases_completed': len(done), 'nonconstant_completed': len(nonconst),
        'H27_holds': not survivors,
        'nonconstant_survivors': [{k: r[k] for k in ('T', 'p', 'a', 'Lmax', 'count_at_Lmax')} for r in survivors],
        'largest_T_completed_per_word': log,
        'largest_T_completed': max(r['T'] for r in nonconst),
        'ratio_L_over_T_max_by_T_band': {b: round(max(v), 3) for b, v in sorted(bands.items(), key=lambda kv: int(kv[0]))},
        'ratio_L_over_T_mean_by_T_band': {b: round(sum(v) / len(v), 3) for b, v in sorted(bands.items(), key=lambda kv: int(kv[0]))},
        'constants': [{k: r[k] for k in ('T', 'a', 'first_zero_L', 'count_at_Lmax', 'capped')} for r in rows if r['p'] == 1][-6:],
        'rows': rows,
    }
    (HERE / 'left_cone_growth.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TU', 'H27', 'F13', 'B5', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-14-left-cone-growth/PROOFS.md'
    lt.add_assertion(book, 'TU', 'For L>=T the left-cone relaxation is in bijection with rows R at time T on positions -T+1..-1 such that the Rule 30 evolution of the left half from R, with the center prescribed as boundary x(0,t)=c\'(t), satisfies x(-1,t)=NOT c\'(t+1) at every one-time t<=T+L-1; column 1 is determined, and count(T,a,L)<=2^(T-1).', 'PROVED_HUMAN_READABLE', ps + ' §TU', deps=['D0', 'T0', 'TS'])
    lt.add_assertion(book, 'H27', f'For every primitive nonconstant word a of period p<={PMAX} and every onset 2<=T<=T_max(a) that exact enumeration completes (live-set cap 2^{CAP.bit_length() - 1}), the left cone excludes the periodic center with L(T,a)<=4T+4p+8.', 'OPEN', deps=['T0', 'TS', 'TU'])
    lt.add_assertion(book, 'F13', f'Exclusion lengths L(T,a) of the left-cone relaxation for every primitive word of period <={PMAX}, onsets from 2 up to the enumeration limit per word (largest completed onset {r["largest_T_completed"]}); vectorised search validated against the loop 13 table and an independent SAT encoding of TU.', 'FINITE_VERIFIED', '', deps=['T0', 'TS', 'TU'])
    bands = r['ratio_L_over_T_max_by_T_band']
    if r['H27_holds']:
        lt.set_status(book, 'H27', 'FINITE_VERIFIED', f'{r["nonconstant_completed"]} nonconstant cases completed, all excluded within 4T+4p+8; max L/T by onset band {json.dumps(bands)} (E32). Finite only.')
    else:
        s = r['nonconstant_survivors'][0]
        lt.set_status(book, 'H27', 'FALSIFIED', f'T={s["T"]} a={s["a"]}: {s["count_at_Lmax"]} compatible windows at L={s["Lmax"]} (E32); {len(r["nonconstant_survivors"])} survivors.', replacement='B5')
    lt.add_evidence(book, 'E32', 'research/loop-14-left-cone-growth/left_cone_growth.json', supports=['H27', 'F13', 'B5'])
    lt.add_evidence(book, 'E33', ps, supports=['TU', 'B5'])
    return (f'TU proved: the relaxation is a driven left half with T-1 free bits. H27 {"held" if r["H27_holds"] else "FALSIFIED"}: '
            f'{r["nonconstant_completed"]} nonconstant cases (p<={PMAX}, onsets to {r["largest_T_completed"]}) {"all" if r["H27_holds"] else "not all"} excluded by the left cone alone; '
            f'max L/T by onset band {json.dumps(bands)}; mean {json.dumps(r["ratio_L_over_T_mean_by_T_band"])}. B5 remains the open child of B1.')


consumed = lt.run_loop('effortless-14', f'H27: the left-cone exclusion L(T,a)<=4T+4p+8 holds for every primitive nonconstant word of period p<={PMAX} at every onset exact enumeration completes; TU rewrites the relaxation as a driven left half with T-1 free bits.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H27_holds', 'cases_completed', 'nonconstant_completed', 'largest_T_completed', 'ratio_L_over_T_max_by_T_band', 'ratio_L_over_T_mean_by_T_band', 'nonconstant_survivors')}, indent=1))
