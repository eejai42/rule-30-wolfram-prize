"""Minimal Rule 30 lattice rulebook used to reproduce the toolchain gaps in docs/toolchain-gaps.md.

Usage: python3 make_lattice_rulebook.py <T> <out.json>
Rules: one row, the rule number as data (30). Cells: the triangle |i| <= t <= T, each cell with
FKs to its three parents at t-1 (a 'zero' sentinel row outside the cone) and
Value = the rule-number bit selected by the parents' neighborhood. Row-level acyclic (time
strictly decreases along every FK); field-level, Cells.Value depends on Cells.Value of other rows.
"""
import json, sys

T, out = int(sys.argv[1]), sys.argv[2]
cid = lambda t, i: f"t{t:03d}p{i:+04d}"


def f(name, dt='string', ty='raw', formula=None, rel=None):
    d = {'name': name, 'datatype': dt, 'type': ty, 'nullable': True, 'Description': name}
    if formula:
        d['formula'] = formula
    if rel:
        d['RelatedTo'] = rel
    return d


LK = lambda fk, fld: f'=INDEX(Cells!{{{{{fld}}}}},MATCH({{{{{fk}}}}},Cells!{{{{CellId}}}},0))'
rows = [{'CellId': 'zero', 'Time': -1, 'Position': 0, 'Rule': 'rule-30'}]
for t in range(T + 1):
    for i in range(-t, t + 1):
        r = {'CellId': cid(t, i), 'Time': t, 'Position': i, 'Rule': 'rule-30'}
        if t > 0:
            for nm, j in (('LeftParent', i - 1), ('CenterParent', i), ('RightParent', i + 1)):
                r[nm] = cid(t - 1, j) if abs(j) <= t - 1 else 'zero'
        rows.append(r)
book = {
    '$schema': 'x', 'Name': 'Rule30LatticeRepro', 'Description': 'Toolchain repro: row-recursive lattice.',
    'Rules': {'Description': 'Elementary CA rules as data.', 'schema': [f('RuleId'), f('Name', ty='calculated', formula='={{RuleId}}'), f('RuleNumber', 'integer')],
              'data': [{'RuleId': 'rule-30', 'RuleNumber': 30}]},
    'Cells': {'Description': 'Lattice cells.', 'schema': [
        f('CellId'), f('Name', ty='calculated', formula='={{CellId}}'), f('Time', 'integer'), f('Position', 'integer'),
        f('Rule', ty='relationship', rel='Rules'),
        f('LeftParent', ty='relationship', rel='Cells'), f('CenterParent', ty='relationship', rel='Cells'), f('RightParent', ty='relationship', rel='Cells'),
        f('RuleNumber', 'integer', 'lookup', '=INDEX(Rules!{{RuleNumber}},MATCH({{Rule}},Rules!{{RuleId}},0))'),
        f('LeftValue', 'integer', 'lookup', LK('LeftParent', 'Value')), f('CenterValue', 'integer', 'lookup', LK('CenterParent', 'Value')), f('RightValue', 'integer', 'lookup', LK('RightParent', 'Value')),
        f('Neighborhood', 'integer', 'calculated', '=4*IF({{LeftValue}}=1,1,0)+2*IF({{CenterValue}}=1,1,0)+IF({{RightValue}}=1,1,0)'),
        f('Value', 'integer', 'calculated', '=IF({{Time}}<0,0,IF({{Time}}=0,IF({{Position}}=0,1,0),MOD(INT({{RuleNumber}}/POWER(2,{{Neighborhood}})),2)))'),
    ], 'data': rows},
}
json.dump(book, open(out, 'w'), indent=1)
print(len(rows), 'cells')
