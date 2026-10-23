"""Controlled mutation build (migration README completion item 4).

Flip T0 to FALSIFIED in place, build, read which assessments the build blocks,
restore the pre-mutation bytes, build again, and check the hub hash returns to
its pre-mutation value. Nothing here computes a status; the build does.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import loop_tools as lt

HERE = Path(__file__).resolve().parent
WATCH = ['T0', 'T004', 'TB', 'TC', 'TD', 'K1', 'F2', 'P1', 'TA', 'CM', 'D0']

pre_bytes = lt.RULEBOOK.read_bytes()
pre_hash = lt.rulebook_hash()
baseline = lt.consume(lt.load(), WATCH)

book = lt.load()
lt.row(book, 'Assertions', 'T0')['ReportedStatus'] = 'FALSIFIED'   # fixture only; no Revision row
lt.save(book)
mut_receipt = lt.build()
mutated = lt.consume(lt.load(), WATCH)

lt.RULEBOOK.write_bytes(pre_bytes)
restore_receipt = lt.build()
post_hash = lt.rulebook_hash()
restored = lt.consume(lt.load(), WATCH)

blocked = sorted(a for a in WATCH if mutated[a]['CurrentStatus'] == 'BLOCKED')
unblocked = sorted(a for a in WATCH if mutated[a]['CurrentStatus'] != 'BLOCKED')
result = {
    'fixture': 'T0.ReportedStatus := FALSIFIED',
    'expected_blocked_min': ['TB', 'TC', 'TD', 'K1'],
    'blocked_by_build': blocked,
    'not_blocked_by_build': unblocked,
    'dashboard_baseline': baseline['_dashboard'],
    'dashboard_mutated': mutated['_dashboard'],
    'restored_equals_baseline': restored == baseline,
    'pre_hash': pre_hash, 'post_hash': post_hash, 'hash_round_trip': pre_hash == post_hash,
    'mutation_build': mut_receipt, 'restore_build': restore_receipt,
    'PASS': set(['TB', 'TC', 'TD', 'K1']) <= set(blocked) and restored == baseline and pre_hash == post_hash,
}
(HERE / 'mutation-test.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: result[k] for k in ('blocked_by_build', 'not_blocked_by_build', 'hash_round_trip', 'restored_equals_baseline', 'PASS')}, indent=1))
