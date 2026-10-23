"""Loop 15: is the left-cone contradiction a bounded distance past the cone?

H28 (stated before computing): for every primitive nonconstant word of period 7 or 8 and every
onset T >= 8 the enumeration completes, L(T,a) - T <= 64. TV proves why the death time sits
just past 2T. F14 records the cells where the last surviving windows die. See PROOFS.md.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-13-top-down'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
import loop_tools as lt
from left_cone import primitive_words
from left_cone_fast import counts

HERE = Path(__file__).resolve().parent
PERIODS, ONSETS, CAP, BOUND, RUN_BUDGET_S = (7, 8), (8, 16, 24, 32, 48, 64, 96, 128, 160, 192), 1 << 23, 64, 150.0
RESULT = {}


def compute():
    t0 = time.time()
    rows = []
    for p in PERIODS:
        words = list(primitive_words(p))
        for wi, a in enumerate(words):
            for T in ONSETS:
                Lmax = T + BOUND + 8
                death = {}
                t1 = time.time()
                cs, fz, cap = counts(T, a, Lmax, cap=CAP, death=death)
                dt = round(time.time() - t1, 2)
                rows.append({'T': T, 'p': p, 'a': a, 'Lmax': Lmax, 'first_zero_L': fz, 'excess': (fz - T) if fz else None,
                             'capped': cap, 'peak_live': max(x for x in cs if x is not None), 'seconds': dt,
                             'count_at_Lmax': cs[-1], 'death': death})
                if cap or dt > RUN_BUDGET_S:
                    break
            if wi % 20 == 0:
                print(f'p={p} word {wi + 1}/{len(words)} ({time.time() - t0:.0f}s)', flush=True)
    done = [r for r in rows if not r['capped']]
    viol = [r for r in done if r['first_zero_L'] is None or r['excess'] > BOUND]
    ex = [r['excess'] for r in done if r['excess'] is not None]
    col_off = [r['death']['fail_col_offset_max'] for r in done if r['death']]
    time_off = [r['death']['fail_time_offset_max'] for r in done if r['death']]
    edge_share = [r['death']['windows_failing_edge_cell'] / r['death']['live_before'] for r in done if r['death']]
    byT = {}
    for r in done:
        if r['excess'] is not None:
            byT.setdefault(str(r['T']), []).append(r['excess'])
    out = {
        'PERIODS': PERIODS, 'ONSETS': ONSETS, 'CAP_live': CAP, 'BOUND': BOUND, 'seconds': round(time.time() - t0, 1),
        'words': {str(p): len(list(primitive_words(p))) for p in PERIODS},
        'cases_completed': len(done), 'H28_holds': not viol,
        'violations': [{k: r[k] for k in ('T', 'p', 'a', 'first_zero_L', 'excess', 'count_at_Lmax')} for r in viol],
        'excess_max': max(ex) if ex else None, 'excess_mean': round(sum(ex) / len(ex), 2) if ex else None,
        'excess_max_by_T': {T: max(v) for T, v in byT.items()}, 'excess_mean_by_T': {T: round(sum(v) / len(v), 1) for T, v in byT.items()},
        'largest_T_completed': max(r['T'] for r in done),
        'death_cells': {'col_offset_past_cone_max': max(col_off) if col_off else None, 'time_offset_past_T_max': max(time_off) if time_off else None,
                        'share_of_cases_with_some_window_failing_edge_cell': round(sum(1 for s in edge_share if s > 0) / len(edge_share), 3) if edge_share else None,
                        'mean_share_of_windows_failing_edge_cell': round(sum(edge_share) / len(edge_share), 3) if edge_share else None},
        'rows': rows,
    }
    (HERE / 'bounded_excess.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TV', 'H28', 'F14', 'B5', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-15-bounded-excess/PROOFS.md'
    lt.add_assertion(book, 'TV', 'For t>=T and j<=t-T, x(-1,t) = x(-j-1,t-j) XOR XOR_{i=1..j}(x(-i,t-i) OR x(-i+1,t-i)); in the relaxation the leading term is a free row bit for t<=2T-2, the edge for t=2T-1 and 0 for t>=2T, so every one-time constraint from time 2T on is a parity of ORs along a light ray with no free-row term.', 'PROVED_HUMAN_READABLE', ps + ' §TV', deps=['D0', 'T0', 'TU'])
    lt.add_assertion(book, 'H28', f'For every primitive nonconstant word of period 7 or 8 and every onset T>=8 that exact enumeration completes (cap 2^23), the left-cone exclusion excess L(T,a)-T is at most {BOUND}: the relaxation dies by time 2T+{BOUND}, independently of T.', 'OPEN', deps=['T0', 'TU', 'TV'])
    lt.add_assertion(book, 'F14', f'Exclusion lengths, death times and violated cone cells of the left-cone relaxation for all {sum(r["words"].values())} primitive words of periods 7 and 8 at onsets {list(ONSETS)} up to the enumeration limit (largest completed {r["largest_T_completed"]}); death-cell histograms recorded.', 'FINITE_VERIFIED', '', deps=['T0', 'TU', 'TV'])
    dc = r['death_cells']
    if r['H28_holds']:
        lt.set_status(book, 'H28', 'FINITE_VERIFIED', f'{r["cases_completed"]} cases completed, max excess {r["excess_max"]} (mean {r["excess_mean"]}); by onset {json.dumps(r["excess_max_by_T"])} (E34). Finite only.')
    else:
        v = r['violations'][0]
        lt.set_status(book, 'H28', 'FALSIFIED', f'T={v["T"]} a={v["a"]}: L={v["first_zero_L"]}, excess {v["excess"]} (E34); {len(r["violations"])} violations.', replacement='B5')
    lt.add_evidence(book, 'E34', 'research/loop-15-bounded-excess/bounded_excess.json', supports=['H28', 'F14', 'B5'])
    lt.add_evidence(book, 'E35', ps, supports=['TV', 'B5'])
    return (f'TV proved: from time 2T every one-time constraint is a ray parity with no free-row term. H28 {"held" if r["H28_holds"] else "FALSIFIED"}: '
            f'{r["cases_completed"]} cases (periods 7-8, onsets to {r["largest_T_completed"]}), max excess L-T = {r["excess_max"]}, mean {r["excess_mean"]}; '
            f'the dying windows violate cone cells at most {dc["col_offset_past_cone_max"]} columns past the first cone column and {dc["time_offset_past_T_max"]} steps after T; '
            f'edge-cell failures in {dc["share_of_cases_with_some_window_failing_edge_cell"]} of cases. B5 remains the open child of B1.')


consumed = lt.run_loop('effortless-15', f'H28: the left-cone exclusion excess L(T,a)-T is at most {BOUND} for every primitive nonconstant word of period 7 or 8 at every onset T>=8 the enumeration completes; TV: from time 2T the one-time constraints are ray parities with no free-row term.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H28_holds', 'cases_completed', 'largest_T_completed', 'excess_max', 'excess_mean', 'excess_max_by_T', 'death_cells', 'violations')}, indent=1))
