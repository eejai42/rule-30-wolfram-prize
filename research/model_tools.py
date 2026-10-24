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

# (OperatorId, Symbol, Kind, Arity). Kind decides how Terms.Rendered writes the term.
OPERATORS = [
    ('for-all', 'ForAll', 'binder', 2), ('exists', 'Exists', 'binder', 2), ('not-exists', 'NotExists', 'binder', 2),
    ('limit', 'DiscreteLimit', 'binder', 2), ('limsup', 'Limsup', 'binder', 2),
    ('and', '&&', 'infix', 2), ('or', '||', 'infix', 2), ('implies', '=>', 'infix', 2),
    ('eq', '==', 'infix', 2), ('neq', '!=', 'infix', 2), ('le', '<=', 'infix', 2), ('lt', '<', 'infix', 2),
    ('ge', '>=', 'infix', 2), ('gt', '>', 'infix', 2), ('plus', '+', 'infix', 2), ('minus', '-', 'infix', 2),
    ('times', '*', 'infix', 2), ('divide', '/', 'infix', 2), ('tends-to', '->', 'infix', 2),
    ('not', '!', 'prefix', 1),
    ('c', 'c', 'apply', 1), ('x', 'x', 'apply', 2), ('abs', 'Abs', 'apply', 1), ('mod', 'Mod', 'apply', 2),
    ('rule30', 'rule30', 'apply', 3), ('ones', 'Ones', 'apply', 1), ('length', 'Length', 'apply', 1),
    ('nonconstant', 'Nonconstant', 'apply', 1), ('least-period', 'LeastPeriod', 'apply', 1),
    ('tail-c', 'cTail', 'apply', 3), ('tail-x', 'xTail', 'apply', 4), ('excess', 'KillExcess', 'apply', 2),
    ('output', 'Output', 'apply', 2), ('effort', 'Effort', 'apply', 2), ('stores-answer', 'StoresAnswer', 'apply', 1),
    ('true', 'True', 'atom', 0), ('infinity', 'Infinity', 'atom', 0),
    ('var', '', 'var', 0), ('const', '', 'const', 0),
]
SYMBOL = {sym: oid for oid, sym, kind, _ in OPERATORS if kind not in ('var', 'const')}
SYMBOL.update({'var': 'var', 'const': 'const', 'true': 'true', 'infinity': 'infinity'})
ARITY = {oid: a for oid, _, _, a in OPERATORS}


def term_rows(prefix: str, tree, loop: str = '') -> tuple[str, list[dict]]:
    """Rows for one term tree, numbered in preorder. Returns (root term id, rows)."""
    out = []

    def walk(node):
        tid = f'{prefix}-{len(out) + 1:02d}'
        r = {'TermId': tid, 'TermOperator': None, 'Variable': None, 'Constant': None, 'BoundsVariable': 0,
             'Arg1': None, 'Arg2': None, 'Arg3': None, 'Arg4': None, 'IntroducedInLoop': loop or None}
        out.append(r)
        head = node[0]
        if head == 'var':
            r.update(TermOperator='var', Variable=node[1])
        elif head == 'const':
            r.update(TermOperator='const', Constant=node[1])
        elif head.rstrip('!') in ('ForAll', 'Exists', 'NotExists', 'DiscreteLimit', 'Limsup'):
            r.update(TermOperator=SYMBOL[head.rstrip('!')], Variable=node[1], BoundsVariable=int(head.endswith('!')))
            r['Arg1'], r['Arg2'] = walk(node[2]), walk(node[3])
        else:
            op = SYMBOL[head]
            assert len(node) - 1 == ARITY[op], node
            r['TermOperator'] = op
            for k, arg in enumerate(node[1:], 1):
                r[f'Arg{k}'] = walk(arg)
        return tid

    root = walk(tree)
    return root, out


def predicate_row(pid, problem, kind, root, statement, meaning, failure_refutes, slope=None, intercept=None, loop=''):
    return {'PredicateId': pid, 'Problem': problem, 'InstanceKind': kind, 'RootTerm': root, 'Statement': statement,
            'InstanceMeaning': meaning, 'FailureRefutes': failure_refutes, 'BoundSlope': slope, 'BoundIntercept': intercept,
            'IntroducedInLoop': loop or None}


INSTANCE_REFS = ('RuleTableEntry', 'Run', 'PeriodicityCandidate', 'MismatchWindow', 'Cell', 'LeftConsistencyCheck',
                 'TailCandidate', 'Tolerance', 'Algorithm')


def instance_row(pid, suffix, ref, key, loop=''):
    r = {'PredicateInstanceId': f'{pid}-{suffix}', 'Predicate': pid, 'IntroducedInLoop': loop or None}
    for k in INSTANCE_REFS:
        r[k] = key if k == ref else None
    return r


def add_loop_predicate(book, pid, problem, kind, tree, statement, meaning, failure_refutes, ref, keys, slope=None, intercept=None):
    """A model-native hypothesis: its statement as terms, its instances as rows. The build decides it."""
    loop = lt.CURRENT_LOOP
    assert loop, 'add_loop_predicate runs inside run_loop'
    assert not lt.has(book, 'Predicates', pid), pid
    root, terms = term_rows(pid, tree, loop)
    lt.rows(book, 'Terms').extend(terms)
    lt.rows(book, 'Predicates').append(predicate_row(pid, problem, kind, root, statement, meaning, failure_refutes, slope, intercept, loop))
    lt.rows(book, 'PredicateInstances').extend(instance_row(pid, k, ref, k, loop) for k in keys)
    return pid
