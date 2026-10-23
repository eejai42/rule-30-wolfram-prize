"""Loop 8: agreement runs of the center column (Problem 1 in a finite currency).

Hypothesis H21 (stated before computing): on the first 2^20 center bits, for every shift
1 <= p <= 4096, every run of consecutive t with c(t) = c(t+p) has length <= 44 (= 2 log2 N + 4).
Input: research/loop-05-center/center_2_20.txt (E17), hash re-checked against the rulebook.
"""
import hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
PMAX, BOUND = 4096, 44
RESULT = {}


def longest_true_run(a: np.ndarray):
    """Length and start of the longest run of True in a boolean array."""
    padded = np.concatenate(([False], a, [False]))
    d = np.diff(padded.astype(np.int8))
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    if starts.size == 0:
        return 0, -1
    lens = ends - starts
    i = int(lens.argmax())
    return int(lens[i]), int(starts[i])


def compute():
    book = lt.load()
    ev = lt.row(book, 'Evidence', 'E17')
    path = lt.ROOT / ev['Path']
    assert lt.sha256_file(path) == ev['Sha256'], 'center file changed since loop 5'
    txt = path.read_text().strip()
    N = len(txt)
    c = np.frombuffer(txt.encode(), dtype=np.uint8) - 48
    t0 = time.time()
    per_p = []
    for p in range(1, PMAX + 1):
        L, s = longest_true_run(c[:N - p] == c[p:])
        per_p.append((p, L, s))
    secs = round(time.time() - t0, 1)
    worst = max(per_p, key=lambda x: x[1])
    fails = [x for x in per_p if x[1] > BOUND]
    lens = [x[1] for x in per_p]
    hist = {str(L): lens.count(L) for L in sorted(set(lens))}
    top = sorted(per_p, key=lambda x: -x[1])[:15]
    out = {
        'N': N, 'log2N': math.log2(N), 'PMAX': PMAX, 'bound': BOUND, 'seconds': secs,
        'H21_counterexamples': [{'p': p, 'run': L, 'start': s} for p, L, s in fails],
        'worst': {'p': worst[0], 'run': worst[1], 'start': worst[2]},
        'p1_longest_run': per_p[0][1], 'median_longest_run': sorted(lens)[len(lens) // 2],
        'histogram_longest_run_per_p': hist,
        'top15': [{'p': p, 'run': L, 'start': s} for p, L, s in top],
        'random_baseline_note': 'For an i.i.d. fair sequence the longest run per shift is about log2(N)=20, and about 32 for the worst of 4096 shifts.',
    }
    (HERE / 'agreement_runs.json').write_text(json.dumps(out, indent=1) + '\n')
    return out


def edit(book):
    r = compute()
    RESULT.update(r)
    ps = 'research/loop-08-agreement-runs/PROOFS.md'
    w = r['worst']
    lt.add_assertion(book, 'TQ', 'The center is eventually p-periodic iff some agreement run c(t)=c(t+p) is infinite; so a finite bound on agreement runs for every p implies P1.', 'PROVED_HUMAN_READABLE', ps + ' §TQ', deps=['D0'])
    lt.add_assertion(book, 'H21', f'On the first 2^20 center bits, every agreement run c(t)=c(t+p) for 1<=p<={PMAX} has length at most {BOUND}.', 'OPEN', deps=['TQ'])
    if r['H21_counterexamples']:
        c0 = r['H21_counterexamples'][0]
        lt.set_status(book, 'H21', 'FALSIFIED', f'p={c0["p"]} has an agreement run of length {c0["run"]} from t={c0["start"]} (E23).', replacement='TQ')
    else:
        lt.set_status(book, 'H21', 'FINITE_VERIFIED', f'Longest run over all {PMAX} shifts is {w["run"]} (p={w["p"]}, t={w["start"]}); median of the per-shift maxima {r["median_longest_run"]}. Finite only.')
    lt.add_evidence(book, 'E23', 'research/loop-08-agreement-runs/agreement_runs.json', supports=['H21', 'TQ'])
    lt.add_evidence(book, 'E24', ps, supports=['TQ'])
    lt.link_evidence(book, 'E17', 'H21')
    return (f'TQ proved: P1 is the finiteness of agreement runs for every shift. H21 '
            f'{"FALSIFIED" if r["H21_counterexamples"] else "held"}: the longest agreement run over shifts 1..{PMAX} on 2^20 bits is {w["run"]} '
            f'(p={w["p"]}), against a random baseline near 32. Finite only; says nothing about later times.')


consumed = lt.run_loop('effortless-8', f'H21: on 2^20 center bits every agreement run for shifts p<={PMAX} has length <= {BOUND}.', edit, ['TQ', 'H21', 'P1', 'B1'], HERE)
print(json.dumps({k: consumed[k] for k in ('TQ', 'H21', '_dashboard')}, indent=1))
print(json.dumps({k: RESULT[k] for k in ('H21_counterexamples', 'worst', 'p1_longest_run', 'median_longest_run', 'histogram_longest_run_per_p', 'seconds')}, indent=1))
