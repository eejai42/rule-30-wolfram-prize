"""Shadle steps 6-10: the Rule 30 domain model, written into the hub.

The ledger (Assertions, Dependencies, Evidence, Loops ...) records claims ABOUT Rule 30. This
script adds Rule 30 itself, the way simpsons-paradox models studies, strata and case cells:
only structure and the problem's inputs are Data; every cell value, count and predicate verdict
is a formula over them. Vocabulary, glossary, narrative and scenarios: bootstrap/rule30-model/.

  The automaton      CellStates, Rules, Neighborhoods, RuleTableEntries
  The evolution      InitialConditions, SeedCells, Runs, TimeSteps, Columns, Cells
  Problem 1          Periods, PeriodTests, PeriodComparisons
  Problem 2          Tolerances, ToleranceChecks, ColorCounts
  Problem 3          MachineModels, Algorithms, Computations
  The logic          Variables, Predicates, Quantifiers, PredicateInstances
  Outside values     AcceleratorClaims (an optimizer's claimed cell values, checked here)
  Bridge to ledger   Assertions.Predicate

Rerunnable: every table it owns is replaced. Python decides no value or verdict here.
Usage: python3 research/hub/build_model.py && effortless build
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

DEPTH, MAX_PERIOD, TOLERANCES = 64, 24, ((1, 5), (1, 10), (1, 20))   # epsilon as an exact fraction
RUN = 'r30-seed'
OWNED = ('CellStates', 'Rules', 'Neighborhoods', 'RuleTableEntries', 'InitialConditions', 'SeedCells',
         'Runs', 'TimeSteps', 'Columns', 'Cells', 'Periods', 'PeriodTests', 'PeriodComparisons',
         'Tolerances', 'ToleranceChecks', 'ColorCounts', 'MachineModels', 'Algorithms', 'Computations',
         'Variables', 'Predicates', 'Quantifiers', 'PredicateInstances', 'AcceleratorClaims')


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
ptid = lambda p: f'{colid(0)}-p{p:02d}'
nbid = lambda n: f'n{n:03b}'
entid = lambda rule, n: f'{rule}-{nbid(n)}'

book = lt.load()
for t in OWNED:
    book.pop(t, None)
for t in ('Lattice', ):
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
book['Periods'] = table(
    'Candidate periods p >= 1 for Problem 1 (bounded at %d in the model; unbounded in the problem).' % MAX_PERIOD,
    KEY('PeriodId', 'p<length>.') + [
        F('Length', 'integer', desc='The period p.', nullable=False),
        AGG('TestCount', '=COUNTIFS(PeriodTests!{{Period}},{{PeriodId}})', 'Columns tested against this period.'),
    ],
    [{'PeriodId': f'p{p:02d}', 'Length': p} for p in range(1, MAX_PERIOD + 1)])

book['PeriodTests'] = table(
    "Is this column eventually periodic with this period? Every onset T up to the last mismatch is refuted; onsets after it survive only because the horizon ends. Problem 1 says every (p, T) is refuted.",
    KEY('PeriodTestId', '<column>-p<period>.') + [
        REL('Column', 'Columns', 'The column tested.', False),
        REL('Period', 'Periods', 'The period p.', False),
        LK('PeriodLength', 'Periods', 'Period', 'PeriodId', 'Length', 'p.'),
        LK('Depth', 'Columns', 'Column', 'ColumnId', 'Depth', 'The horizon.'),
        AGG('ComparisonCount', '=COUNTIFS(PeriodComparisons!{{PeriodTest}},{{PeriodTestId}})', 'Comparisons c(t) vs c(t + p) inside the horizon.'),
        AGG('MismatchCount', '=COUNTIFS(PeriodComparisons!{{PeriodTest}},{{PeriodTestId}},PeriodComparisons!{{IsMismatch}},1)', 'Comparisons with c(t + p) != c(t).'),
        AGG('LastMismatchTime', '=MAXIFS(PeriodComparisons!{{Time}},PeriodComparisons!{{PeriodTest}},{{PeriodTestId}},PeriodComparisons!{{IsMismatch}},1)', 'The witness: the last t with c(t + p) != c(t). Every onset T <= it is refuted.'),
        AGG('LongestAgreementStreak', '=MAXIFS(PeriodComparisons!{{AgreementStreak}},PeriodComparisons!{{PeriodTest}},{{PeriodTestId}})', 'Longest stretch on which the column looked p-periodic.'),
        CALC('FirstSurvivingOnset', '={{LastMismatchTime}}+1', 'The first onset the horizon cannot refute.'),
        CALC('FinalAgreementLength', '={{Depth}}-({{PeriodLength}}+{{LastMismatchTime}})', 'Matching comparisons after the last mismatch, up to the horizon.'),
        CALC('OnsetBound', '=INT(({{Depth}}-{{PeriodLength}})/2)', 'Bounded form of Problem 1: every onset up to this must be refuted.'),
        CALC('BoundedRefutationHolds', '=IF({{LastMismatchTime}}>={{OnsetBound}},1,0)', 'Problem 1 instance: 1 when every onset T <= OnsetBound has a mismatch at some t >= T.'),
    ],
    [{'PeriodTestId': ptid(p), 'Column': colid(0), 'Period': f'p{p:02d}'} for p in range(1, MAX_PERIOD + 1)])

comps = []
for p in range(1, MAX_PERIOD + 1):
    for t in range(DEPTH + 1 - p):
        comps.append({'PeriodComparisonId': f'{ptid(p)}-t{t:03d}', 'PeriodTest': ptid(p), 'Time': t,
                      'EarlierCell': cid(t, 0), 'LaterCell': cid(t + p, 0),
                      'PreviousComparison': f'{ptid(p)}-t{t - 1:03d}' if t else None})
book['PeriodComparisons'] = table(
    'One comparison of a periodicity test: c(t) against c(t + p).',
    KEY('PeriodComparisonId', '<period test>-t<time>.') + [
        REL('PeriodTest', 'PeriodTests', 'The test this comparison belongs to.', False),
        F('Time', 'integer', desc='t.', nullable=False),
        REL('EarlierCell', 'Cells', 'The term c(t).', False),
        REL('LaterCell', 'Cells', 'The term c(t + p).', False),
        REL('PreviousComparison', 'PeriodComparisons', 'The comparison at t - 1; empty at t = 0.'),
        LK('EarlierValue', 'Cells', 'EarlierCell', 'CellId', 'Value', 'c(t).'),
        LK('LaterValue', 'Cells', 'LaterCell', 'CellId', 'Value', 'c(t + p).'),
        CALC('IsMismatch', '=IF({{EarlierValue}}<>{{LaterValue}},1,0)', '1 when c(t + p) != c(t): refutes period p from every onset T <= t.'),
        LK('PriorAgreementStreak', 'PeriodComparisons', 'PreviousComparison', 'PeriodComparisonId', 'AgreementStreak', 'Streak through t - 1.'),
        CALC('AgreementStreak', '=IF({{IsMismatch}}=1,0,IF({{Time}}=0,1,{{PriorAgreementStreak}}+1))', 'Consecutive matching comparisons ending at t.'),
    ],
    comps)

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
    ('onset', 'T', "Onset of periodicity (Wolfram's i)", 'PeriodComparisons', 1),
    ('prefix-length', 'N', 'Number of terms averaged', 'Cells', 1),
    ('epsilon', 'eps', 'Margin around 1/2', 'Tolerances', 1),
    ('index', 'n', 'Index of the term to compute', 'Computations', 1),
    ('machine', 'm', 'Machine / algorithm', 'Algorithms', 1),
    ('neighborhood', 'pqr', 'Input neighborhood', 'Neighborhoods', 0),
    ('run-end', 'V', 'Last time step of a constant run', 'Cells', 1),
]
book['Variables'] = table(
    'The variables the predicates quantify over, the table whose rows are their values in the model, and whether their domain is infinite in the problem.',
    KEY('VariableId', 'Name of the variable.') + [
        F('Symbol', desc='How the problem writes it.'),
        F('Meaning', desc='What it ranges over.'),
        F('DomainTable', desc='The table whose rows are its values in the model (finite there).'),
        F('IsUnboundedInProblem', 'integer', desc='1 when its domain in the problem is infinite.', nullable=False),
        AGG('QuantifierCount', '=COUNTIFS(Quantifiers!{{Variable}},{{VariableId}})', 'Quantifiers binding it.'),
    ],
    [{'VariableId': v, 'Symbol': s, 'Meaning': m, 'DomainTable': d, 'IsUnboundedInProblem': u} for v, s, m, d, u in VARS])

PREDS = [
    ('pr-rule30-polynomial', 'Definition', 'RuleTableEntry',
     'ForAll[{p,q,r}, rule30[p,q,r] == Mod[p + q + r + q r, 2]]',
     "Rule 30's table is Wolfram's polynomial (equivalently left XOR (center OR right)).",
     'One instance per transition of rule 30.',
     [('for-all', 'neighborhood', '')]),
    ('pr-light-cone', 'Definition', 'Run',
     'ForAll[{i,t}, Abs[i] > t, x[i,t] == 0]',
     'From the single seed under a quiescent rule, every cell outside the light cone is white.',
     'One instance per run: the run satisfies the conditions that make the cone exact.',
     [('for-all', 'time', ''), ('for-all', 'position', 'Abs[i] > t')]),
    ('pr-p1-non-periodic', 'P1', 'PeriodTest',
     'NotExists[{p, i}, ForAll[t, t > i, c[t + p] == c[t]]]',
     'Problem 1: the center column is not eventually periodic.',
     'One instance per period p <= %d: every onset T <= (depth - p)/2 has a mismatch c(t+p) != c(t) at some t >= T.' % MAX_PERIOD,
     [('not-exists', 'period', 'p >= 1'), ('not-exists', 'onset', 'i >= 0'), ('for-all', 'time', 't > i')]),
    ('pr-k1-not-constant', 'Known result', 'PeriodTest',
     'NotExists[i, ForAll[t, t > i, c[t + 1] == c[t]]]',
     'The center column is not eventually constant (the period-1 case of Problem 1).',
     'One instance: the period-1 test.',
     [('not-exists', 'onset', 'i >= 0'), ('for-all', 'time', 't > i')]),
    ('pr-td-run-bounds', 'Theorem', 'Cell',
     'ForAll[{T, V}, (ForAll[t, T <= t <= V, c[t] == 1] => V <= 2T + 1) && (ForAll[t, T <= t <= V, c[t] == 0] => V <= 4T + 5)]',
     'Theorem D: a black center run starting at T ends by 2T+1, a white one by 4T+5.',
     'One instance per center cell: the cell lies within the bound of the run it belongs to.',
     [('for-all', 'onset', 'run start T'), ('for-all', 'run-end', 'V >= T'), ('for-all', 'time', 'T <= t <= V')]),
    ('pr-p2-equal-frequency', 'P2', 'Tolerance',
     'DiscreteLimit[Total[c[t]]/t, t -> Infinity] == 1/2',
     'Problem 2: each color occurs on average equally often in the center column.',
     'One instance per tolerance epsilon: the density of the whole computed prefix is within epsilon of 1/2.',
     [('for-all', 'epsilon', 'eps > 0'), ('exists', 'prefix-length', 'N0'), ('for-all', 'prefix-length', 'N > N0')]),
    ('pr-p3-effort', 'P3', 'Algorithm',
     'NotExists[m, ForAll[n, machine[m][n][[1]] == c[n]] && Limsup[machine[m][n][[2]]/n, n -> Infinity] < Infinity]',
     'Problem 3: no admissible machine computes c(n) with effort O(n) (the displayed predicate; the prose says "at least O(n)").',
     'One instance per algorithm: an admissible algorithm\'s effort ratio still grows at the horizon.',
     [('not-exists', 'machine', 'does not store the answer'), ('for-all', 'index', 'n >= 1'), ('limsup', 'index', 'n -> Infinity')]),
]
book['Predicates'] = table(
    'The properties stated about the model: the definitions, the known results and the three prize problems. Each has a formal statement, quantifiers, and bounded instances computed from the model.',
    KEY('PredicateId', 'Name of the predicate.') + [
        F('Problem', desc='Definition, Known result, Theorem, or the prize problem it is (P1, P2, P3).'),
        F('InstanceKind', desc='The table whose rows are its bounded instances.'),
        F('Formal', desc='The statement in Wolfram Language notation.'),
        F('Statement', desc='The statement in words.'),
        F('InstanceMeaning', desc='What one bounded instance asserts.'),
        AGG('QuantifierCount', '=COUNTIFS(Quantifiers!{{Predicate}},{{PredicateId}})', 'Quantifiers in the statement.'),
        AGG('UnboundedQuantifierCount', '=SUMIFS(Quantifiers!{{IsUnbounded}},Quantifiers!{{Predicate}},{{PredicateId}})', 'Quantifiers over an infinite domain.'),
        CALC('IsFinitelyDecidable', '=IF({{UnboundedQuantifierCount}}=0,1,0)', '1 when the model can decide the full statement, not only bounded instances.'),
        AGG('InstanceCount', '=COUNTIFS(PredicateInstances!{{Predicate}},{{PredicateId}})', 'Bounded instances in the model.'),
        AGG('HoldingCount', '=SUMIFS(PredicateInstances!{{Holds}},PredicateInstances!{{Predicate}},{{PredicateId}})', 'Instances that hold.'),
        CALC('FailingCount', '={{InstanceCount}}-{{HoldingCount}}', 'Instances that fail.'),
        CALC('FiniteVerdict', '=IF({{InstanceCount}}=0,"NO INSTANCES",IF({{FailingCount}}=0,"HOLDS ON EVERY INSTANCE",CONCAT("FAILS ON ",{{FailingCount}}," OF ",{{InstanceCount}})))', 'What the model says about its bounded instances. Never a verdict on an unbounded statement.', 'string'),
        AGG('AssertionCount', '=COUNTIFS(Assertions!{{Predicate}},{{PredicateId}})', 'Ledger claims about this predicate.'),
    ],
    [{'PredicateId': pid, 'Problem': prob, 'InstanceKind': kind, 'Formal': formal, 'Statement': st, 'InstanceMeaning': im}
     for pid, prob, kind, formal, st, im, _ in PREDS])

book['Quantifiers'] = table(
    'One quantifier of a predicate: the binder, the variable it binds and its condition.',
    KEY('QuantifierId', '<predicate>-q<order>.') + [
        REL('Predicate', 'Predicates', 'The predicate.', False),
        F('Position', 'integer', desc='Order in the statement, outermost first.', nullable=False),
        F('Binder', desc='for-all, exists, not-exists, limit or limsup.'),
        REL('Variable', 'Variables', 'The variable bound.', False),
        F('Condition', desc='The restriction on the variable, if any.'),
        LK('Symbol', 'Variables', 'Variable', 'VariableId', 'Symbol', 'How the problem writes the variable.', 'string'),
        LK('DomainTable', 'Variables', 'Variable', 'VariableId', 'DomainTable', 'The table holding its values in the model.', 'string'),
        LK('IsUnbounded', 'Variables', 'Variable', 'VariableId', 'IsUnboundedInProblem', '1 when it ranges over an infinite domain.'),
    ],
    [{'QuantifierId': f'{pid}-q{k + 1}', 'Predicate': pid, 'Position': k + 1, 'Binder': b, 'Variable': v, 'Condition': c}
     for pid, *_, qs in PREDS for k, (b, v, c) in enumerate(qs)])

inst = [{'PredicateInstanceId': f'pr-rule30-polynomial-{nbid(n)}', 'Predicate': 'pr-rule30-polynomial', 'RuleTableEntry': entid('rule-30', n)} for n in range(7, -1, -1)]
inst.append({'PredicateInstanceId': f'pr-light-cone-{RUN}', 'Predicate': 'pr-light-cone', 'Run': RUN})
inst += [{'PredicateInstanceId': f'pr-p1-non-periodic-p{p:02d}', 'Predicate': 'pr-p1-non-periodic', 'PeriodTest': ptid(p)} for p in range(1, MAX_PERIOD + 1)]
inst.append({'PredicateInstanceId': 'pr-k1-not-constant-p01', 'Predicate': 'pr-k1-not-constant', 'PeriodTest': ptid(1)})
inst += [{'PredicateInstanceId': f'pr-td-run-bounds-t{t:03d}', 'Predicate': 'pr-td-run-bounds', 'Cell': cid(t, 0)} for t in range(DEPTH + 1)]
inst += [{'PredicateInstanceId': f'pr-p2-equal-frequency-eps-{a}-{b}', 'Predicate': 'pr-p2-equal-frequency', 'Tolerance': f'eps-{a}-{b}'} for a, b in TOLERANCES]
inst += [{'PredicateInstanceId': f'pr-p3-effort-{a}', 'Predicate': 'pr-p3-effort', 'Algorithm': a} for a in ('light-cone-simulation', 'answer-table')]
for r in inst:
    for k in ('RuleTableEntry', 'Run', 'PeriodTest', 'Cell', 'Tolerance', 'Algorithm'):
        r.setdefault(k, None)
book['PredicateInstances'] = table(
    'One bounded instance of a predicate, pointing at the model row that decides it. This is the roof all predicates share: every verdict here is computed from the cells.',
    KEY('PredicateInstanceId', '<predicate>-<instance>.') + [
        REL('Predicate', 'Predicates', 'The predicate.', False),
        LK('InstanceKind', 'Predicates', 'Predicate', 'PredicateId', 'InstanceKind', 'Which of the references below decides it.', 'string'),
        REL('RuleTableEntry', 'RuleTableEntries', 'Deciding row, for a rule-table predicate.'),
        REL('Run', 'Runs', 'Deciding row, for a run predicate.'),
        REL('PeriodTest', 'PeriodTests', 'Deciding row, for a Problem 1 predicate.'),
        REL('Cell', 'Cells', 'Deciding row, for a cell predicate.'),
        REL('Tolerance', 'Tolerances', 'Deciding row, for a Problem 2 predicate.'),
        REL('Algorithm', 'Algorithms', 'Deciding row, for a Problem 3 predicate.'),
        LK('EntryHolds', 'RuleTableEntries', 'RuleTableEntry', 'RuleTableEntryId', 'MatchesPolynomial', 'The transition matches the polynomial.'),
        LK('RunHolds', 'Runs', 'Run', 'RunId', 'IsLightConeExact', 'The run is light-cone exact.'),
        LK('PeriodTestHolds', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'BoundedRefutationHolds', 'Every onset up to the bound is refuted.'),
        LK('PeriodTestWitness', 'PeriodTests', 'PeriodTest', 'PeriodTestId', 'LastMismatchTime', 'The last mismatch.'),
        LK('CellHolds', 'Cells', 'Cell', 'CellId', 'RunBoundHolds', 'The cell respects the Theorem D bound.'),
        LK('ToleranceHolds', 'Tolerances', 'Tolerance', 'ToleranceId', 'SettledAtHorizon', 'The density at the horizon is within epsilon.'),
        LK('ToleranceWitness', 'Tolerances', 'Tolerance', 'ToleranceId', 'LastExcursionTime', 'The last excursion.'),
        LK('AlgorithmHolds', 'Algorithms', 'Algorithm', 'AlgorithmId', 'EffortHolds', 'The algorithm shows no sign of O(n) effort.'),
        CALC('Holds', '=IF({{InstanceKind}}="RuleTableEntry",{{EntryHolds}},IF({{InstanceKind}}="Run",{{RunHolds}},IF({{InstanceKind}}="PeriodTest",{{PeriodTestHolds}},IF({{InstanceKind}}="Cell",{{CellHolds}},IF({{InstanceKind}}="Tolerance",{{ToleranceHolds}},IF({{InstanceKind}}="Algorithm",{{AlgorithmHolds}},0))))))', '1 when the instance holds, read from its deciding row.'),
    ],
    inst)

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


# ============================ bridges into the ledger ============================
def ensure_field(tbl, field):
    sch = book[tbl]['schema']
    sch[:] = [f for f in sch if f['name'] != field['name']] + [field]


ensure_field('Evidence', AGG('ClaimCount', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}})', 'Cell values this evidence file claims.'))
ensure_field('Evidence', AGG('ClaimMismatchCount', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}},AcceleratorClaims!{{IsMatch}},0)', 'Claimed values the model computes differently. Must be 0.'))
ensure_field('Assertions', REL('Predicate', 'Predicates', 'The modeled predicate this claim is about, if any.'))
ensure_field('Assertions', LK('PredicateVerdict', 'Predicates', 'Predicate', 'PredicateId', 'FiniteVerdict', "The model's verdict on the predicate's bounded instances.", 'string'))
ensure_field('Assertions', LK('PredicateIsFinitelyDecidable', 'Predicates', 'Predicate', 'PredicateId', 'IsFinitelyDecidable', '1 when the model can decide the full statement.'))
book['Dashboards']['schema'] = [f for f in book['Dashboards']['schema'] if f['name'] != 'PredicateCount']  # bare COUNT breaks rulebook-to-postgres (docs/toolchain-gaps.md gap 6)
for r in book['Dashboards']['data']:
    r.pop('PredicateCount', None)
ensure_field('Dashboards', AGG('ConformanceMismatchCount', '=COUNTIFS(AcceleratorClaims!{{IsMatch}},0)', 'Optimizer claims the model disagrees with. Must be 0.'))
ensure_field('Dashboards', AGG('PredicatesFailingAnInstance', '=COUNTIFS(Predicates!{{IsFinitelyDecidable}},0,Predicates!{{FailingCount}},">0")', 'Predicates with at least one failing bounded instance.'))
LINK = {'P1': 'pr-p1-non-periodic', 'P2': 'pr-p2-equal-frequency', 'P3': 'pr-p3-effort', 'K1': 'pr-k1-not-constant', 'TD': 'pr-td-run-bounds'}
for a in book['Assertions']['data']:
    a['Predicate'] = LINK.get(a['AssertionId'])

lt.save(book)
print({t: len(book[t]['data']) for t in OWNED})
