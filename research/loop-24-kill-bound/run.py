"""Loop 24, the first model-native loop: H39 stated as rows, decided by the build.

H39 (serves B9 -> B1 -> P1): on the real prefix, left-consistency kills every nonconstant primitive
tail a with |a| <= 3, spliced on at any onset 1 <= T <= 10, within 3|a| steps of the onset:
KillExcess(a, T) <= 3|a|.

Nothing here computes a cell, a kill or a verdict. The loop adds the hypothesis as a predicate (its
statement a term tree), one instance per existing TailCandidates row, and the claim H39 linked to
the predicate with ReportedStatus OPEN. The build computes each tail's kill from the rule and the
real prefix, decides each instance, and sets H39's EffectiveStatus; the loop then records what the
build decided as a Revision. Chosen with the depth-64 oracle in view (bootstrap/rule30-model), so
this is a demonstration of the mechanism more than a blind test.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import model_tools as mt

HERE = Path(__file__).resolve().parent
LOOP, PID = 'effortless-24', 'pr-h39-kill-within-3p'
V, K = (lambda n: ('var', n)), (lambda n: ('const', n))
a, T = V('word'), V('onset')
TREE = ('ForAll!', 'word', ('&&', ('&&', ('Nonconstant', a), ('==', ('LeastPeriod', a), ('Length', a))), ('<=', ('Length', a), K(3))),
        ('ForAll!', 'onset', ('&&', ('>=', T, K(1)), ('<=', T, K(10))),
         ('<=', ('KillExcess', a, T), ('*', K(3), ('Length', a)))))
STATEMENT = ('H39: on the real prefix, left-consistency kills every nonconstant primitive tail a with |a| <= 3, '
             'spliced on at any onset 1 <= T <= 10, within 3|a| steps of the onset.')
HYPOTHESIS = STATEMENT + ' Stated as model rows; the build decides it.'


def edit(book):
    keys = [r['TailCandidateId'] for r in lt.rows(book, 'TailCandidates')]
    mt.add_loop_predicate(book, PID, 'Hypothesis', 'TailCandidateExcessBound', TREE, STATEMENT,
                          'One instance per tail candidate: killed, with KillExcess <= 3|a|.', 1, 'TailCandidate', keys, slope=3, intercept=0)
    lt.add_assertion(book, 'H39', STATEMENT, deps=('TX',))
    lt.row(book, 'Assertions', 'H39')['Predicate'] = PID
    return f'H39 stated as rows: predicate {PID} with {len(keys)} instance rows over TailCandidates.'


def summarize(book):
    p, h = lt.row(book, 'Predicates', PID), lt.row(book, 'Assertions', 'H39')
    failing = [(r['TailCandidate'], r['TailKillExcess']) for r in lt.rows(book, 'PredicateInstances')
               if r['Predicate'] == PID and r['InDomain'] == 1 and r['Holds'] == 0]
    return (f'Decided by the build: {h["EffectiveStatus"]} ({p["FiniteVerdict"]}). '
            f'Counterexamples (candidate, excess): {failing}.')


if __name__ == '__main__':
    consumed = lt.run_loop(LOOP, HYPOTHESIS, edit, ['H39', 'B9'], HERE, summarize=summarize)
    print({k: v for k, v in consumed.items() if not k.startswith('_')})
