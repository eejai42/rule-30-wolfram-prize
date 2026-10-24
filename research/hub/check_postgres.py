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

snake = lambda s: re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', s).lower()
book = lt.load()
total, skipped, bad = 0, 0, []
for t in OWNED:
    pk = book[t]['schema'][0]['name']
    computed = [f['name'] for f in book[t]['schema'] if f['type'] in ('calculated', 'lookup', 'aggregation')]
    # A lookup through an empty reference has no defined value: compile-rulebook evaluates the
    # target formula on an all-blank row, Postgres returns NULL (docs/toolchain-gaps.md gap 10).
    via = {f['name']: m.group(1) for f in book[t]['schema'] if f['type'] == 'lookup'
           for m in [re.search(r'MATCH\(\{\{(\w+)\}\}', f.get('formula', ''))] if m}
    pg = {r[snake(pk)]: r for r in json.load(urllib.request.urlopen(f'{lt.EDITOR_API}/api/tables/{t}', timeout=120))['rows']}
    if len(pg) != len(book[t]['data']):
        bad.append(f'{t}: {len(pg)} rows in Postgres, {len(book[t]["data"])} in the rulebook')
    for r in book[t]['data']:
        p = pg.get(r[pk], {})
        for f in computed:
            if f in via and r.get(via[f]) in (None, ''):
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
print(f'{total} computed values compared, {len(bad)} differ ({skipped} lookups through an empty reference skipped)')
for k, n in sorted(by_field.items()):
    print(f'  {k}: {n}')
print('\n'.join(bad[:10]))
sys.exit(1 if bad else 0)
