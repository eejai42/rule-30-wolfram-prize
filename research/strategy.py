"""The current strategy toward P1, as ledger rows the explorer's landing page reads.

Strategies       one plan: the goal, where things stand, the route, the next loop's target and
                 hypothesis, an honest estimate, the loop that last updated it. IsCurrent = 1 on
                 exactly one row; older plans stay as history.
StrategySteps    the claims on that route, in order from the goal down, each with a role (Goal,
                 Reduction, Open obligation, Evidence, Ruled out) and a one-line note. Their
                 statuses are lookups of the claims, so the page updates when a loop changes them.

The plan itself is judgement, so it is Data, written by whoever runs the loop (step 6a in
CLAUDE.md). Every status, count and flag the page shows is a formula.
Usage: python3 research/strategy.py && effortless build
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_tools as lt


def F(name, dt='string', ty='raw', formula=None, rel=None, desc='', nullable=True):
    f = {'name': name, 'datatype': dt, 'type': ty, 'nullable': nullable, 'Description': desc}
    if formula:
        f['formula'] = formula
    if rel:
        f['RelatedTo'] = rel
    return f


def LK(name, table, fk, key, field, desc, dt='string'):
    return F(name, dt, 'lookup', f'=INDEX({table}!{{{{{field}}}}},MATCH({{{{{fk}}}}},{table}!{{{{{key}}}}},0))', desc=desc)


STRATEGY_SCHEMA = [
    F('StrategyId', desc='after-loop-<n>: the plan as it stood after that loop.', nullable=False),
    F('Name', ty='calculated', formula='={{StrategyId}}', desc='Display alias.'),
    F('Goal', ty='relationship', rel='Assertions', desc='The prize problem this plan aims at.', nullable=False),
    F('IsCurrent', 'integer', desc='1 on the plan in force now, 0 on history.', nullable=False),
    F('Headline', desc='Where things stand, in one sentence.'),
    F('Approach', desc='The route being taken and why, in a short paragraph.'),
    F('Missing', desc='What the route still lacks.'),
    F('NextTarget', ty='relationship', rel='Assertions', desc='The open claim the next loop serves.'),
    F('NextHypothesis', desc='Where the next loop is aiming: its hypothesis in words.'),
    F('Estimate', desc='An honest estimate of the odds, with what each number is for.'),
    F('UpdatedInLoop', ty='relationship', rel='Loops', desc='The loop after which this plan was written.'),
    F('ProjectKey', ty='relationship', rel='Dashboards', desc='Dashboard this plan rolls up to.', nullable=False),
    LK('GoalStatement', 'Assertions', 'Goal', 'AssertionId', 'Statement', "The goal's statement."),
    LK('GoalStatusGroup', 'Assertions', 'Goal', 'AssertionId', 'StatusGroup', "The goal's status group."),
    LK('GoalAncestorBlockedCount', 'Assessments', 'Goal', 'AssessmentId', 'AncestorBlockedCount', 'Open claims the goal waits on.', 'integer'),
    LK('NextTargetStatement', 'Assertions', 'NextTarget', 'AssertionId', 'Statement', "The next target's statement."),
    LK('NextTargetStatusGroup', 'Assertions', 'NextTarget', 'AssertionId', 'StatusGroup', "The next target's status group."),
    LK('UpdatedInLoopState', 'Loops', 'UpdatedInLoop', 'LoopId', 'State', 'State of the loop that last updated the plan.'),
    F('StepCount', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Strategy}},{{StrategyId}})', desc='Claims on the route.'),
    F('OpenStepCount', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Strategy}},{{StrategyId}},StrategySteps!{{IsOpen}},1)', desc='Steps still open.'),
    F('EstablishedStepCount', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Strategy}},{{StrategyId}},StrategySteps!{{IsEstablished}},1)', desc='Steps proved or finitely checked.'),
    F('BlockingStepCount', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Strategy}},{{StrategyId}},StrategySteps!{{BlocksGoal}},1)', desc='Steps that are open claims the goal waits on.'),
    F('RuledOutCount', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Strategy}},{{StrategyId}},StrategySteps!{{Role}},"Ruled out")', desc='Mechanisms on the record as ruled out.'),
]

STEP_SCHEMA = [
    F('StrategyStepId', desc='<strategy>-<sequence>.', nullable=False),
    F('Name', ty='calculated', formula='={{StrategyStepId}}', desc='Display alias.'),
    F('Strategy', ty='relationship', rel='Strategies', desc='The plan.', nullable=False),
    F('Assertion', ty='relationship', rel='Assertions', desc='The claim at this step.', nullable=False),
    F('Sequence', 'integer', desc='Order on the route, the goal first.', nullable=False),
    F('Role', desc='Goal, Reduction, Open obligation, Evidence or Ruled out.', nullable=False),
    F('Note', desc='Why this claim is on the route, in one line.'),
    LK('Statement', 'Assertions', 'Assertion', 'AssertionId', 'Statement', 'The claim.'),
    LK('Kind', 'Assertions', 'Assertion', 'AssertionId', 'Kind', 'Kind of claim.'),
    LK('StatusGroup', 'Assertions', 'Assertion', 'AssertionId', 'StatusGroup', 'Proved, Checked, Open, Falsified or Superseded.'),
    LK('EffectiveStatus', 'Assertions', 'Assertion', 'AssertionId', 'EffectiveStatus', 'The status the ledger uses.'),
    LK('CurrentStatus', 'Assessments', 'Assertion', 'AssessmentId', 'CurrentStatus', 'Compiled status: BLOCKED when an ancestor is not usable.'),
    LK('StrategyGoal', 'Strategies', 'Strategy', 'StrategyId', 'Goal', "The plan's goal."),
    LK('StrategyIsCurrent', 'Strategies', 'Strategy', 'StrategyId', 'IsCurrent', '1 when the plan is in force.', 'integer'),
    F('GoalPrerequisiteKey', 'string', 'calculated', '=CONCAT({{StrategyGoal}},"-",{{Assertion}})', desc='Key of the Prerequisites row linking the goal to this claim.'),
    LK('IsBlockingAncestorOfGoal', 'Prerequisites', 'GoalPrerequisiteKey', 'PrerequisiteId', 'IsBlockingAncestor', '1 when this claim is an unusable ancestor of the goal.', 'integer'),
    F('IsOpen', 'integer', 'calculated', '=IF({{StatusGroup}}="Open",1,0)', desc='1 while the claim is open.'),
    F('IsEstablished', 'integer', 'calculated', '=IF(OR({{StatusGroup}}="Proved",{{StatusGroup}}="Checked"),1,0)', desc='1 when proved or finitely checked.'),
    F('BlocksGoal', 'integer', 'calculated', '=IF(AND({{IsOpen}}=1,{{IsBlockingAncestorOfGoal}}=1),1,0)', desc='1 when this open claim is one the goal waits on.'),
]


def ensure_tables(book):
    if 'Strategies' not in book:
        book['Strategies'] = {'Description': 'The plan toward a prize problem: where things stand, the route, and where the next loop aims. One row is in force (IsCurrent = 1); older plans are history.', 'schema': STRATEGY_SCHEMA, 'data': []}
    else:
        book['Strategies']['schema'] = STRATEGY_SCHEMA
    if 'StrategySteps' not in book:
        book['StrategySteps'] = {'Description': 'The claims on a plan\'s route, in order from the goal, each with its role and a note. Statuses are looked up from the claims.', 'schema': STEP_SCHEMA, 'data': []}
    else:
        book['StrategySteps']['schema'] = STEP_SCHEMA
    sch = book['Assertions']['schema']
    sch[:] = [f for f in sch if f['name'] != 'OnCurrentPath'] + [
        F('OnCurrentPath', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Assertion}},{{AssertionId}},StrategySteps!{{StrategyIsCurrent}},1)', desc='1 when the claim is a step of the plan in force.')]


def set_strategy(book, sid: str, goal: str, fields: dict, steps: list[tuple[str, str, str]]):
    """Make `sid` the current plan (replacing an earlier row with the same id) with these steps."""
    ensure_tables(book)
    for r in book['Strategies']['data']:
        r['IsCurrent'] = 0
    book['Strategies']['data'] = [r for r in book['Strategies']['data'] if r['StrategyId'] != sid]
    book['StrategySteps']['data'] = [r for r in book['StrategySteps']['data'] if r['Strategy'] != sid]
    raw = {f['name'] for f in STRATEGY_SCHEMA if f['type'] in ('raw', 'relationship')}
    row = {'StrategyId': sid, 'Goal': goal, 'IsCurrent': 1, 'ProjectKey': 'Rule30'}
    row.update({k: v for k, v in fields.items() if k in raw})
    for k in raw - set(row):
        row[k] = None
    book['Strategies']['data'].append(row)
    for n, (aid, role, note) in enumerate(steps, 1):
        assert lt.has(book, 'Assertions', aid), aid
        book['StrategySteps']['data'].append({'StrategyStepId': f'{sid}-{n:02d}', 'Strategy': sid, 'Assertion': aid, 'Sequence': n, 'Role': role, 'Note': note})


CURRENT = dict(
    sid='after-loop-25', goal='P1',
    fields=dict(
        Headline='P1 waits on two open obligations, B7 (period 2) and B8 (period 3 and up), at the bottom of a chain of proved reductions. No prize problem is closer to proved; the open obligations are sharper.',
        Approach='Go after period 2 first, through B9: no left-consistent sequence ends in a 2-periodic tail. TX makes the center left-consistent, so B9 is exactly what B1 needs, and it is weaker than B5. Finite checks are strong: every left-consistent start at onsets 20 to 46 dies within 22 steps of a period-2 tail (F21), and every near-center window of width 25 that such sequences produce at times 19 to 45 dies within 23 steps (H38).',
        Missing='A uniform description of the reachable windows that still kills. The simplest one, closing the window set under one step with the outer cell free, covers every window and lets 18,432 of them survive (H40). The description has to keep information from the far left.',
        NextTarget='B7',
        NextHypothesis='Tie the outer cell of the window to the settled left-edge diagonals instead of leaving it free (or widen the window and constrain its outer part by the seed), and test whether the closure of the reachable windows still kills both period-2 tails. If it does, that is a finite proof of B9 for period 2.',
        Estimate='Proving P1 itself: well under 1 percent, unchanged. Proving the period-2 case on this route: about 1 in 10. A decisive answer either way about this route within a few loops: likely.',
        UpdatedInLoop='effortless-25'),
    steps=[
        ('P1', 'Goal', 'Problem 1: the center column is not eventually periodic.'),
        ('B1', 'Reduction', 'A periodic center of period 2 or more is impossible; with K1 this is P1. Derived from B9 and TX.'),
        ('TX', 'Reduction', 'The center is left-consistent: after every 1, its next bit is forced by its own past.'),
        ('B9', 'Reduction', 'No left-consistent sequence ends in a nonconstant periodic tail. The statement B1 actually needs.'),
        ('B5', 'Reduction', 'The free-row left-cone relaxation excludes every periodic center; it implies B9.'),
        ('B6', 'Reduction', 'B5 restated with the free data named, then split by period.'),
        ('B7', 'Open obligation', 'Period 2. The current target, attacked through the period-2 case of B9.'),
        ('B8', 'Open obligation', 'Period 3 and up. Waits until period 2 shows a proof shape.'),
        ('F21', 'Evidence', 'Every left-consistent start at onsets 20 to 46 dies within 22 steps of a period-2 tail.'),
        ('H38', 'Evidence', 'Every reachable width-25 window dies within 23 steps under both period-2 tails: the finite half.'),
        ('H37', 'Evidence', 'The reachable windows are a thin set: 631 of about 2 billion at width 31.'),
        ('H40', 'Ruled out', 'A free outer cell lets the window closure reach everything: too lossy.'),
        ('H34', 'Ruled out', 'The settled left-edge zone does not make the free-row clash local.'),
        ('H30', 'Ruled out', 'The kill is not linear algebra over the free bits.'),
    ])


if __name__ == '__main__':
    book = lt.load()
    set_strategy(book, CURRENT['sid'], CURRENT['goal'], CURRENT['fields'], CURRENT['steps'])
    lt.save(book)
    print('current strategy:', CURRENT['sid'], 'steps:', len(CURRENT['steps']))
