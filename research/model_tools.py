"""The formal side of the Rule 30 model: term trees for predicates, and loop-owned predicates.

A formal statement is authored as nested tuples and stored as rows of Terms, so its structure is
data and its text is computed by the build (Terms.Rendered), never typed:

  ('ForAll', 'time', <condition>, <body>)     a binder: operator, bound variable, condition, body
  ('ForAll!', 'time', <condition>, <body>)    the same binder, whose condition bounds the variable
  ('==', a, b) / ('c', t) / ('x', i, t)       an operator applied to its arguments
  ('var', 'time') / ('const', 3) / ('true',)  leaves

Used by research/hub/build_model.py for the core predicates, and by model-native loops through
add_loop_predicate(), which tags every row with the running loop so build_model.py keeps it.
"""
import loop_tools as lt

# (OperatorId, Symbol, Kind, Arity, IsModeled). Kind decides how Terms.Rendered writes the term;
# IsModeled is 1 when the model computes the operator's value (a table or field gives it meaning),
# 0 when it is only a named symbol so far: a statement using one is formal but not yet computable.
OPERATORS = [
    ('for-all', 'ForAll', 'binder', 2, 1), ('exists', 'Exists', 'binder', 2, 1), ('not-exists', 'NotExists', 'binder', 2, 1),
    ('limit', 'DiscreteLimit', 'binder', 2, 1), ('limsup', 'Limsup', 'binder', 2, 1),
    ('and', '&&', 'infix', 2, 1), ('or', '||', 'infix', 2, 1), ('implies', '=>', 'infix', 2, 1), ('iff', '<=>', 'infix', 2, 1),
    ('eq', '==', 'infix', 2, 1), ('neq', '!=', 'infix', 2, 1), ('le', '<=', 'infix', 2, 1), ('lt', '<', 'infix', 2, 1),
    ('ge', '>=', 'infix', 2, 1), ('gt', '>', 'infix', 2, 1), ('plus', '+', 'infix', 2, 1), ('minus', '-', 'infix', 2, 1),
    ('times', '*', 'infix', 2, 1), ('divide', '/', 'infix', 2, 1), ('tends-to', '->', 'infix', 2, 1), ('divides', '|', 'infix', 2, 1),
    ('not', '!', 'prefix', 1, 1),
    ('c', 'c', 'apply', 1, 1), ('x', 'x', 'apply', 2, 1), ('abs', 'Abs', 'apply', 1, 1), ('mod', 'Mod', 'apply', 2, 1),
    ('power', 'Power', 'apply', 2, 1), ('ceiling', 'Ceiling', 'apply', 1, 1), ('log2', 'Log2', 'apply', 1, 1),
    ('rule30', 'rule30', 'apply', 3, 1), ('ones', 'Ones', 'apply', 1, 1), ('length', 'Length', 'apply', 1, 1),
    ('nonconstant', 'Nonconstant', 'apply', 1, 1), ('least-period', 'LeastPeriod', 'apply', 1, 1),
    ('tail-c', 'cTail', 'apply', 3, 1), ('tail-x', 'xTail', 'apply', 4, 1), ('excess', 'KillExcess', 'apply', 2, 1),
    ('y', 'y', 'apply', 2, 1), ('w', 'w', 'apply', 2, 1), ('diag-period', 'P', 'apply', 1, 1), ('doubles', 'Eps', 'apply', 1, 1),
    ('ones-per-period', 'OnesPerPeriod', 'apply', 1, 1), ('first-one', 'FirstOne', 'apply', 1, 1),
    ('left-eventual-period', 'Pw', 'apply', 1, 1), ('agreement-run', 'AgreementRun', 'apply', 2, 1),
    ('maximal-run', 'MaximalRun', 'apply', 2, 1), ('eventually-periodic', 'EventuallyPeriodic', 'apply', 2, 1),
    ('output', 'Output', 'apply', 2, 1), ('effort', 'Effort', 'apply', 2, 1), ('stores-answer', 'StoresAnswer', 'apply', 1, 1),
    ('true', 'True', 'atom', 0, 1), ('infinity', 'Infinity', 'atom', 0, 1),
    ('var', '', 'var', 0, 1), ('const', '', 'const', 0, 1),
]
# Operators the formal statements of the ledger's claims need (research/hub/formal_claims.py).
UNMODELED_OPERATORS = [  # (OperatorId, Symbol, Kind, Arity): named symbols the model does not compute yet
    ('forcing-period', 'Q', 'apply', 1), ('forcing-word', 'q', 'apply', 2), ('antiderivative-period', 'AntiPeriod', 'apply', 1),
    ('forcing-parity', 'ForcingParity', 'apply', 1), ('odd-position-ones', 'OddPositionOnes', 'apply', 1), ('plateau-length', 'PlateauLength', 'apply', 1),
    ('step-output', 'StepOutput', 'apply', 2), ('left-input', 'LeftInput', 'apply', 1), ('rest-input', 'RestInput', 'apply', 1),
    ('function-apply', 'FApply', 'apply', 2), ('tuple4', 'Tuple4', 'apply', 4), ('cone-support', 'ConeSupport', 'atom', 0),
    ('first-arrival', 'FirstArrival', 'atom', 0), ('aperiodic-moving-diagonal', 'AperiodicMovingDiagonal', 'atom', 0),
    ('reported', 'Reported', 'apply', 1),
    ('relaxation-satisfiable', 'RelaxationSatisfiable', 'apply', 3), ('relaxation-count', 'RelaxationCount', 'apply', 3),
    ('consistent-row-count', 'ConsistentRowCount', 'apply', 3), ('tw-row-count', 'TWRowCount', 'apply', 2), ('zero-times', 'ZeroTimes', 'apply', 2),
    ('is-tw-row', 'IsTWRow', 'apply', 3), ('row-violates', 'RowViolates', 'apply', 4), ('exclusion-length', 'ExclusionLength', 'apply', 2),
    ('t-max', 'TMax', 'apply', 1), ('enumerated', 'Enumerated', 'apply', 2), ('single-zero-word', 'IsSingleZeroWord', 'apply', 1),
    ('constraint-degree', 'ConstraintDegree', 'apply', 2), ('common-killing-cell', 'HasCommonKillingCell', 'apply', 2),
    ('kill-time-star', 'KillTimeStar', 'apply', 2), ('death-window', 'DeathWindow', 'apply', 2), ('pinned-word', 'IsPinnedWord', 'apply', 1),
    ('first-pinned-onset', 'FirstPinnedOnset', 'apply', 1), ('pinned-window', 'PinnedWindow', 'apply', 1),
    ('settled-death-window', 'SettledDeathWindow', 'apply', 2), ('settled-frontier', 'SettledFrontier', 'apply', 1),
    ('left-consistent-prefix', 'LeftConsistentPrefix', 'apply', 2), ('seeded-kill-time', 'SeededKillTime', 'apply', 3),
    ('seeded-survivors', 'SeededSurvivors', 'apply', 2), ('window-language-size', 'WindowLanguageSize', 'apply', 2),
    ('in-window-language', 'InWindowLanguage', 'apply', 3), ('window-dies', 'WindowDies', 'apply', 3),
    ('death-ray-forced-cells', 'DeathRayForcedCells', 'apply', 2),
    ('is-supplied-output', 'IsSuppliedOutput', 'apply', 1), ('rerun', 'Rerun', 'apply', 1), ('supplied', 'Supplied', 'apply', 1),
    ('is-sqlite-cell', 'IsSqliteCell', 'apply', 1), ('sqlite-value', 'SqliteValue', 'apply', 1), ('cell-position', 'CellPosition', 'apply', 1),
    ('cell-time', 'CellTime', 'apply', 1), ('acid', 'ACID', 'atom', 0), ('order-independent', 'TransactionOrderIndependent', 'atom', 0),
    ('nested-aggregate', 'NestedAggregate', 'apply', 1), ('flat-aggregate', 'FlatAggregate', 'apply', 1),
]
MODELED_OPERATORS = [  # computed by the model or plain arithmetic/logic
    ('max', 'Max', 'apply', 2), ('floor', 'Floor', 'apply', 1), ('xor', 'Xor', 'apply', 2), ('or-bit', 'Or', 'apply', 2),
    ('left-onset', 'OnsetW', 'apply', 1), ('model-cell', 'ModelCell', 'apply', 2), ('word-01', '"01"', 'atom', 0), ('word-10', '"10"', 'atom', 0),
]
BINDERS = [('xor-sum', 'XorSum', 'binder', 2)]

