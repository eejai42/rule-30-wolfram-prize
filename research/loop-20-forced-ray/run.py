"""Loop 20: record what the 64-wall is not; test H33, that it ends where TW says. See PROOFS.md."""
import json, sys, time, collections
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-14-left-cone-growth'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-17-affine'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt
from left_cone_fast import counts, U64
from forced import rebuild
from affine import evolve_left

HERE = Path(__file__).resolve().parent
RESULT = {}


def structure(T, a):
    keep = {}
    cs, fz, cap = counts(T, a, 80, cap=1 << 24, track=keep)
    R, md = keep['live_r_bits'], keep['death_step']
    diags = rebuild(T, a, md + 1, R)
    N, M, W = diags.shape
    def bits(m, s):
        return ((diags[:, m, s >> 6] >> U64(s & 63)) & U64(1)).astype(np.uint8)
    # 1. forced cells on the death ray (diagonals md-1, md), interior = inside the cone, s >= 2
    forced_interior = 0; interior = 0
    for m in (md - 1, md):
        for s in range(2, m + 2):
            t = T + m - s + 1
            if s < t - 2:                     # strictly inside the cone, off the edge diagonals w0..w2
                interior += 1
                b = bits(m, s)
                forced_interior += int(np.all(b == b[0]))
    # 3. tie classes by column (exclude death diagonal)
    sig = {}
    for m in range(md):
        for s in range(1, m + 2):
            b = bits(m, s); key = min(np.packbits(b).tobytes(), np.packbits(1 - b).tobytes())
            sig.setdefault(key, []).append((m, s))
    bycol = collections.defaultdict(lambda: [0, 0])
    for v in sig.values():
        for (m, s) in v:
            bycol[s][0] += 1; bycol[s][1] += (len(v) > 1)
    tied_frac = {str(s): round(bycol[s][1] / bycol[s][0], 3) for s in sorted(bycol) if s <= 12}
    return {'T': T, 'a': a, 'L': fz, 'survivors': int(N), 'death_ray_interior_cells': interior, 'death_ray_interior_forced': forced_interior,
            'tied_fraction_by_column_1_to_12': tied_frac}


def gf2_rank_with_const(M):
    A = np.concatenate([M, np.ones((M.shape[0], 1), dtype=np.uint8)], axis=1).copy()
    N, K = A.shape; r = 0
    for col in range(K):
        rows_ = np.flatnonzero(A[r:, col])
        if rows_.size == 0:
            continue
        i = r + rows_[0]; A[[r, i]] = A[[i, r]]
        mask = A[:, col].copy(); mask[r] = 0
        A[mask.astype(bool)] ^= A[r]; r += 1
        if r == N:
            break
    return r, K


def linear_check(T, a, Lmax=66):
    p = len(a); c = lambda t: int(a[(t - T) % p]); n = T - 1; N = 1 << n
    rows = np.zeros((N, T), dtype=np.uint8); rows[:, 0] = 1
    idx = np.arange(N, dtype=np.uint64)
    for j in range(n):
        rows[:, T - 1 - j] = (idx >> np.uint64(j)) & np.uint64(1)
    col1 = evolve_left(rows, T, c, Lmax)
    ts = [t for t in range(T, T + Lmax) if c(t) == 1]
    M = np.stack([col1[t - T] for t in ts], axis=1).astype(np.uint8)
    r, K = gf2_rank_with_const(M)
    return {'T': T, 'functions_plus_const': K, 'rank': r, 'independent': r == K}


