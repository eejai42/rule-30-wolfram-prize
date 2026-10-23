"""Loop 3: the plateau case of H7.

Hypothesis H14 (stated first): y_j(P_j/2) = 1 for every j >= 1.  If true, TF closes
the open case of H7 at t = 0.  Tested on E10's offsets 1..64 by recomputation.
Outcome recorded whatever it is; PROOFS.md carries the proofs written after the test
(TJ cascade lemma, TK = H7 and H4 as theorems, TL repeat-or-double).
Numerical sanity checks for TJ/TK: for each k >= 4 the least j0 with P_j0 = P_{k-1}
has eps_j0 = 1 and y_j0(P/2) = 1, and q_k(t) != q_k(t + P/2) for some t (Q_k = P).
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import diagonals as dg

HERE = Path(__file__).resolve().parent
K = 64
W, info = dg.words(K)

h14_fail = [j for j in range(1, K + 1) if dg.bit(W[j][0], W[j][1], W[j][1] // 2) != 1]
first_fail = h14_fail[0]
w5, p5 = W[first_fail]
word5 = ''.join(str((w5 >> t) & 1) for t in range(p5))

tk_rows = []
for k in range(4, K + 1):
    P = max(W[k - 1][1], W[k - 2][1])
    j0 = min(j for j in range(1, k) if W[j][1] == P)
    q = info[k]['q']
    gamma_witness = next(t for t in range(P // 2) if ((q >> t) & 1) != ((q >> (t + P // 2)) & 1))
    tk_rows.append({'k': k, 'P': P, 'j0': j0, 'eps_j0': info[j0]['eps'], 'y_j0_at_half': dg.bit(W[j0][0], W[j0][1], P // 2),
                    'Q_k': info[k]['Q'], 'Q_equals_P': info[k]['Q'] == P, 'first_t_with_q(t)!=q(t+P/2)': gamma_witness, 'TH_covers': any(W[j][1] == P and info[j]['eps'] == 1 for j in (k - 1, k - 2))})
tk_ok = all(r['eps_j0'] == 1 and r['y_j0_at_half'] == 1 and r['Q_equals_P'] for r in tk_rows)

result = {
    'K': K,
    'H14': {'statement': 'y_j(P_j/2) = 1 for all j >= 1', 'counterexamples': h14_fail, 'first': first_fail, 'first_period_word': word5, 'FALSIFIED': bool(h14_fail)},
    'TK_witness_check': {'all_ok': tk_ok, 'rows': tk_rows},
    'open_case_offsets_now_covered_by_TJ': [r['k'] for r in tk_rows if not r['TH_covers']],
    'base_case': {'P0': W[0][1], 'P1': W[1][1], 'P2': W[2][1], 'P3': W[3][1], 'Q3': info[3]['Q'], 'eps3': info[3]['eps']},
}
(HERE / 'plateau_witness_check.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'TK_witness_check'}, indent=1), '| TK witness rows ok:', tk_ok)
assert h14_fail and tk_ok and result['base_case'] == {'P0': 1, 'P1': 2, 'P2': 2, 'P3': 4, 'Q3': 2, 'eps3': 1}


def edit(book):
    ps = 'research/loop-03-plateau-witness/PROOFS.md'
    lt.add_assertion(book, 'H14', 'Every diagonal is 1 at its half period: y_j(P_j/2)=1 for all j>=1 (would close the open case of H7 through TF at t=0).', 'OPEN', '', deps=[])
    lt.set_status(book, 'H14', 'FALSIFIED', f'y_{first_fail} has period {p5} and word {word5}; bit {p5//2} is 0. {len(h14_fail)} counterexamples through k={K} (E11).', replacement='TJ')
    lt.add_assertion(book, 'TJ', 'Cascade lemma: for k>=4 and P=max(P_{k-1},P_{k-2}), if y_j(P/2)=1 for some 2<=j<=k-1 then Q_k=P.', 'PROVED_HUMAN_READABLE', ps + ' §TJ', deps=['D0', 'T0', 'TB', 'T004', 'TA'])
    lt.add_assertion(book, 'TK', 'For every k>=3, Q_k=max(P_{k-1},P_{k-2}), and the least diagonal periods are nondecreasing (induction on k using TJ, TG, TA).', 'PROVED_HUMAN_READABLE', ps + ' §TK', deps=['TJ', 'TG', 'TA', 'T004', 'TB'])
    lt.add_dependency(book, 'H7', 'TK')
    lt.row(book, 'Assertions', 'H7')['ProofSection'] = ps + ' §TK'
    lt.set_status(book, 'H7', 'PROVED_HUMAN_READABLE', 'Proved by TK (induction with the cascade lemma TJ); the finite checks E8/E10 are now corroboration only.')
    lt.row(book, 'Assertions', 'H4')['ProofSection'] = ps + ' §TK; TI'
    lt.set_status(book, 'H4', 'PROVED_HUMAN_READABLE', 'Follows from H7 by TI, and is also the second half of TK.')
    lt.add_assertion(book, 'TL', 'For every k>=3, P_k = P_{k-1}*(1+eps_k): the least period repeats or doubles, never otherwise; and it doubles infinitely often.', 'PROVED_HUMAN_READABLE', ps + ' §TL', deps=['H7', 'TA', 'TB'])
    lt.add_evidence(book, 'E11', 'research/loop-03-plateau-witness/plateau_witness_check.json', supports=['H14', 'TK', 'TJ'])
    lt.add_evidence(book, 'E12', ps, supports=['TJ', 'TK', 'TL', 'H7', 'H4'])
    return (f'H14 falsified at k={first_fail}. Added TJ (cascade lemma), TK (H7 and H4 proved by induction), TL (repeat-or-double). '
            f'H7 and H4 FINITE_VERIFIED->PROVED_HUMAN_READABLE; {len(result["open_case_offsets_now_covered_by_TJ"])} plateau-fed offsets through {K} are now covered by proof, not data.')


consumed = lt.run_loop('effortless-3', 'H14: y_j(P_j/2)=1 for all j (closes the plateau case of H7 at t=0).', edit, ['H14', 'TJ', 'TK', 'TL', 'H7', 'H4', 'TI', 'F5', 'P1'], HERE)
print(json.dumps({k: consumed[k] for k in ('H14', 'TJ', 'TK', 'TL', 'H7', 'H4', '_dashboard')}, indent=1))
