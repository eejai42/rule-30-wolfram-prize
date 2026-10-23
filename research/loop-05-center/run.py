"""Loop 5: back to the center column, 2^20 bits.

Hypotheses stated before compute_center.py ran (its docstring):
  H9:  |2 S(N) - N| <= 3 sqrt(N) for all 16 <= N <= 2^20  (finite; Problem 2 flavour).
  H13: every maximal constant run [T,V] with T >= 1, V < 2^20 - 1 has length <= 2 log2(T+1) + 4
       (finite; TD only proves V <= 4T+5).
Added here:
  F6:  for every period 1 <= p <= 2^17 there is a mismatch c(t) != c(t+p) at some t >= T,
       for every onset T <= T*, with T* computed below (extends F3 from 10^4 / 9*10^4).
Independent reproduction: the first 100,001 bits must hash to E2's recorded sha256.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
E2 = json.loads((lt.ROOT / 'bootstrap/cmcc_rule30_effortless_migration/research_v05/data/center_results.json').read_text())
txt = (HERE / 'center_2_20.txt').read_text().strip()
res = json.loads((HERE / 'center_2_20.json').read_text())
N = len(txt)
assert N == res['N'] == 1 << 20
assert hashlib.sha256(txt.encode()).hexdigest() == res['sha256_all_no_newline']
assert hashlib.sha256(txt[:E2['n']].encode()).hexdigest() == E2['sha256_no_newline'], 'center disagrees with E2'
c = np.frombuffer(txt.encode(), dtype=np.uint8) - 48

PMAX = 1 << 17
last = np.empty(PMAX + 1, dtype=np.int64)
for p in range(1, PMAX + 1):
    a, b = c[:N - p], c[p:]
    hi = N - p
    found = -1
    while hi > 0:
        lo = max(0, hi - 4096)
        d = np.flatnonzero(a[lo:hi] != b[lo:hi])
        if d.size:
            found = lo + int(d[-1])
            break
        hi = lo
    assert found >= 0, p
    last[p] = found
Tstar = int(last[1:].min())
p_at = int(last[1:].argmin()) + 1
f6 = {'PMAX': PMAX, 'uniform_onsets_excluded_through': Tstar, 'binding_period': p_at, 'note': 'For each p, an onset T is excluded when some t >= T has c(t) != c(t+p) with t+p < 2^20.'}
assert Tstar >= 90000

out = {'center_sha256_first_100001_matches_E2': True, 'N': N, 'ones': res['ones'], 'H9': res['H9'], 'H13': {k: v for k, v in res['H13'].items() if k != 'longest_runs'} | {'longest_runs_[len,T,V,bit]': res['H13']['longest_runs'][:5]}, 'F6': f6, 'TD_bound_check': res['TD_bound_check']}
(HERE / 'center_checks.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
assert res['H9']['failure_count'] == 0 and res['H13']['failure_count'] == 0 and res['TD_bound_check']


def edit(book):
    lt.add_assertion(book, 'H9', 'Finite discrepancy: |2 S(N) - N| <= 3 sqrt(N) for all 16 <= N <= 2^20, S(N) the number of ones among c(0..N-1).', 'OPEN')
    lt.add_assertion(book, 'H13', 'Finite run bound: every maximal constant center run [T,V] with 1 <= T and V < 2^20 - 1 has length <= 2 log2(T+1) + 4.', 'OPEN')
    lt.add_assertion(book, 'F6', f'For every period 1 <= p <= 2^17 and every onset T <= {Tstar}, some t >= T has c(t) != c(t+p) (2^20 center bits; independent reproduction of E2).', 'FINITE_VERIFIED', '', deps=['D0'])
    lt.set_status(book, 'H9', 'FINITE_VERIFIED', f'Max |2S-N|/sqrt(N) = {res["H9"]["max_ratio"]} at N={res["H9"]["argmax_N"]}; no N in range exceeds 3. Finite statement only; says nothing about the limit (B2, P2).')
    lt.set_status(book, 'H13', 'FINITE_VERIFIED', f'{res["H13"]["run_count"]} runs checked; longest is {res["H13"]["longest_runs"][0][0]} at T={res["H13"]["longest_runs"][0][1]}. Finite statement only; TD remains the proved bound.')
    lt.add_evidence(book, 'E15', 'research/loop-05-center/center_2_20.json', supports=['H9', 'H13'])
    lt.add_evidence(book, 'E16', 'research/loop-05-center/center_checks.json', supports=['F6', 'H9', 'H13', 'F3'])
    lt.add_evidence(book, 'E17', 'research/loop-05-center/center_2_20.txt', supports=['F6'])
    return (f'Center column to 2^20: E2 hash reproduced; F6 excludes all periods <= 2^17 for onsets <= {Tstar} (F3 was 10^4 / 9*10^4). '
            f'H9 (max ratio {res["H9"]["max_ratio"]}) and H13 (longest run {res["H13"]["longest_runs"][0][0]}) finite-verified. P1, P2 unchanged.')


consumed = lt.run_loop('effortless-5', 'H9 and H13 hold on the first 2^20 center bits; the onset/period exclusion F3 extends to p <= 2^17.', edit, ['H9', 'H13', 'F6', 'F3', 'P1', 'P2', 'P3', 'B1', 'B2'], HERE)
print(json.dumps({k: consumed[k] for k in ('H9', 'H13', 'F6', 'P1', 'P2', '_dashboard')}, indent=1))
