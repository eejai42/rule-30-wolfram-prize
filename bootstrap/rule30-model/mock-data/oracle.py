"""Shadle step 5: the expected values for every scenario, computed independently of the rulebook.

The model's data is not invented: it is the real Rule 30 evolution, so "mock data" here means
the small, fully known instance (depth 64) and the answers each business rule must produce on
it. research/hub/check_model.py compares the built rulebook against scenarios.json.

Usage: python3 oracle.py   (writes scenarios.json next to this file)
"""
import json
from fractions import Fraction
from pathlib import Path

DEPTH, MAX_PERIOD, TOLERANCES = 64, 24, ((1, 5), (1, 10), (1, 20))


def rule_bit(rule, n):
    return (rule >> n) & 1


def mirror(rule):
    return sum(rule_bit(rule, ((n & 1) << 2) | (n & 2) | (n >> 2)) << n for n in range(8))


def complement(rule):
    return sum((1 - rule_bit(rule, 7 - n)) << n for n in range(8))


def evolve(rule, depth):
    rows = [{0: 1}]
    for t in range(1, depth + 1):
        prev = rows[-1]
        g = lambda i: prev.get(i, 0)
        rows.append({i: rule_bit(rule, 4 * g(i - 1) + 2 * g(i) + g(i + 1)) for i in range(-t, t + 1)})
    return rows


rows = evolve(30, DEPTH)
c = [r[0] for r in rows]
use = {n: 0 for n in range(8)}
for t in range(1, DEPTH + 1):
    prev = rows[t - 1]
    for i in rows[t]:
        use[4 * prev.get(i - 1, 0) + 2 * prev.get(i, 0) + prev.get(i + 1, 0)] += 1

last_mismatch = {p: max(t for t in range(DEPTH + 1 - p) if c[t] != c[t + p]) for p in range(1, MAX_PERIOD + 1)}
streak = {}
for p in range(1, MAX_PERIOD + 1):
    best = cur = 0
    for t in range(DEPTH + 1 - p):
        cur = cur + 1 if c[t] == c[t + p] else 0
        best = max(best, cur)
    streak[p] = best

run_start, td_violations = [], 0
for t, v in enumerate(c):
    run_start.append(run_start[-1] if t and c[t - 1] == v else t)
    bound = 2 * run_start[t] + 1 if v == 1 else 4 * run_start[t] + 5
    td_violations += t > bound

ones = [sum(c[:t + 1]) for t in range(DEPTH + 1)]
dev = [abs(Fraction(ones[t], t + 1) - Fraction(1, 2)) for t in range(DEPTH + 1)]
last_excursion = {f'{a}-{b}': max((t for t in range(DEPTH + 1) if dev[t] > Fraction(a, b)), default=None) for a, b in TOLERANCES}

out = {
    'depth': DEPTH,
    'S01_rule30_table': {f'{n:03b}': rule_bit(30, n) for n in range(7, -1, -1)},
    'S02_polynomial_mismatches': {r: sum(rule_bit(r, n) != (((n >> 2) + ((n >> 1) & 1) + (n & 1) + ((n >> 1) & 1) * (n & 1)) % 2) for n in range(8)) for r in (30, 86, 135, 149)},
    'S03_equivalence': {r: {'mirror': mirror(r), 'complement': complement(r)} for r in (30, 86, 135, 149)},
    'S04_quiescent': {r: rule_bit(r, 0) == 0 for r in (30, 86, 135, 149)},
    'S05_first_lines': {t: [rows[t][i] for i in range(-t, t + 1)] for t in range(4)},
    'S06_center': ''.join(map(str, c)),
    'S07_transition_use': {f'{n:03b}': use[n] for n in range(8)},
    'S08_line_black_counts': [sum(r.values()) for r in rows],
    'S09_last_mismatch': last_mismatch,
    'S09_longest_streak': streak,
    'S09_bounded_p1_holds': {p: last_mismatch[p] >= (DEPTH - p) // 2 for p in last_mismatch},
    'S10_td_violations': td_violations,
    'S10_longest_center_run': max(t - run_start[t] + 1 for t in range(DEPTH + 1)),
    'S11_ones_at_horizon': ones[-1],
    'S11_discrepancy_at_horizon': 2 * ones[-1] - (DEPTH + 1),
    'S11_max_abs_discrepancy': max(abs(2 * ones[t] - (t + 1)) for t in range(DEPTH + 1)),
    'S11_last_excursion': last_excursion,
    'S12_center_color_counts': {'white': c.count(0), 'black': c.count(1)},
    'S13_light_cone_effort': {n: (n + 1) ** 2 - 1 for n in (1, 8, 32, 64)},
    'S14_cells': sum(len(r) for r in rows),
    'S14_black_cells': sum(sum(r.values()) for r in rows),
}
Path(__file__).with_name('scenarios.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps({k: out[k] for k in ('S03_equivalence', 'S04_quiescent', 'S07_transition_use', 'S10_td_violations', 'S11_last_excursion', 'S12_center_color_counts', 'S14_cells')}))
