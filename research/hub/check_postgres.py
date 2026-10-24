"""Substrate conformance: every computed field of the Rule 30 model, Postgres (the running editor's
views) against compile-rulebook (the values written into the rulebook).

Needs the editor to have built the current rulebook (./start.sh editor, or loop_tools.build()).
Usage: python3 research/hub/check_postgres.py
"""
import ast, json, re, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt
# build_model.py is a script (importing it would rewrite the hub), so read its table list from source.
OWNED = ast.literal_eval(re.search(r'^OWNED = (\(.*?\))$', (Path(__file__).with_name('build_model.py')).read_text(), re.S | re.M).group(1))

# Fields that exist only to expose a documented substrate difference; the model reads a guarded field
# instead: KilledExcessMax and every field named *Raw hold an aggregate over a possibly empty set (gap 12).
KNOWN_GAPS = {('PeriodicWords', 'KilledExcessMax'): 'gap 12, read through MaxKillExcess'}
is_known_gap = lambda t, f: (t, f) in KNOWN_GAPS or f.endswith('Raw')
snake = lambda s: re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', s).lower()
book = lt.load()
total, skipped, bad = 0, 0, []

# A lookup has no defined value when its reference is empty, or when the value it reads is itself
# undefined (a lookup chained through an empty reference one level down): gap 10, transitively.
LOOKUP = {}
for t in OWNED:
    for f in book[t]['schema']:
        m = re.match(r'=INDEX\((\w+)!\{\{(\w+)\}\},MATCH\(\{\{(\w+)\}\}', f.get('formula', '')) if f['type'] == 'lookup' else None
        if m:
            LOOKUP[(t, f['name'])] = m.groups()   # (target table, target field, local reference)
PK = {t: book[t]['schema'][0]['name'] for t in OWNED}
ROWS = {t: {r[PK[t]]: r for r in book[t]['data']} for t in OWNED}
undefined = set()
changed = True
while changed:
    changed = False
    for (t, f), (tt, tf, ref) in LOOKUP.items():
        for key, r in ROWS[t].items():
            if (t, f, key) in undefined:
                continue
            target = r.get(ref)
            if target in (None, '') or (tt, tf, target) in undefined:
                undefined.add((t, f, key))
                changed = True
for t in OWNED:
    pk = book[t]['schema'][0]['name']
    computed = [f['name'] for f in book[t]['schema'] if f['type'] in ('calculated', 'lookup', 'aggregation')]
    pg = {r[snake(pk)]: r for r in json.load(urllib.request.urlopen(f'{lt.EDITOR_API}/api/tables/{t}', timeout=120))['rows']}
    if len(pg) != len(book[t]['data']):
        bad.append(f'{t}: {len(pg)} rows in Postgres, {len(book[t]["data"])} in the rulebook')
    for r in book[t]['data']:
        p = pg.get(r[pk], {})
        for f in computed:
            if is_known_gap(t, f) or (t, f, r[pk]) in undefined:
                skipped += 1
                continue
            a, b = r.get(f), p.get(snake(f))
            total += 1
            same = (a in (None, '') and b in (None, '')) or str(a) == str(b)
            if not same:
                try:
                    same = abs(float(a) - float(b)) < 1e-9
                except (TypeError, ValueError):
                    pass
            if not same:
                bad.append(f'{t}.{f}[{r[pk]}]: rulebook {a!r}, postgres {b!r}')
by_field = {}
for b in bad:
    by_field[b.split('[')[0]] = by_field.get(b.split('[')[0], 0) + 1
print(f'{total} computed values compared, {len(bad)} differ ({skipped} skipped: lookups through an empty reference, directly or chained, and documented gap fields)')
for k, n in sorted(by_field.items()):
    print(f'  {k}: {n}')
print('\n'.join(bad[:10]))
sys.exit(1 if bad else 0)
