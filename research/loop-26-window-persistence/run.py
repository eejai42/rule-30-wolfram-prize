"""Loop 26 (H41, TY): the finite period-2 kill past t = 45, over merged states. See PROOFS.md."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-22-left-consistent'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-25-closure'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt
from seeded import grow, step_left, x_m1, U64
from closure import survivors
from states import grow_states
from flood import check_all

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
E, TLO, THI, LMAX = 24, 19, 160, 120
WD = (THI + LMAX + 3 + 63) // 64
RESULT = {}


def survival(S, a):
    """Per tail a from t+1: the largest number of checks any state passes (its first failing check index),
    and how many states pass all LMAX checks."""
    cur, longest = S.copy(), 0
    for j in range(LMAX):
        nxt = U64(int(a[j % 2]))
        viol = ((cur[:, 0] & U64(1)) == U64(1)) & ((x_m1(cur) ^ U64(1)) != nxt)
        if viol.any():
            longest = j
        cur = cur[~viol]
        if not len(cur):
            return longest, 0
        cur = step_left(cur, 0, cur.shape[1])
        cur[:, 0] |= nxt
    return LMAX, int(len(cur))


def compute():
    t0 = time.time()
    flood = check_all(16)
    ref = {t: np.unique(B, axis=0) for t, B in grow(36, 1)}
    merge_ok = all(np.array_equal(S, ref[t]) for t, S in grow_states(36))
    mask = U64((1 << (E + 1)) - 1)
    states, windows, win_surv, longest, outlast = {}, {}, {'01': {}, '10': {}}, {'01': {}, '10': {}}, {'01': {}, '10': {}}
    for t, S in grow_states(THI, WD):
        states[str(t)] = int(len(S))
        if t >= TLO:
            win = np.unique(S[:, 0] & mask)
            windows[str(t)] = int(len(win))
            for a in ('01', '10'):
                win_surv[a][str(t)] = int(survivors(win, E, a).sum())
        if t >= 3:
            for a in ('01', '10'):
                longest[a][str(t)], outlast[a][str(t)] = survival(S, a)
        if t % 10 == 0:
            print(f't={t} states={len(S)} longest={ {a: longest[a].get(str(t)) for a in longest} } ({time.time() - t0:.0f}s)', flush=True)
    # cross-checks: loop 22 (excess t* - T, T = t + 1, so excess = longest - 1) and loop 23 (|W_24|)
    l22 = json.loads((RESEARCH / 'loop-22-left-consistent' / 'seeded.json').read_text())['period2_excess_max_by_T']
    l23 = json.loads((RESEARCH / 'loop-23-window-language' / 'window_language.json').read_text())['language_size'][str(E)]
    agree22 = all(longest[a][str(int(T) - 1)] - 1 == ex for a in l22 for T, ex in l22[a].items())
    agree23 = all(windows[t] == n for t, n in l23.items())
    rng = [str(t) for t in range(TLO, THI + 1)]
    h41 = all(win_surv[a][t] == 0 for a in win_surv for t in rng)
    exact = all((win_surv[a][t] == 0) == (longest[a][t] < E) for a in win_surv for t in rng)
    peak = {a: max(longest[a][t] for t in rng) for a in longest}
    peak_at = {a: [int(t) for t in rng if longest[a][t] == peak[a]] for a in longest}
    first_survivor = {a: next((int(t) for t in rng if win_surv[a][t]), None) for a in win_surv}
    out = {'E': E, 'TLO': TLO, 'THI': THI, 'LMAX': LMAX, 'seconds': round(time.time() - t0, 1),
           'TY_flood_check': flood, 'TY_strongly_connected_E1_16': all(r['strong_components'] == 1 for r in flood),
           'merge_matches_loop22_tree_t_le_36': bool(merge_ok), 'agrees_with_loop22_excess': bool(agree22),
           'agrees_with_loop23_language': bool(agree23), 'window_test_equals_state_test': bool(exact),
           'H41_holds': bool(h41), 'first_t_with_survivor': first_survivor, 'longest_survival_peak_19_160': peak,
           'longest_survival_peak_at': peak_at, 'states': states, 'windows_width25': windows,
           'window_survivors': win_surv, 'longest_survival': longest, 'states_passing_all_LMAX': outlast}
    (HERE / 'persistence.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['TY', 'H41', 'F23', 'H38', 'H40', 'B9', 'B7', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    assert r['TY_strongly_connected_E1_16'] and r['merge_matches_loop22_tree_t_le_36'] and r['agrees_with_loop22_excess'] \
        and r['agrees_with_loop23_language'] and r['window_test_equals_state_test'], 'a cross-check failed: not a research outcome'
    ps = 'research/loop-26-window-persistence/PROOFS.md'
    lt.add_assertion(book, 'TY', 'For every E >= 1, the width-(E+1) window step with the outer cell free (center NOT x(-1) after a 1, free after a 0) reaches every window from every window in at most 2E+1 steps; so the closure of any nonempty window set is all 2^(E+1) windows. A free outer cell never gives an invariant, at any width.',
                     'PROVED_HUMAN_READABLE', ps + ' §TY', deps=['TX'])
    lt.add_assertion(book, 'H41', f'For every time {TLO} <= t <= {THI} and each tail 01, 10, every width-25 near-center window shown at t by a left-consistent prefix fails one of the next 24 one-time checks (H38 at E=24 extended from t <= 45 to t <= {THI}).',
                     'OPEN', ps + ' §H41', deps=['TX', 'H38'])
    lt.add_assertion(book, 'F23', f'Merged left-consistent states for t = 0..{THI}: the number of distinct rows, the distinct width-25 windows (t >= {TLO}), the windows among the loop 25 survivors, and the longest survival of a state under each period-2 tail (up to {LMAX} checks).',
                     'FINITE_VERIFIED', '', deps=['TX'])
    pk, ft = r['longest_survival_peak_19_160'], r['first_t_with_survivor']
    if r['H41_holds']:
        lt.set_status(book, 'H41', 'FINITE_VERIFIED', f'No reachable state at t = {TLO}..{THI} survives 24 checks; longest survival {json.dumps(pk)} at t = {json.dumps(r["longest_survival_peak_at"])} (E56). Finite only.')
    else:
        lt.set_status(book, 'H41', 'FALSIFIED', f'Reachable states survive 24 checks of a period-2 tail; first at t = {json.dumps(ft)}; longest survival over t = {TLO}..{THI}: {json.dumps(pk)} checks (E56).', replacement='TY')
    lt.add_evidence(book, 'E56', 'research/loop-26-window-persistence/persistence.json', supports=['H41', 'F23', 'TY'])
    lt.add_evidence(book, 'E57', ps, supports=['TY', 'H41'])
    lt.add_evidence(book, 'E58', 'research/loop-26-window-persistence/run.py', supports=['H41', 'F23'])
    lt.add_evidence(book, 'E59', 'research/loop-26-window-persistence/flood.py', supports=['TY'])
    return (f'TY proved: a free outer cell floods the window closure at every width (every window reaches every window within 2E+1 steps; exhaustive for E = 1..16). '
            f'H41 {"held" if r["H41_holds"] else "FALSIFIED"}: over merged states ({r["states"][str(THI)]} at t = {THI}), '
            + (f'no state at t = {TLO}..{THI} survives 24 checks of a period-2 tail; longest survival {json.dumps(pk)}.' if r['H41_holds'] else
               f'states survive 24 checks of a period-2 tail from t = {json.dumps(ft)}; longest survival over t = {TLO}..{THI}: {json.dumps(pk)} checks. No fixed-width finite kill at width 25.'))


if __name__ == '__main__':
    consumed = lt.run_loop('effortless-26', f'H41: every width-25 near-center window shown by a left-consistent prefix at any time {TLO} <= t <= {THI} dies within 24 checks under both period-2 tails (H38 extended); TY: a free outer cell floods the window closure at every width.', edit, CONSUME, HERE)
    print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
    print(json.dumps({k: RESULT[k] for k in ('seconds', 'TY_strongly_connected_E1_16', 'merge_matches_loop22_tree_t_le_36', 'agrees_with_loop22_excess', 'agrees_with_loop23_language', 'window_test_equals_state_test', 'H41_holds', 'first_t_with_survivor', 'longest_survival_peak_19_160', 'longest_survival_peak_at')}, indent=1))