OPERATORS += [o + (0,) for o in UNMODELED_OPERATORS] + [o + (1,) for o in MODELED_OPERATORS + BINDERS]
SYMBOL = {sym: oid for oid, sym, kind, _, _ in OPERATORS if kind not in ('var', 'const')}
SYMBOL.update({'var': 'var', 'const': 'const', 'true': 'true', 'infinity': 'infinity'})
ARITY = {oid: a for oid, _, _, a, _ in OPERATORS}
KIND = {oid: kind for oid, _, kind, _, _ in OPERATORS}
_syms = [sym for _, sym, kind, _, _ in OPERATORS if kind not in ('var', 'const')]
assert len(_syms) == len(set(_syms)), 'operator symbols must be unique'


def term_rows(prefix: str, tree, loop: str = '') -> tuple[str, list[dict]]:
    """Rows for one term tree, numbered in preorder. Returns (root term id, rows)."""
    out = []

    def walk(node):
        tid = f'{prefix}-{len(out) + 1:02d}'
        r = {'TermId': tid, 'BoundsVariable': 0, 'PredicateKey': prefix}
        if loop:
            r['IntroducedInLoop'] = loop
        out.append(r)
        head = node[0]
        if head == 'var':
            r.update(TermOperator='var', Variable=node[1])
        elif head == 'const':
            r.update(TermOperator='const', Constant=node[1])
        elif KIND.get(SYMBOL.get(head.rstrip('!'))) == 'binder':
            r.update(TermOperator=SYMBOL[head.rstrip('!')], Variable=node[1], BoundsVariable=int(head.endswith('!')))
            r['Arg1'], r['Arg2'] = walk(node[2]), walk(node[3])
        else:
            op = SYMBOL.get(head, head if head in ARITY else None)
            assert op, f'unknown operator {head!r}'
            assert len(node) - 1 == ARITY[op], node
            r['TermOperator'] = op
            for k, arg in enumerate(node[1:], 1):
                r[f'Arg{k}'] = walk(arg)
        return tid

    root = walk(tree)
    return root, out


