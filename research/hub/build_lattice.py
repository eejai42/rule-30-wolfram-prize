"""Stage 1 of moving Rule 30 into the rulebook: the lattice itself, and the accelerator contract.

Adds (replacing any earlier copy of these three tables):
  Rules              the rule as Data (RuleNumber 30).
  Cells              the light-cone triangle 0 <= t <= DEPTH, |i| <= t. The single seed is Data
                     (InitialValue on the t = 0 cells); every later Value is the rule bit selected
                     by the three parent lookups. RightOffset = t - i is the right-edge diagonal k
                     (y_k), LeftOffset = t + i the left-edge diagonal (w_k); IsCenter marks c(t).
  AcceleratorClaims  values an optimizer outside the rulebook claims for a cell, entered as Data.
                     The rulebook looks up its own Value and decides IsMatch. Evidence aggregates
                     ClaimCount / ClaimMismatchCount; the Dashboard shows ConformanceMismatchCount.

Claims added here: the center bits c(0..DEPTH) from E17 (loop 5's 2^20-bit evolution) and the
right-edge diagonal values y_k(t), k <= 8, t <= DEPTH, recomputed by research/diagonals.py and
saved as research/hub/diagonal_claims.json (E30).

Python is only the optimizer here; nothing below decides a value or a verdict.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
import diagonals as dg

DEPTH = 64
HERE = Path(__file__).resolve().parent
cid = lambda t, i: f"t{t:03d}p{i:+04d}"


def F(name, dt='string', ty='raw', formula=None, rel=None, desc='', nullable=True):
    f = {'name': name, 'datatype': dt, 'type': ty, 'nullable': nullable, 'Description': desc}
    if formula:
        f['formula'] = formula
    if rel:
        f['RelatedTo'] = rel
    return f


LK = lambda fk, fld: f'=INDEX(Cells!{{{{{fld}}}}},MATCH({{{{{fk}}}}},Cells!{{{{CellId}}}},0))'

book = lt.load()
for t in ('AcceleratorClaims', 'Cells', 'Rules'):
    book.pop(t, None)

book['Rules'] = {
    'Description': 'Elementary cellular-automaton rules, as data. The bit for neighborhood n (left*4 + center*2 + right) is bit n of RuleNumber.',
    'schema': [
        F('RuleId', desc='Rule identifier.', nullable=False),
        F('Name', ty='calculated', formula='={{RuleId}}', desc='Display alias.'),
        F('RuleNumber', 'integer', desc='Wolfram rule number, 0..255.', nullable=False),
    ],
    'data': [{'RuleId': 'rule-30', 'RuleNumber': 30}],
}

rows = []
for t in range(DEPTH + 1):
    for i in range(-t, t + 1):
        r = {'CellId': cid(t, i), 'Time': t, 'Position': i, 'Rule': 'rule-30'}
        if t == 0:
            r['InitialValue'] = 1 if i == 0 else 0
        else:
            for nm, j in (('LeftParent', i - 1), ('CenterParent', i), ('RightParent', i + 1)):
                r[nm] = cid(t - 1, j) if abs(j) <= t - 1 else None
        rows.append(r)

book['Cells'] = {
    'Description': f'The Rule 30 light cone from a single seed, 0 <= t <= {DEPTH}. Cells outside the cone are 0 and have no row; a parent outside the cone is an empty reference.',
    'schema': [
        F('CellId', desc='t<time>p<position>.', nullable=False),
        F('Name', ty='calculated', formula='={{CellId}}', desc='Display alias.'),
        F('Time', 'integer', desc='Time step t >= 0.', nullable=False),
        F('Position', 'integer', desc='Position i, |i| <= t.', nullable=False),
        F('InitialValue', 'integer', desc='The seed: set only on t = 0 cells (1 at i = 0).'),
        F('Rule', ty='relationship', rel='Rules', desc='The rule this cell evolves under.'),
        F('LeftParent', ty='relationship', rel='Cells', desc='Cell (t-1, i-1); empty outside the cone.'),
        F('CenterParent', ty='relationship', rel='Cells', desc='Cell (t-1, i); empty outside the cone.'),
        F('RightParent', ty='relationship', rel='Cells', desc='Cell (t-1, i+1); empty outside the cone.'),
        F('RuleNumber', 'integer', 'lookup', '=INDEX(Rules!{{RuleNumber}},MATCH({{Rule}},Rules!{{RuleId}},0))', desc='The rule number.'),
        F('LeftValue', 'integer', 'lookup', LK('LeftParent', 'Value'), desc='Value of the left parent (blank outside the cone).'),
        F('CenterValue', 'integer', 'lookup', LK('CenterParent', 'Value'), desc='Value of the center parent.'),
        F('RightValue', 'integer', 'lookup', LK('RightParent', 'Value'), desc='Value of the right parent.'),
        F('Neighborhood', 'integer', 'calculated', '=4*IF({{LeftValue}}=1,1,0)+2*IF({{CenterValue}}=1,1,0)+IF({{RightValue}}=1,1,0)', desc='left*4 + center*2 + right; a blank parent counts as 0.'),
        F('Value', 'integer', 'calculated', '=IF({{Time}}=0,{{InitialValue}},MOD(INT({{RuleNumber}}/POWER(2,{{Neighborhood}})),2))', desc='The cell: the seed at t = 0, otherwise bit Neighborhood of RuleNumber.'),
        F('RightOffset', 'integer', 'calculated', '={{Time}}-{{Position}}', desc='k of the right-edge diagonal y_k(t) = x(t-k, t) this cell lies on.'),
        F('LeftOffset', 'integer', 'calculated', '={{Time}}+{{Position}}', desc='k of the left-edge diagonal w_k(t) = x(-t+k, t) this cell lies on.'),
        F('IsCenter', 'integer', 'calculated', '=IF({{Position}}=0,1,0)', desc='1 on the center column c(t) = x(0, t).'),
        F('ClaimCount', 'integer', 'aggregation', '=COUNTIFS(AcceleratorClaims!{{Cell}},{{CellId}})', desc='Accelerator claims made about this cell.'),
    ],
    'data': rows,
}

# --- accelerator claims -------------------------------------------------------
center_ev = lt.row(book, 'Evidence', 'E17')
center_txt = (lt.ROOT / center_ev['Path']).read_text().strip()
assert lt.sha256_file(lt.ROOT / center_ev['Path']) == center_ev['Sha256']
claims = []
for t in range(DEPTH + 1):
    claims.append({'AcceleratorClaimId': f'E17-{cid(t, 0)}', 'Cell': cid(t, 0), 'ClaimedValue': int(center_txt[t]), 'Source': 'E17'})

W, _ = dg.words(8)
diag = []
for k in range(0, 9):
    w, P = W[k]
    for t in range(DEPTH + 1):
        if k <= 2 * t:
            diag.append({'k': k, 't': t, 'value': (w >> (t % P)) & 1})
(HERE / 'diagonal_claims.json').write_text(json.dumps({'producer': 'research/diagonals.py words(8)', 'depth': DEPTH, 'claims': diag}, indent=0) + '\n')
lt.add_evidence(book, 'E30', 'research/hub/diagonal_claims.json')
for c in diag:
    claims.append({'AcceleratorClaimId': f"E30-{cid(c['t'], c['t'] - c['k'])}", 'Cell': cid(c['t'], c['t'] - c['k']), 'ClaimedValue': c['value'], 'Source': 'E30'})

book['AcceleratorClaims'] = {
    'Description': 'A value an optimizer outside the rulebook claims for a lattice cell. The rulebook computes the cell itself and decides whether the claim matches.',
    'schema': [
        F('AcceleratorClaimId', desc='<evidence>-<cell>.', nullable=False),
        F('Name', ty='calculated', formula='={{AcceleratorClaimId}}', desc='Display alias.'),
        F('Cell', ty='relationship', rel='Cells', desc='The lattice cell the claim is about.'),
        F('Source', ty='relationship', rel='Evidence', desc='The evidence file the claimed value comes from.'),
        F('ClaimedValue', 'integer', desc='The value the optimizer reports.', nullable=False),
        F('HubValue', 'integer', 'lookup', '=INDEX(Cells!{{Value}},MATCH({{Cell}},Cells!{{CellId}},0))', desc='The value the rulebook computes for that cell.'),
        F('IsMatch', 'integer', 'calculated', '=IF({{ClaimedValue}}={{HubValue}},1,0)', desc='1 when the optimizer agrees with the rulebook.'),
    ],
    'data': claims,
}

# Evidence: per-file conformance; Dashboard: overall mismatches
ev_schema = book['Evidence']['schema']
if not any(f['name'] == 'ClaimCount' for f in ev_schema):
    ev_schema += [
        F('ClaimCount', 'integer', 'aggregation', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}})', desc='Lattice values this evidence file claims.'),
        F('ClaimMismatchCount', 'integer', 'aggregation', '=COUNTIFS(AcceleratorClaims!{{Source}},{{EvidenceId}},AcceleratorClaims!{{IsMatch}},0)', desc='Claimed values the rulebook computes differently. Must be 0.'),
    ]
ds = book['Dashboards']['schema']
if not any(f['name'] == 'ConformanceMismatchCount' for f in ds):
    ds.append(F('ConformanceMismatchCount', 'integer', 'aggregation', '=COUNTIFS(AcceleratorClaims!{{IsMatch}},0)', desc='Optimizer claims the rulebook disagrees with, across all evidence. Must be 0.'))

lt.save(book)
print(f'Rules 1, Cells {len(rows)}, AcceleratorClaims {len(claims)} (center {DEPTH + 1}, diagonal {len(diag)})')
