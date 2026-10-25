"""The analysis database: the rulebook's Postgres projection plus bulk data the rulebook does not hold.

The rulebook drives it. `reset` builds the database from postgres/ (generated from the rulebook by
rulebook-to-postgres on every build): its tables, its formulas as views, and the witness data the
rulebook itself carries. `load` then COPYs the bulk datasets listed in research/ingest/manifest.json
into the rulebook's own base tables, so the same views compute every value over them, and saves the
computed values once:

  1. COPY each dataset (data/*.csv, gitignored, regenerable) after checking its sha256;
  2. bring every cached field (IsCached / *Cache) to its fresh value over all rows (fill_caches),
     with the memo tables of the self-referencing lookups refreshed as it goes;
  3. check that the witness rows still carry compile-rulebook's values (check_witness), so the
     database's own computation is verified on every load before any bulk value is trusted.

That is loop_tools.build()'s cache discipline, run in the database: a cache always equals its fresh
value. After `load` the database is static: reads come from the caches and memos, not a recompute.

A dataset is rows of raw fields only (keys, references, inputs). Values the model computes stay
formulas; a value a script computes enters as a claim the model checks (CLAUDE.md, rule 5a).

Usage:
  python3 research/ingest/ingest.py reset   # drop and rebuild the analysis DB from postgres/
  python3 research/ingest/ingest.py load    # COPY the manifest's datasets, then fill the caches
  python3 research/ingest/ingest.py         # both
DATABASE_URL overrides the default postgresql://localhost:5432/rule30_analysis.
"""
from __future__ import annotations
import csv, json, os, re, subprocess, sys, time
from pathlib import Path
import psycopg2
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

DB = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/rule30_analysis')
MANIFEST = Path(__file__).resolve().parent / 'manifest.json'
snake = lambda s: re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', s).lower()


def log(msg):
    print(f'[ingest] {msg}', flush=True)


def reset():
    name = DB.rsplit('/', 1)[1]
    admin = DB.rsplit('/', 1)[0] + '/postgres'
    with psycopg2.connect(admin) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (name,))
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE "{name}"')
                log(f'created database {name}')
    t0 = time.time()
    proc = subprocess.run(['bash', str(lt.ROOT / 'postgres' / 'init-db.sh')], env=dict(os.environ, DATABASE_URL=DB), capture_output=True, text=True)
    if proc.returncode:
        sys.exit(f'init-db.sh failed:\n{(proc.stdout + proc.stderr)[-3000:]}')
    log(f'reset {DB} from postgres/ ({time.time() - t0:.0f}s)')


def fill_caches(cur, book, cached):
    """Bring every cached field to its fresh value: sweep the cached tables, recomputing each one's view
    with only its own flag cleared (the others read their caches), until a sweep changes nothing. The
    field DAG is acyclic, so each sweep fixes at least one more level of it, and at the fixed point
    every cache equals the value its formula computes over all rows, bulk and witness."""
    deps = {t: {u for f in book[t]['schema'] for u in re.findall(r'(\w+)!\{\{', f.get('formula') or '')} & set(cached) - {t} for t in cached}
    order, seen = [], set()

    def visit(t):                                   # upstream first; a table-level cycle is broken anywhere
        if t not in seen:
            seen.add(t)
            for u in sorted(deps[t]):
                visit(u)
            order.append(t)
    for t in sorted(cached):
        visit(t)
    # Every write to a memoised table fires erb_memo_invalidate, which empties the memos, and without
    # them a self-referencing chain recomputes exponentially (each cell re-derives its three parents).
    # Writing a cache never changes a computed value once the caches are fresh, so the trigger is held
    # off while the sweeps run and the memos are refreshed at the start of each sweep instead.
    cur.execute("SELECT tgrelid::regclass::text FROM pg_trigger WHERE tgname = 'erb_memo_invalidate'")
    memoised = [r[0] for r in cur.fetchall()]
    for m in memoised:
        cur.execute(f'ALTER TABLE {m} DISABLE TRIGGER erb_memo_invalidate')
    for sweep in range(1, 50):
        t0 = time.time()
        cur.execute('SELECT erb_refresh_memos()')
        log(f'sweep {sweep}: memos refreshed ({time.time() - t0:.0f}s)')
        changed = 0
        for t in order:
            names, pk = cached[t], snake(book[t]['schema'][0]['name'])
            t0 = time.time()
            cur.execute(f'UPDATE {snake(t)} SET is_cached = 0')
            cur.execute(f'DROP TABLE IF EXISTS erb_fresh; CREATE TEMP TABLE erb_fresh AS SELECT {pk}, '
                        + ', '.join(snake(f) for f in names) + f' FROM vw_{snake(t)}')
            differs = ' OR '.join(f'b.{snake(f)}_cache IS DISTINCT FROM v.{snake(f)}' for f in names)
            cur.execute(f'UPDATE {snake(t)} b SET ' + ', '.join(f'{snake(f)}_cache = v.{snake(f)}' for f in names)
                        + f' FROM erb_fresh v WHERE b.{pk} = v.{pk} AND ({differs})')
            n = cur.rowcount
            cur.execute(f'UPDATE {snake(t)} SET is_cached = 1')
            changed += n
            if n:
                log(f'sweep {sweep}: {t} {n} rows changed ({time.time() - t0:.1f}s)')
        if not changed:
            for m in memoised:
                cur.execute(f'ALTER TABLE {m} ENABLE TRIGGER erb_memo_invalidate')
            log(f'caches at their fixed point after {sweep} sweep(s)')
            return
    raise RuntimeError('caches did not reach a fixed point')


