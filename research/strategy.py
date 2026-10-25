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
    sid='after-loop-27', goal='P1',
    fields=dict(
        Headline="Measured against the official challenge: period 1 and every eventual period with P <= 4096 and T <= 8192 are proved in Lean (the kit); period 2 waits on Q01, which is open, and our left-consistency route attacks the same object from the real seed.",
        Approach="Two routes to P1 meet at one frontier, period 2. The kit's route (B10) splits P1 by the least period and reduces period 2 to Q01, a statement about the zero-boundary left half from any finite start. The kit also proves barriers: no finite abstraction, local ranking or edge-DFA ranking proves Q01, because truncated stripes survive arbitrarily long. Our route (B1, B9, TX) only ever uses the left half the real seed produces, and TX is now kernel-checked. The barrier witnesses are never real left halves (Rule30ZeroBoundaryBarriers.trunc_not_left_half), so the real left halves are where a finite description can still exist.",
        Missing="B9's period-2 case stated in Lean over the kit's driven left half (Rule30DrivenLeft.L) with the real seed's rows as starts, and a proof in Lean that it gives KC4; then a description of those rows that a proof can carry.",
        NextTarget='B7',
        NextLoop='effortless-28',
        NextHypothesis="Read each left half that the real seed produces at the start of a period-2 tail from the left edge inward, and build the smallest automaton accepting exactly those rows at each t. If its size stops growing in t through t = 160, a regular invariant of real left halves is plausible, and it is outside the kit's barrier B6 (which needs arbitrary finite starts). If it grows like the state count, the regular route is closed for real left halves too.",
        Estimate="Proving P1: well under 1 percent, unchanged. Period 2 (Q01, or our B7): about 1 in 30; the kit's barriers lower it for generic finite-state arguments and leave the real-seed route as the one they do not cover. A kit contribution from this ledger soon: unlikely as it stands; the claims of ours that Lean now verifies are known (K1, T0, TX, D0, T004) or elementary (TS).",
        UpdatedInLoop='effortless-27'),
    next_loop=dict(
        id='effortless-28',
        hypothesis="H43 (draft, fix before the run): the left halves the real seed produces at the start of a period-2 tail, read from the left edge inward, are accepted for each t <= 160 by a minimal automaton whose number of states stops growing in t.",
        plan="Use loop 26 merged states (states.py), restricted to real left halves. For each t, build the minimal DFA of the reachable rows read from the left edge inward, padded to a common length, and record its size against t and against the state count. Set it against the kit's barrier B6 (Rule30ZeroBoundaryBarriers.no_edge_dfa_ranking): an automaton that levels off is only interesting because these rows exclude the barrier's truncated stripes (trunc_not_left_half). Reading: a size that levels off makes a regular invariant plausible (next: close it under the step, state it in Lean against Q01); a size that tracks the state count closes the regular whole-row route.",
        targets=[
            ('B7', 'Serves', 'The open obligation for period 2 on our route.'),
            ('Q-Q01', 'Serves', "The kit's open statement for period 2."),
            ('B9', 'Serves', 'Its period-2 case is what a regular invariant of real left halves would prove.'),
            ('P1', 'Serves', 'The goal.'),
            ('F23', 'Builds on', 'Loop 26: the merged reachable states through t = 160, all killed by both period-2 tails.'),
            ('TX', 'Builds on', 'Left-consistency, kernel-checked in Lean in loop 27.'),
            ('L-Rule30ZeroBoundaryBarriers', 'Builds on', "The kit's barriers: what a finite-state argument over all finite starts cannot do."),
            ('H41', 'Builds on', 'Loop 26: no fixed-width window kill; the description must cover whole rows.'),
        ]),
    steps=[
        ('P1', 'Goal', "Problem 1. Our formal statement is proved equivalent to the official Problem1 in Lean (loop 27)."),
        ('B10', 'Reduction', "The kit's route: P1 by the least period. Every case must fall."),
        ('KC1', 'Reduction', 'Period 1: proved in Lean (the kit; our K1 is kernel-checked against it).'),
        ('KC4', 'Open obligation', 'Period 2: reduced to Q01, open.'),
        ('Q-Q01', 'Open obligation', 'Q01: no finite row of the zero-boundary left half keeps the center alternating. Proved to width 52. The frontier.'),
        ('KC5', 'Open obligation', 'Least period 3: four open statements.'),
        ('KC6', 'Open obligation', 'Least period 4: Absorption, open.'),
        ('KC7', 'Open obligation', 'Every longer least period: open; many words excluded.'),
        ('B1', 'Reduction', "Our route: no periodic center of period 2 or more, through left-consistency."),
        ('TX', 'Reduction', 'The center is left-consistent: kernel-checked in Lean.'),
        ('B9', 'Reduction', 'No left-consistent sequence ends in a nonconstant periodic tail: Q01 seen from the real seed.'),
        ('B7', 'Open obligation', 'Period 2 on our route. The next target.'),
        ('KC2', 'Evidence', 'No eventual period P <= 4096 with transient <= 8192 (kit, kernel-checked).'),
        ('KC3', 'Evidence', 'Any eventual period has T + P >= 16359 (kit, kernel-checked).'),
        ('F23', 'Evidence', 'Merged by row, the reachable states through t = 160 all die under both period-2 tails.'),
        ('L-Rule30ZeroBoundaryBarriers', 'Ruled out', 'Finite abstractions, local rankings and edge-DFA rankings cannot prove Q01 over all finite starts (kit, kernel-checked).'),
        ('TY', 'Ruled out', 'A free outer cell floods any window closure, at every width.'),
        ('H41', 'Ruled out', 'No fixed-width window kill: the longest survival grows with t.'),
        ('H30', 'Ruled out', 'The kill is not linear algebra over the free bits.'),
    ])

if __name__ == '__main__':
    book = lt.load()
    nl = CURRENT['next_loop']
    set_next_loop(book, nl['id'], nl['hypothesis'], nl['plan'], nl['targets'])
    set_strategy(book, CURRENT['sid'], CURRENT['goal'], CURRENT['fields'], CURRENT['steps'])
    lt.save(book)
    print('current strategy:', CURRENT['sid'], 'steps:', len(CURRENT['steps']))
