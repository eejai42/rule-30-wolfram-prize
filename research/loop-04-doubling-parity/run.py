"""Loop 4: what decides eps_k right after a doubling.

Hypotheses stated before testing:
  H15: for k >= 4, if eps_{k-1} = 1 then eps_k = ones_{k-2} mod 2.
  H16: the same congruence holds for every k >= 4, with no doubling assumption.
  H17: never three consecutive doublings (k >= 5).
All three are tested on offsets 4..64 by recomputing the diagonals. Proofs (TM, TN)
are in PROOFS.md; H17 is TN.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import diagonals as dg

HERE = Path(__file__).resolve().parent
K = 64
W, info = dg.words(K)
ones = {j: W[j][0].bit_count() for j in range(0, K + 1)}
eps = {j: info[j]['eps'] for j in range(1, K + 1)}

h15_tested, h15_fail, h16_fail, h17_fail = [], [], [], []
for k in range(4, K + 1):
    pred = ones[k - 2] & 1
    if eps[k - 1] == 1:
        h15_tested.append(k)
        if eps[k] != pred:
            h15_fail.append(k)
    if eps[k] != pred:
        h16_fail.append(k)
for k in range(5, K + 1):
    if eps[k - 2] == eps[k - 1] == eps[k] == 1:
        h17_fail.append(k)

zero_runs, run = [], 0
for k in range(3, K + 1):
    if eps[k] == 0:
        run += 1
    else:
        if run:
            zero_runs.append(run)
        run = 0
growth = {k: W[k][1].bit_length() - 1 for k in range(3, K + 1)}
upper_ok = all(growth[k] <= growth[3] + -(-2 * (k - 3) // 3) for k in range(3, K + 1))

result = {
    'K': K,
    'eps_sequence_3_to_K': ''.join(str(eps[k]) for k in range(3, K + 1)),
    'H15': {'tested_k': h15_tested, 'counterexamples': h15_fail},
    'H16': {'counterexamples': h16_fail, 'first': h16_fail[0] if h16_fail else None,
            'first_detail': {'eps_prev': eps[h16_fail[0] - 1], 'ones_k_minus_2': ones[h16_fail[0] - 2], 'eps': eps[h16_fail[0]]} if h16_fail else None},
    'H17': {'counterexamples': h17_fail},
    'plateau_lengths': zero_runs, 'longest_plateau': max(zero_runs),
    'TN_corollary_upper_bound_holds': upper_ok,
    'log2_P': growth,
}
(HERE / 'doubling_parity_check.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'log2_P'}, indent=1))
assert not h15_fail and h16_fail and not h17_fail and upper_ok


def edit(book):
    ps = 'research/loop-04-doubling-parity/PROOFS.md'
    lt.add_assertion(book, 'H15', 'For k>=4, if eps_{k-1}=1 then eps_k = ones_{k-2} mod 2 (doubling at k decided by the parity of the grandparent diagonal).', 'OPEN')
    lt.add_assertion(book, 'H16', 'eps_k = ones_{k-2} mod 2 for every k>=4, with no doubling assumption on k-1.', 'OPEN')
    lt.add_assertion(book, 'TM', 'After a doubling at k-1 (k>=4), eps_k equals the parity of the number of ones of y_{k-2} over its least period.', 'PROVED_HUMAN_READABLE', ps + ' §TM', deps=['TA', 'TK', 'TL'])
    lt.add_assertion(book, 'TN', 'For k>=5 the least diagonal period never doubles three times in a row; hence log2 P_k <= log2 P_k0 + ceil(2(k-k0)/3).', 'PROVED_HUMAN_READABLE', ps + ' §TN', deps=['TM', 'TA', 'TK'])
    lt.add_dependency(book, 'H15', 'TM')
    lt.row(book, 'Assertions', 'H15')['ProofSection'] = ps + ' §TM'
    lt.set_status(book, 'H15', 'PROVED_HUMAN_READABLE', f'No counterexample on the {len(h15_tested)} doubling offsets in 4..{K} (E13); then proved as TM.')
    d = result['H16']['first_detail']
    lt.set_status(book, 'H16', 'FALSIFIED', f'k={result["H16"]["first"]}: eps_(k-1)={d["eps_prev"]}, ones_(k-2)={d["ones_k_minus_2"]}, but eps_k={d["eps"]}. {len(h16_fail)} counterexamples in 4..{K}.', replacement='TM')
    lt.add_evidence(book, 'E13', 'research/loop-04-doubling-parity/doubling_parity_check.json', supports=['H15', 'H16', 'TN'])
    lt.add_evidence(book, 'E14', ps, supports=['TM', 'TN', 'H15'])
    return (f'H15 tested on {len(h15_tested)} offsets then proved as TM; H16 falsified at k={result["H16"]["first"]}; TN (no triple doubling) proved, '
            f'giving log2 P_k <= log2 P_k0 + ceil(2(k-k0)/3). Longest observed plateau {result["longest_plateau"]}.')


consumed = lt.run_loop('effortless-4', 'H15: after a doubling at k-1, eps_k = ones_{k-2} mod 2 (and H16: the same without the doubling).', edit, ['H15', 'H16', 'TM', 'TN', 'TK', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H15', 'H16', 'TM', 'TN', '_dashboard')}, indent=1))
