"""Loop 25 (H40): the closure of the width-25 window language and the period-2 kill. See PROOFS.md."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'loop-22-left-consistent'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt
from seeded import grow
from closure import closure, survivors, U

HERE = Path(__file__).resolve().parent
E, T0 = 24, 19
RESULT = {}


def bits(v):
    return format(int(v), f'0{E + 1}b')[::-1]          # c(t) first, then x(-1..-24, t)


def compute():
    t0 = time.time()
    mask = U((1 << (E + 1)) - 1)
    seen = {}
    for t, B in grow(45, 3, cap=1 << 27):
        if t >= T0:
            seen[t] = np.unique(B[:, 0] & mask)
    base = seen[T0]
    A, rounds = closure(E, base)
    Aset = set(A.tolist()) if len(A) < 5_000_000 else None
    contains_seen = all(np.isin(seen[t], A).all() for t in seen)
    surv = {a: survivors(A, E, a) for a in ('01', '10')}
    seen_surv = {a: int(sum(survivors(seen[t], E, a).sum() for t in seen)) for a in ('01', '10')}
    out = {'E': E, 'T0': T0, 'seconds': round(time.time() - t0, 1), 'base_size': int(len(base)),
           'closure_size': int(len(A)), 'closure_rounds': rounds, 'all_windows': 1 << (E + 1),
           'closure_fraction_of_all': round(len(A) / (1 << (E + 1)), 6),
           'closure_contains_seen_t19_45': bool(contains_seen),
           'survivors_in_closure': {a: int(surv[a].sum()) for a in surv},
           'survivor_examples_c_then_x-1..x-24': {a: [bits(v) for v in A[surv[a]][:10]] for a in surv},
           'survivors_among_seen_windows_t19_45': seen_surv,
           'H40_holds': all(int(surv[a].sum()) == 0 for a in surv)}
    (HERE / 'closure.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


CONSUME = ['H40', 'TX', 'B9', 'B7', 'P1']


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-25-closure/PROOFS.md'
    lt.add_assertion(book, 'H40', f'Let A be the least set of width-25 near-center windows (c(t), x(-1..-24,t)) that contains every window shown by a left-consistent prefix at t={T0} and is closed under one step of the left half (outer bit free, next center bit forced by TX after a 1). For each period-2 tail, every window in A fails one of the next 24 one-time checks. H40 implies B9 for period 2 at every onset.', 'OPEN', ps + ' §H40', deps=['TX', 'F22'])
    if r['H40_holds']:
        lt.set_status(book, 'H40', 'FINITE_VERIFIED', f'Closure of {r["base_size"]} base windows has {r["closure_size"]} windows ({r["closure_fraction_of_all"]} of all) after {r["closure_rounds"]} rounds; none survives either period-2 tail (E53). Exhaustive over a finite set; reported, not model-decided.')
    else:
        lt.set_status(book, 'H40', 'FALSIFIED', f'Closure of {r["base_size"]} base windows has {r["closure_size"]} windows ({r["closure_fraction_of_all"]} of all) after {r["closure_rounds"]} rounds; survivors: {json.dumps(r["survivors_in_closure"])} (E53). The real windows seen at t=19..45 still all die ({json.dumps(r["survivors_among_seen_windows_t19_45"])}).', replacement='H38')
    lt.add_evidence(book, 'E53', 'research/loop-25-closure/closure.json', supports=['H40'])
    lt.add_evidence(book, 'E54', ps, supports=['H40'])
    lt.add_evidence(book, 'E55', 'research/loop-25-closure/closure.py', supports=['H40'])
    return (f'H40 {"held" if r["H40_holds"] else "FALSIFIED"}: the closure of the {r["base_size"]} width-25 windows seen at t={T0} under the step with a free outer bit has {r["closure_size"]} windows '
            f'({r["closure_fraction_of_all"]} of all 2^25); survivors of the 23-step kill: {json.dumps(r["survivors_in_closure"])}. '
            + ('This proves B9 for period 2 by a finite computation; the next loop records it as a theorem after an independent re-check.' if r['H40_holds'] else 'The simple invariant with a free outer bit is too lossy at width 25; a local invariant needs the far-left information.'))


consumed = lt.run_loop('effortless-25', 'H40: the closure of the width-25 near-center windows of left-consistent sequences (base t=19, free outer bit) is killed within 24 checks by both period-2 tails; H40 implies B9 for period 2.', edit, CONSUME, HERE)
print(json.dumps({k: consumed[k] for k in CONSUME + ['_dashboard']}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('seconds', 'base_size', 'closure_size', 'closure_rounds', 'closure_fraction_of_all', 'closure_contains_seen_t19_45', 'survivors_in_closure', 'survivors_among_seen_windows_t19_45', 'H40_holds')}, indent=1))
