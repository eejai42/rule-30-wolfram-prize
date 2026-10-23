"""Loop 5 experiment: the center column c(t) = x(0,t) for t < 2^20.

Hypotheses stated before running (see run.py):
  H9  (Problem 2 flavour): D(N) = |2*S(N) - N| <= 3*sqrt(N) for all 16 <= N <= 2^20,
      where S(N) = number of ones among c(0..N-1).  A finite statement only.
  H13 (sharpening TD finitely): every maximal constant run [T,V] of c with T >= 1
      and V < 2^20 has length V-T+1 <= 2*log2(T+1) + 4.  TD proves V <= 4T+5.
Also: the first 100,001 bits must hash to E2's sha256 (independent reproduction of F3).

Direct big-int evolution: bit j of `row` is x(j+lo, t); one step is three big-int ops.
"""
import hashlib, json, math, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 1 << 20
t0 = time.time()
row, lo = 1, 0
bits = bytearray(N)
for t in range(N):
    bits[t] = (row >> (-lo)) & 1
    row <<= 1; lo -= 1
    row = ((row << 1) ^ (row | (row >> 1))) & ((1 << (2 * t + 3)) - 1)
evolve_seconds = round(time.time() - t0, 1)

s = ''.join('1' if b else '0' for b in bits)
first_100001_sha = hashlib.sha256(s[:100001].encode()).hexdigest()

# H9: discrepancy
S, worst, worst_N, h9_fail = 0, 0.0, 0, []
for n in range(1, N + 1):
    S += bits[n - 1]
    if n >= 16:
        r = abs(2 * S - n) / math.sqrt(n)
        if r > worst:
            worst, worst_N = r, n
        if r > 3.0:
            h9_fail.append(n)

# H13: maximal constant runs
runs, T = [], 0
for t in range(1, N + 1):
    if t == N or bits[t] != bits[T]:
        runs.append((T, t - 1, int(bits[T])))
        T = t
h13_fail, longest = [], []
for (T, V, v) in runs:
    if T >= 1 and V < N - 1:
        L = V - T + 1
        if L > 2 * math.log2(T + 1) + 4:
            h13_fail.append([T, V, v])
        longest.append((L, T, V, v))
longest.sort(reverse=True)

result = {
    'N': N, 'evolve_seconds': evolve_seconds, 'ones': S, 'zeros': N - S,
    'sha256_first_100001_no_newline': first_100001_sha,
    'sha256_all_no_newline': hashlib.sha256(s.encode()).hexdigest(),
    'H9': {'bound': '3*sqrt(N)', 'range': [16, N], 'failures': h9_fail[:20], 'failure_count': len(h9_fail), 'max_ratio': round(worst, 4), 'argmax_N': worst_N},
    'H13': {'bound': '2*log2(T+1)+4', 'failures': h13_fail[:20], 'failure_count': len(h13_fail), 'longest_runs': [list(x) for x in longest[:12]], 'run_count': len(runs)},
    'blocks': {k: dict(sorted(Counter(s[i:i + k] for i in range(N - k + 1)).items())) for k in (2, 3, 4)},
    'TD_bound_check': all(V <= 4 * T + 5 for (T, V, v) in runs[:-1]),
}
(HERE / 'center_2_20.json').write_text(json.dumps(result, indent=1) + '\n')
(HERE / 'center_2_20.txt').write_text(s + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'blocks'}, indent=1))
