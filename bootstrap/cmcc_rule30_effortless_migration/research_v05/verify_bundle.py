"""Validate retained finite certificates and proof-status boundaries."""
from pathlib import Path
import hashlib,json,sqlite3
R=Path(__file__).parent;O=R/'data'
s=(O/'center_100000.txt').read_text().strip();r=json.loads((O/'center_results.json').read_text())
assert len(s)==100001 and s.count('1')==50098
assert hashlib.sha256(s.encode()).hexdigest()==r['sha256_no_newline']
w=json.loads((O/'period_witnesses.json').read_text());assert set(map(int,w))==set(range(1,10001))
for p,(t,a,b) in w.items():
 assert int(s[t])==a and int(s[t+int(p)])==b and a!=b
 assert all(s[u]==s[u+int(p)] for u in range(t+1,len(s)-int(p)))
assert min(v[0] for v in w.values())==90000
assert json.loads((O/'period_verification.json').read_text())['PASS']
con=sqlite3.connect(O/'cmcc.sqlite');assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert con.execute("SELECT count(*) FROM Claims WHERE id IN ('P1','P2','P3') AND status='OPEN'").fetchone()[0]==3
assert con.execute('SELECT count(*) FROM Cells').fetchone()[0]==33411
con.close()
for p in R.rglob('*.json'):json.loads(p.read_text())
print('PASS: hashes, 10000 maximal period witnesses, full-period receipt, SQLite integrity, open-prize status, all JSON.')
