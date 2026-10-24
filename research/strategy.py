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
    F('NextLoop', ty='relationship', rel='Loops', desc='The planned loop (State PLANNED) that carries out the next step.'),
    F('ProjectKey', ty='relationship', rel='Dashboards', desc='Dashboard this plan rolls up to.', nullable=False),
    LK('GoalStatement', 'Assertions', 'Goal', 'AssertionId', 'Statement', "The goal's statement."),
    LK('GoalStatusGroup', 'Assertions', 'Goal', 'AssertionId', 'StatusGroup', "The goal's status group."),
    LK('GoalAncestorBlockedCount', 'Assessments', 'Goal', 'AssessmentId', 'AncestorBlockedCount', 'Open claims the goal waits on.', 'integer'),
    LK('NextTargetStatement', 'Assertions', 'NextTarget', 'AssertionId', 'Statement', "The next target's statement."),
    LK('NextTargetStatusGroup', 'Assertions', 'NextTarget', 'AssertionId', 'StatusGroup', "The next target's status group."),
    LK('UpdatedInLoopState', 'Loops', 'UpdatedInLoop', 'LoopId', 'State', 'State of the loop that last updated the plan.'),
    LK('NextLoopState', 'Loops', 'NextLoop', 'LoopId', 'State', 'PLANNED until the loop starts, then RUNNING and VERIFIED.'),
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


LOOP_TARGET_SCHEMA = [
    F('LoopTargetId', desc='<loop>-<assertion>.', nullable=False),
    F('Name', ty='calculated', formula='={{LoopTargetId}}', desc='Display alias.'),
    F('Loop', ty='relationship', rel='Loops', desc='The loop.', nullable=False),
    F('Assertion', ty='relationship', rel='Assertions', desc='A claim the loop serves, tests or builds on.', nullable=False),
    F('Role', desc='Serves (the open claim it advances), Tests (the hypothesis it decides), Builds on (results it uses) or Rules out.', nullable=False),
    F('Note', desc='How the loop relates to the claim, in one line.'),
    LK('Statement', 'Assertions', 'Assertion', 'AssertionId', 'Statement', 'The claim.'),
    LK('Kind', 'Assertions', 'Assertion', 'AssertionId', 'Kind', 'Kind of claim.'),
    LK('StatusGroup', 'Assertions', 'Assertion', 'AssertionId', 'StatusGroup', 'Proved, Checked, Open, Falsified or Superseded.'),
    LK('LoopState', 'Loops', 'Loop', 'LoopId', 'State', 'State of the loop.'),
]


def ensure_field(book, tbl, field):
    sch = book[tbl]['schema']
    sch[:] = [f for f in sch if f['name'] != field['name']] + [field]


def ensure_tables(book):
    if 'Strategies' not in book:
        book['Strategies'] = {'Description': 'The plan toward a prize problem: where things stand, the route, and where the next loop aims. One row is in force (IsCurrent = 1); older plans are history.', 'schema': STRATEGY_SCHEMA, 'data': []}
    else:
        book['Strategies']['schema'] = STRATEGY_SCHEMA
    if 'StrategySteps' not in book:
        book['StrategySteps'] = {'Description': 'The claims on a plan\'s route, in order from the goal, each with its role and a note. Statuses are looked up from the claims.', 'schema': STEP_SCHEMA, 'data': []}
    else:
        book['StrategySteps']['schema'] = STEP_SCHEMA
    if 'LoopTargets' not in book:
        book['LoopTargets'] = {'Description': 'The claims a loop serves, tests or builds on, so a loop page (planned, running or done) links to them.', 'schema': LOOP_TARGET_SCHEMA, 'data': []}
    else:
        book['LoopTargets']['schema'] = LOOP_TARGET_SCHEMA
    ensure_field(book, 'Assertions', F('OnCurrentPath', 'integer', 'aggregation', '=COUNTIFS(StrategySteps!{{Assertion}},{{AssertionId}},StrategySteps!{{StrategyIsCurrent}},1)', desc='1 when the claim is a step of the plan in force.'))
    ensure_field(book, 'Assertions', F('LoopTargetCount', 'integer', 'aggregation', '=COUNTIFS(LoopTargets!{{Assertion}},{{AssertionId}})', desc='Loops (planned, running or done) linked to this claim.'))
    ensure_field(book, 'Loops', F('Plan', desc='For a planned loop: what it will do and how its outcome will be read.'))
    ensure_field(book, 'Loops', F('TargetCount', 'integer', 'aggregation', '=COUNTIFS(LoopTargets!{{Loop}},{{LoopId}})', desc='Claims linked to this loop.'))
    ensure_field(book, 'Dashboards', F('PlannedLoopCount', 'integer', 'aggregation', '=COUNTIFS(Loops!{{ProjectKey}},{{DashboardId}},Loops!{{State}},"PLANNED")', desc='Loops planned but not started.'))


