"""Loop 23: near-center window language of left-consistent sequences; finite part K(E). See PROOFS.md."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-22-left-consistent'))
import loop_tools as lt
from seeded import grow

HERE = Path(__file__).resolve().parent
TLO, THI, Wd = 19, 45, 3
ES = list(range(4, 31, 2))
U = np.uint64
RESULT = {}


def window_survivors(win: np.ndarray, E: int, a: str) -> int:
    """Number of windows (uint64, bits 0..E) that survive E-1 one-time checks under tail a from t+1."""
    w = win.copy()
    alive = np.ones(len(w), dtype=bool)
    p = len(a)
    for j in range(E):                      # checks at times t+j, j=0..E-1
        if E - j < 1:
            break
        c = w & U(1)
        nxt = U(int(a[j % p]))
        xm1 = (w >> U(1)) & U(1)
        viol = (c == U(1)) & ((xm1 ^ U(1)) != nxt)
        alive &= ~viol
        new = (w >> U(1)) ^ (w | (w << U(1)))
        new &= ~U(1)
        new |= nxt
        valid = E - j - 1                     # top valid bit index after this step
        new &= (U(1) << U(valid + 1)) - U(1) if valid < 63 else ~U(0)
        w = new
        if j == E - 1:
            break
    return int(alive.sum())


def compute():
    t0 = time.time()
    counts = {str(E): {} for E in ES}
    stable = {str(E): {} for E in ES if E <= 22}
    prev_maps = {}
    K = {str(E): {'01': {}, '10': {}} for E in ES}
    missing = None
    for t, B in grow(THI, Wd, cap=1 << 27):
        if t < TLO:
            continue
        low = B[:, 0]
        for E in ES:
            win = np.unique(low & U((1 << (E + 1)) - 1))
            counts[str(E)][str(t)] = int(len(win))
            if E <= 22:
                m = np.zeros(1 << (E + 1), dtype=bool); m[win.astype(np.int64)] = True
                if E in prev_maps:
                    stable[str(E)][str(t)] = bool(np.array_equal(m, prev_maps[E]))
                prev_maps[E] = m
            for a in ('01', '10'):
                K[str(E)][a][str(t)] = window_survivors(win, E, a)
        print(f't={t} prefixes={B.shape[0]} |W_12|={counts["12"][str(t)]} |W_20|={counts["20"][str(t)]} ({time.time() - t0:.0f}s)', flush=True)
    # smallest non-full width at t = THI, and a few missing windows
    for E in ES:
        if counts[str(E)][str(THI)] < (1 << (E + 1)):
            if E <= 22:
                miss = np.flatnonzero(~prev_maps[E])[:20]
                missing = {'E': E, 'count_missing': int((1 << (E + 1)) - counts[str(E)][str(THI)]),
                           'examples_c_then_x-1..x-E': [format(int(v), f'0{E + 1}b')[::-1] for v in miss]}
            break
    frac_missing = {str(E): round(1 - counts[str(E)][str(THI)] / (1 << (E + 1)), 4) for E in ES}
    h37 = any(E >= 12 and frac_missing[str(E)] >= 0.5 for E in ES)
    k_holds = {str(E): all(K[str(E)][a][str(t)] == 0 for a in ('01', '10') for t in range(TLO, THI + 1)) for E in ES}
    h38 = any(k_holds.values())
    out = {'TLO': TLO, 'THI': THI, 'ES': ES, 'seconds': round(time.time() - t0, 1), 'H37_holds': h37, 'H38_holds': h38,
           'fraction_missing_at_THI': frac_missing, 'smallest_nonfull': missing, 'K_holds_by_E': k_holds,
           'smallest_E_with_K': min((int(E) for E, v in k_holds.items() if v), default=None),
           'language_size': counts, 'language_stable_vs_previous_t': stable, 'K_survivors': K}
    (HERE / 'window_language.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H37', 'H38', 'F22', 'B9', 'B1', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-23-window-language/PROOFS.md'
    lt.add_assertion(book, 'H37', f'For some E>=12, the near-center windows (c(t), x(-1..-E,t)) shown by left-consistent sequences at t={THI} miss at least half of the 2^(E+1) possible windows.', 'OPEN', deps=['TX'])
    lt.add_assertion(book, 'H38', f'There is an E<=30 such that every width-(E+1) near-center window shown by a left-consistent sequence at any time {TLO}<=t<={THI} dies within E-1 steps under the tail 01 and under the tail 10 (the finite part K(E) of B9 for period 2).', 'OPEN', deps=['TX'])
    lt.add_assertion(book, 'F22', f'Near-center window language of left-consistent sequences for E=4..30 (even) and t={TLO}..{THI}: language sizes, stability in t (E<=22), the smallest missing windows, and the windows surviving E-1 steps under each period-2 tail.', 'FINITE_VERIFIED', '', deps=['TX'])
    fm = r['fraction_missing_at_THI']
    if r['H37_holds']:
        lt.set_status(book, 'H37', 'FINITE_VERIFIED', f'Fraction of windows missing at t={THI} by E: {json.dumps(fm)} (E51). Finite only.')
    else:
        lt.set_status(book, 'H37', 'FALSIFIED', f'Fraction of windows missing at t={THI} by E: {json.dumps(fm)} (E51).', replacement='TX')
    if r['H38_holds']:
        lt.set_status(book, 'H38', 'FINITE_VERIFIED', f'K(E) holds for E in {[E for E, v in r["K_holds_by_E"].items() if v]}; smallest {r["smallest_E_with_K"]} (E51). Finite only.')
    else:
        lt.set_status(book, 'H38', 'FALSIFIED', f'No E<=30 with K(E); survivors at E=30, t={THI}: {r["K_survivors"]["30"]["01"][str(THI)]} (01), {r["K_survivors"]["30"]["10"][str(THI)]} (10) (E51).', replacement='TX')
    lt.add_evidence(book, 'E51', 'research/loop-23-window-language/window_language.json', supports=['H37', 'H38', 'F22', 'B9'])
    lt.add_evidence(book, 'E52', ps, supports=['H37', 'H38'])
    return (f'Near-center language of left-consistent sequences: H37 {"held" if r["H37_holds"] else "FALSIFIED"} (fraction missing at t={THI}: {json.dumps(fm)}); '
            f'H38 {"held" if r["H38_holds"] else "FALSIFIED"} (smallest E with the finite kill K(E): {r["smallest_E_with_K"]}).')


consumed = lt.run_loop('effortless-23', f'H37: the near-center window language of left-consistent sequences misses at least half of all windows at some width E>=12; H38: some E<=30 has every reachable window killed within E-1 steps by both period-2 tails (t={TLO}..{THI}).', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H37_holds', 'H38_holds', 'fraction_missing_at_THI', 'smallest_nonfull', 'K_holds_by_E', 'smallest_E_with_K')}, indent=1))
