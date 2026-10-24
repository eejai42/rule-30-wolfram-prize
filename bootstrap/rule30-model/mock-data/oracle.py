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

# --- Problem 1 as tables (S15-S19) ---
TAIL_WORD_LENGTHS, TAIL_ONSETS, TAIL_MARGIN = (1, 2, 3), range(1, 11), 12
words = [''.join(str((n >> (L - 1 - k)) & 1) for k in range(L)) for L in TAIL_WORD_LENGTHS for n in range(2 ** L)]
least = {w: min(d for d in range(1, len(w) + 1) if w == w[d:] + w[:d]) for w in words}
x = lambda i, t: rows[t].get(i, 0) if t >= 0 else 0
tx_violations = sum(1 for t in range(DEPTH) if c[t] == 1 and c[t + 1] != 1 - x(-1, t))


def first_mismatch(i, p, T):
    return next((t for t in range(T, DEPTH - p + 1) if x(i, t) != x(i, t + p)), DEPTH - p + 1)


windows = [(p, T) for p in range(1, MAX_PERIOD + 1) for T in range((DEPTH - 2 * p) // 2 + 1)]
tc_fail = sum(1 for p, T in windows if min(first_mismatch(0, p, T), first_mismatch(1, p, T)) > 2 * T + p)
tc_center = sum(1 for p, T in windows if first_mismatch(0, p, T) <= 2 * T + p)


def kill(w, T):
    """First one-time t >= T - 1 of the real prefix + w w w ... with c'(t + 1) != NOT x'(-1, t); H + 1 if none."""
    H, L = T + TAIL_MARGIN, len(w)
    cc = lambda t: c[t] if t < T else int(w[(t - T) % L])
    left = {i: x(i, T) for i in range(-T, 0)}
    for t in range(T - 1, H + 1):
        x1 = x(-1, t) if t < T else left.get(-1, 0)
        if cc(t) == 1 and cc(t + 1) != 1 - x1:
            return t
        if t >= T:
            left = {i: (lambda g: g(i - 1) ^ (g(i) | g(i + 1)))(lambda j: cc(t) if j == 0 else left.get(j, 0)) for i in range(-(t + 1), 0)}
    return H + 1


tail_words = [w for w in words if least[w] == len(w)]
kills = {f'{w}-T{T:02d}': kill(w, T) for w in tail_words for T in TAIL_ONSETS}

# --- diagonals (S20): least dyadic period of y_k from t = 0; least dyadic eventual period of w_k ---
def dyadic(seq, cap, kmax, eventual):
    d = 1
    while d <= min(2 ** kmax, cap):
        mism = [t for t in range(DEPTH + 1 - d) if seq[t] != seq[t + d]]
        if not eventual and not mism and DEPTH + 1 - d >= d:
            return d, 0
        onset = max(mism) + 1 if mism else 0
        if eventual and 2 * onset <= DEPTH and (DEPTH + 1 - d) - onset >= 2 * d:
            return d, onset
        d *= 2
    return -1, 0


right = {k: dyadic([x(t - k, t) for t in range(DEPTH + 1)], 32, k, False)[0] for k in range(9)}
left = {k: dyadic([x(k - t, t) for t in range(DEPTH + 1)], 8, k, True) for k in range(11)}

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
    'S15_least_periods': least,
    'S16_tx_violations': tx_violations,
    'S17_tc_windows': len(windows), 'S17_tc_failures': tc_fail, 'S17_tc_center_witnesses': tc_center,
    'S18_first_mismatch_sample': {f'{i}-p{p:02d}-T{T:03d}': first_mismatch(i, p, T) for i in (0, 1) for p in (1, 2, 3, 7) for T in (0, 5, 20, 40) if T <= DEPTH - p},
    'S19_tail_kill_times': kills,
    'S20_right_least_periods': right,
    'S20_left_eventual': {k: list(v) for k, v in left.items()},
}
Path(__file__).with_name('scenarios.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps({k: out[k] for k in ('S03_equivalence', 'S04_quiescent', 'S07_transition_use', 'S10_td_violations', 'S11_last_excursion', 'S12_center_color_counts', 'S14_cells')}))
