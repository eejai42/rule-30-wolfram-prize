"""Fixture test for live monitoring: does a RUNNING loop reach the explorer's API, and how fast?

Adds a throwaway RUNNING loop through loop_tools.start_loop, builds, and times how long the
rulebook editor's file watcher takes to serve it from vw_loops. Then restores the exact
pre-test bytes and builds. The editor's rebuild only adds and upserts rows, so a row removed
from the hub stays in its database until the container is recreated; the test therefore
recreates it (edit-rulebook.sh) and checks the fixture row is gone. The hub hash must round-trip.
"""
import json, subprocess, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
API = 'http://localhost:42441/api/tables/Loops'
TEST_ID = 'monitor-test'


def visible():
    try:
        rows = json.load(urllib.request.urlopen(API, timeout=3))['rows']
        r = next((x for x in rows if x['loop_id'] == TEST_ID), None)
        return r
    except Exception:
        return 'down'


def wait(cond, limit=300):
    t0 = time.time()
    while time.time() - t0 < limit:
        if cond():
            return round(time.time() - t0, 1)
        time.sleep(1)
    return None


pre_bytes, pre_hash = lt.RULEBOOK.read_bytes(), lt.rulebook_hash()
book = lt.load()
lt.start_loop(book, TEST_ID, 'Fixture: verify the explorer shows a running loop.')
lt.save(book)
t_edit = time.time()
lt.build()
build_s = round(time.time() - t_edit, 1)
seen = wait(lambda: isinstance(visible(), dict))
row = visible()
dash = json.load(urllib.request.urlopen('http://localhost:42441/api/tables/Dashboards'))['rows'][0]

lt.RULEBOOK.write_bytes(pre_bytes)
lt.build()
post_hash = lt.rulebook_hash()
lingers_after_upsert_rebuild = wait(lambda: visible() is None, limit=20) is None
log = open(lt.ROOT / '.logs' / 'rulebook-editor.log', 'w')
subprocess.Popen(['bash', 'edit-rulebook.sh'], cwd=lt.ROOT / 'effortless-rulebook', stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
time.sleep(10)
gone = wait(lambda: visible() is None, limit=600)

out = {
    'build_seconds': build_s, 'api_shows_running_loop_after_build_s': seen,
    'row_state': row.get('state') if isinstance(row, dict) else row,
    'dashboard_running_loop_count_while_running': dash.get('running_loop_count'),
    'fixture_row_lingers_after_upsert_rebuild': lingers_after_upsert_rebuild,
    'gone_after_editor_recreate_s': gone, 'hash_round_trip': pre_hash == post_hash,
    'PASS': bool(seen is not None and isinstance(row, dict) and row.get('state') == 'RUNNING' and int(dash.get('running_loop_count', 0)) == 1 and gone is not None and pre_hash == post_hash),
}
(HERE / 'monitor-test.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