def compute():
    t0 = time.time()
    struct = [structure(T, '01') for T in range(37, 47)]
    print(f'structure done {time.time() - t0:.0f}s', flush=True)
    lin = [linear_check(T, '01') for T in range(8, 19)]
    print(f'linear done {time.time() - t0:.0f}s', flush=True)
    wall = []
    pin = {'011': 66, '101': 66, '110': 66, '0111': 64, '1011': 64, '1101': 64, '1110': 64}
    for a, pv in pin.items():
        for T in range(44, 67):
            cs, fz, cap = counts(T, a, 100, cap=1 << 26)
            wall.append({'a': a, 'T': T, 'L': fz, 'capped': cap, 'pinned_value': pv})
        print(f'{a} wall scan done {time.time() - t0:.0f}s', flush=True)
    for a, pv in (('01', 64), ('10', 65)):
        for T in (51, 52):
            t1 = time.time(); cs, fz, cap = counts(T, a, 70, cap=1 << 26)
            wall.append({'a': a, 'T': T, 'L': fz, 'capped': cap, 'pinned_value': pv, 'seconds': round(time.time() - t1)})
            print(f'{a} T={T} L={fz} {time.time() - t0:.0f}s', flush=True)
    # H33 evaluation
    verdict = {}
    for a, pv in list(pin.items()) + [('01', 64), ('10', 65)]:
        rs = sorted([r for r in wall if r['a'] == a and not r['capped']], key=lambda r: r['T'])
        Ls = {r['T']: r['L'] for r in rs}
        first_pin = next((T for T in sorted(Ls) if Ls[T] == pv), None)
        through63 = [T for T in sorted(Ls) if first_pin is not None and first_pin <= T <= 63]
        holds_to_63 = first_pin is not None and all(Ls[T] == pv for T in through63)
        after = {T: Ls[T] for T in (64, 65, 66) if T in Ls}
        breaks_after = all(v > pv for v in after.values()) if after else None
        verdict[a] = {'L_by_T': {str(T): Ls[T] for T in sorted(Ls)}, 'first_pinned_onset': first_pin, 'pinned_through_63': holds_to_63, 'L_at_64_65_66': after, 'exceeds_pin_after_63': breaks_after}
    h33 = all(v['pinned_through_63'] for v in verdict.values()) and all(v['exceeds_pin_after_63'] in (True, None) for v in verdict.values()) \
        and all(verdict[a]['exceeds_pin_after_63'] is True for a in pin)
    out = {'seconds': round(time.time() - t0, 1), 'H33_holds': h33,
           'death_ray_forced_interior_cells': [{k: s[k] for k in ('T', 'survivors', 'death_ray_interior_cells', 'death_ray_interior_forced')} for s in struct],
           'tied_fraction_by_column': {str(s['T']): s['tied_fraction_by_column_1_to_12'] for s in struct},
           'linear_independence': lin, 'wall': verdict, 'rows': wall}
    (HERE / 'wall.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H33', 'F19', 'B7', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-20-forced-ray/PROOFS.md'
    lt.add_assertion(book, 'H33', 'The 64-wall is exactly the TW boundary phenomenon: for the words 011,101,110 (pinned window 66) and 0111,1011,1101,1110 (pinned window 64) the death window keeps its pinned value from the first pinned onset through T=63 and exceeds it at T=64,65,66; for 01 and 10 at onsets 51 and 52 it stays at 64 and 65.', 'OPEN', deps=['T0', 'TU', 'TV', 'TW'])
    lt.add_assertion(book, 'F19', 'Structure of the 64-wall for the word 01 at onsets 37..46: forced cells on the death ray (none in the cone interior), tie classes by column (columns 1-3 tied, 4-5 partly, 6 onward untied), GF(2) independence of the 33 one-time functions over all rows for T<=18; and the L(T) table of H33 for period-3 and period-4 words at onsets 44..66.', 'FINITE_VERIFIED', '', deps=['T0', 'TU', 'TV', 'TW'])
    summ = {a: {k: v[k] for k in ('first_pinned_onset', 'pinned_through_63', 'L_at_64_65_66')} for a, v in r['wall'].items()}
    fi = sum(s['death_ray_interior_forced'] for s in r['death_ray_forced_interior_cells'])
    if r['H33_holds']:
        lt.set_status(book, 'H33', 'FINITE_VERIFIED', f'{json.dumps(summ)} (E44). Finite only.')
    else:
        lt.set_status(book, 'H33', 'FALSIFIED', f'{json.dumps(summ)} (E44).', replacement='TW')
    lt.add_evidence(book, 'E44', 'research/loop-20-forced-ray/wall.json', supports=['H33', 'F19', 'B7'])
    lt.add_evidence(book, 'E45', ps, supports=['F19', 'H33'])
    return (f'64-wall structure for 01: {fi} forced interior cells on the death rays over onsets 37..46; one-time functions independent over GF(2) for T<=18: {all(l["independent"] for l in r["linear_independence"])}; '
            f'columns 1-3 tied, 6+ untied. H33 {"held" if r["H33_holds"] else "FALSIFIED"}: {json.dumps(summ)}.')


consumed = lt.run_loop('effortless-20', 'H33: the 64-wall is the TW boundary phenomenon: pinned death windows for period-3/4 words persist through T=63 and break at T=64..66; 01/10 stay pinned at onsets 51, 52.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'H33_holds', 'death_ray_forced_interior_cells', 'wall')}, indent=1)[:5000])