def predicate_row(pid, problem, kind, root, statement, meaning, failure_refutes, slope=None, intercept=None, loop='',
                  covers_domain=0, domain_min=None):
    return {'PredicateId': pid, 'Problem': problem, 'InstanceKind': kind, 'RootTerm': root, 'Statement': statement,
            'InstanceMeaning': meaning, 'FailureRefutes': failure_refutes, 'BoundSlope': slope, 'BoundIntercept': intercept,
            'CoversDomain': covers_domain, 'DomainMin': domain_min, 'IntroducedInLoop': loop or None}


INSTANCE_REFS = ('RuleTableEntry', 'Run', 'PeriodTest', 'PeriodicityCandidate', 'MismatchWindow', 'Cell', 'LeftConsistencyCheck',
                 'TailCandidate', 'DiagonalPeriodTest', 'DiagonalFact', 'AcceleratorClaim', 'Tolerance', 'Algorithm')


def instance_row(pid, suffix, ref, key, loop=''):
    assert ref in INSTANCE_REFS, ref
    r = {'PredicateInstanceId': f'{pid}-{suffix}', 'Predicate': pid, ref: key}   # empty references are left out (smaller file)
    if loop:
        r['IntroducedInLoop'] = loop
    return r


def add_loop_predicate(book, pid, problem, kind, tree, statement, meaning, failure_refutes, ref, keys, slope=None, intercept=None,
                       covers_domain=1, domain_min=None):
    """A model-native hypothesis: its statement as terms, its instances as rows. The build decides it.

    covers_domain=1 says the instance rows enumerate the whole (bounded) domain of the statement, so
    holding on all of them verifies it; pass 0 when the rows are only a sample."""
    loop = lt.CURRENT_LOOP
    assert loop, 'add_loop_predicate runs inside run_loop'
    assert not lt.has(book, 'Predicates', pid), pid
    root, terms = term_rows(pid, tree, loop)
    lt.rows(book, 'Terms').extend(terms)
    lt.rows(book, 'Predicates').append(predicate_row(pid, problem, kind, root, statement, meaning, failure_refutes, slope, intercept, loop, covers_domain, domain_min))
    lt.rows(book, 'PredicateInstances').extend(instance_row(pid, k, ref, k, loop) for k in keys)
    return pid
