"""Shadle steps 6-10: the Rule 30 domain model, written into the hub.

The ledger (Assertions, Dependencies, Evidence, Loops ...) records claims ABOUT Rule 30. This
script adds Rule 30 itself, the way simpsons-paradox models studies, strata and case cells:
only structure and the problem's inputs are Data; every cell value, count and predicate verdict
is a formula over them. Vocabulary, glossary, narrative and scenarios: bootstrap/rule30-model/.

  The automaton      CellStates, Rules, Neighborhoods, RuleTableEntries
  The evolution      InitialConditions, SeedCells, Runs, TimeSteps, Columns, Cells
  Problem 1          Periods, PeriodTests, PeriodicityCandidates, MismatchWindows, LeftConsistencyChecks,
                     PeriodicWords, WordLetters, WordShifts, WordShiftChecks,
                     TailCandidates, TailCenterTerms, TailCells, TailChecks
  Problem 2          Tolerances, ToleranceChecks, ColorCounts
  Problem 3          MachineModels, Algorithms, Computations
  The logic          Variables, Operators, Terms, Predicates, PredicateInstances
  Outside values     AcceleratorClaims (an optimizer's claimed cell values, checked here)
  Bridge to ledger   Assertions.Predicate and Assertions.EffectiveStatus: the ledger reads the model

Rerunnable: every table it owns is replaced, except the Terms, Predicates and PredicateInstances
rows a model-native loop added (IntroducedInLoop set), which are kept. Python decides no value or
verdict here.
Usage: python3 research/hub/build_model.py && effortless build
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import model_tools as mt
import formal_claims as fc

DEPTH, MAX_PERIOD, TOLERANCES = 64, 24, ((1, 5), (1, 10), (1, 20))   # epsilon as an exact fraction
TAIL_WORD_LENGTHS, TAIL_ONSETS, TAIL_MARGIN = (1, 2, 3), range(1, 11), 12   # B9 tail candidates: words, onsets, horizon past the onset
RUN = 'r30-seed'
OWNED = ('CellStates', 'Rules', 'Neighborhoods', 'RuleTableEntries', 'InitialConditions', 'SeedCells',
         'Runs', 'TimeSteps', 'Columns', 'Cells', 'Periods', 'PeriodTests', 'PeriodicityCandidates', 'MismatchWindows',
         'LeftConsistencyChecks', 'PeriodicWords', 'WordLetters', 'WordShifts', 'WordShiftChecks',
         'TailCandidates', 'TailCenterTerms', 'TailCells', 'TailChecks', 'Diagonals', 'DiagonalPeriodTests', 'DiagonalPeriodChecks', 'DiagonalFacts',
         'Tolerances', 'ToleranceChecks', 'ColorCounts', 'MachineModels', 'Algorithms', 'Computations',
         'Variables', 'Operators', 'Terms', 'Predicates', 'PredicateInstances', 'AcceleratorClaims')
RETIRED = ('Lattice', 'PeriodComparisons', 'Quantifiers')   # tables earlier versions of this script owned
LOOP_OWNED = ('Terms', 'Predicates', 'PredicateInstances')  # rows with IntroducedInLoop survive a rerun


def F(name, dt='string', ty='raw', formula=None, rel=None, desc='', nullable=True):
    f = {'name': name, 'datatype': dt, 'type': ty, 'nullable': nullable, 'Description': desc}
    if formula:
        f['formula'] = formula
    if rel:
        f['RelatedTo'] = rel
    return f


def KEY(name, desc):
    return [F(name, desc=desc, nullable=False), F('Name', ty='calculated', formula=f'={{{{{name}}}}}', desc='Display alias.')]


def LK(name, table, fk, key, field, desc, dt='integer'):
    return F(name, dt, 'lookup', f'=INDEX({table}!{{{{{field}}}}},MATCH({{{{{fk}}}}},{table}!{{{{{key}}}}},0))', desc=desc)


def CALC(name, formula, desc, dt='integer'):
    return F(name, dt, 'calculated', formula, desc=desc)


def AGG(name, formula, desc, dt='integer'):
    return F(name, dt, 'aggregation', formula, desc=desc)


def REL(name, table, desc, nullable=True):
    return F(name, ty='relationship', rel=table, desc=desc, nullable=nullable)


def table(desc, schema, data):
    return {'Description': desc, 'schema': schema, 'data': data}


tid = lambda t: f'{RUN}-t{t:03d}'
colid = lambda i: f'{RUN}-p{i:+04d}'
cid = lambda t, i: f'{RUN}-t{t:03d}p{i:+04d}'
nbid = lambda n: f'n{n:03b}'
entid = lambda rule, n: f'{rule}-{nbid(n)}'

book = lt.load()
kept = {t: [lt._strip_derived(book, t, r) for r in book[t]['data'] if r.get('IntroducedInLoop')] for t in LOOP_OWNED if t in book}
for t in OWNED + RETIRED:
    book.pop(t, None)

# ============================ the automaton ============================
book['CellStates'] = table(
    'The two states a cell can hold, with their colors. Problem 2 asks whether each occurs equally often.',
    KEY('CellStateId', 'The color: white or black.') + [
        F('StateValue', 'integer', desc='The numeric value: white 0, black 1.', nullable=False),
    ],
    [{'CellStateId': 'white', 'StateValue': 0}, {'CellStateId': 'black', 'StateValue': 1}])

RULES = (30, 86, 135, 149)
book['Rules'] = table(
    "Elementary cellular-automaton rules, as data. Rule 30 and the rest of its equivalence class (mirror 86, complement 135, both 149); each rule's table, symmetries and permutivity are computed from its RuleTableEntries.",
    KEY('RuleId', 'rule-<number>.') + [
        F('RuleNumber', 'integer', desc='Wolfram rule number 0..255: the output for neighborhood n is bit n.', nullable=False),
        AGG('TableNumber', '=SUMIFS(RuleTableEntries!{{Weight}},RuleTableEntries!{{Rule}},{{RuleId}})', 'The rule number read back from the 8 computed transitions; equals RuleNumber when the table is consistent.'),
        AGG('BlackOutputCount', '=SUMIFS(RuleTableEntries!{{OutputValue}},RuleTableEntries!{{Rule}},{{RuleId}})', 'How many of the 8 neighborhoods output black.'),
        CALC('IsBalanced', '=IF({{BlackOutputCount}}=4,1,0)', '1 when exactly half the neighborhoods output black (a precondition for density 1/2 heuristics).'),
        AGG('ZeroNeighborhoodOutput', '=SUMIFS(RuleTableEntries!{{OutputValue}},RuleTableEntries!{{Rule}},{{RuleId}},RuleTableEntries!{{NeighborhoodIndex}},0)', 'Output for the all-white neighborhood 000.'),
        CALC('IsQuiescent', '=IF({{ZeroNeighborhoodOutput}}=0,1,0)', '1 when 000 stays white, so a white background stays white and the light cone is exact.'),
        AGG('MirrorRuleNumber', '=SUMIFS(RuleTableEntries!{{MirrorWeight}},RuleTableEntries!{{Rule}},{{RuleId}})', 'The rule with left and right swapped (30 -> 86).'),
        AGG('ComplementRuleNumber', '=SUMIFS(RuleTableEntries!{{ComplementWeight}},RuleTableEntries!{{Rule}},{{RuleId}})', 'The rule with black and white swapped in inputs and output (30 -> 135).'),
        CALC('IsMirrorSymmetric', '=IF({{MirrorRuleNumber}}={{RuleNumber}},1,0)', '1 when the rule is its own mirror.'),
        AGG('PolynomialMismatchCount', '=COUNTIFS(RuleTableEntries!{{Rule}},{{RuleId}},RuleTableEntries!{{MatchesPolynomial}},0)', 'Neighborhoods where the rule differs from Mod[p + q + r + q r, 2].'),
        CALC('IsRule30Polynomial', '=IF({{PolynomialMismatchCount}}=0,1,0)', "1 when the rule is exactly Wolfram's polynomial form of Rule 30."),
        AGG('LeftInsensitiveCount', '=COUNTIFS(RuleTableEntries!{{Rule}},{{RuleId}},RuleTableEntries!{{LeftState}},0,RuleTableEntries!{{IsLeftSensitive}},0)', 'Pairs of neighborhoods differing only in the left cell that give the same output.'),
        CALC('IsLeftPermutive', '=IF({{LeftInsensitiveCount}}=0,1,0)', '1 when flipping the left neighbor always flips the output (Rule 30: new = left XOR f(center, right)).'),
        AGG('RightInsensitiveCount', '=COUNTIFS(RuleTableEntries!{{Rule}},{{RuleId}},RuleTableEntries!{{RightState}},0,RuleTableEntries!{{IsRightSensitive}},0)', 'Pairs of neighborhoods differing only in the right cell that give the same output.'),
        CALC('IsRightPermutive', '=IF({{RightInsensitiveCount}}=0,1,0)', '1 when flipping the right neighbor always flips the output.'),
        AGG('RunCount', '=COUNTIFS(Runs!{{Rule}},{{RuleId}})', 'Runs evolving under this rule.'),
    ],
    [{'RuleId': f'rule-{r}', 'RuleNumber': r} for r in RULES])

book['Neighborhoods'] = table(
    'The 8 neighborhoods a new cell is computed from: the cell and its immediate neighbors (left, center, right). Index = left*4 + center*2 + right selects the bit of the rule number.',
    KEY('NeighborhoodId', 'n<left><center><right>.') + [
        F('LeftState', 'integer', desc='The left neighbor (p).', nullable=False),
        F('CenterState', 'integer', desc='The cell itself (q).', nullable=False),
        F('RightState', 'integer', desc='The right neighbor (r).', nullable=False),
        CALC('NeighborhoodIndex', '=4*{{LeftState}}+2*{{CenterState}}+{{RightState}}', 'left*4 + center*2 + right.'),
        CALC('MirrorIndex', '=4*{{RightState}}+2*{{CenterState}}+{{LeftState}}', 'Index of the left-right reflected neighborhood.'),
        CALC('ComplementIndex', '=7-{{NeighborhoodIndex}}', 'Index of the color-swapped neighborhood.'),
        CALC('PolynomialValue', '=MOD({{LeftState}}+{{CenterState}}+{{RightState}}+{{CenterState}}*{{RightState}},2)', "Wolfram's Rule 30 polynomial Mod[p + q + r + q r, 2] at this neighborhood."),
        AGG('EntryCount', '=COUNTIFS(RuleTableEntries!{{Neighborhood}},{{NeighborhoodId}})', 'Rule tables that list this neighborhood.'),
    ],
    [{'NeighborhoodId': nbid(n), 'LeftState': n >> 2, 'CenterState': (n >> 1) & 1, 'RightState': n & 1} for n in range(7, -1, -1)])

entries = []
for r in RULES:
    for n in range(7, -1, -1):
        entries.append({'RuleTableEntryId': entid(f'rule-{r}', n), 'Rule': f'rule-{r}', 'Neighborhood': nbid(n),
                        'LeftPartner': entid(f'rule-{r}', n | 4) if not n & 4 else None,
                        'RightPartner': entid(f'rule-{r}', n | 1) if not n & 1 else None})
book['RuleTableEntries'] = table(
    "One transition of one rule: neighborhood -> output value. The rule table is computed from the rule number; symmetries and permutivity are read off the table.",
    KEY('RuleTableEntryId', '<rule>-n<pattern>.') + [
        REL('Rule', 'Rules', 'The rule this transition belongs to.', False),
        REL('Neighborhood', 'Neighborhoods', 'The input neighborhood.', False),
        REL('LeftPartner', 'RuleTableEntries', 'Set when the left cell is white: the same rule with the left cell black. (One direction only, so the row graph stays acyclic.)'),
        REL('RightPartner', 'RuleTableEntries', 'Set when the right cell is white: the same rule with the right cell black.'),
        LK('LeftState', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'LeftState', 'The left cell of the neighborhood.'),
        LK('RightState', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'RightState', 'The right cell of the neighborhood.'),
        LK('RuleNumber', 'Rules', 'Rule', 'RuleId', 'RuleNumber', 'The rule number.'),
        LK('NeighborhoodIndex', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'NeighborhoodIndex', 'Which bit of the rule number this is.'),
        LK('MirrorIndex', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'MirrorIndex', 'Index of the mirrored neighborhood.'),
        LK('ComplementIndex', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'ComplementIndex', 'Index of the complemented neighborhood.'),
        LK('PolynomialValue', 'Neighborhoods', 'Neighborhood', 'NeighborhoodId', 'PolynomialValue', 'The Rule 30 polynomial at this neighborhood.'),
        CALC('OutputValue', '=MOD(INT({{RuleNumber}}/POWER(2,{{NeighborhoodIndex}})),2)', 'The new cell state: bit NeighborhoodIndex of the rule number.'),
        CALC('Weight', '={{OutputValue}}*POWER(2,{{NeighborhoodIndex}})', "This transition's contribution to the rule number."),
        CALC('MirrorWeight', '={{OutputValue}}*POWER(2,{{MirrorIndex}})', "This transition's contribution to the mirror rule's number."),
        CALC('ComplementWeight', '=(1-{{OutputValue}})*POWER(2,{{ComplementIndex}})', "This transition's contribution to the complement rule's number."),
        CALC('MatchesPolynomial', '=IF(ABS({{OutputValue}}-{{PolynomialValue}})=0,1,0)', '1 when the output equals Mod[p + q + r + q r, 2].'),
        LK('LeftPartnerOutput', 'RuleTableEntries', 'LeftPartner', 'RuleTableEntryId', 'OutputValue', 'Output with the left cell flipped.'),
        CALC('IsLeftSensitive', '=IF(ABS({{OutputValue}}-{{LeftPartnerOutput}})=1,1,0)', 'On rows with a left partner: 1 when flipping the left cell flips the output.'),
        LK('RightPartnerOutput', 'RuleTableEntries', 'RightPartner', 'RuleTableEntryId', 'OutputValue', 'Output with the right cell flipped.'),
        CALC('IsRightSensitive', '=IF(ABS({{OutputValue}}-{{RightPartnerOutput}})=1,1,0)', 'On rows with a right partner: 1 when flipping the right cell flips the output.'),
        AGG('UseCount', '=COUNTIFS(Cells!{{TransitionKey}},{{RuleTableEntryId}})', 'How many cells of the runs were produced by this transition.'),
    ],
    entries)

# ============================ the evolution ============================
book['InitialConditions'] = table(
    'The states of all cells at time 0: a background color plus the listed seed cells.',
    KEY('InitialConditionId', 'Name of the initial condition.') + [
        REL('Background', 'CellStates', 'The state of every cell not listed as a seed cell.', False),
        LK('BackgroundValue', 'CellStates', 'Background', 'CellStateId', 'StateValue', 'Numeric background state.'),
        AGG('SeedCellCount', '=COUNTIFS(SeedCells!{{InitialCondition}},{{InitialConditionId}})', 'Explicitly listed cells.'),
        AGG('BlackSeedCount', '=SUMIFS(SeedCells!{{StateValue}},SeedCells!{{InitialCondition}},{{InitialConditionId}})', 'Listed cells that are black.'),
        AGG('OriginSeedCount', '=COUNTIFS(SeedCells!{{InitialCondition}},{{InitialConditionId}},SeedCells!{{Position}},0)', 'Listed cells at position 0.'),
        CALC('IsSingleSeed', '=IF(AND({{BackgroundValue}}=0,{{SeedCellCount}}=1,{{BlackSeedCount}}=1,{{OriginSeedCount}}=1),1,0)', '1 for the prize problems\' initial condition: one nonzero cell (black) at position 0 on white.'),
    ],
    [{'InitialConditionId': 'single-seed', 'Background': 'white'}])

book['SeedCells'] = table(
    'A cell of an initial condition that differs from (or is stated beside) the background.',
    KEY('SeedCellId', '<initial condition>-p<position>.') + [
        REL('InitialCondition', 'InitialConditions', 'The initial condition this cell belongs to.', False),
        F('Position', 'integer', desc='Position i of the seed cell.', nullable=False),
        REL('State', 'CellStates', 'Its state.', False),
        LK('StateValue', 'CellStates', 'State', 'CellStateId', 'StateValue', 'Numeric state.'),
    ],
    [{'SeedCellId': 'single-seed-p+000', 'InitialCondition': 'single-seed', 'Position': 0, 'State': 'black'}])

book['Runs'] = table(
    'One evolution: a rule applied to an initial condition up to a depth. The prize problems are about the run of Rule 30 from the single seed.',
    KEY('RunId', 'Name of the run.') + [
        REL('Rule', 'Rules', 'The rule applied at every time step.', False),
        REL('InitialCondition', 'InitialConditions', 'The states at time 0.', False),
        F('Depth', 'integer', desc='The last time step computed: the horizon.', nullable=False),
        LK('RuleNumber', 'Rules', 'Rule', 'RuleId', 'RuleNumber', 'The rule number.'),
        LK('IsQuiescent', 'Rules', 'Rule', 'RuleId', 'IsQuiescent', '1 when 000 -> white.'),
        LK('BackgroundValue', 'InitialConditions', 'InitialCondition', 'InitialConditionId', 'BackgroundValue', 'The background state.'),
        LK('IsSingleSeed', 'InitialConditions', 'InitialCondition', 'InitialConditionId', 'IsSingleSeed', '1 for the single seed.'),
        CALC('IsLightConeExact', '=IF(AND({{IsQuiescent}}=1,{{BackgroundValue}}=0,{{IsSingleSeed}}=1),1,0)', '1 when every cell outside |i| <= t is white, so computing only the cone is exact.'),
        CALC('IsPrizeSetup', '=IF(AND({{IsSingleSeed}}=1,{{RuleNumber}}=30),1,0)', '1 for the prize problems\' setup: Rule 30 from the single seed.'),
        AGG('CellCount', '=COUNTIFS(Cells!{{Run}},{{RunId}})', 'Cells computed (the light cone).'),
        AGG('BlackCellCount', '=SUMIFS(Cells!{{Value}},Cells!{{Run}},{{RunId}})', 'Black cells in the cone.'),
        AGG('LineCount', '=COUNTIFS(TimeSteps!{{Run}},{{RunId}})', 'Time steps computed.'),
        AGG('TotalCellUpdates', '=MAXIFS(TimeSteps!{{CumulativeCellUpdates}},TimeSteps!{{Run}},{{RunId}})', 'Cell updates needed to reach the depth.'),
        AGG('CenterLength', '=COUNTIFS(Cells!{{Run}},{{RunId}},Cells!{{IsCenter}},1)', 'Terms of the center column computed: c(0) .. c(Depth).'),
        AGG('CenterOnes', '=SUMIFS(Cells!{{Value}},Cells!{{Run}},{{RunId}},Cells!{{IsCenter}},1)', 'Black terms in the center column.'),
        CALC('CenterDensity', '={{CenterOnes}}/{{CenterLength}}', 'Share of black in the computed center column.', 'number'),
        CALC('CenterDiscrepancy', '=2*{{CenterOnes}}-{{CenterLength}}', 'Ones minus zeros in the computed center column.'),
        AGG('MaxAbsCenterDiscrepancy', '=MAXIFS(Cells!{{AbsDiscrepancy}},Cells!{{Run}},{{RunId}},Cells!{{IsCenter}},1)', 'Largest |ones - zeros| over all center prefixes.'),
        AGG('LongestCenterRun', '=MAXIFS(Cells!{{RunLength}},Cells!{{Run}},{{RunId}},Cells!{{IsCenter}},1)', 'Longest constant run in the center column.'),
        AGG('CenterRunBoundViolations', '=SUMIFS(Cells!{{ViolatesRunBound}},Cells!{{Run}},{{RunId}})', 'Center cells past the Theorem D bound for their run. Must be 0.'),
    ],
    [{'RunId': RUN, 'Rule': 'rule-30', 'InitialCondition': 'single-seed', 'Depth': DEPTH}])

book['TimeSteps'] = table(
    'One line of a run: time step t. Width, black count and the center term are aggregated from its cells; cell updates accumulate along the time chain.',
    KEY('TimeStepId', '<run>-t<time>.') + [
        REL('Run', 'Runs', 'The run.', False),
        F('Time', 'integer', desc='Time step t.', nullable=False),
        REL('PreviousStep', 'TimeSteps', 'Time step t - 1; empty at t = 0.'),
        LK('Depth', 'Runs', 'Run', 'RunId', 'Depth', "The run's horizon."),
        CALC('Width', '=2*{{Time}}+1', 'Cells in the light cone at this time step.'),
        AGG('CellCount', '=COUNTIFS(Cells!{{TimeStep}},{{TimeStepId}})', 'Cells computed at this time step; equals Width.'),
        AGG('BlackCount', '=SUMIFS(Cells!{{Value}},Cells!{{TimeStep}},{{TimeStepId}})', 'Black cells on this line.'),
        CALC('LineDensity', '={{BlackCount}}/{{CellCount}}', 'Share of black on this line.', 'number'),
        AGG('CenterValue', '=SUMIFS(Cells!{{Value}},Cells!{{TimeStep}},{{TimeStepId}},Cells!{{IsCenter}},1)', 'c(t), the center term.'),
        CALC('CellUpdates', '=IF({{Time}}=0,0,{{Width}})', 'Cells the rule computes to produce this line (none at t = 0).'),
        LK('PreviousCumulativeCellUpdates', 'TimeSteps', 'PreviousStep', 'TimeStepId', 'CumulativeCellUpdates', 'Updates through t - 1.'),
        CALC('CumulativeCellUpdates', '=IF({{Time}}=0,0,{{PreviousCumulativeCellUpdates}}+{{CellUpdates}})', 'Cell updates needed to reach this line: (t + 1)^2 - 1.'),
    ],
    [{'TimeStepId': tid(t), 'Run': RUN, 'Time': t, 'PreviousStep': tid(t - 1) if t else None} for t in range(DEPTH + 1)])

book['Columns'] = table(
    'The cells at one position over time, read as a sequence in t. The center column (position 0) is the sequence of center-cell values all three problems are about.',
    KEY('ColumnId', '<run>-p<position>.') + [
        REL('Run', 'Runs', 'The run.', False),
        F('Position', 'integer', desc='Position i.', nullable=False),
        LK('Depth', 'Runs', 'Run', 'RunId', 'Depth', "The run's horizon."),
        CALC('IsCenter', '=IF({{Position}}=0,1,0)', '1 for the center column.'),
        CALC('FirstTime', '=ABS({{Position}})', 'First time step at which the light cone reaches this column; earlier terms are background.'),
        AGG('CellCount', '=COUNTIFS(Cells!{{Column}},{{ColumnId}})', 'Computed cells in this column.'),
        AGG('BlackCount', '=SUMIFS(Cells!{{Value}},Cells!{{Column}},{{ColumnId}})', 'Black cells in this column.'),
        CALC('Density', '={{BlackCount}}/({{Depth}}+1)', 'Share of black among terms 0 .. Depth (background terms count as white).', 'number'),
    ],
    [{'ColumnId': colid(i), 'Run': RUN, 'Position': i} for i in range(-DEPTH, DEPTH + 1)])

cells = []
for t in range(DEPTH + 1):
    for i in range(-t, t + 1):
        r = {'CellId': cid(t, i), 'Run': RUN, 'TimeStep': tid(t), 'Column': colid(i), 'Time': t, 'Position': i}
        if t == 0:
            r['SeedCell'] = 'single-seed-p+000' if i == 0 else None
        for nm, j in (('LeftParent', i - 1), ('CenterParent', i), ('RightParent', i + 1)):
            r[nm] = cid(t - 1, j) if t > 0 and abs(j) <= t - 1 else None
        cells.append(r)

bit = lambda f: f'IF({{{{{f}}}}}=1,1,0)'
book['Cells'] = table(
    f'x(i, t): one cell of a run, inside the light cone |i| <= t <= {DEPTH}. Its value is the seed at t = 0, otherwise the rule-table output selected by its three parents. Along the column (CenterParent is the previous term) it accumulates the Problem 2 prefix counts and the Problem 1 constant runs.',
    KEY('CellId', '<run>-t<time>p<position>.') + [
        REL('Run', 'Runs', 'The run.', False),
        REL('TimeStep', 'TimeSteps', 'The line (time step) this cell is on.', False),
        REL('Column', 'Columns', 'The column (position) this cell is in.', False),
        REL('SeedCell', 'SeedCells', 'At t = 0: the seed cell listed at this position, if any.'),
        F('Time', 'integer', desc='Time step t.', nullable=False),
        F('Position', 'integer', desc='Position i.', nullable=False),
        REL('LeftParent', 'Cells', 'Cell (t-1, i-1); empty outside the cone.'),
        REL('CenterParent', 'Cells', 'Cell (t-1, i): the previous term of this column; empty outside the cone.'),
        REL('RightParent', 'Cells', 'Cell (t-1, i+1); empty outside the cone.'),
        LK('RuleNumber', 'Runs', 'Run', 'RunId', 'RuleNumber', 'The rule number of the run.'),
        LK('RunRule', 'Runs', 'Run', 'RunId', 'Rule', 'The rule of the run.', 'string'),
        LK('BackgroundValue', 'Runs', 'Run', 'RunId', 'BackgroundValue', 'The background state of the run.'),
        LK('SeedValue', 'SeedCells', 'SeedCell', 'SeedCellId', 'StateValue', 'State of the seed cell here, if listed.'),
        LK('LeftValue', 'Cells', 'LeftParent', 'CellId', 'Value', 'Value of the left parent (blank outside the cone).'),
        LK('CenterValue', 'Cells', 'CenterParent', 'CellId', 'Value', 'Value of the center parent: the previous term of this column.'),
        LK('RightValue', 'Cells', 'RightParent', 'CellId', 'Value', 'Value of the right parent.'),
        CALC('Neighborhood', '=4*' + bit('LeftValue') + '+2*' + bit('CenterValue') + '+' + bit('RightValue'), 'Index of the parents\' neighborhood; a blank parent is white (exact when the run is light-cone exact).'),
        CALC('TransitionKey', '=IF({{Time}}=0,"",CONCAT({{RunRule}},"-n",IF({{LeftValue}}=1,"1","0"),IF({{CenterValue}}=1,"1","0"),IF({{RightValue}}=1,"1","0")))', 'The RuleTableEntry that produced this cell; blank at t = 0.', 'string'),
        CALC('Value', '=IF({{Time}}=0,IF({{SeedValue}}=1,1,{{BackgroundValue}}),MOD(INT({{RuleNumber}}/POWER(2,{{Neighborhood}})),2))', 'The cell: the initial condition at t = 0, otherwise bit Neighborhood of the rule number.'),
        CALC('StateKey', '=IF({{Value}}=1,"black","white")', 'The color of the cell.', 'string'),
        CALC('IsCenter', '=IF({{Position}}=0,1,0)', '1 on the center column c(t) = x(0, t).'),
        CALC('IsColumnStart', '=IF({{Time}}=ABS({{Position}}),1,0)', '1 on the first computed cell of its column; earlier terms are background.'),
        CALC('RightOffset', '={{Time}}-{{Position}}', 'k of the right-edge diagonal y_k(t) = x(t-k, t) this cell lies on.'),
        CALC('LeftOffset', '={{Time}}+{{Position}}', 'k of the left-edge diagonal w_k(t) = x(-t+k, t) this cell lies on.'),
        LK('PriorColumnOnes', 'Cells', 'CenterParent', 'CellId', 'ColumnOnes', 'Black terms of this column through t - 1.'),
        CALC('ColumnOnes', '=IF({{IsColumnStart}}=1,{{Value}},{{PriorColumnOnes}}+{{Value}})', 'Black terms of this column in the prefix 0 .. t (background terms are white).'),
        CALC('PrefixLength', '={{Time}}+1', 'Terms in the prefix 0 .. t.'),
        CALC('ColumnDensity', '={{ColumnOnes}}/{{PrefixLength}}', 'Share of black in the prefix: the running average of Problem 2.', 'number'),
        CALC('Discrepancy', '=2*{{ColumnOnes}}-{{PrefixLength}}', 'Ones minus zeros in the prefix.'),
        CALC('AbsDiscrepancy', '=ABS({{Discrepancy}})', '|ones - zeros| in the prefix.'),
        CALC('DensityDeviation', '=ABS({{ColumnDensity}}-0.5)', 'Distance of the running density from 1/2.', 'number'),
        LK('PriorRunStart', 'Cells', 'CenterParent', 'CellId', 'RunStart', 'Start of the constant run the previous term belongs to.'),
        CALC('RunStart', '=IF({{IsColumnStart}}=1,IF({{Value}}-{{BackgroundValue}}=0,0,{{Time}}),IF({{Value}}-{{CenterValue}}=0,{{PriorRunStart}},{{Time}}))', 'First time step of the constant run this term belongs to. (Equality is written as a difference: rulebook-to-postgres mistypes field = field inside a self-referencing chain, docs/toolchain-gaps.md gap 7.)'),
        CALC('RunLength', '={{Time}}-{{RunStart}}+1', 'Length of the constant run so far.'),
        CALC('RunBound', '=IF({{Value}}=1,2*{{RunStart}}+1,4*{{RunStart}}+5)', 'Theorem D, the center-run bounds: a black run starting at T ends by 2T+1, a white one by 4T+5.'),
        CALC('ViolatesRunBound', '=IF(AND({{IsCenter}}=1,{{Time}}>{{RunBound}}),1,0)', '1 when this center term lies past the Theorem D bound of its run.'),
        CALC('RunBoundHolds', '=1-{{ViolatesRunBound}}', 'Theorem D instance: 1 when this term respects the bound.'),
        AGG('ClaimCount', '=COUNTIFS(AcceleratorClaims!{{Cell}},{{CellId}})', 'Accelerator claims made about this cell.'),
    ],
    cells)

# ============================ Problem 1 ============================
# Two ways a periodic center is refuted. Observation: the real center disagrees with c(t + p) = c(t)
# after the onset (PeriodicityCandidates, Theorem C's MismatchWindows). Structure: a center that ends
# in a periodic tail cannot be left-consistent (TX, B9), shown on the real prefix with each tail
# spliced on (TailCandidates), using no real center value after the onset.
PERIOD_COLUMNS = (0, 1)
ptid = lambda i, p: f'{colid(i)}-p{p:02d}'
pcid = lambda i, p, t: f'{ptid(i, p)}-T{t:03d}'

book['Periods'] = table(
    'Candidate periods p >= 1 for Problem 1 (bounded at %d in the model; unbounded in the problem).' % MAX_PERIOD,
    KEY('PeriodId', 'p<length>.') + [
        F('Length', 'integer', desc='The period p.', nullable=False),
        AGG('TestCount', '=COUNTIFS(PeriodTests!{{Period}},{{PeriodId}})', 'Columns tested against this period.'),
    ],
    [{'PeriodId': f'p{p:02d}', 'Length': p} for p in range(1, MAX_PERIOD + 1)])

book['PeriodTests'] = table(
    "Is this column eventually periodic with this period? A summary of its PeriodicityCandidates: every onset up to the last mismatch is refuted; later onsets survive only because the horizon ends.",
    KEY('PeriodTestId', '<column>-p<period>.') + [
        REL('Column', 'Columns', 'The column tested.', False),
        REL('Period', 'Periods', 'The period p.', False),
        LK('PeriodLength', 'Periods', 'Period', 'PeriodId', 'Length', 'p.'),
        LK('Depth', 'Columns', 'Column', 'ColumnId', 'Depth', 'The horizon.'),
        LK('Position', 'Columns', 'Column', 'ColumnId', 'Position', 'The column position.'),
        CALC('LastOnset', '={{Depth}}-{{PeriodLength}}', 'The last onset T whose comparison c(T) vs c(T + p) is inside the horizon.'),
        AGG('ComparisonCount', '=COUNTIFS(PeriodicityCandidates!{{PeriodTest}},{{PeriodTestId}})', 'Comparisons x(i, t) vs x(i, t + p) inside the horizon.'),
        AGG('MismatchCount', '=COUNTIFS(PeriodicityCandidates!{{PeriodTest}},{{PeriodTestId}},PeriodicityCandidates!{{IsMismatch}},1)', 'Comparisons that differ.'),
        AGG('LastMismatchTime', '=MAXIFS(PeriodicityCandidates!{{Onset}},PeriodicityCandidates!{{PeriodTest}},{{PeriodTestId}},PeriodicityCandidates!{{IsMismatch}},1)', 'The last t with x(i, t + p) != x(i, t). Every onset T <= it is refuted.'),
        AGG('LongestAgreementStreak', '=MAXIFS(PeriodicityCandidates!{{AgreementRunFrom}},PeriodicityCandidates!{{PeriodTest}},{{PeriodTestId}})', 'Longest stretch on which the column looked p-periodic.'),
        AGG('RefutedCandidateCount', '=COUNTIFS(PeriodicityCandidates!{{PeriodTest}},{{PeriodTestId}},PeriodicityCandidates!{{IsRefuted}},1)', 'Onsets with a witness inside the horizon.'),
        CALC('FirstSurvivingOnset', '={{LastMismatchTime}}+1', 'The first onset the horizon cannot refute.'),
        CALC('FinalAgreementLength', '={{Depth}}-({{PeriodLength}}+{{LastMismatchTime}})', 'Matching comparisons after the last mismatch, up to the horizon.'),
        CALC('OnsetBound', '=INT(({{Depth}}-{{PeriodLength}})/2)', 'Bounded form of Problem 1: every onset up to this must be refuted.'),
        CALC('BoundedRefutationHolds', '=IF({{LastMismatchTime}}>={{OnsetBound}},1,0)', '1 when every onset T <= OnsetBound has a mismatch at some t >= T.'),
        AGG('WindowCount', '=COUNTIFS(MismatchWindows!{{CenterTest}},{{PeriodTestId}})', 'Theorem C windows for this period that end inside the horizon.'),
        AGG('WindowFailureCount', '=COUNTIFS(MismatchWindows!{{CenterTest}},{{PeriodTestId}},MismatchWindows!{{WindowHolds}},0)', 'Windows with no mismatch in either column. Theorem C says 0.'),
        AGG('CenterWitnessWindowCount', '=COUNTIFS(MismatchWindows!{{CenterTest}},{{PeriodTestId}},MismatchWindows!{{CenterInWindow}},1)', 'Windows where column 0 alone has the mismatch.'),
        CALC('WindowsHold', '=IF(AND({{WindowCount}}>0,{{WindowFailureCount}}=0),1,0)', '1 when every Theorem C window of this period holds.'),
    ],
    [{'PeriodTestId': ptid(i, p), 'Column': colid(i), 'Period': f'p{p:02d}'} for i in PERIOD_COLUMNS for p in range(1, MAX_PERIOD + 1)])

cands = []
for i in PERIOD_COLUMNS:
    for p in range(1, MAX_PERIOD + 1):
        for t in range(DEPTH + 1 - p):
            cands.append({'PeriodicityCandidateId': pcid(i, p, t), 'PeriodTest': ptid(i, p), 'Onset': t,
                          'EarlierCell': cid(t, i) if abs(i) <= t else None, 'LaterCell': cid(t + p, i),
                          'NextCandidate': pcid(i, p, t + 1) if t < DEPTH - p else None})
book['PeriodicityCandidates'] = table(
    "The hypothesis 'column i is periodic with period p from onset T' (Problem 1 quantifies over these (p, T)). Each row is also the comparison x(i, T) vs x(i, T + p); the chain to T + 1 finds the first mismatch at or after T: the witness that refutes the candidate.",
    KEY('PeriodicityCandidateId', '<period test>-T<onset>.') + [
        REL('PeriodTest', 'PeriodTests', 'The column and period.', False),
        F('Onset', 'integer', desc='The onset T.', nullable=False),
        REL('EarlierCell', 'Cells', 'x(i, T); empty before the light cone reaches the column (white).'),
        REL('LaterCell', 'Cells', 'x(i, T + p).', False),
        REL('NextCandidate', 'PeriodicityCandidates', 'The candidate with onset T + 1; empty at the last onset.'),
        LK('PeriodLength', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'PeriodLength', 'p.'),
        LK('LastOnset', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'LastOnset', 'Last onset inside the horizon.'),
        LK('OnsetBound', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'OnsetBound', 'Largest onset in the bounded form of Problem 1.'),
        LK('EarlierValue', 'Cells', 'EarlierCell', 'CellId', 'Value', 'x(i, T).'),
        LK('LaterValue', 'Cells', 'LaterCell', 'CellId', 'Value', 'x(i, T + p).'),
        CALC('EarlierBit', '=IF({{EarlierValue}}=1,1,0)', 'x(i, T), white outside the cone.'),
        CALC('IsMismatch', '=IF(ABS({{EarlierBit}}-{{LaterValue}})=1,1,0)', '1 when x(i, T + p) != x(i, T).'),
        LK('NextFirstMismatch', 'PeriodicityCandidates', 'NextCandidate', 'PeriodicityCandidateId', 'FirstMismatchFrom', 'Witness of the candidate with onset T + 1.'),
        CALC('FirstMismatchFrom', '=IF({{IsMismatch}}=1,{{Onset}},IF({{Onset}}-{{LastOnset}}=0,{{LastOnset}}+1,{{NextFirstMismatch}}))', 'The witness: the first t >= T with x(i, t + p) != x(i, t); LastOnset + 1 when there is none inside the horizon.'),
        CALC('IsRefuted', '=IF({{FirstMismatchFrom}}<={{LastOnset}},1,0)', '1 when the horizon holds a witness against this candidate.'),
        LK('NextAgreementRun', 'PeriodicityCandidates', 'NextCandidate', 'PeriodicityCandidateId', 'AgreementRunFrom', 'Agreement run of onset T + 1.'),
        CALC('AgreementRunFrom', '=IF({{IsMismatch}}=1,0,IF({{Onset}}-{{LastOnset}}=0,1,{{NextAgreementRun}}+1))', 'Consecutive matching comparisons starting at T.'),
        CALC('InBoundedDomain', '=IF({{Onset}}<={{OnsetBound}},1,0)', '1 when the onset is in the bounded form of Problem 1 (T <= (depth - p)/2).'),
    ],
    cands)

windows = []
for p in range(1, MAX_PERIOD + 1):
    for t in range((DEPTH - 2 * p) // 2 + 1):
        windows.append({'MismatchWindowId': f'tc-p{p:02d}-T{t:03d}', 'Onset': t, 'Period': f'p{p:02d}', 'CenterTest': ptid(0, p),
                        'CenterCandidate': pcid(0, p, t), 'NeighborCandidate': pcid(1, p, t)})
book['MismatchWindows'] = table(
    'Theorem C for one (T, p): some i in {0, 1} and t in [T, 2T + p] have x(i, t) != x(i, t + p). Only windows that end inside the horizon are rows.',
    KEY('MismatchWindowId', 'tc-p<period>-T<onset>.') + [
        F('Onset', 'integer', desc='T.', nullable=False),
        REL('Period', 'Periods', 'p.', False),
        REL('CenterTest', 'PeriodTests', 'The center column test for p (for the roll-up).', False),
        REL('CenterCandidate', 'PeriodicityCandidates', 'Column 0 with period p from onset T.', False),
        REL('NeighborCandidate', 'PeriodicityCandidates', 'Column 1 with period p from onset T.', False),
        LK('PeriodLength', 'Periods', 'Period', 'PeriodId', 'Length', 'p.'),
        LK('CenterWitness', 'PeriodicityCandidates', 'CenterCandidate', 'PeriodicityCandidateId', 'FirstMismatchFrom', 'First mismatch at or after T in column 0.'),
        LK('NeighborWitness', 'PeriodicityCandidates', 'NeighborCandidate', 'PeriodicityCandidateId', 'FirstMismatchFrom', 'First mismatch at or after T in column 1.'),
        CALC('WindowEnd', '=2*{{Onset}}+{{PeriodLength}}', '2T + p.'),
        CALC('CenterInWindow', '=IF({{CenterWitness}}<={{WindowEnd}},1,0)', '1 when column 0 alone has a mismatch in the window (Theorem C does not promise this).'),
        CALC('NeighborInWindow', '=IF({{NeighborWitness}}<={{WindowEnd}},1,0)', '1 when column 1 has a mismatch in the window.'),
        CALC('WindowHolds', '=IF({{CenterInWindow}}+{{NeighborInWindow}}>0,1,0)', 'Theorem C instance: 1 when column 0 or column 1 has a mismatch in [T, 2T + p].'),
    ],
    windows)

book['LeftConsistencyChecks'] = table(
    'TX at one time step of the real center: when c(t) = 1 the rule at column 0 forces c(t + 1) = NOT x(-1, t), so the center is decided by its own past through the left half. After a 0 the left half says nothing.',
    KEY('LeftConsistencyCheckId', '<run>-tx-t<time>.') + [
        F('Time', 'integer', desc='t.', nullable=False),
        REL('Term', 'Cells', 'c(t).', False),
        REL('NextTerm', 'Cells', 'c(t + 1).', False),
        REL('LeftCell', 'Cells', 'x(-1, t); empty at t = 0 (white).'),
        LK('TermValue', 'Cells', 'Term', 'CellId', 'Value', 'c(t).'),
        LK('NextValue', 'Cells', 'NextTerm', 'CellId', 'Value', 'c(t + 1).'),
        LK('LeftValue', 'Cells', 'LeftCell', 'CellId', 'Value', 'x(-1, t).'),
        CALC('LeftBit', '=IF({{LeftValue}}=1,1,0)', 'x(-1, t), white outside the cone.'),
        CALC('IsOneTime', '=IF({{TermValue}}=1,1,0)', '1 when c(t) = 1, the times at which the left half decides the next term.'),
        CALC('ForcedNext', '=1-{{LeftBit}}', 'The value NOT x(-1, t) the left half forces at a one-time.'),
        CALC('IsConsistent', '=IF({{IsOneTime}}=0,1,IF(ABS({{NextValue}}-{{ForcedNext}})=0,1,0))', 'TX instance: 1 unless c(t) = 1 and c(t + 1) != NOT x(-1, t).'),
    ],
    [{'LeftConsistencyCheckId': f'{RUN}-tx-t{t:03d}', 'Time': t, 'Term': cid(t, 0), 'NextTerm': cid(t + 1, 0), 'LeftCell': cid(t, -1) if t >= 1 else None}
     for t in range(DEPTH)])

# --- periodic words: the tails a^ω a periodic center could end in ---
words = [''.join(str((n >> (L - 1 - k)) & 1) for k in range(L)) for L in TAIL_WORD_LENGTHS for n in range(2 ** L)]
wid = lambda w: f'w{w}'
book['PeriodicWords'] = table(
    'A finite word a; the tail a a a ... is what an eventually periodic center would repeat. Its least period, constancy and B9 membership are computed from its letters.',
    KEY('PeriodicWordId', 'w<letters>.') + [
        F('Length', 'integer', desc='Number of letters |a|.', nullable=False),
        AGG('OnesCount', '=SUMIFS(WordLetters!{{LetterBit}},WordLetters!{{PeriodicWord}},{{PeriodicWordId}})', 'Black letters.'),
        CALC('IsNonconstant', '=IF(AND({{OnesCount}}>0,{{OnesCount}}<{{Length}}),1,0)', '1 when the word has both colors.'),
        AGG('LeastPeriod', '=MINIFS(WordShifts!{{Shift}},WordShifts!{{PeriodicWord}},{{PeriodicWordId}},WordShifts!{{IsSymmetry}},1)', 'Smallest d >= 1 with a rotated by d equal to a (d = |a| always qualifies).'),
        CALC('IsPrimitive', '=IF({{LeastPeriod}}-{{Length}}=0,1,0)', '1 when the least period is the full length.'),
        CALC('IsInB9Domain', '=IF(AND({{IsNonconstant}}=1,{{IsPrimitive}}=1),1,0)', '1 for a nonconstant word of least period |a|: the tails B9 excludes.'),
        AGG('TailCandidateCount', '=COUNTIFS(TailCandidates!{{PeriodicWord}},{{PeriodicWordId}})', 'Onsets this tail is spliced on at.'),
        AGG('KilledCandidateCount', '=COUNTIFS(TailCandidates!{{PeriodicWord}},{{PeriodicWordId}},TailCandidates!{{IsKilled}},1)', 'Of those, the ones left-consistency kills inside the horizon.'),
        AGG('KilledExcessMax', '=MAXIFS(TailCandidates!{{KillExcess}},TailCandidates!{{PeriodicWord}},{{PeriodicWordId}},TailCandidates!{{IsKilled}},1)', 'Raw MAXIFS; over an empty set it is blank in compile-rulebook and 0 in Postgres (docs/toolchain-gaps.md gap 12), so read MaxKillExcess.'),
        CALC('MaxKillExcess', '=IF({{KilledCandidateCount}}>0,{{KilledExcessMax}},-2)', 'Longest a killed tail survived past its onset; -2 when no candidate of this word was killed (or none exists).'),
    ],
    [{'PeriodicWordId': wid(w), 'Length': len(w)} for w in words])

book['WordLetters'] = table(
    'One letter a[k] of a word.',
    KEY('WordLetterId', '<word>-k<index>.') + [
        REL('PeriodicWord', 'PeriodicWords', 'The word.', False),
        F('LetterIndex', 'integer', desc='k, from 0.', nullable=False),
        F('LetterBit', 'integer', desc='a[k].', nullable=False),
    ],
    [{'WordLetterId': f'{wid(w)}-k{k}', 'PeriodicWord': wid(w), 'LetterIndex': k, 'LetterBit': int(b)} for w in words for k, b in enumerate(w)])

book['WordShifts'] = table(
    'A rotation of a word by d positions; a symmetry when every letter matches its rotated partner.',
    KEY('WordShiftId', '<word>-d<shift>.') + [
        REL('PeriodicWord', 'PeriodicWords', 'The word.', False),
        F('Shift', 'integer', desc='d, 1 .. |a|.', nullable=False),
        AGG('MismatchCount', '=COUNTIFS(WordShiftChecks!{{WordShift}},{{WordShiftId}},WordShiftChecks!{{IsMismatch}},1)', 'Letters with a[k] != a[(k + d) mod |a|].'),
        CALC('IsSymmetry', '=IF({{MismatchCount}}=0,1,0)', '1 when rotating by d leaves the word unchanged.'),
    ],
    [{'WordShiftId': f'{wid(w)}-d{d}', 'PeriodicWord': wid(w), 'Shift': d} for w in words for d in range(1, len(w) + 1)])

book['WordShiftChecks'] = table(
    'One letter against its rotated partner: a[k] vs a[(k + d) mod |a|].',
    KEY('WordShiftCheckId', '<shift>-k<index>.') + [
        REL('WordShift', 'WordShifts', 'The rotation.', False),
        REL('Letter', 'WordLetters', 'a[k].', False),
        REL('PartnerLetter', 'WordLetters', 'a[(k + d) mod |a|].', False),
        LK('LetterBit', 'WordLetters', 'Letter', 'WordLetterId', 'LetterBit', 'a[k].'),
        LK('PartnerBit', 'WordLetters', 'PartnerLetter', 'WordLetterId', 'LetterBit', 'a[(k + d) mod |a|].'),
        CALC('IsMismatch', '=IF(ABS({{LetterBit}}-{{PartnerBit}})=1,1,0)', '1 when the two letters differ.'),
    ],
    [{'WordShiftCheckId': f'{wid(w)}-d{d}-k{k}', 'WordShift': f'{wid(w)}-d{d}', 'Letter': f'{wid(w)}-k{k}', 'PartnerLetter': f'{wid(w)}-k{(k + d) % len(w)}'}
     for w in words for d in range(1, len(w) + 1) for k in range(len(w))])

# --- tails spliced on the real prefix: B9's instances ---
tcid = lambda w, T: f'tail-{w}-T{T:02d}'
tails, tterms, tcells, tchecks = [], [], [], []
# One candidate per distinct tail: a word and its repetitions (00, 000) give the same sequence, so only
# the shortest spelling is spliced on. The model still computes every word's least period itself.
tail_words = [w for w in words if all(w != w[d:] + w[:d] for d in range(1, len(w)))]
for w in tail_words:
    for T in TAIL_ONSETS:
        k, H = tcid(w, T), T + TAIL_MARGIN
        tails.append({'TailCandidateId': k, 'Run': RUN, 'PeriodicWord': wid(w), 'Onset': T, 'Horizon': H})
        for t in range(T - 1, H + 2):
            tterms.append({'TailCenterTermId': f'{k}-c{t:02d}', 'TailCandidate': k, 'Time': t,
                           'RealCell': cid(t, 0) if t < T else None, 'Letter': f'{wid(w)}-k{(t - T) % len(w)}' if t >= T else None})
        width = lambda s: min(s, H - s + 1)
        for s in range(T, H + 1):
            for i in range(-width(s), 0):
                r = {'TailCellId': f'{k}-{s}{i}', 'TailCandidate': k, 'Time': s, 'Position': i,
                     'RealCell': cid(s, i) if s == T else None, 'LeftParent': None, 'CenterParent': None, 'RightParent': None, 'CenterTerm': None}
                if s > T:
                    inb = lambda j: -width(s - 1) <= j <= -1
                    r['LeftParent'] = f'{k}-{s - 1}{i - 1}' if inb(i - 1) else None
                    r['CenterParent'] = f'{k}-{s - 1}{i}' if inb(i) else None
                    if i == -1:
                        r['CenterTerm'] = f'{k}-c{s - 1:02d}'
                    else:
                        r['RightParent'] = f'{k}-{s - 1}{i + 1}'
                tcells.append(r)
        for t in range(T - 1, H + 1):
            tchecks.append({'TailCheckId': f'{k}-x{t:02d}', 'TailCandidate': k, 'Time': t, 'Term': f'{k}-c{t:02d}', 'NextTerm': f'{k}-c{t + 1:02d}',
                            'RealLeftCell': cid(t, -1) if t < T and t >= 1 else None, 'TailLeftCell': f'{k}-{t}-1' if t >= T else None,
                            'NextCheck': f'{k}-x{t + 1:02d}' if t < H else None})

book['TailCandidates'] = table(
    "The real center up to onset T, then the tail a a a ... from T: the center an eventual a-periodicity from T would have. TX says the real center is left-consistent; B9 says no left-consistent sequence ends in a nonconstant periodic tail, so every candidate must fail a one-time check. The kill uses only the real prefix and the rule, never the real center after T.",
    KEY('TailCandidateId', 'tail-<word>-T<onset>.') + [
        REL('Run', 'Runs', 'The run whose prefix is used.', False),
        REL('PeriodicWord', 'PeriodicWords', 'The tail word a.', False),
        F('Onset', 'integer', desc='T: the first time step of the tail.', nullable=False),
        F('Horizon', 'integer', desc='The last time step checked (onset + %d).' % TAIL_MARGIN, nullable=False),
        LK('RuleNumber', 'Runs', 'Run', 'RunId', 'RuleNumber', 'The rule.'),
        LK('WordLength', 'PeriodicWords', 'PeriodicWord', 'PeriodicWordId', 'Length', '|a|.'),
        LK('IsInB9Domain', 'PeriodicWords', 'PeriodicWord', 'PeriodicWordId', 'IsInB9Domain', '1 for a nonconstant primitive tail.'),
        AGG('KillTime', '=MINIFS(TailChecks!{{FirstViolationFrom}},TailChecks!{{TailCandidate}},{{TailCandidateId}})', 'The witness: the first one-time t >= T - 1 at which c(t + 1) != NOT x(-1, t); Horizon + 1 when none.'),
        CALC('IsKilled', '=IF({{KillTime}}<={{Horizon}},1,0)', '1 when left-consistency kills the tail inside the horizon.'),
        CALC('KillExcess', '={{KillTime}}-{{Onset}}', 'How long past the onset the tail survived (-1: killed by the first tail bit).'),
        AGG('OneTimeCount', '=SUMIFS(TailChecks!{{IsOneTime}},TailChecks!{{TailCandidate}},{{TailCandidateId}})', 'One-times checked.'),
        AGG('CellCount', '=COUNTIFS(TailCells!{{TailCandidate}},{{TailCandidateId}})', 'Left-half cells computed for this tail.'),
    ],
    tails)

book['TailCenterTerms'] = table(
    "c'(t) of a tail candidate: the real center before the onset, the tail word's letter a[(t - T) mod |a|] from it.",
    KEY('TailCenterTermId', '<candidate>-c<time>.') + [
        REL('TailCandidate', 'TailCandidates', 'The candidate.', False),
        F('Time', 'integer', desc='t.', nullable=False),
        REL('RealCell', 'Cells', 'Before the onset: c(t).'),
        REL('Letter', 'WordLetters', 'From the onset: the letter a[(t - T) mod |a|].'),
        LK('Onset', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'Onset', 'T.'),
        LK('RealValue', 'Cells', 'RealCell', 'CellId', 'Value', 'c(t).'),
        LK('LetterValue', 'WordLetters', 'Letter', 'WordLetterId', 'LetterBit', 'a[(t - T) mod |a|].'),
        CALC('Value', '=IF({{Time}}<{{Onset}},{{RealValue}},{{LetterValue}})', "c'(t)."),
    ],
    tterms)

book['TailCells'] = table(
    "x'(i, t), i <= -1, of a tail candidate: the left half driven by c'. At the onset it equals the real left half (TX: the left half depends only on the center's past); after it, Rule 30 with c' as the right boundary. Only cells that can reach x'(-1, t) by the horizon are rows.",
    KEY('TailCellId', '<candidate>-<time><position>.') + [
        REL('TailCandidate', 'TailCandidates', 'The candidate.', False),
        F('Time', 'integer', desc='t.', nullable=False),
        F('Position', 'integer', desc='i <= -1.', nullable=False),
        REL('RealCell', 'Cells', 'At the onset: the real cell x(i, T).'),
        REL('LeftParent', 'TailCells', "x'(i - 1, t - 1); empty outside the cone (white)."),
        REL('CenterParent', 'TailCells', "x'(i, t - 1)."),
        REL('RightParent', 'TailCells', "x'(i + 1, t - 1), for i <= -2."),
        REL('CenterTerm', 'TailCenterTerms', "c'(t - 1), the right parent of column -1."),
        LK('Onset', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'Onset', 'T.'),
        LK('RuleNumber', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'RuleNumber', 'The rule.'),
        LK('RealValue', 'Cells', 'RealCell', 'CellId', 'Value', 'x(i, T).'),
        LK('LeftValue', 'TailCells', 'LeftParent', 'TailCellId', 'Value', 'Left parent.'),
        LK('CenterValue', 'TailCells', 'CenterParent', 'TailCellId', 'Value', 'Center parent.'),
        LK('RightValue', 'TailCells', 'RightParent', 'TailCellId', 'Value', 'Right parent (i <= -2).'),
        LK('CenterTermValue', 'TailCenterTerms', 'CenterTerm', 'TailCenterTermId', 'Value', "c'(t - 1) (i = -1)."),
        CALC('Neighborhood', '=4*IF({{LeftValue}}=1,1,0)+2*IF({{CenterValue}}=1,1,0)+IF({{Position}}=-1,IF({{CenterTermValue}}=1,1,0),IF({{RightValue}}=1,1,0))', "Index of the parents' neighborhood; the right parent of column -1 is the candidate center."),
        CALC('Value', '=IF({{Time}}-{{Onset}}=0,{{RealValue}},MOD(INT({{RuleNumber}}/POWER(2,{{Neighborhood}})),2))', "x'(i, t)."),
    ],
    tcells)

book['TailChecks'] = table(
    "The one-time check at t of a tail candidate: when c'(t) = 1, left-consistency requires c'(t + 1) = NOT x'(-1, t). The chain to t + 1 finds the first violation: the kill.",
    KEY('TailCheckId', '<candidate>-x<time>.') + [
        REL('TailCandidate', 'TailCandidates', 'The candidate.', False),
        F('Time', 'integer', desc='t.', nullable=False),
        REL('Term', 'TailCenterTerms', "c'(t).", False),
        REL('NextTerm', 'TailCenterTerms', "c'(t + 1).", False),
        REL('RealLeftCell', 'Cells', 'Before the onset: x(-1, t) (empty at t = 0, white).'),
        REL('TailLeftCell', 'TailCells', "From the onset: x'(-1, t)."),
        REL('NextCheck', 'TailChecks', 'The check at t + 1; empty at the horizon.'),
        LK('Onset', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'Onset', 'T.'),
        LK('Horizon', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'Horizon', 'Last time checked.'),
        LK('TermValue', 'TailCenterTerms', 'Term', 'TailCenterTermId', 'Value', "c'(t)."),
        LK('NextValue', 'TailCenterTerms', 'NextTerm', 'TailCenterTermId', 'Value', "c'(t + 1)."),
        LK('RealLeftValue', 'Cells', 'RealLeftCell', 'CellId', 'Value', 'x(-1, t).'),
        LK('TailLeftValue', 'TailCells', 'TailLeftCell', 'TailCellId', 'Value', "x'(-1, t)."),
        CALC('LeftBit', '=IF({{Time}}<{{Onset}},IF({{RealLeftValue}}=1,1,0),IF({{TailLeftValue}}=1,1,0))', "x'(-1, t)."),
        CALC('IsOneTime', '=IF({{TermValue}}=1,1,0)', "1 when c'(t) = 1."),
        CALC('IsViolation', '=IF(AND({{IsOneTime}}=1,ABS({{NextValue}}+{{LeftBit}}-1)=1),1,0)', "1 when c'(t) = 1 and c'(t + 1) != NOT x'(-1, t): the tail is not left-consistent."),
        LK('NextFirstViolation', 'TailChecks', 'NextCheck', 'TailCheckId', 'FirstViolationFrom', 'First violation from t + 1.'),
        CALC('FirstViolationFrom', '=IF({{IsViolation}}=1,{{Time}},IF({{Time}}-{{Horizon}}=0,{{Horizon}}+1,{{NextFirstViolation}}))', 'First violating time >= t; Horizon + 1 when none.'),
    ],
    tchecks)

# --- diagonals: y_k(t) = x(t - k, t) along the right edge, w_k(t) = x(k - t, t) along the left ---
# Loops 1-12 studied their periods. Candidate periods are the powers of two up to min(2^k, cap): the
# model certifies the least dyadic period (T004 says the least period divides 2^k, so for right
# diagonals it is the least period; the left side is only searched among dyadic periods).
RIGHT_K, LEFT_K, RIGHT_CAP, LEFT_CAP = range(0, 9), range(0, 11), 32, 8
did = lambda side, k: f'{side}-k{k:02d}'
dcell = lambda side, k, t: (cid(t, t - k) if abs(t - k) <= t else None) if side == 'right' else (cid(t, k - t) if abs(k - t) <= t else None)
diags, dtests, dchecks = [], [], []
for side, ks, cap in (('right', RIGHT_K, RIGHT_CAP), ('left', LEFT_K, LEFT_CAP)):
    for k in ks:
        diags.append({'DiagonalId': did(side, k), 'Side': side, 'Offset': k, 'PreviousDiagonal': did(side, k - 1) if k else None,
                      'OppositeDiagonal': did('right', k) if side == 'left' and k in RIGHT_K else None})
        d = 1
        while d <= min(2 ** k, cap):
            tid_ = f'{did(side, k)}-d{d:02d}'
            dtests.append({'DiagonalPeriodTestId': tid_, 'Diagonal': did(side, k), 'Period': d, 'HalfCell': dcell(side, k, d // 2) if d > 1 else None})
            for t in range(DEPTH + 1 - d):
                dchecks.append({'DiagonalPeriodCheckId': f'{tid_}-t{t:02d}', 'DiagonalPeriodTest': tid_, 'Time': t,
                                'EarlierCell': dcell(side, k, t), 'LaterCell': dcell(side, k, t + d)})
            d *= 2

book['Diagonals'] = table(
    'A diagonal of the cone read as a sequence in t: right side y_k(t) = x(t - k, t), left side w_k(t) = x(k - t, t) (k = 0 is the edge). Before the cone reaches it a diagonal is white.',
    KEY('DiagonalId', '<side>-k<offset>.') + [
        F('Side', desc='right (y_k) or left (w_k).'),
        F('Offset', 'integer', desc='k.', nullable=False),
        REL('PreviousDiagonal', 'Diagonals', 'The diagonal k - 1 on the same side; empty at k = 0.'),
        REL('OppositeDiagonal', 'Diagonals', 'For a left diagonal w_k: the right diagonal y_k (one direction only).'),
        F('Depth', 'integer', desc='The horizon (the run depth).', nullable=False),
        AGG('RightOnes', '=SUMIFS(Cells!{{Value}},Cells!{{RightOffset}},{{Offset}})', 'Black cells with t - i = k.'),
        AGG('LeftOnes', '=SUMIFS(Cells!{{Value}},Cells!{{LeftOffset}},{{Offset}})', 'Black cells with t + i = k.'),
        AGG('RightCells', '=COUNTIFS(Cells!{{RightOffset}},{{Offset}})', 'Cells with t - i = k.'),
        AGG('LeftCells', '=COUNTIFS(Cells!{{LeftOffset}},{{Offset}})', 'Cells with t + i = k.'),
        AGG('RightFirstOneRaw', '=MINIFS(Cells!{{Time}},Cells!{{RightOffset}},{{Offset}},Cells!{{Value}},1)', 'Raw MINIFS (gap 12); read FirstOneTime.'),
        AGG('LeftFirstOneRaw', '=MINIFS(Cells!{{Time}},Cells!{{LeftOffset}},{{Offset}},Cells!{{Value}},1)', 'Raw MINIFS (gap 12); read FirstOneTime.'),
        CALC('OnesCount', '=IF({{Side}}="right",{{RightOnes}},{{LeftOnes}})', 'Black cells on the diagonal inside the horizon.'),
        CALC('CellCount', '=IF({{Side}}="right",{{RightCells}},{{LeftCells}})', 'Cells of the diagonal inside the cone and the horizon.'),
        CALC('FirstOneTime', '=IF({{OnesCount}}=0,-1,IF({{Side}}="right",{{RightFirstOneRaw}},{{LeftFirstOneRaw}}))', 'First t with a black cell on the diagonal; -1 when none inside the horizon.'),
        AGG('PureCount', '=COUNTIFS(DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsPurePeriod}},1)', 'Dyadic periods the whole observed diagonal has.'),
        AGG('LeastPureRaw', '=MINIFS(DiagonalPeriodTests!{{Period}},DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsPurePeriod}},1)', 'Raw MINIFS (gap 12); read LeastPeriod.'),
        CALC('LeastPeriod', '=IF({{PureCount}}>0,{{LeastPureRaw}},-1)', 'P_k: the least dyadic period of the diagonal from t = 0; -1 when none is certified inside the horizon.'),
        AGG('EventualCount', '=COUNTIFS(DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsEventualPeriod}},1)', 'Dyadic periods the diagonal eventually has.'),
        AGG('LeastEventualRaw', '=MINIFS(DiagonalPeriodTests!{{Period}},DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsEventualPeriod}},1)', 'Raw MINIFS (gap 12); read EventualPeriod.'),
        CALC('EventualPeriod', '=IF({{EventualCount}}>0,{{LeastEventualRaw}},-1)', 'Least dyadic eventual period; -1 when none is certified inside the horizon.'),
        AGG('EventualOnset', '=SUMIFS(DiagonalPeriodTests!{{EventualOnset}},DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsLeastEventual}},1)', 'Onset of the least eventual period.'),
        AGG('OnesPerPeriod', '=SUMIFS(DiagonalPeriodTests!{{OnesInFirstPeriod}},DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsLeast}},1)', 'Black cells in one least period y_k(0 .. P_k - 1).'),
        AGG('HalfPeriodValue', '=SUMIFS(DiagonalPeriodTests!{{HalfValue}},DiagonalPeriodTests!{{Diagonal}},{{DiagonalId}},DiagonalPeriodTests!{{IsLeast}},1)', 'y_k(P_k / 2).'),
        LK('PreviousLeastPeriod', 'Diagonals', 'PreviousDiagonal', 'DiagonalId', 'LeastPeriod', 'P_{k-1}.'),
        CALC('Doubles', '=IF(AND({{Offset}}>=1,{{LeastPeriod}}-2*{{PreviousLeastPeriod}}=0),1,0)', 'eps_k: 1 when P_k = 2 P_{k-1}.'),
        LK('PreviousDoubles', 'Diagonals', 'PreviousDiagonal', 'DiagonalId', 'Doubles', 'eps_{k-1}.'),
        LK('PreviousPreviousDoubles', 'Diagonals', 'PreviousDiagonal', 'DiagonalId', 'PreviousDoubles', 'eps_{k-2}.'),
        LK('PreviousOnesPerPeriod', 'Diagonals', 'PreviousDiagonal', 'DiagonalId', 'OnesPerPeriod', 'Ones per period of y_{k-1}.'),
        LK('PreviousPreviousOnesPerPeriod', 'Diagonals', 'PreviousDiagonal', 'DiagonalId', 'PreviousOnesPerPeriod', 'Ones per period of y_{k-2}.'),
        LK('OppositeLeastPeriod', 'Diagonals', 'OppositeDiagonal', 'DiagonalId', 'LeastPeriod', 'P_k of the right diagonal with the same offset.'),
    ],
    [dict(r, Depth=DEPTH) for r in diags])

book['DiagonalPeriodTests'] = table(
    'Is the dyadic d a period of the diagonal, from t = 0 (pure) or from some onset (eventual)?',
    KEY('DiagonalPeriodTestId', '<diagonal>-d<period>.') + [
        REL('Diagonal', 'Diagonals', 'The diagonal.', False),
        F('Period', 'integer', desc='d, a power of two.', nullable=False),
        REL('HalfCell', 'Cells', 'The cell of the diagonal at t = d / 2 (empty before the cone: white).'),
        LK('Depth', 'Diagonals', 'Diagonal', 'DiagonalId', 'Depth', 'The horizon.'),
        LK('DiagonalLeastPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'LeastPeriod', 'P_k.'),
        LK('DiagonalEventualPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'EventualPeriod', 'Least eventual period.'),
        LK('HalfCellValue', 'Cells', 'HalfCell', 'CellId', 'Value', 'The diagonal at t = d / 2.'),
        CALC('HalfValue', '=IF({{HalfCellValue}}=1,1,0)', 'The diagonal at d / 2, white before the cone.'),
        AGG('ComparisonCount', '=COUNTIFS(DiagonalPeriodChecks!{{DiagonalPeriodTest}},{{DiagonalPeriodTestId}})', 'Comparisons inside the horizon.'),
        AGG('MismatchCount', '=COUNTIFS(DiagonalPeriodChecks!{{DiagonalPeriodTest}},{{DiagonalPeriodTestId}},DiagonalPeriodChecks!{{IsMismatch}},1)', 'Comparisons that differ.'),
        AGG('LastMismatchRaw', '=MAXIFS(DiagonalPeriodChecks!{{Time}},DiagonalPeriodChecks!{{DiagonalPeriodTest}},{{DiagonalPeriodTestId}},DiagonalPeriodChecks!{{IsMismatch}},1)', 'Raw MAXIFS (gap 12); read EventualOnset.'),
        AGG('OnesInFirstPeriod', '=SUMIFS(DiagonalPeriodChecks!{{EarlierBit}},DiagonalPeriodChecks!{{DiagonalPeriodTest}},{{DiagonalPeriodTestId}},DiagonalPeriodChecks!{{IsInFirstPeriod}},1)', 'Black cells among t = 0 .. d - 1.'),
        CALC('IsPurePeriod', '=IF(AND({{MismatchCount}}=0,{{ComparisonCount}}>={{Period}}),1,0)', '1 when every comparison matches and every residue mod d is compared at least once.'),
        CALC('EventualOnset', '=IF({{MismatchCount}}=0,0,{{LastMismatchRaw}}+1)', 'The first t from which every comparison matches.'),
        CALC('IsEventualPeriod', '=IF(AND({{EventualOnset}}*2<={{Depth}},{{ComparisonCount}}-{{EventualOnset}}>=2*{{Period}}),1,0)', '1 when d is a period from the onset on, with the onset in the first half of the horizon and at least 2d matching comparisons after it.'),
        CALC('IsLeast', '=IF({{Period}}-{{DiagonalLeastPeriod}}=0,1,0)', '1 for the least pure period.'),
        CALC('IsLeastEventual', '=IF({{Period}}-{{DiagonalEventualPeriod}}=0,1,0)', '1 for the least eventual period.'),
    ],
    dtests)

book['DiagonalPeriodChecks'] = table(
    'One comparison of a diagonal period test: the diagonal at t against t + d.',
    KEY('DiagonalPeriodCheckId', '<test>-t<time>.') + [
        REL('DiagonalPeriodTest', 'DiagonalPeriodTests', 'The test.', False),
        F('Time', 'integer', desc='t.', nullable=False),
        REL('EarlierCell', 'Cells', 'The diagonal at t (empty before the cone: white).'),
        REL('LaterCell', 'Cells', 'The diagonal at t + d.'),
        LK('Period', 'DiagonalPeriodTests', 'DiagonalPeriodTest', 'DiagonalPeriodTestId', 'Period', 'd.'),
        LK('EarlierValue', 'Cells', 'EarlierCell', 'CellId', 'Value', 'At t.'),
        LK('LaterValue', 'Cells', 'LaterCell', 'CellId', 'Value', 'At t + d.'),
        CALC('EarlierBit', '=IF({{EarlierValue}}=1,1,0)', 'At t, white before the cone.'),
        CALC('LaterBit', '=IF({{LaterValue}}=1,1,0)', 'At t + d, white before the cone.'),
        CALC('IsMismatch', '=IF(ABS({{EarlierBit}}-{{LaterBit}})=1,1,0)', '1 when the diagonal differs at t and t + d.'),
        CALC('IsInFirstPeriod', '=IF({{Time}}<{{Period}},1,0)', '1 for t < d.'),
    ],
    dchecks)

FACTS = {  # fact -> (diagonals it is stated for, what Holds reads)
    'all-ones': ([('right', 0), ('left', 0)], 'every cone cell on the edge is black'),
    'first-one-at-half': ([('right', k) for k in RIGHT_K], 'first black cell at t = ceil(k/2), and P_k exceeds that time'),
    'balanced': ([('right', k) for k in RIGHT_K if k >= 1], 'exactly half the cells of one least period are black'),
    'doubles': ([('right', k) for k in RIGHT_K if k >= 3], 'P_k = 2 P_{k-1}'),
    'nondecreasing': ([('right', k) for k in RIGHT_K if k >= 1], 'P_k >= P_{k-1}'),
    'repeat-or-double': ([('right', k) for k in RIGHT_K if k >= 3], 'P_k is P_{k-1} or 2 P_{k-1}'),
    'no-triple-double': ([('right', k) for k in RIGHT_K if k >= 5], 'not (eps_k = eps_{k-1} = eps_{k-2} = 1)'),
    'half-period-one': ([('right', k) for k in RIGHT_K if k >= 1], 'y_k(P_k / 2) = 1'),
    'eventually-dyadic': ([('left', k) for k in LEFT_K], 'w_k has a dyadic eventual period <= min(2^k, %d) inside the horizon' % LEFT_CAP),
    'parity-after-doubling': ([('right', k) for k in RIGHT_K if k >= 4], 'if eps_{k-1} = 1 then eps_k = ones of y_{k-2} per period mod 2'),
    'parity-always': ([('right', k) for k in RIGHT_K if k >= 4], 'eps_k = ones of y_{k-2} per period mod 2'),
    'left-half-speed': ([('left', k) for k in LEFT_K if 1 <= k <= max(RIGHT_K)], 'Pw_k^2 <= P_k (log2 Pw_k <= log2 P_k / 2)'),
}
book['DiagonalFacts'] = table(
    'One fact a predicate states about one diagonal, decided from the diagonal\'s computed periods and cells.',
    KEY('DiagonalFactId', '<fact>-<diagonal>.') + [
        F('Fact', desc='Which fact: ' + '; '.join(f'{k}: {v[1]}' for k, v in FACTS.items()) + '.'),
        REL('Diagonal', 'Diagonals', 'The diagonal.', False),
        LK('Offset', 'Diagonals', 'Diagonal', 'DiagonalId', 'Offset', 'k.'),
        LK('OnesCount', 'Diagonals', 'Diagonal', 'DiagonalId', 'OnesCount', 'Black cells observed.'),
        LK('CellCount', 'Diagonals', 'Diagonal', 'DiagonalId', 'CellCount', 'Cells observed.'),
        LK('FirstOneTime', 'Diagonals', 'Diagonal', 'DiagonalId', 'FirstOneTime', 'First black cell.'),
        LK('LeastPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'LeastPeriod', 'P_k.'),
        LK('PreviousLeastPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'PreviousLeastPeriod', 'P_{k-1}.'),
        LK('OnesPerPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'OnesPerPeriod', 'Black cells per least period.'),
        LK('HalfPeriodValue', 'Diagonals', 'Diagonal', 'DiagonalId', 'HalfPeriodValue', 'y_k(P_k / 2).'),
        LK('Doubles', 'Diagonals', 'Diagonal', 'DiagonalId', 'Doubles', 'eps_k.'),
        LK('PreviousDoubles', 'Diagonals', 'Diagonal', 'DiagonalId', 'PreviousDoubles', 'eps_{k-1}.'),
        LK('PreviousPreviousDoubles', 'Diagonals', 'Diagonal', 'DiagonalId', 'PreviousPreviousDoubles', 'eps_{k-2}.'),
        LK('EventualPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'EventualPeriod', 'Least dyadic eventual period.'),
        LK('PreviousPreviousOnesPerPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'PreviousPreviousOnesPerPeriod', 'Ones per period of y_{k-2}.'),
        LK('OppositeLeastPeriod', 'Diagonals', 'Diagonal', 'DiagonalId', 'OppositeLeastPeriod', 'P_k of the right diagonal with the same offset.'),
        CALC('Holds', '=IF({{Fact}}="all-ones",IF({{OnesCount}}-{{CellCount}}=0,1,0),IF({{Fact}}="first-one-at-half",IF(AND({{FirstOneTime}}-INT(({{Offset}}+1)/2)=0,{{LeastPeriod}}>{{FirstOneTime}}),1,0),IF({{Fact}}="balanced",IF(2*{{OnesPerPeriod}}-{{LeastPeriod}}=0,1,0),IF({{Fact}}="doubles",{{Doubles}},IF({{Fact}}="nondecreasing",IF({{LeastPeriod}}>={{PreviousLeastPeriod}},1,0),IF({{Fact}}="repeat-or-double",IF(OR({{LeastPeriod}}-{{PreviousLeastPeriod}}=0,{{Doubles}}=1),1,0),IF({{Fact}}="no-triple-double",IF({{Doubles}}+{{PreviousDoubles}}+{{PreviousPreviousDoubles}}<3,1,0),IF({{Fact}}="half-period-one",{{HalfPeriodValue}},IF({{Fact}}="eventually-dyadic",IF({{EventualPeriod}}>0,1,0),IF({{Fact}}="parity-after-doubling",IF({{PreviousDoubles}}=1,IF({{Doubles}}-MOD({{PreviousPreviousOnesPerPeriod}},2)=0,1,0),1),IF({{Fact}}="parity-always",IF({{Doubles}}-MOD({{PreviousPreviousOnesPerPeriod}},2)=0,1,0),IF({{Fact}}="left-half-speed",IF({{EventualPeriod}}*{{EventualPeriod}}<={{OppositeLeastPeriod}},1,0),0))))))))))))',
             '1 when the fact holds for this diagonal.'),
        CALC('IsDecided', '=IF({{Fact}}="left-half-speed",IF(AND({{EventualPeriod}}>0,{{OppositeLeastPeriod}}>0),1,0),IF(OR({{Fact}}="all-ones",{{Fact}}="eventually-dyadic",{{LeastPeriod}}>0),1,0))', '1 when the horizon certifies the periods the fact needs; otherwise the fact is not an instance.'),
    ],
    [{'DiagonalFactId': f'{fact}-{did(s, k)}', 'Fact': fact, 'Diagonal': did(s, k)} for fact, (ds, _) in FACTS.items() for s, k in ds])

# ============================ Problem 2 ============================
book['Tolerances'] = table(
    'Margins epsilon around 1/2 for Problem 2. The limit is 1/2 exactly when, for every epsilon, excursions eventually stop.',
    KEY('ToleranceId', 'eps-<numerator>-<denominator>.') + [
        F('EpsilonNumerator', 'integer', desc='Numerator of the margin.', nullable=False),
        F('EpsilonDenominator', 'integer', desc='Denominator of the margin. Exact integers, because a float margin and a NUMERIC margin disagree at exact boundaries (docs/toolchain-gaps.md gap 9).', nullable=False),
        CALC('Epsilon', '={{EpsilonNumerator}}/{{EpsilonDenominator}}', 'The margin, for display.', 'number'),
        AGG('ExcursionCount', '=COUNTIFS(ToleranceChecks!{{Tolerance}},{{ToleranceId}},ToleranceChecks!{{IsExcursion}},1)', 'Prefixes whose density is more than epsilon from 1/2.'),
        AGG('LastExcursionTime', '=MAXIFS(ToleranceChecks!{{Time}},ToleranceChecks!{{Tolerance}},{{ToleranceId}},ToleranceChecks!{{IsExcursion}},1)', 'The witness: the last prefix end t outside the margin.'),
        AGG('HorizonTime', '=MAXIFS(ToleranceChecks!{{Time}},ToleranceChecks!{{Tolerance}},{{ToleranceId}})', 'The last prefix checked.'),
        CALC('SettledAtHorizon', '=IF({{LastExcursionTime}}<{{HorizonTime}},1,0)', 'Problem 2 instance: 1 when the density at the horizon is within epsilon of 1/2.'),
    ],
    [{'ToleranceId': f'eps-{a}-{b}', 'EpsilonNumerator': a, 'EpsilonDenominator': b} for a, b in TOLERANCES])

book['ToleranceChecks'] = table(
    'One prefix of the center column against one tolerance: is its density within epsilon of 1/2?',
    KEY('ToleranceCheckId', '<tolerance>-t<time>.') + [
        REL('Tolerance', 'Tolerances', 'The margin.', False),
        REL('Cell', 'Cells', 'The center cell ending the prefix.', False),
        LK('EpsilonNumerator', 'Tolerances', 'Tolerance', 'ToleranceId', 'EpsilonNumerator', 'Numerator of the margin.'),
        LK('EpsilonDenominator', 'Tolerances', 'Tolerance', 'ToleranceId', 'EpsilonDenominator', 'Denominator of the margin.'),
        LK('AbsDiscrepancy', 'Cells', 'Cell', 'CellId', 'AbsDiscrepancy', '|ones - zeros| of the prefix.'),
        LK('PrefixLength', 'Cells', 'Cell', 'CellId', 'PrefixLength', 'Terms in the prefix.'),
        LK('Time', 'Cells', 'Cell', 'CellId', 'Time', 'Prefix end t.'),
        LK('DensityDeviation', 'Cells', 'Cell', 'CellId', 'DensityDeviation', '|density - 1/2| of the prefix.', 'number'),
        CALC('IsExcursion', '=IF({{AbsDiscrepancy}}*{{EpsilonDenominator}}>2*{{EpsilonNumerator}}*{{PrefixLength}},1,0)', '1 when the prefix density is more than epsilon from 1/2, in exact integers: |ones - zeros| / N > 2 epsilon.'),
    ],
    [{'ToleranceCheckId': f'eps-{a}-{b}-t{t:03d}', 'Tolerance': f'eps-{a}-{b}', 'Cell': cid(t, 0)} for a, b in TOLERANCES for t in range(DEPTH + 1)])

book['ColorCounts'] = table(
    'How often each color occurs in each column ("does each color of cell occur on average equally often").',
    KEY('ColorCountId', '<column>-<color>.') + [
        REL('Column', 'Columns', 'The column.', False),
        REL('CellState', 'CellStates', 'The color.', False),
        LK('Depth', 'Columns', 'Column', 'ColumnId', 'Depth', 'The horizon.'),
        AGG('ConeCount', '=COUNTIFS(Cells!{{Column}},{{Column}},Cells!{{StateKey}},{{CellState}})', 'Computed cells of this column with this color.'),
        LK('ColumnFirstTime', 'Columns', 'Column', 'ColumnId', 'FirstTime', 'Terms before this are background (white).'),
        CALC('OccurrenceCount', '=IF({{CellState}}="white",{{ConeCount}}+{{ColumnFirstTime}},{{ConeCount}})', 'Terms 0 .. Depth of this column with this color, counting background terms as white.'),
        CALC('Share', '={{OccurrenceCount}}/({{Depth}}+1)', 'Share of terms with this color.', 'number'),
        CALC('ShareDeviation', '=ABS({{Share}}-0.5)', 'Distance of the share from 1/2.', 'number'),
    ],
    [{'ColorCountId': f'{colid(i)}-{s}', 'Column': colid(i), 'CellState': s} for i in range(-DEPTH, DEPTH + 1) for s in ('white', 'black')])

# ============================ Problem 3 ============================
book['MachineModels'] = table(
    'What one step of computational effort is: the cost model. Problem 3 needs one fixed; universality relates them only up to simulation overhead.',
    KEY('MachineModelId', 'Name of the model.') + [
        F('StepMeaning', desc='What one unit of effort counts.'),
        F('InputEncoding', desc='How n is given to the machine.'),
        AGG('AlgorithmCount', '=COUNTIFS(Algorithms!{{MachineModel}},{{MachineModelId}})', 'Algorithms recorded on this model.'),
    ],
    [{'MachineModelId': 'turing-machine', 'StepMeaning': 'one head move / transition', 'InputEncoding': 'n in binary on the tape'},
     {'MachineModelId': 'cellular-automaton', 'StepMeaning': 'one cell update', 'InputEncoding': 'the time step reached'},
     {'MachineModelId': 'ram', 'StepMeaning': 'one word instruction (unit cost; not bit cost)', 'InputEncoding': 'n in a register'}])

book['Algorithms'] = table(
    "A way of computing c(n) on a machine model. An algorithm that stores the answer is not admissible. Problem 3 asks whether every admissible algorithm's effort ratio effort/n is unbounded. Light-cone simulation costs O(n²) cell updates; beating O(n²) would be a partial result.",
    KEY('AlgorithmId', 'Name of the algorithm.') + [
        REL('MachineModel', 'MachineModels', 'The machine model its effort is counted in.', False),
        F('EffortRule', desc='How its effort for n is counted: cone-updates (simulate the light cone) or table-read (one read).'),
        F('StoresAnswer', 'integer', desc='1 when the machine contains the sequence itself.', nullable=False),
        CALC('IsAdmissible', '=1-{{StoresAnswer}}', '1 when the algorithm does not store the answer.'),
        AGG('ComputationCount', '=COUNTIFS(Computations!{{Algorithm}},{{AlgorithmId}})', 'Values of n computed.'),
        AGG('WrongOutputCount', '=COUNTIFS(Computations!{{Algorithm}},{{AlgorithmId}},Computations!{{IsCorrect}},0)', 'Outputs that differ from c(n). Must be 0.'),
        AGG('RatioAtHorizon', '=MAXIFS(Computations!{{EffortRatio}},Computations!{{Algorithm}},{{AlgorithmId}},Computations!{{IsHorizon}},1)', 'effort/n at n = depth.', 'number'),
        AGG('RatioAtHalfHorizon', '=MAXIFS(Computations!{{EffortRatio}},Computations!{{Algorithm}},{{AlgorithmId}},Computations!{{IsHalfHorizon}},1)', 'effort/n at n = depth/2.', 'number'),
        CALC('IsRatioGrowing', '=IF({{RatioAtHorizon}}>{{RatioAtHalfHorizon}},1,0)', '1 when effort/n grows between half the horizon and the horizon (no sign of O(n)).'),
        CALC('EffortHolds', '=IF({{IsAdmissible}}=1,{{IsRatioGrowing}},1)', 'Problem 3 instance: an admissible algorithm shows no sign of O(n) effort (inadmissible ones are excluded, so hold vacuously).'),
    ],
    [{'AlgorithmId': 'light-cone-simulation', 'MachineModel': 'cellular-automaton', 'EffortRule': 'cone-updates', 'StoresAnswer': 0},
     {'AlgorithmId': 'answer-table', 'MachineModel': 'ram', 'EffortRule': 'table-read', 'StoresAnswer': 1}])

book['Computations'] = table(
    'machine[m][n] = {v, t}: one algorithm computing c(n), with its output value and effort.',
    KEY('ComputationId', '<algorithm>-n<n>.') + [
        REL('Algorithm', 'Algorithms', 'The algorithm m.', False),
        REL('TimeStep', 'TimeSteps', 'The target time step n.', False),
        LK('EffortRule', 'Algorithms', 'Algorithm', 'AlgorithmId', 'EffortRule', 'How effort is counted.', 'string'),
        LK('TargetIndex', 'TimeSteps', 'TimeStep', 'TimeStepId', 'Time', 'n.'),
        LK('Depth', 'TimeSteps', 'TimeStep', 'TimeStepId', 'Depth', 'The horizon.'),
        LK('CenterValue', 'TimeSteps', 'TimeStep', 'TimeStepId', 'CenterValue', 'c(n) in the model.'),
        LK('ConeUpdates', 'TimeSteps', 'TimeStep', 'TimeStepId', 'CumulativeCellUpdates', 'Cell updates to reach line n.'),
        CALC('OutputValue', '={{CenterValue}}', 'v: the value the algorithm outputs (both recorded algorithms read the computed cell).'),
        CALC('IsCorrect', '=IF({{OutputValue}}={{CenterValue}},1,0)', '1 when v = c(n).'),
        CALC('Effort', '=IF({{EffortRule}}="cone-updates",{{ConeUpdates}},1)', 't: the effort spent.'),
        CALC('EffortRatio', '={{Effort}}/{{TargetIndex}}', 'effort / n.', 'number'),
        CALC('IsHorizon', '=IF({{TargetIndex}}={{Depth}},1,0)', '1 at n = depth.'),
        CALC('IsHalfHorizon', '=IF({{TargetIndex}}=INT({{Depth}}/2),1,0)', '1 at n = depth/2.'),
    ],
    [{'ComputationId': f'{a}-n{n:03d}', 'Algorithm': a, 'TimeStep': tid(n)} for a in ('light-cone-simulation', 'answer-table') for n in range(1, DEPTH + 1)])

# ============================ the logic ============================
VARS = [
    ('time', 't', 'Time step', 'TimeSteps', 1),
    ('position', 'i', 'Cell position', 'Columns', 1),
    ('period', 'p', 'Candidate period', 'Periods', 1),
    ('onset', 'T', "Onset of periodicity (Wolfram's i)", 'PeriodicityCandidates', 1),
    ('prefix-length', 'N', 'Number of terms averaged', 'Cells', 1),
    ('epsilon', 'eps', 'Margin around 1/2', 'Tolerances', 1),
    ('index', 'n', 'Index of the term to compute', 'Computations', 1),
    ('machine', 'm', 'Machine / algorithm', 'Algorithms', 1),
    ('left-bit', 'l', 'Left cell of a neighborhood (0 or 1)', 'Neighborhoods', 0),
    ('center-bit', 'q', 'Center cell of a neighborhood (0 or 1)', 'Neighborhoods', 0),
    ('right-bit', 'r', 'Right cell of a neighborhood (0 or 1)', 'Neighborhoods', 0),
    ('run-end', 'V', 'Last time step of a constant run', 'Cells', 1),
    ('word', 'a', 'A finite word whose repetition is a tail', 'PeriodicWords', 1),
    ('offset', 'k', 'Diagonal offset', 'Diagonals', 1),
    ('offset-j', 'j', 'A second diagonal offset', 'Diagonals', 1),
] + fc.NEW_VARIABLES
book['Variables'] = table(
    'The variables the predicates quantify over, the table whose rows are their values in the model, and whether their domain is infinite in the problem.',
    KEY('VariableId', 'Name of the variable.') + [
        F('Symbol', desc='How the problem writes it.'),
        F('Meaning', desc='What it ranges over.'),
        F('DomainTable', desc='The table whose rows are its values in the model (finite there).'),
        F('IsUnboundedInProblem', 'integer', desc='1 when its domain in the problem is infinite.', nullable=False),
        AGG('BinderCount', '=COUNTIFS(Terms!{{Variable}},{{VariableId}},Terms!{{OpKind}},"binder")', 'Quantifiers binding it, across all predicates.'),
    ],
    [{'VariableId': v, 'Symbol': s, 'Meaning': m, 'DomainTable': d, 'IsUnboundedInProblem': u} for v, s, m, d, u in VARS])

book['Operators'] = table(
    'The symbols formal statements are built from: binders (quantifiers, limits), connectives, relations, arithmetic and the functions of the model (c, x, rule30, cTail, ...).',
    KEY('OperatorId', 'Name of the operator.') + [
        F('Symbol', desc='How it is written.'),
        F('Kind', desc='binder, infix, prefix, apply, atom, var or const: how a term with this operator is written out.'),
        F('Arity', 'integer', desc='Number of arguments (a binder has two: its condition and its body).', nullable=False),
        F('IsModeled', 'integer', desc='1 when the model computes this operator (a table or field gives it its value); 0 when it is only a named symbol so far.', nullable=False),
        AGG('UseCount', '=COUNTIFS(Terms!{{TermOperator}},{{OperatorId}})', 'Terms using it.'),
    ],
    [{'OperatorId': o, 'Symbol': s, 'Kind': k, 'Arity': a, 'IsModeled': m} for o, s, k, a, m in mt.OPERATORS])

ARGS = ('Arg1', 'Arg2', 'Arg3', 'Arg4')
book['Terms'] = table(
    'One node of a formal statement: an operator with its argument terms, a variable, or a constant. A binder holds its bound variable, its condition (Arg1) and its body (Arg2). The text, the quantifier count and whether a quantifier ranges over an infinite domain are computed from the tree.',
    KEY('TermId', '<predicate>-<preorder index>.') + [
        REL('TermOperator', 'Operators', 'The operator (var and const for leaves).', False),
        REL('Variable', 'Variables', 'The variable of a var leaf, or the variable a binder binds.'),
        F('Constant', 'integer', desc='The value of a const leaf.'),
        F('BoundsVariable', 'integer', desc="On a binder: 1 when its condition gives the variable a finite range (as in Theorem C's t in [T, 2T + p]).", nullable=False),
        REL('Arg1', 'Terms', 'First argument (a binder: its condition).'),
        REL('Arg2', 'Terms', 'Second argument (a binder: its body).'),
        REL('Arg3', 'Terms', 'Third argument.'),
        REL('Arg4', 'Terms', 'Fourth argument.'),
        REL('IntroducedInLoop', 'Loops', 'The model-native loop that added this term; empty for the core predicates.'),
        F('PredicateKey', desc='The predicate whose statement this node belongs to (a plain key, not a reference: Predicates already points at the root term).'),
        LK('OpSymbol', 'Operators', 'TermOperator', 'OperatorId', 'Symbol', 'How the operator is written.', 'string'),
        LK('OpKind', 'Operators', 'TermOperator', 'OperatorId', 'Kind', 'How the term is written out.', 'string'),
        LK('OpArity', 'Operators', 'TermOperator', 'OperatorId', 'Arity', 'Number of arguments.'),
        LK('OpIsModeled', 'Operators', 'TermOperator', 'OperatorId', 'IsModeled', '1 when the model computes the operator.'),
        LK('VarSymbol', 'Variables', 'Variable', 'VariableId', 'Symbol', 'The variable as written.', 'string'),
        LK('VarUnbounded', 'Variables', 'Variable', 'VariableId', 'IsUnboundedInProblem', '1 when the variable ranges over an infinite domain.'),
    ] + [LK(f'{a}Text', 'Terms', a, 'TermId', 'Rendered', f'{a} written out.', 'string') for a in ARGS] + [
        CALC('Rendered', '=IF({{OpKind}}="var",{{VarSymbol}},IF({{OpKind}}="const",CONCAT("",{{Constant}}),IF({{OpKind}}="atom",{{OpSymbol}},IF({{OpKind}}="binder",CONCAT({{OpSymbol}},"[",{{VarSymbol}},", ",{{Arg1Text}},", ",{{Arg2Text}},"]"),IF({{OpKind}}="infix",CONCAT("(",{{Arg1Text}}," ",{{OpSymbol}}," ",{{Arg2Text}},")"),IF({{OpKind}}="prefix",CONCAT({{OpSymbol}},{{Arg1Text}}),CONCAT({{OpSymbol}},"[",{{Arg1Text}},IF({{OpArity}}>=2,CONCAT(", ",{{Arg2Text}}),""),IF({{OpArity}}>=3,CONCAT(", ",{{Arg3Text}}),""),IF({{OpArity}}>=4,CONCAT(", ",{{Arg4Text}}),""),"]")))))))',
             'The term written out in Wolfram Language style, computed from the tree.', 'string'),
        CALC('IsUnboundedBinder', '=IF(AND({{OpKind}}="binder",{{VarUnbounded}}=1,{{BoundsVariable}}=0),1,0)', '1 for a quantifier over an infinite domain.'),
        CALC('IsBinder', '=IF({{OpKind}}="binder",1,0)', '1 for a quantifier (or another binder).'),
        CALC('IsUnmodeledOperator', '=IF({{OpIsModeled}}=1,0,1)', '1 when the model does not compute this operator yet.'),
    ],
    [])

V, K, TRUE, INF = (lambda n: ('var', n)), (lambda n: ('const', n)), ('true',), ('infinity',)
c, x, pl, tm = (lambda e: ('c', e)), (lambda i, t: ('x', i, t)), (lambda a, b: ('+', a, b)), (lambda a, b: ('*', a, b))
t_, i_, p_, T_, N_, n_, m_, a_, Vr = (V(v) for v in ('time', 'position', 'period', 'onset', 'prefix-length', 'index', 'machine', 'word', 'run-end'))
lb, cb, rb = V('left-bit'), V('center-bit'), V('right-bit')
in_run = ('&&', ('>=', t_, T_), ('<=', t_, Vr))
PREDS = [
    ('pr-d0-setup', 'Definition', 'RunSetup', 1,
     ('&&', ('&&', ('==', x(K(0), K(0)), K(1)), ('ForAll', 'position', ('!=', i_, K(0)), ('==', x(i_, K(0)), K(0)))),
      ('ForAll', 'time', ('>=', t_, K(0)), ('ForAll', 'position', TRUE, ('==', x(i_, pl(t_, K(1))), ('rule30', x(('-', i_, K(1)), t_), x(i_, t_), x(pl(i_, K(1)), t_)))))),
     'The prize setup: a single black cell at position 0 at time 0, then Rule 30 at every cell and time.',
     'One instance per run: the run is Rule 30 from the single seed.'),
    ('pr-rule30-polynomial', 'Definition', 'RuleTableEntry', 1,
     ('ForAll', 'left-bit', TRUE, ('ForAll', 'center-bit', TRUE, ('ForAll', 'right-bit', TRUE,
      ('==', ('rule30', lb, cb, rb), ('Mod', pl(pl(pl(lb, cb), rb), tm(cb, rb)), K(2)))))),
     "Rule 30's table is Wolfram's polynomial (equivalently left XOR (center OR right)).",
     'One instance per transition of rule 30.'),
    ('pr-light-cone', 'Definition', 'Run', 1,
     ('ForAll', 'time', ('>=', t_, K(0)), ('ForAll', 'position', ('>', ('Abs', i_), t_), ('==', x(i_, t_), K(0)))),
     'From the single seed under a quiescent rule, every cell outside the light cone is white.',
     'One instance per run: the run satisfies the conditions that make the cone exact.'),
    ('pr-p1-non-periodic', 'P1', 'PeriodTest', 0,
     ('NotExists', 'period', ('>=', p_, K(1)), ('NotExists', 'onset', ('>=', T_, K(0)), ('ForAll', 'time', ('>=', t_, T_), ('==', c(pl(t_, p_)), c(t_))))),
     'Problem 1: the center column is not eventually periodic.',
     'One instance per period p <= %d: every candidate (p, T) with T <= (depth - p)/2 has a witness t >= T with c(t + p) != c(t) inside the horizon (the witnesses are PeriodicityCandidates.FirstMismatchFrom).' % MAX_PERIOD),
    ('pr-k1-not-constant', 'Known result', 'PeriodTest', 0,
     ('NotExists', 'onset', ('>=', T_, K(0)), ('ForAll', 'time', ('>=', t_, T_), ('==', c(pl(t_, K(1))), c(t_)))),
     'The center column is not eventually constant (the period-1 case of Problem 1).',
     'One instance: every onset T <= (depth - 1)/2 has a witness t >= T with c(t + 1) != c(t).'),
    ('pr-tc-mismatch-window', 'Theorem', 'PeriodTestWindows', 1,
     ('ForAll', 'onset', ('>=', T_, K(0)), ('ForAll', 'period', ('>=', p_, K(1)),
      ('Exists!', 'position', ('&&', ('>=', i_, K(0)), ('<=', i_, K(1))),
       ('Exists!', 'time', ('&&', ('>=', t_, T_), ('<=', t_, pl(tm(K(2), T_), p_))), ('!=', x(i_, t_), x(i_, pl(t_, p_))))))),
     'Theorem C: for every T and p, column 0 or column 1 has x(i, t) != x(i, t + p) for some t in [T, 2T + p].',
     'One instance per period p: every window (T, p) that ends inside the horizon holds (the windows are MismatchWindows rows).'),
    ('pr-td-run-bounds', 'Theorem', 'Cell', 1,
     ('ForAll', 'onset', ('>=', T_, K(0)), ('ForAll', 'run-end', ('>=', Vr, T_), ('&&',
      ('=>', ('ForAll!', 'time', in_run, ('==', c(t_), K(1))), ('<=', Vr, pl(tm(K(2), T_), K(1)))),
      ('=>', ('ForAll!', 'time', in_run, ('==', c(t_), K(0))), ('<=', Vr, pl(tm(K(4), T_), K(5))))))),
     'Theorem D: a black center run starting at T ends by 2T+1, a white one by 4T+5.',
     'One instance per center cell: the cell lies within the bound of the run it belongs to.'),
    ('pr-tx-left-consistent', 'Theorem', 'LeftConsistencyCheck', 1,
     ('ForAll', 'time', ('>=', t_, K(0)), ('=>', ('==', c(t_), K(1)), ('==', c(pl(t_, K(1))), ('-', K(1), x(K(-1), t_))))),
     'TX: whenever c(t) = 1 the rule forces c(t + 1) = NOT x(-1, t), and the left half depends only on the center\'s past: the center is left-consistent.',
     'One instance per time step t < depth of the real center.'),
    ('pr-b9-tail-killed', 'Bridge obligation', 'TailCandidate', 0,
     ('ForAll', 'word', ('&&', ('Nonconstant', a_), ('==', ('LeastPeriod', a_), ('Length', a_))),
      ('ForAll', 'onset', ('>=', T_, K(1)), ('Exists', 'time', ('>=', t_, ('-', T_, K(1))),
       ('&&', ('==', ('cTail', a_, T_, t_), K(1)), ('!=', ('cTail', a_, T_, pl(t_, K(1))), ('-', K(1), ('xTail', a_, T_, K(-1), t_))))))),
     'B9 on the real prefix: the real center up to T followed by a a a ... (a nonconstant, primitive) is not left-consistent: some one-time t has cTail(t + 1) != NOT xTail(-1, t). B9 and TX imply it; B1 follows from it.',
     'One instance per tail candidate (word, onset): left-consistency kills it inside the horizon (onset + %d).' % TAIL_MARGIN),
    ('pr-p2-equal-frequency', 'P2', 'Tolerance', 0,
     ('==', ('DiscreteLimit', 'prefix-length', ('->', N_, INF), ('/', ('Ones', N_), N_)), ('/', K(1), K(2))),
     'Problem 2: each color occurs on average equally often in the center column.',
     'One instance per tolerance epsilon: the density of the whole computed prefix is within epsilon of 1/2.'),
    ('pr-p3-effort', 'P3', 'Algorithm', 0,
     ('NotExists', 'machine', ('!', ('StoresAnswer', m_)), ('&&', ('ForAll', 'index', ('>=', n_, K(1)), ('==', ('Output', m_, n_), c(n_))),
      ('<', ('Limsup', 'index', ('->', n_, INF), ('/', ('Effort', m_, n_), n_)), INF))),
     'Problem 3: no admissible machine computes c(n) with effort O(n) (the displayed predicate; the prose says "at least O(n)").',
     "One instance per algorithm: an admissible algorithm's effort ratio still grows at the horizon."),
]
k_, j_ = V('offset'), V('offset-j')
P_, Eps, dy = (lambda k: ('P', k)), (lambda k: ('Eps', k)), (lambda k, n: ('-', k, K(n)))
TWO20 = ('Power', K(2), K(20))
PREDS += [
    ('pr-t0-edges', 'Theorem', 'DiagonalFact', 1,
     ('ForAll', 'time', ('>=', t_, K(0)), ('&&', ('==', x(('-', K(0), t_), t_), K(1)), ('==', x(t_, t_), K(1)))),
     'T0: both boundary cells of the cone are black at every time (cone support is pr-light-cone).',
     'One instance per edge diagonal: every cone cell on it is black inside the horizon.'),
    ('pr-t004-dyadic-period', 'Theorem', 'DiagonalPeriodTest', 1,
     ('ForAll', 'offset', ('>=', k_, K(0)), ('|', P_(k_), ('Power', K(2), k_))),
     'T004: the right diagonal y_k is periodic with a period dividing 2^k.',
     'One instance per k <= 5: 2^k is a period of the observed y_k.'),
    ('pr-tb-first-one', 'Theorem', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(0)), ('&&', ('==', ('FirstOne', k_), ('Ceiling', ('/', k_, K(2)))), ('>', P_(k_), ('FirstOne', k_)))),
     'TB: the first black cell of y_k is at t = ceil(k/2), and its least period exceeds that time.',
     'One instance per right diagonal whose least period the horizon certifies.'),
    ('pr-h1-balanced', 'Hypothesis', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(1)), ('==', tm(K(2), ('OnesPerPeriod', k_)), P_(k_))),
     'H1: every right diagonal k >= 1 is balanced over its least period.',
     'One instance per certified right diagonal k >= 1.'),
    ('pr-h2-always-doubles', 'Hypothesis', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(3)), ('==', P_(k_), tm(K(2), P_(dy(k_, 1))))),
     'H2: the least period doubles at every k >= 3.',
     'One instance per certified right diagonal k >= 3.'),
    ('pr-h4-nondecreasing', 'Hypothesis', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(1)), ('>=', P_(k_), P_(dy(k_, 1)))),
     'H4: least diagonal periods never decrease.',
     'One instance per certified right diagonal k >= 1.'),
    ('pr-tl-repeat-or-double', 'Theorem', 'DiagonalFact', 1,
     ('&&', ('ForAll', 'offset', ('>=', k_, K(3)), ('==', P_(k_), tm(P_(dy(k_, 1)), pl(K(1), Eps(k_))))),
      ('ForAll', 'offset', ('>=', k_, K(3)), ('Exists', 'offset-j', ('>', j_, k_), ('==', Eps(j_), K(1))))),
     'TL: P_k = P_{k-1} (1 + eps_k) for every k >= 3, and the period doubles infinitely often.',
     'One instance per certified right diagonal k >= 3: the repeat-or-double conjunct.'),
    ('pr-tn-no-triple-double', 'Theorem', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(5)), ('!', ('&&', ('&&', ('==', Eps(k_), K(1)), ('==', Eps(dy(k_, 1)), K(1))), ('==', Eps(dy(k_, 2)), K(1))))),
     'TN: for k >= 5 the least diagonal period never doubles three times in a row.',
     'One instance per certified right diagonal k >= 5.'),
    ('pr-h14-half-period-one', 'Hypothesis', 'DiagonalFact', 1,
     ('ForAll', 'offset', ('>=', k_, K(1)), ('==', ('y', k_, ('/', P_(k_), K(2))), K(1))),
     'H14: every right diagonal is black at its half period: y_j(P_j / 2) = 1.',
     'One instance per certified right diagonal k >= 1.'),
    ('pr-tr-left-dyadic', 'Theorem', 'DiagonalFact', 0,
     ('ForAll', 'offset', ('>=', k_, K(0)), ('|', ('Pw', k_), ('Power', K(2), k_))),
     'TR: every left diagonal w_k is eventually periodic, with least eventual period a power of two dividing 2^k.',
     'One instance per left diagonal k <= 10: the horizon shows a dyadic eventual period <= min(2^k, 8) (only dyadic periods are searched).'),
    ('pr-h23-left-period-8', 'Hypothesis', 'DiagonalFact', 0,
     ('ForAll', 'offset', ('>=', k_, K(0)), ('<=', ('Pw', k_), K(8))),
     'H23: every left diagonal w_k has least eventual period at most 8.',
     'One instance per left diagonal k <= 10 (its refutation lies beyond the model: far larger k).'),
    ('pr-h9-discrepancy-root', 'Hypothesis', 'CellSquaredDiscrepancyBound', 1,
     ('ForAll!', 'prefix-length', ('&&', ('>=', N_, K(16)), ('<=', N_, TWO20)), ('<=', ('Power', ('-', tm(K(2), ('Ones', N_)), N_), K(2)), tm(K(9), N_))),
     'H9: |2 S(N) - N| <= 3 sqrt(N) for every 16 <= N <= 2^20 (squared, so it is exact in integers).',
     'One instance per center prefix with N >= 16 inside the horizon (a sample of the domain).',
     {'slope': 9, 'domain_min': 16}),
    ('pr-h13-run-log-bound', 'Hypothesis', 'CellRunLengthLogBound', 1,
     ('ForAll!', 'onset', ('&&', ('>=', T_, K(1)), ('<', T_, TWO20)), ('ForAll!', 'run-end', ('&&', ('>=', Vr, T_), ('<', Vr, ('-', TWO20, K(1)))),
      ('=>', ('MaximalRun', T_, Vr), ('<=', pl(('-', Vr, T_), K(1)), pl(tm(K(2), ('Log2', pl(T_, K(1)))), K(4)))))),
     'H13: every maximal constant center run [T, V] with 1 <= T and V < 2^20 - 1 has length <= 2 log2(T + 1) + 4.',
     'One instance per center cell whose run starts at T >= 1: the run so far is within the bound (2^(L - 4) <= (T + 1)^2).',
     {'slope': 2, 'intercept': 4, 'domain_min': 1}),
    ('pr-h21-agreement-44', 'Hypothesis', 'PeriodTestAgreementBound', 1,
     ('ForAll!', 'period', ('&&', ('>=', p_, K(1)), ('<=', p_, K(4096))), ('ForAll!', 'time', ('&&', ('>=', t_, K(0)), ('<', t_, TWO20)), ('<=', ('AgreementRun', p_, t_), K(44)))),
     'H21: on the first 2^20 center bits, every agreement run c(t) = c(t + p), 1 <= p <= 4096, has length at most 44.',
     'One instance per period p <= %d: the longest agreement run inside the horizon.' % MAX_PERIOD,
     {'intercept': 44}),
    ('pr-tq-agreement-runs', 'Theorem', '', 0,
     ('ForAll', 'period', ('>=', p_, K(1)), ('<=>', ('Exists', 'onset', ('>=', T_, K(0)), ('ForAll', 'time', ('>=', t_, T_), ('==', c(pl(t_, p_)), c(t_)))),
      ('Exists', 'time', ('>=', t_, K(0)), ('==', ('AgreementRun', p_, t_), INF)))),
     'TQ: the center is eventually p-periodic iff some agreement run c(t) = c(t + p) is infinite.',
     'No bounded instances: an infinite run is not visible inside a horizon.'),
]
PREDS += [(pid, prob, '', refutes, tree, gloss, 'No instances yet: the statement is formal; IsComputable says whether the model can compute its operators.')
          for pid, prob, _, refutes, tree, gloss in fc.CLAIMS]
PREDS += [(pid, prob, kind, refutes, tree, gloss, f'One instance per {kind} row the statement is about.') for pid, prob, _, refutes, kind, tree, gloss, _ in fc.DECIDED]
COVERS = {'pr-rule30-polynomial'}
preds = []
for pid, prob, kind, refutes, tree, st, meaning, *extra in PREDS:
    root, rows_ = mt.term_rows(pid, tree)
    book['Terms']['data'].extend(rows_)
    preds.append(mt.predicate_row(pid, prob, kind, root, st, meaning, refutes, covers_domain=int(pid in COVERS), **(extra[0] if extra else {})))
book['Predicates'] = table(
    'The properties stated about the model: definitions, theorems, bridge obligations and the three prize problems. The formal statement is a Terms tree; its bounded instances are computed from the model; a model-native loop adds its hypotheses here as rows.',
    KEY('PredicateId', 'Name of the predicate.') + [
        F('Problem', desc='Definition, Known result, Theorem, Bridge obligation, Hypothesis, or the prize problem it is (P1, P2, P3).'),
        F('InstanceKind', desc='Which reference of PredicateInstances decides an instance.'),
        REL('RootTerm', 'Terms', 'The formal statement.', False),
        F('Statement', desc='A gloss in words; the formal content is the term tree.'),
        F('InstanceMeaning', desc='What one bounded instance asserts.'),
        F('FailureRefutes', 'integer', desc='1 when a failing instance is a counterexample to the statement; 0 when it only means the horizon did not decide it.', nullable=False),
        F('BoundSlope', 'integer', desc='For bound hypotheses: the bound is slope * |a| + intercept.'),
        F('BoundIntercept', 'integer', desc='For bound hypotheses: see BoundSlope.'),
        F('DomainMin', 'integer', desc='For bound hypotheses: the smallest index (N, T) the statement covers.'),
        F('CoversDomain', 'integer', desc='1 when the instance rows enumerate the whole bounded domain of the statement, so holding on all of them verifies it; 0 when they are a sample (a model horizon shorter than the statement).', nullable=False),
        REL('IntroducedInLoop', 'Loops', 'The model-native loop that stated this predicate; empty for the core predicates.'),
        LK('Formal', 'Terms', 'RootTerm', 'TermId', 'Rendered', 'The formal statement, written out from its term tree.', 'string'),
        AGG('QuantifierCount', '=COUNTIFS(Terms!{{PredicateKey}},{{PredicateId}},Terms!{{IsBinder}},1)', 'Quantifiers in the statement.'),
        AGG('UnboundedQuantifierCount', '=COUNTIFS(Terms!{{PredicateKey}},{{PredicateId}},Terms!{{IsUnboundedBinder}},1)', 'Quantifiers over an infinite domain.'),
        AGG('UnmodeledOperatorCount', '=COUNTIFS(Terms!{{PredicateKey}},{{PredicateId}},Terms!{{IsUnmodeledOperator}},1)', 'Operators of the statement the model does not compute yet.'),
        CALC('IsComputable', '=IF({{UnmodeledOperatorCount}}=0,1,0)', '1 when every operator of the statement has a meaning in the model.'),
        CALC('IsFinitelyDecidable', '=IF({{UnboundedQuantifierCount}}=0,1,0)', '1 when the model can decide the full statement, not only bounded instances.'),
        AGG('RowCount', '=COUNTIFS(PredicateInstances!{{Predicate}},{{PredicateId}})', 'Instance rows, in or out of the domain.'),
        AGG('InstanceCount', '=COUNTIFS(PredicateInstances!{{Predicate}},{{PredicateId}},PredicateInstances!{{InDomain}},1)', 'Bounded instances in the domain of the statement.'),
        AGG('HoldingCount', '=SUMIFS(PredicateInstances!{{Holds}},PredicateInstances!{{Predicate}},{{PredicateId}},PredicateInstances!{{InDomain}},1)', 'Instances that hold.'),
        CALC('FailingCount', '={{InstanceCount}}-{{HoldingCount}}', 'Instances that fail.'),
        CALC('IsRefuted', '=IF(AND({{FailureRefutes}}=1,{{FailingCount}}>0),1,0)', '1 when a counterexample instance fails: the statement is false.'),
        CALC('IsVerified', '=IF(AND({{IsFinitelyDecidable}}=1,{{CoversDomain}}=1,{{InstanceCount}}>0,{{FailingCount}}=0),1,0)', '1 when the statement is finite, its instances cover its domain and every one holds: the model decides it true.'),
        CALC('FiniteVerdict', '=IF({{InstanceCount}}=0,"NO INSTANCES",IF({{FailingCount}}=0,"HOLDS ON EVERY INSTANCE",IF({{FailureRefutes}}=1,CONCAT("REFUTED BY ",{{FailingCount}}," OF ",{{InstanceCount}}," INSTANCES"),CONCAT({{FailingCount}}," OF ",{{InstanceCount}}," UNDECIDED AT THE HORIZON"))))', 'What the model says about the bounded instances.', 'string'),
        AGG('AssertionCount', '=COUNTIFS(Assertions!{{Predicate}},{{PredicateId}})', 'Ledger claims about this predicate.'),
    ],
    preds)

inst = [mt.instance_row('pr-d0-setup', RUN, 'Run', RUN)]
inst += [mt.instance_row('pr-rule30-polynomial', nbid(n), 'RuleTableEntry', entid('rule-30', n)) for n in range(7, -1, -1)]
inst.append(mt.instance_row('pr-light-cone', RUN, 'Run', RUN))
# One instance per period: the (p, T) candidates and Theorem C windows are already rows with their own
# witnesses; the instance reads their roll-up on the period test.
inst += [mt.instance_row('pr-p1-non-periodic', f'p{p:02d}', 'PeriodTest', ptid(0, p)) for p in range(1, MAX_PERIOD + 1)]
inst.append(mt.instance_row('pr-k1-not-constant', 'p01', 'PeriodTest', ptid(0, 1)))
inst += [mt.instance_row('pr-tc-mismatch-window', f'p{p:02d}', 'PeriodTest', ptid(0, p)) for p in range(1, MAX_PERIOD + 1)]
inst += [mt.instance_row('pr-td-run-bounds', f't{t:03d}', 'Cell', cid(t, 0)) for t in range(DEPTH + 1)]
inst += [mt.instance_row('pr-tx-left-consistent', f't{t:03d}', 'LeftConsistencyCheck', f'{RUN}-tx-t{t:03d}') for t in range(DEPTH)]
inst += [mt.instance_row('pr-b9-tail-killed', r['TailCandidateId'], 'TailCandidate', r['TailCandidateId']) for r in tails]
inst += [mt.instance_row('pr-p2-equal-frequency', f'eps-{a}-{b}', 'Tolerance', f'eps-{a}-{b}') for a, b in TOLERANCES]
inst += [mt.instance_row('pr-p3-effort', a, 'Algorithm', a) for a in ('light-cone-simulation', 'answer-table')]
FACT_OF = {'pr-t0-edges': 'all-ones', 'pr-tb-first-one': 'first-one-at-half', 'pr-h1-balanced': 'balanced', 'pr-h2-always-doubles': 'doubles',
           'pr-h4-nondecreasing': 'nondecreasing', 'pr-tl-repeat-or-double': 'repeat-or-double', 'pr-tn-no-triple-double': 'no-triple-double',
           'pr-h14-half-period-one': 'half-period-one', 'pr-tr-left-dyadic': 'eventually-dyadic', 'pr-h23-left-period-8': 'eventually-dyadic'}
for pid, fact in FACT_OF.items():
    inst += [mt.instance_row(pid, did(sd, k), 'DiagonalFact', f'{fact}-{did(sd, k)}') for sd, k in FACTS[fact][0]]
inst += [mt.instance_row('pr-t004-dyadic-period', f'k{k:02d}', 'DiagonalPeriodTest', f"{did('right', k)}-d{2 ** k:02d}") for k in RIGHT_K if 2 ** k <= RIGHT_CAP]
inst += [mt.instance_row('pr-h9-discrepancy-root', f't{t:03d}', 'Cell', cid(t, 0)) for t in range(DEPTH + 1)]
inst += [mt.instance_row('pr-h13-run-log-bound', f't{t:03d}', 'Cell', cid(t, 0)) for t in range(DEPTH + 1)]
inst += [mt.instance_row('pr-h21-agreement-44', f'p{p:02d}', 'PeriodTest', ptid(0, p)) for p in range(1, MAX_PERIOD + 1)]
for pid, _, _, _, kind, _, _, fact in fc.DECIDED:
    if fact:
        inst += [mt.instance_row(pid, did(sd, k), 'DiagonalFact', f'{fact}-{did(sd, k)}') for sd, k in FACTS[fact][0]]
inst += [mt.instance_row('pr-cm-model-reproduces', f't{t:03d}', 'AcceleratorClaim', f'E17-{cid(t, 0)}') for t in range(DEPTH + 1)]
KINDS = [  # InstanceKind, reference, field read for Holds
    ('RuleTableEntry', 'RuleTableEntry', 'MatchesPolynomial'), ('Run', 'Run', 'IsLightConeExact'), ('RunSetup', 'Run', 'IsPrizeSetup'),
    ('PeriodicityCandidate', 'PeriodicityCandidate', 'IsRefuted'), ('MismatchWindow', 'MismatchWindow', 'WindowHolds'),
    ('Cell', 'Cell', 'RunBoundHolds'), ('LeftConsistencyCheck', 'LeftConsistencyCheck', 'IsConsistent'),
    ('TailCandidate', 'TailCandidate', 'IsKilled'), ('Tolerance', 'Tolerance', 'SettledAtHorizon'), ('Algorithm', 'Algorithm', 'EffortHolds'),
    ('DiagonalPeriodTest', 'DiagonalPeriodTest', 'IsPurePeriod'), ('DiagonalFact', 'DiagonalFact', 'Holds'), ('AcceleratorClaim', 'AcceleratorClaim', 'IsMatch'),
    ('PeriodTest', 'PeriodTest', 'BoundedRefutationHolds'), ('PeriodTestWindows', 'PeriodTest', 'WindowsHold'),
]
REF_TABLE = {'RuleTableEntry': 'RuleTableEntries', 'Run': 'Runs', 'PeriodTest': 'PeriodTests', 'PeriodicityCandidate': 'PeriodicityCandidates', 'MismatchWindow': 'MismatchWindows',
             'DiagonalPeriodTest': 'DiagonalPeriodTests', 'DiagonalFact': 'DiagonalFacts', 'AcceleratorClaim': 'AcceleratorClaims',
             'Cell': 'Cells', 'LeftConsistencyCheck': 'LeftConsistencyChecks', 'TailCandidate': 'TailCandidates', 'Tolerance': 'Tolerances', 'Algorithm': 'Algorithms'}
holds = '0'
for kind, ref, field in reversed(KINDS):
    holds = f'IF({{{{InstanceKind}}}}="{kind}",{{{{{kind}Holds}}}},{holds})'
# Parametrized kinds: the bound is data on the predicate (BoundSlope, BoundIntercept, DomainMin), so a
# loop states a new bound hypothesis with rows only.
PARAM = [
    ('TailCandidateExcessBound', 'IF(AND({{TailCandidateHolds}}=1,{{TailKillExcess}}<={{BoundSlope}}*{{TailWordLength}}+{{BoundIntercept}}),1,0)'),
    ('CellSquaredDiscrepancyBound', 'IF({{CellDiscrepancy}}*{{CellDiscrepancy}}<={{BoundSlope}}*{{CellPrefixLength}},1,0)'),
    ('CellRunLengthLogBound', 'IF(POWER(2,{{CellRunLength}}-{{BoundIntercept}})<=POWER({{CellRunStart}}+1,{{BoundSlope}}),1,0)'),
    ('PeriodTestAgreementBound', 'IF({{TestLongestAgreement}}<={{BoundIntercept}},1,0)'),
]
for kind, f in reversed(PARAM):
    holds = f'IF({{{{InstanceKind}}}}="{kind}",{f},{holds})'
book['PredicateInstances'] = table(
    'One bounded instance of a predicate, pointing at the model row that decides it. This is the roof all predicates share: whether an instance is in the domain, whether it holds and its witness are all read from the model.',
    KEY('PredicateInstanceId', '<predicate>-<instance>.') + [
        REL('Predicate', 'Predicates', 'The predicate.', False),
        REL('IntroducedInLoop', 'Loops', 'The model-native loop that added this instance; empty for the core predicates.'),
        LK('InstanceKind', 'Predicates', 'Predicate', 'PredicateId', 'InstanceKind', 'Which reference decides it.', 'string'),
        LK('BoundSlope', 'Predicates', 'Predicate', 'PredicateId', 'BoundSlope', 'Bound hypotheses: slope.'),
        LK('BoundIntercept', 'Predicates', 'Predicate', 'PredicateId', 'BoundIntercept', 'Bound hypotheses: intercept.'),
        LK('DomainMin', 'Predicates', 'Predicate', 'PredicateId', 'DomainMin', 'Bound hypotheses: smallest index covered.'),
    ] + [REL(ref, REF_TABLE[ref], f'Deciding row, for a {ref} instance.') for ref in mt.INSTANCE_REFS]
      + [LK(f'{kind}Holds', REF_TABLE[ref], ref, f'{ref}Id', field, f'{REF_TABLE[ref]}.{field}.') for kind, ref, field in KINDS] + [
        LK('CandidateInDomain', 'PeriodicityCandidates', 'PeriodicityCandidate', 'PeriodicityCandidateId', 'InBoundedDomain', 'Onset within the bounded form.'),
        LK('CandidateWitness', 'PeriodicityCandidates', 'PeriodicityCandidate', 'PeriodicityCandidateId', 'FirstMismatchFrom', 'First mismatch at or after the onset.'),
        LK('TailInDomain', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'IsInB9Domain', 'Nonconstant primitive tail.'),
        LK('TailKillTime', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'KillTime', 'When left-consistency kills the tail.'),
        LK('TailKillExcess', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'KillExcess', 'Kill time minus onset.'),
        LK('TailWordLength', 'TailCandidates', 'TailCandidate', 'TailCandidateId', 'WordLength', '|a|.'),
        LK('CellDiscrepancy', 'Cells', 'Cell', 'CellId', 'Discrepancy', 'Ones minus zeros of the prefix.'),
        LK('CellPrefixLength', 'Cells', 'Cell', 'CellId', 'PrefixLength', 'N.'),
        LK('CellIsCenter', 'Cells', 'Cell', 'CellId', 'IsCenter', '1 on the center column.'),
        LK('CellRunLength', 'Cells', 'Cell', 'CellId', 'RunLength', 'Constant run length so far.'),
        LK('CellRunStart', 'Cells', 'Cell', 'CellId', 'RunStart', 'Start of the constant run.'),
        LK('TestLongestAgreement', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'LongestAgreementStreak', 'Longest agreement run.'),
        LK('FactIsDecided', 'DiagonalFacts', 'DiagonalFact', 'DiagonalFactId', 'IsDecided', 'The horizon certifies what the fact needs.'),
        CALC('InDomain', '=IF({{InstanceKind}}="PeriodicityCandidate",{{CandidateInDomain}},IF(OR({{InstanceKind}}="TailCandidate",{{InstanceKind}}="TailCandidateExcessBound"),{{TailInDomain}},IF({{InstanceKind}}="CellSquaredDiscrepancyBound",IF(AND({{CellIsCenter}}=1,{{CellPrefixLength}}>={{DomainMin}}),1,0),IF({{InstanceKind}}="CellRunLengthLogBound",IF(AND({{CellIsCenter}}=1,{{CellRunStart}}>={{DomainMin}}),1,0),IF({{InstanceKind}}="DiagonalFact",{{FactIsDecided}},1)))))', '1 when the instance lies in the domain the statement quantifies over (computed, not chosen).'),
        CALC('Holds', '=' + holds, '1 when the instance holds, read from its deciding row.'),
        CALC('Witness', '=IF({{InstanceKind}}="PeriodicityCandidate",{{CandidateWitness}},IF(OR({{InstanceKind}}="TailCandidate",{{InstanceKind}}="TailCandidateExcessBound"),{{TailKillTime}},0))', 'The time step that decides it, where there is one: the refuting mismatch or the kill.'),
    ],
    inst)
for r in kept.get('Predicates', []):
    r.setdefault('CoversDomain', 1)   # loop predicates written before CoversDomain existed enumerated their domain
for r in kept.get('Terms', []):
    r.setdefault('PredicateKey', r['TermId'].rsplit('-', 1)[0])   # terms written before PredicateKey existed
for t in LOOP_OWNED:
    book[t]['data'].extend(kept.get(t, []))

# ============================ outside values ============================
center_ev = lt.row(book, 'Evidence', 'E17')
center_txt = (lt.ROOT / center_ev['Path']).read_text().strip()
assert lt.sha256_file(lt.ROOT / center_ev['Path']) == center_ev['Sha256']
book['AcceleratorClaims'] = table(
    'A value an optimizer outside the rulebook claims for a cell. The rulebook computes the cell itself and decides whether the claim matches.',
    KEY('AcceleratorClaimId', '<evidence>-<cell>.') + [
        REL('Cell', 'Cells', 'The cell the claim is about.', False),
        REL('Source', 'Evidence', 'The evidence file the claimed value comes from.', False),
        F('ClaimedValue', 'integer', desc='The value the optimizer reports.', nullable=False),
        LK('ModelValue', 'Cells', 'Cell', 'CellId', 'Value', 'The value the model computes for that cell.'),
        CALC('IsMatch', '=IF({{ClaimedValue}}={{ModelValue}},1,0)', '1 when the optimizer agrees with the model.'),
    ],
    [{'AcceleratorClaimId': f'E17-{cid(t, 0)}', 'Cell': cid(t, 0), 'Source': 'E17', 'ClaimedValue': int(center_txt[t])} for t in range(DEPTH + 1)])


# ============================ the ledger reads the model ============================
def ensure_field(tbl, field):
    sch = book[tbl]['schema']
    for n, f in enumerate(sch):
        if f['name'] == field['name']:
            sch[n] = field
            return
    sch.append(field)


def drop_field(tbl, name):
    book[tbl]['schema'] = [f for f in book[tbl]['schema'] if f['name'] != name]
    for r in book[tbl]['data']:
        r.pop(name, None)


ensure_field('Evidence', AGG('ClaimCount', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}})', 'Cell values this evidence file claims.'))
ensure_field('Evidence', AGG('ClaimMismatchCount', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}},AcceleratorClaims!{{IsMatch}},0)', 'Claimed values the model computes differently. Must be 0.'))

# A claim linked to a predicate takes its status from the model where the model can decide it:
# a counterexample instance makes it FALSIFIED whatever was reported, and a finite statement whose
# every instance holds is FINITE_VERIFIED without anyone typing it. Unlinked claims keep their report.
ensure_field('Assertions', REL('Predicate', 'Predicates', 'The modeled predicate this claim is about, if any.'))
ensure_field('Assertions', AGG('IsModelLinked', '=COUNTIFS(Predicates!{{PredicateId}},{{Predicate}})', '1 when the claim is tied to a modeled predicate.'))
ensure_field('Assertions', LK('PredicateVerdict', 'Predicates', 'Predicate', 'PredicateId', 'FiniteVerdict', "The model's verdict on the predicate's bounded instances.", 'string'))
ensure_field('Assertions', LK('PredicateIsFinitelyDecidable', 'Predicates', 'Predicate', 'PredicateId', 'IsFinitelyDecidable', '1 when the model can decide the full statement.'))
ensure_field('Assertions', LK('PredicateIsRefuted', 'Predicates', 'Predicate', 'PredicateId', 'IsRefuted', '1 when a counterexample instance fails in the model.'))
ensure_field('Assertions', LK('PredicateIsVerified', 'Predicates', 'Predicate', 'PredicateId', 'IsVerified', '1 when the model decides the statement true.'))
ensure_field('Assertions', CALC('ModelVerdict', '=IF({{IsModelLinked}}=1,{{PredicateVerdict}},"NOT MODELED")', "The model's verdict on the claim's predicate; NOT MODELED for a claim stated only in words.", 'string'))
ensure_field('Assertions', CALC('EffectiveStatus', '=IF(AND({{IsModelLinked}}=1,{{PredicateIsRefuted}}=1),"FALSIFIED",IF(AND({{IsModelLinked}}=1,{{PredicateIsVerified}}=1,OR({{ReportedStatus}}="OPEN",{{ReportedStatus}}="FINITE_VERIFIED")),"FINITE_VERIFIED",{{ReportedStatus}}))',
                                 'The status the ledger uses: FALSIFIED when the model holds a counterexample, FINITE_VERIFIED when the model decides an open or checked claim true, otherwise the reported status.', 'string'))
ensure_field('Assertions', CALC('IsModelDecided', '=IF(AND({{IsModelLinked}}=1,OR({{PredicateIsRefuted}}=1,{{PredicateIsVerified}}=1)),1,0)', '1 when the model, not a report, decides the status.'))
ensure_field('Assertions', CALC('IsModelContradicted', '=IF(AND({{IsModelLinked}}=1,{{PredicateIsRefuted}}=1,OR({{ReportedStatus}}="DEFINITION",{{ReportedStatus}}="PROVED_HUMAN_READABLE",{{ReportedStatus}}="REDERIVED_KNOWN",{{ReportedStatus}}="FINITE_VERIFIED")),1,0)', '1 when the report asserts the claim (proved, checked or definitional) and the model refutes it: the report is wrong. An OPEN claim the model refutes is decided, not contradicted.'))
for f in book['Assertions']['schema']:
    if f['name'] in ('StatusGroup', 'IsUsable', 'IsProofEligible'):
        f['formula'] = f['formula'].replace('{{ReportedStatus}}', '{{EffectiveStatus}}')
ensure_field('Assessments', LK('EffectiveStatus', 'Assertions', 'Assertion', 'AssertionId', 'EffectiveStatus', 'The status the ledger uses (model-decided where it can be).', 'string'))
ensure_field('Assessments', LK('IsModelDecided', 'Assertions', 'Assertion', 'AssertionId', 'IsModelDecided', '1 when the model decides the status.'))
ensure_field('Assessments', CALC('CurrentStatus', '=IF({{BlockedCount}}>0,"BLOCKED",{{EffectiveStatus}})', 'BLOCKED when an ancestor is not usable, otherwise the effective status.', 'string'))
ensure_field('Assessments', CALC('EvidenceGap', '=IF(AND({{EffectiveStatus}}="FINITE_VERIFIED",{{SupportCount}}=0,{{IsModelDecided}}=0),1,0)', '1 for a reported finite verification with no evidence file; a model-decided one is its own evidence.'))

drop_field('Dashboards', 'PredicateCount')  # bare COUNT breaks rulebook-to-postgres (docs/toolchain-gaps.md gap 6)
ensure_field('Dashboards', AGG('ConformanceMismatchCount', '=COUNTIFS(AcceleratorClaims!{{IsMatch}},0)', 'Optimizer claims the model disagrees with. Must be 0.'))
ensure_field('Dashboards', AGG('PredicatesFailingAnInstance', '=COUNTIFS(Predicates!{{FailingCount}},">0")', 'Predicates with at least one failing bounded instance.'))
ensure_field('Dashboards', AGG('ModelLinkedClaimCount', '=COUNTIFS(Assertions!{{IsModelLinked}},1)', 'Claims tied to a modeled predicate.'))
ensure_field('Dashboards', AGG('ModelDecidedClaimCount', '=COUNTIFS(Assertions!{{IsModelDecided}},1)', 'Claims whose status the model decides.'))
ensure_field('Dashboards', AGG('ModelContradictionCount', '=COUNTIFS(Assertions!{{IsModelContradicted}},1)', 'Claims the model refutes although their report does not. Must be 0.'))
ensure_field('Dashboards', AGG('UnmodeledClaimCount', '=COUNTIFS(Assertions!{{IsModelLinked}},0)', 'Claims still only stated in words.'))

LINK = {'D0': 'pr-d0-setup', 'P1': 'pr-p1-non-periodic', 'P2': 'pr-p2-equal-frequency', 'P3': 'pr-p3-effort', 'K1': 'pr-k1-not-constant',
        'TC': 'pr-tc-mismatch-window', 'TD': 'pr-td-run-bounds', 'TX': 'pr-tx-left-consistent', 'B9': 'pr-b9-tail-killed', 'B1': 'pr-b9-tail-killed',
        'T0': 'pr-t0-edges', 'T004': 'pr-t004-dyadic-period', 'TB': 'pr-tb-first-one', 'H1': 'pr-h1-balanced', 'H2': 'pr-h2-always-doubles',
        'H4': 'pr-h4-nondecreasing', 'TL': 'pr-tl-repeat-or-double', 'TN': 'pr-tn-no-triple-double', 'H14': 'pr-h14-half-period-one',
        'TR': 'pr-tr-left-dyadic', 'H23': 'pr-h23-left-period-8', 'H9': 'pr-h9-discrepancy-root', 'H13': 'pr-h13-run-log-bound',
        'H21': 'pr-h21-agreement-44', 'TQ': 'pr-tq-agreement-runs'}
LINK.update({aid: pid for pid, _, aid, *_ in fc.CLAIMS})
LINK.update({aid: pid for pid, _, aid, *_ in fc.DECIDED})
# ============================ caches on the load-bearing nodes ============================
# Every ledger read (Assertions, Assessments, Dashboards, the explorer) goes through these fields, and
# Postgres recomputes the whole model chain behind them on every read. Each becomes
# IF({{IsCached}}=1, {{<Field>Cache}}, <formula>); loop_tools.build() fills the caches from a fresh
# compile and every save clears the flags, so a cached value is always the current computed value.
CACHE = {
    'Runs': ['IsLightConeExact', 'IsPrizeSetup'],
    'RuleTableEntries': ['MatchesPolynomial'],
    'Cells': ['IsCenter', 'PrefixLength', 'Discrepancy', 'RunStart', 'RunLength', 'RunBoundHolds'],
    'LeftConsistencyChecks': ['IsConsistent'],
    'DiagonalPeriodTests': ['IsPurePeriod'],
    'Tolerances': ['LastExcursionTime', 'SettledAtHorizon'],
    'Algorithms': ['EffortHolds'],
    'AcceleratorClaims': ['IsMatch'],
    'TailCandidates': ['KillTime', 'IsKilled', 'KillExcess'],
    'PeriodTests': ['LastMismatchTime', 'LongestAgreementStreak', 'BoundedRefutationHolds', 'WindowCount', 'WindowFailureCount', 'WindowsHold'],
    'DiagonalFacts': ['Holds', 'IsDecided'],
    'PredicateInstances': ['InDomain', 'Holds', 'Witness'],
    'Predicates': ['QuantifierCount', 'UnboundedQuantifierCount', 'UnmodeledOperatorCount', 'IsFinitelyDecidable', 'IsComputable',
                   'RowCount', 'InstanceCount', 'HoldingCount', 'FailingCount', 'IsRefuted', 'IsVerified', 'FiniteVerdict'],
    'Assertions': ['IsModelLinked', 'ModelVerdict', 'EffectiveStatus', 'IsModelDecided', 'IsModelContradicted',
                   'StatusGroup', 'IsUsable', 'IsProofEligible'],
}
for tbl, names in CACHE.items():
    ensure_field(tbl, F(lt.CACHE_FLAG, 'integer', desc='1 when the *Cache fields of this row hold the last fresh compile (filled by loop_tools.build, cleared by every save).'))
    for name in names:
        f = next(x for x in book[tbl]['schema'] if x['name'] == name)
        if not f['formula'].startswith(lt.CACHED_PREFIX):
            f['formula'] = lt.CACHED_PREFIX + '{{%sCache}},%s)' % (name, f['formula'][1:])
        ensure_field(tbl, F(f'{name}Cache', f['datatype'], desc=f'Cached {name} from the last fresh compile; read by {name} while {lt.CACHE_FLAG} = 1.'))

loop_preds = {r['PredicateId'] for r in book['Predicates']['data'] if r.get('IntroducedInLoop')}
for a in book['Assertions']['data']:
    if a.get('Predicate') not in loop_preds:   # a loop's own claims keep the predicate the loop gave them
        a['Predicate'] = LINK.get(a['AssertionId'])

lt.save(book)
print({t: len(book[t]['data']) for t in OWNED})
