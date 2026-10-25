"""Bulk datasets for the analysis database: rows of a rulebook table, too many for the rulebook itself.

Each generator is deterministic (Rule 30 has no randomness), so its output is not checked in: it
writes data/<name>.csv (gitignored) and records the table, row count, sha256 and parameters in
research/ingest/manifest.json (checked in). Regenerating must reproduce the same sha256.
The table and its formulas are defined in the rulebook (research/hub/build_model.py); a generator
writes only raw fields. Then `python3 research/ingest/ingest.py load`.

Usage: python3 research/ingest/generate.py <name> [<name> ...]
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

MANIFEST = Path(__file__).resolve().parent / 'manifest.json'
DATA = lt.ROOT / 'data'

# name -> (table, params, function(params) -> (columns, iterable of rows)). Loops add generators here.
GENERATORS: dict = {}


def write_dataset(name: str, table: str, params: dict, columns: list[str], rows) -> dict:
    DATA.mkdir(exist_ok=True)
    path = DATA / f'{name}.csv'
    n = 0
    with path.open('w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(columns)
        for r in rows:
            w.writerow(r)
            n += 1
    entry = {'name': name, 'table': table, 'file': str(path.relative_to(lt.ROOT)) if path.is_relative_to(lt.ROOT) else str(path), 'rows': n,
             'sha256': lt.sha256_file(path), 'generator': f'research/ingest/generate.py {name}', 'params': params}
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'datasets': []}
    manifest['datasets'] = [d for d in manifest['datasets'] if d['name'] != name] + [entry]
    MANIFEST.write_text(json.dumps(manifest, indent=1) + '\n')
    return entry


if __name__ == '__main__':
    for name in sys.argv[1:]:
        table, params, fn = GENERATORS[name]
        cols, rows = fn(params)
        print(json.dumps(write_dataset(name, table, params, cols, rows)))