def set_next_loop(book, loop_id: str, hypothesis: str, plan: str, targets: list[tuple[str, str, str]]):
    """Write the planned loop (State PLANNED) and its claim links. A loop that already started is left alone."""
    ensure_tables(book)
    loops = book['Loops']['data']
    if lt.has(book, 'Loops', loop_id) and lt.row(book, 'Loops', loop_id)['State'] != 'PLANNED':
        return
    book['Loops']['data'] = [r for r in loops if r['State'] != 'PLANNED']
    seq = 1 + max(r['Sequence'] for r in book['Loops']['data'])
    book['Loops']['data'].append({'LoopId': loop_id, 'Kind': 'EFFORTLESS', 'State': 'PLANNED', 'BuildReceipt': '', 'InputHash': '', 'OutputHash': '',
                                  'Sequence': seq, 'StartedAt': '', 'FinishedAt': '', 'ProjectKey': 'Rule30', 'Hypothesis': hypothesis, 'Summary': '', 'Plan': plan})
    book['LoopTargets']['data'] = [r for r in book['LoopTargets']['data'] if r['Loop'] != loop_id]
    for aid, role, note in targets:
        assert lt.has(book, 'Assertions', aid), aid
        book['LoopTargets']['data'].append({'LoopTargetId': f'{loop_id}-{aid}', 'Loop': loop_id, 'Assertion': aid, 'Role': role, 'Note': note})


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
        Missing='A uniform description of the reachable windows that still kills. Freeing the outer cell at each step reaches every window and lets 18,432 survive (H40). Tying the outer cell to the settled left-edge zone does not help for long: the settled zone starts about 0.27 t columns out (17 at t = 64, 35 at t = 128), so column 24 is settled only until about t = 85, and the unsettled band between the window and the settled zone widens without bound.',
        NextTarget='B7',
        NextLoop='effortless-26',
        NextHypothesis='Decide whether this route can work at all: is there any window width at which the free-outer-cell closure is not the whole space, and does the reachable language keep growing or settle? If the closure is everything at every width and the language keeps growing, no finite-window invariant proves B9 for period 2, and the route closes.',
        Estimate='Proving P1 itself: well under 1 percent, unchanged. Proving the period-2 case on this route: lowered to about 1 in 20, because the window idea needs information from a band that widens with t. Loop 26 is designed to settle whether the route is viable at all.',
        UpdatedInLoop='effortless-25'),
    next_loop=dict(
        id='effortless-26',
        hypothesis='H41 (draft, to be fixed before the run): for every window width E from 8 to 26, the closure of the near-center windows seen at t = 19, under one step with the outer cell free, is the whole space of 2^(E+1) windows; and the number of distinct reachable windows of width 25 keeps growing through t = 60.',
        plan='Sweep the window width with the loop 25 closure, record the smallest width (if any) where the closure is a strict subset, and extend the reachable-language count of loop 23 to t = 60. Reading: a strict subset that still kills would revive the route with a concrete invariant; a full closure at every width, with a language that keeps growing, closes the finite-window route to B9 for period 2. Either way the plan is updated and the next target chosen from what is left.',
        targets=[
            ('B7', 'Serves', 'The open obligation for period 2 that this route would discharge.'),
            ('B9', 'Serves', 'Its period-2 case is what a working invariant would prove.'),
            ('P1', 'Serves', 'The goal, through B1.'),
            ('H40', 'Builds on', 'Loop 25: at width 25 the free-outer-cell closure is everything.'),
            ('H38', 'Builds on', 'Every reachable width-25 window dies: the finite half the invariant must preserve.'),
            ('H37', 'Builds on', 'The reachable windows are a thin set.'),
            ('F22', 'Builds on', 'The language sizes up to t = 45 that the run extends.'),
            ('TX', 'Builds on', 'The step relation: the next center bit is forced after a 1.'),
        ]),
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
    nl = CURRENT['next_loop']
    set_next_loop(book, nl['id'], nl['hypothesis'], nl['plan'], nl['targets'])
    set_strategy(book, CURRENT['sid'], CURRENT['goal'], CURRENT['fields'], CURRENT['steps'])
    lt.save(book)
    print('current strategy:', CURRENT['sid'], 'steps:', len(CURRENT['steps']))
