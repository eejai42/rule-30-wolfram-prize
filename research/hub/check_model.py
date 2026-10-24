"""Conformance: the built Rule 30 model against the independent oracle (bootstrap/rule30-model/mock-data).

Reads compiled values only. A failed compile-rulebook run can look like a no-op (CLAUDE.md rule 7),
so a blank computed value counts as a failure here.
Usage: python3 research/hub/check_model.py   (after effortless build)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

S = json.loads((lt.ROOT / 'bootstrap/rule30-model/mock-data/scenarios.json').read_text())
book = lt.load()
T = {t: {r[next(iter(r))]: r for r in book[t]['data']} for t in book if isinstance(book[t], dict) and 'data' in book[t]}
RUN, D = 'r30-seed', S['depth']
cid = lambda t, i: f'{RUN}-t{t:03d}p{i:+04d}'
fails = []


def eq(label, got, want):
    if got != want:
        fails.append(f'{label}: got {got!r}, want {want!r}')


for pat, out in S['S01_rule30_table'].items():
    eq(f'S01 rule-30 n{pat}', T['RuleTableEntries'][f'rule-30-n{pat}']['OutputValue'], out)
for r, want in S['S02_polynomial_mismatches'].items():
    eq(f'S02 rule-{r} polynomial mismatches', T['Rules'][f'rule-{r}']['PolynomialMismatchCount'], want)
for r, want in S['S03_equivalence'].items():
    eq(f'S03 rule-{r} mirror', T['Rules'][f'rule-{r}']['MirrorRuleNumber'], want['mirror'])
    eq(f'S03 rule-{r} complement', T['Rules'][f'rule-{r}']['ComplementRuleNumber'], want['complement'])
    eq(f'S03 rule-{r} table number', T['Rules'][f'rule-{r}']['TableNumber'], int(r))
for r, want in S['S04_quiescent'].items():
    eq(f'S04 rule-{r} quiescent', T['Rules'][f'rule-{r}']['IsQuiescent'], int(want))
eq('S04 rule-30 left permutive', T['Rules']['rule-30']['IsLeftPermutive'], 1)
eq('S04 rule-30 right permutive', T['Rules']['rule-30']['IsRightPermutive'], 0)
for t, line in S['S05_first_lines'].items():
    eq(f'S05 line {t}', [T['Cells'][cid(int(t), i)]['Value'] for i in range(-int(t), int(t) + 1)], line)
eq('S06 center column', ''.join(str(T['Cells'][cid(t, 0)]['Value']) for t in range(D + 1)), S['S06_center'])
for pat, n in S['S07_transition_use'].items():
    eq(f'S07 use n{pat}', T['RuleTableEntries'][f'rule-30-n{pat}']['UseCount'], n)
eq('S08 line black counts', [T['TimeSteps'][f'{RUN}-t{t:03d}']['BlackCount'] for t in range(D + 1)], S['S08_line_black_counts'])
for p, lm in S['S09_last_mismatch'].items():
    pt = T['PeriodTests'][f'{RUN}-p+000-p{int(p):02d}']
    eq(f'S09 p{p} last mismatch', pt['LastMismatchTime'], lm)
    eq(f'S09 p{p} longest streak', pt['LongestAgreementStreak'], S['S09_longest_streak'][p])
    eq(f'S09 p{p} bounded holds', pt['BoundedRefutationHolds'], int(S['S09_bounded_p1_holds'][p]))
run = T['Runs'][RUN]
eq('S10 Theorem D violations', run['CenterRunBoundViolations'], S['S10_td_violations'])
eq('S10 longest center run', run['LongestCenterRun'], S['S10_longest_center_run'])
eq('S11 center ones', run['CenterOnes'], S['S11_ones_at_horizon'])
eq('S11 discrepancy', run['CenterDiscrepancy'], S['S11_discrepancy_at_horizon'])
eq('S11 max |discrepancy|', run['MaxAbsCenterDiscrepancy'], S['S11_max_abs_discrepancy'])
for e, t in S['S11_last_excursion'].items():
    eq(f'S11 eps {e} last excursion', T['Tolerances'][f'eps-{e}']['LastExcursionTime'], t)
for color, n in S['S12_center_color_counts'].items():
    eq(f'S12 center {color}', T['ColorCounts'][f'{RUN}-p+000-{color}']['OccurrenceCount'], n)
for n, eff in S['S13_light_cone_effort'].items():
    eq(f'S13 effort n={n}', T['Computations'][f'light-cone-simulation-n{int(n):03d}']['Effort'], eff)
eq('S14 cells', run['CellCount'], S['S14_cells'])
eq('S14 black cells', run['BlackCellCount'], S['S14_black_cells'])
eq('S14 accelerator mismatches', T['Dashboards']['Rule30']['ConformanceMismatchCount'], 0)
eq('light cone exact', run['IsLightConeExact'], 1)
for w, lp in S['S15_least_periods'].items():
    eq(f'S15 least period {w}', T['PeriodicWords'][f'w{w}']['LeastPeriod'], lp)
eq('S16 TX violations', sum(1 - r['IsConsistent'] for r in T['LeftConsistencyChecks'].values()), S['S16_tx_violations'])
eq('S17 Theorem C windows', len(T['MismatchWindows']), S['S17_tc_windows'])
eq('S17 Theorem C failures', sum(1 - r['WindowHolds'] for r in T['MismatchWindows'].values()), S['S17_tc_failures'])
eq('S17 windows with a center witness', sum(r['CenterInWindow'] for r in T['MismatchWindows'].values()), S['S17_tc_center_witnesses'])
for key, want in S['S18_first_mismatch_sample'].items():
    i, p, onset = key.split('-')
    eq(f'S18 first mismatch {key}', T['PeriodicityCandidates'][f'{RUN}-p{int(i):+04d}-{p}-{onset}']['FirstMismatchFrom'], want)
for key, want in S['S19_tail_kill_times'].items():
    eq(f'S19 kill time {key}', T['TailCandidates'][f'tail-{key}']['KillTime'], want)
for a in book['Assertions']['data']:
    if a.get('IsModelContradicted'):
        fails.append(f"ledger: {a['AssertionId']} is reported {a['ReportedStatus']} but the model refutes it")

print('\n'.join(fails) if fails else 'all scenarios match')
print({p: (r['FiniteVerdict'], r['IsFinitelyDecidable']) for p, r in T['Predicates'].items()})
print({a['AssertionId']: (a['ReportedStatus'], a['EffectiveStatus']) for a in book['Assertions']['data'] if a.get('IsModelLinked')})
sys.exit(1 if fails else 0)
