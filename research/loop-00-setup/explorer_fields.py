"""Setup step 2: the fields the Rule 30 Explorer shows (docs/app.md).

Every status, count and flag a screen shows is a rulebook field, so the app
never computes one. Adds:
  Assertions:    Kind, IntroducedInLoop, StatusGroup, PremiseCount, DependentCount, EvidenceCount, RevisionCount
  Assessments:   Statement, Kind, StatusGroup, SelfUsable, AncestorBlockedCount, IsAtRisk
  Prerequisites: IsSelf, IsBlockingAncestor
  EvidenceLinks: EvidencePath
  Revisions:     Loop
  Loops:         Sequence, StartedAt, FinishedAt, ClaimsAdded, RevisionsMade, FalsificationsMade, ProofsMade
  Dashboards:    ProvedCount, CheckedCount, FalsifiedCount, OpenCount, AtRiskCount, OpenPrizeProblemCount,
                 RunningLoopCount, LegacyLoopCount
Backfills Kind, IntroducedInLoop and Revisions.Loop for the five Effortless loops, and the
legacy loops' hypotheses and results from research_v05/REPORT.md §8 (cycles 0-11) and §10.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

book = lt.load()


def F(name, datatype='string', type='raw', formula=None, related=None, desc='', nullable=True):
    f = {'name': name, 'datatype': datatype, 'type': type, 'nullable': nullable, 'Description': desc}
    if formula:
        f['formula'] = formula
    if related:
        f['RelatedTo'] = related
    return f


def add_fields(table, fields, before=None):
    """Idempotent: fields already in the schema are left as they are."""
    sch = book[table]['schema']
    names = {f['name'] for f in sch}
    fields = [f for f in fields if f['name'] not in names]
    if not fields:
        return
    if before:
        i = [f['name'] for f in sch].index(before)
        sch[i:i] = fields
    else:
        sch.extend(fields)


GROUP = ('=IF(OR({{ReportedStatus}}="DEFINITION",{{ReportedStatus}}="PROVED_HUMAN_READABLE",{{ReportedStatus}}="REDERIVED_KNOWN"),"Proved",'
         'IF({{ReportedStatus}}="FINITE_VERIFIED","Checked",IF({{ReportedStatus}}="FALSIFIED","Falsified",IF({{ReportedStatus}}="SUPERSEDED","Superseded","Open"))))')
LK = lambda field: f'=INDEX(Assertions!{{{{{field}}}}},MATCH({{{{Assertion}}}},Assertions!{{{{AssertionId}}}},0))'

add_fields('Assertions', [
    F('Kind', desc='Role of the claim in the research: Definition, Theorem, Known result, Finite check, Hypothesis, Bridge obligation or Prize problem.', nullable=False),
    F('IntroducedInLoop', type='relationship', related='Loops', desc='The Effortless loop that added this claim; empty for claims carried over from research v05.'),
    F('StatusGroup', type='calculated', formula=GROUP, desc='Proved (definition, proved or rederived known), Checked (finite verification only), Falsified, Superseded or Open.'),
    F('PremiseCount', 'integer', 'aggregation', '=COUNTIFS(Dependencies!{{Conclusion}},{{AssertionId}})', desc='Direct premises this claim depends on.'),
    F('DependentCount', 'integer', 'aggregation', '=COUNTIFS(Dependencies!{{Premise}},{{AssertionId}})', desc='Claims that list this one as a direct premise.'),
    F('EvidenceCount', 'integer', 'aggregation', '=COUNTIFS(EvidenceLinks!{{Assertion}},{{AssertionId}})', desc='Evidence files linked to this claim.'),
    F('RevisionCount', 'integer', 'aggregation', '=COUNTIFS(Revisions!{{Assertion}},{{AssertionId}})', desc='Recorded status changes of this claim.'),
], before='IsUsable')
add_fields('Assertions', [
    F('DescendantCount', 'integer', 'aggregation', '=COUNTIFS(Prerequisites!{{Premise}},{{AssertionId}},Prerequisites!{{IsSelf}},0)', desc='Claims that rest on this one, directly or transitively.'),
])

add_fields('Assessments', [
    F('Statement', type='lookup', formula=LK('Statement'), desc='The claim being assessed, in words.'),
    F('Kind', type='lookup', formula=LK('Kind'), desc='Role of the claim (see Assertions.Kind).'),
    F('StatusGroup', type='lookup', formula=LK('StatusGroup'), desc='Proved, Checked, Falsified, Superseded or Open, from the reported status.'),
    F('SelfUsable', 'integer', 'lookup', LK('IsUsable'), desc='1 when the claim itself is usable as a premise.'),
], before='BlockedCount')
add_fields('Assessments', [
    F('AncestorCount', 'integer', 'aggregation', '=COUNTIFS(Prerequisites!{{ConclusionKey}},{{AssessmentId}},Prerequisites!{{IsSelf}},0)', desc='Claims this one rests on, directly or transitively.'),
    F('AncestorBlockedCount', 'integer', 'calculated', '={{BlockedCount}}-(1-{{SelfUsable}})', desc='Ancestors (not counting the claim itself) that are not usable.'),
    F('IsAtRisk', 'integer', 'calculated', '=IF(AND({{SelfUsable}}=1,{{AncestorBlockedCount}}>0),1,0)', desc='1 when a claim reported as established rests on an ancestor that is open, falsified or superseded. Should always be 0.'),
], before='ProjectKey')

add_fields('Prerequisites', [
    F('IsSelf', 'integer', 'calculated', '=IF({{ConclusionKey}}={{Premise}},1,0)', desc='1 for the row pairing a claim with itself.'),
    F('IsBlockingAncestor', 'integer', 'calculated', '=IF(AND({{Blocked}}=1,{{IsSelf}}=0),1,0)', desc='1 when this ancestor is not usable and so blocks the conclusion.'),
])

add_fields('EvidenceLinks', [
    F('EvidencePath', type='lookup', formula='=INDEX(Evidence!{{Path}},MATCH({{Evidence}},Evidence!{{EvidenceId}},0))', desc='Repo-relative path of the evidence file.'),
])

add_fields('Revisions', [
    F('Loop', type='relationship', related='Loops', desc='The Effortless loop that made this change; empty for v05 revisions recorded before native loops.'),
])

add_fields('Loops', [
    F('Sequence', 'integer', desc='Order of the loop across legacy and native loops (legacy 1-13, then native).', nullable=False),
    F('StartedAt', desc='ISO time the loop started; recorded from the native loops after effortless-5.'),
    F('FinishedAt', desc='ISO time the loop was verified.'),
    F('ClaimsAdded', 'integer', 'aggregation', '=COUNTIFS(Assertions!{{IntroducedInLoop}},{{LoopId}})', desc='Claims this loop added.'),
    F('RevisionsMade', 'integer', 'aggregation', '=COUNTIFS(Revisions!{{Loop}},{{LoopId}})', desc='Status changes this loop recorded.'),
    F('FalsificationsMade', 'integer', 'aggregation', '=COUNTIFS(Revisions!{{Loop}},{{LoopId}},Revisions!{{NewStatus}},"FALSIFIED")', desc='Hypotheses this loop falsified.'),
    F('ProofsMade', 'integer', 'aggregation', '=COUNTIFS(Revisions!{{Loop}},{{LoopId}},Revisions!{{NewStatus}},"PROVED_HUMAN_READABLE")', desc='Claims this loop moved to proved.'),
], before='ProjectKey')

D = lambda status_formula: status_formula
add_fields('Dashboards', [
    F('ProvedCount', 'integer', 'aggregation', '=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{StatusGroup}},"Proved")', desc='Claims proved, rederived or definitional.'),
    F('CheckedCount', 'integer', 'aggregation', '=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{StatusGroup}},"Checked")', desc='Claims verified by finite computation only.'),
    F('FalsifiedCount', 'integer', 'aggregation', '=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{StatusGroup}},"Falsified")', desc='Hypotheses shown false.'),
    F('OpenCount', 'integer', 'aggregation', '=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{StatusGroup}},"Open")', desc='Claims still open.'),
    F('AtRiskCount', 'integer', 'aggregation', '=SUMIFS(Assessments!{{IsAtRisk}},Assessments!{{ProjectKey}},{{DashboardId}})', desc='Established claims resting on something not established. Should be 0.'),
    F('OpenPrizeProblemCount', 'integer', 'aggregation', '=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{Kind}},"Prize problem",Assessments!{{StatusGroup}},"Open")', desc='Prize problems not yet resolved.'),
    F('RunningLoopCount', 'integer', 'aggregation', '=COUNTIFS(Loops!{{ProjectKey}},{{DashboardId}},Loops!{{State}},"RUNNING")', desc='Loops in progress right now.'),
    F('LegacyLoopCount', 'integer', 'aggregation', '=COUNTIFS(Loops!{{ProjectKey}},{{DashboardId}},Loops!{{Kind}},"LEGACY_RESEARCH")', desc='Research cycles from v05, before native builds.'),
])

# ---------- backfill ----------
KIND = {'D0': 'Definition', 'K1': 'Known result'}
for a in lt.rows(book, 'Assertions'):
    i = a['AssertionId']
    if a.get('Kind'):
        continue
    a['Kind'] = KIND.get(i) or ('Theorem' if i.startswith('T') or i in ('CM',) else 'Finite check' if i.startswith('F') else
                                'Hypothesis' if i.startswith('H') else 'Bridge obligation' if i.startswith('B') else
                                'Prize problem' if i.startswith('P') else None)
    assert a['Kind'], i
    a.setdefault('IntroducedInLoop', '')
INTRO = {'effortless-1': ['TF', 'TG', 'TH', 'TI', 'H7'], 'effortless-2': ['F5'], 'effortless-3': ['H14', 'TJ', 'TK', 'TL'],
         'effortless-4': ['H15', 'H16', 'TM', 'TN'], 'effortless-5': ['H9', 'H13', 'F6']}
for loop, ids in INTRO.items():
    for i in ids:
        lt.row(book, 'Assertions', i)['IntroducedInLoop'] = loop   # fixed history; later loops tag their own claims

REV = {'revision-H1': 'legacy-2', 'revision-H2': 'legacy-3', 'revision-H3': 'legacy-4', 'revision-H5': 'legacy-10', 'revision-H6': 'legacy-10',
       'revision-H4-1': 'effortless-1', 'revision-H7-1': 'effortless-2', 'revision-H4-2': 'effortless-2', 'revision-H14-1': 'effortless-3',
       'revision-H7-2': 'effortless-3', 'revision-H4-3': 'effortless-3', 'revision-H15-1': 'effortless-4', 'revision-H16-1': 'effortless-4',
       'revision-H9-1': 'effortless-5', 'revision-H13-1': 'effortless-5'}
for r in lt.rows(book, 'Revisions'):
    if r['RevisionId'] in REV:
        r['Loop'] = REV[r['RevisionId']]

LEGACY = [  # REPORT.md §8 cycles 0-11, then §10 follow-up
    ('Supplied numerical outputs are correct', 'All original scripts rerun; independent indexing. Confirmed; clarify hash and horizon conventions.'),
    ('Every fixed diagonal is balanced', 'Exact full periods. Falsified at k=5; replace by forcing-parity condition.'),
    ('Period doubles at every k>=3', 'Exact period recurrence. Falsified at k=5; retain Q and parity separately.'),
    ('Unbounded diagonal periods force aperiodic center', 'Explicit z-array with cone support and first arrivals. Falsified as an implication; recurrence coupling remains essential.'),
    ('Periodic adjacent columns are compatible with the seed', 'Inverse rule plus finite cone boundary. Impossible; explicit finite mismatch window proved.'),
    ('A constant center tail might survive the two-column obstruction', 'One-tail forces a fixed left neighbor; zero-tail forces monotone right neighbor. Excluded for all onsets; identified as known qualitative result.'),
    ('Local periodic spacetime constraints alone refute candidate center periods', 'Exhaustive pair-word graphs for p<=8. Local periodic solutions exist; seed compatibility cannot be dropped.'),
    ('Input ensemble balance proves time balance', 'Sensitivity theorem and exact truth tables. Ensemble theorem proved; transfer to the fixed orbit remains unsupported.'),
    ('CMCC and ordinary evolution agree', 'SQLite lookups/formulas versus independent rows. All 33,411 cells agree; representation theorem proved.'),
    ('ACID / arbitrary aggregation nesting supply additional invariants', 'Explicit serial-order and unequal-group counterexamples. General implications rejected; narrow their hypotheses.'),
    ('The finite center exclusions persist at a larger horizon', 'Two implementations through t=100,000. Stronger finite certificates; no infinite-time promotion.'),
    ('Period calculations survive a different implementation', 'Whole triangular-state orbit replay. See data/period_verification.json.'),
    ('A periodic center word forces its right neighbor eventually periodic (relaxed graph)', 'All 1,966 primitive words of length <=10. Every nonconstant word admits recurrent branching; the constant-zero argument does not generalize.'),
]
for r in lt.rows(book, 'Loops'):
    lid = r['LoopId']
    kind, n = lid.split('-')
    r.setdefault('Sequence', int(n) if kind == 'legacy' else 13 + int(n))
    r.setdefault('StartedAt', '')
    r.setdefault('FinishedAt', '')
    if kind == 'legacy':
        r['Hypothesis'], r['Summary'] = LEGACY[int(n) - 1]

lt.save(book)
print('explorer fields added')