def check_witness(cur, book, cached):
    """The witness rows are in the rulebook too, with compile-rulebook's values. After the caches are filled
    from Postgres's own computation, each witness row must still carry exactly those values; a difference
    means Postgres computes that field differently from compile-rulebook, and the load is rolled back."""
    bad = {}
    for t, names in cached.items():
        pk = book[t]['schema'][0]['name']
        cur.execute(f'SELECT {snake(pk)}, ' + ', '.join(f'{snake(f)}_cache' for f in names) + f' FROM {snake(t)}')
        got = {r[0]: r[1:] for r in cur.fetchall()}
        for r in book[t]['data']:
            for f, v in zip(names, got.get(r[pk], [None] * len(names))):
                a = r.get(f)
                if not ((a in (None, '') and v in (None, '')) or str(a) == str(v) or _num_eq(a, v)):
                    bad[f'{t}.{f}'] = bad.get(f'{t}.{f}', 0) + 1
    if bad:
        raise RuntimeError(f'Postgres disagrees with compile-rulebook on witness rows, so its values over bulk rows cannot '
                           f'be trusted: {bad} (docs/toolchain-gaps.md; check with check_postgres.py --db {DB} --fresh)')
    log('witness rows agree with compile-rulebook on every cached field')


def _num_eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return False


def load():
    datasets = json.loads(MANIFEST.read_text())['datasets'] if MANIFEST.exists() else []
    book = lt.load()
    cached = lt.cached_fields(book)
    with psycopg2.connect(DB) as conn, conn.cursor() as cur:
        for d in datasets:
            path = lt.ROOT / d['file']
            assert lt.sha256_file(path) == d['sha256'], f'{d["file"]} differs from the manifest: regenerate it'
            with path.open() as fh:
                cols = next(csv.reader(fh))
                fh.seek(0)
                t0 = time.time()
                cur.copy_expert(f'COPY {snake(d["table"])} ({", ".join(chr(34) + snake(c) + chr(34) for c in cols)}) FROM STDIN WITH (FORMAT csv, HEADER true)', fh)
            log(f'{d["table"]}: {cur.rowcount} rows from {d["file"]} ({time.time() - t0:.0f}s)')
            assert cur.rowcount == d['rows'], f'{d["file"]}: {cur.rowcount} rows, manifest says {d["rows"]}'
        fill_caches(cur, book, cached)
        check_witness(cur, book, cached)
    with psycopg2.connect(DB) as conn:
        conn.autocommit = True
        conn.cursor().execute('ANALYZE')
    log(f'loaded {len(datasets)} dataset(s); caches filled')


if __name__ == '__main__':
    steps = sys.argv[1:] or ['reset', 'load']
    for s in steps:
        {'reset': reset, 'load': load}[s]()
