"""Loop 1: the forcing-period lemma.

Hypothesis H7: for every k >= 3 the least period Q_k of q_k = y_{k-1} OR y_{k-2}
equals max(P_{k-1}, P_{k-2}).  Checked against the certified period table E1
(k <= 51). Proves TF/TG/TH/TI (PROOFS.md) and reduces H4 to H7.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
E1 = lt.ROOT / 'bootstrap/cmcc_rule30_effortless_migration/research_v05/data/diagonal_periods.json'
rows = {r['k']: r for r in json.loads(E1.read_text())}
K = max(rows)

checks = []
h7_fail, h4_fail, th_covered, th_uncovered = [], [], [], []
for k in range(3, K + 1):
    P = max(rows[k - 1]['period'], rows[k - 2]['period'])
    Q = rows[k]['forcing_period']
    parents_doubling = [j for j in (k - 1, k - 2) if rows[j]['period'] == P and rows[j].get('forcing_parity') == 1]
    ok = (Q == P)
    if not ok:
        h7_fail.append(k)
    if rows[k]['period'] < rows[k - 1]['period']:
        h4_fail.append(k)
    (th_covered if parents_doubling else th_uncovered).append(k)
    checks.append({'k': k, 'P_max_parent': P, 'Q_k': Q, 'eps_k': rows[k]['forcing_parity'], 'P_k': rows[k]['period'], 'H7_ok': ok, 'TH_applies': bool(parents_doubling)})

result = {
    'source': str(E1.relative_to(lt.ROOT)), 'k_range': [3, K],
    'H7_counterexamples': h7_fail, 'H4_counterexamples': h4_fail,
    'TH_covers_k': th_covered, 'H7_open_case_k': th_uncovered,
    'checks': checks,
}
(HERE / 'forcing_period_check.json').write_text(json.dumps(result, indent=1) + '\n')
print('H7 fails:', h7_fail, '| H4 fails:', h4_fail, '| TH covers', len(th_covered), 'open case', len(th_uncovered))
assert not h7_fail and not h4_fail


def edit(book):
    ps = 'research/loop-01-forcing-period/PROOFS.md'
    lt.add_assertion(book, 'TF', 'For k>=3 and P=max(P_{k-1},P_{k-2}): if q_k(P/2)=1 then the least period of the forcing word q_k=y_{k-1} OR y_{k-2} is exactly P.', 'PROVED_HUMAN_READABLE', ps + ' §TF', deps=['D0', 'T0', 'T004', 'TA', 'TB'])
    lt.add_assertion(book, 'TG', 'If j>=1 and eps_j=1 (least period of y_j is twice that of its forcing word) then y_j(P_j/2)=1.', 'PROVED_HUMAN_READABLE', ps + ' §TG', deps=['T0', 'TA'])
    lt.add_assertion(book, 'TH', 'For k>=3, if some parent j in {k-1,k-2} attains P=max(P_{k-1},P_{k-2}) and has eps_j=1, then Q_k=P.', 'PROVED_HUMAN_READABLE', ps + ' §TH', deps=['TF', 'TG'])
    lt.add_assertion(book, 'H7', 'For all k>=3 the least period of the forcing word equals max(P_{k-1},P_{k-2}); no OR of two parent diagonals ever has a period smaller than both.', 'FINITE_VERIFIED', '', deps=['T004'])
    lt.add_assertion(book, 'TI', 'If H7 holds for all k>=3 then the least diagonal periods are nondecreasing (H7 implies H4).', 'PROVED_HUMAN_READABLE', ps + ' §TI', deps=['T004', 'TA'])
    lt.add_dependency(book, 'H4', 'TI')
    lt.add_dependency(book, 'H4', 'H7')
    lt.set_status(book, 'H4', 'FINITE_VERIFIED', f'Checked directly for k<={K} in E1/E8; reduced to H7 by TI. Not a proof: H7 is finite only.')
    lt.add_evidence(book, 'E8', 'research/loop-01-forcing-period/forcing_period_check.json', supports=['H7', 'H4', 'TH'])
    lt.add_evidence(book, 'E9', ps, supports=['TF', 'TG', 'TH', 'TI'])
    return (f'Added TF, TG, TH, TI (proved) and H7 (finite through k={K}). H4 OPEN->FINITE_VERIFIED with new dependency edges H4<-TI, H4<-H7; '
            f'TH covers {len(th_covered)} of {K-2} offsets, the remaining {len(th_uncovered)} plateau-fed offsets are the open case of H7.')


consumed = lt.run_loop('effortless-1', 'H7: Q_k = max(P_{k-1},P_{k-2}) for all k>=3; TF/TG/TH/TI provable; H4 reduces to H7.', edit, ['TF', 'TG', 'TH', 'TI', 'H7', 'H4', 'F2', 'P1'], HERE)
print(json.dumps(consumed, indent=1))
