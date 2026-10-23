"""Project the declarative claim/revision model to SQLite; not a proof checker."""
from pathlib import Path
import json,sqlite3,hashlib
R=Path(__file__).parent
model=json.loads((R/'rulebook.json').read_text());claims={r['id']:r for r in model['claims']}
allowed={'DEFINITION','PROVED_HUMAN_READABLE','REDERIVED_KNOWN','FINITE_VERIFIED','FALSIFIED','OPEN','SUPERSEDED'}
for c in claims.values():
 assert c['status'] in allowed
 for d in c['dependencies']:assert d in claims
 if c['status'] in ('PROVED_HUMAN_READABLE','REDERIVED_KNOWN'):
  assert all(claims[d]['status'] in ('DEFINITION','PROVED_HUMAN_READABLE','REDERIVED_KNOWN') for d in c['dependencies'])
  assert c['proof_section'] is not None
visiting=set();done=set()
def visit(k):
 assert k not in visiting,'Undeclared dependency cycle'
 if k in done:return
 visiting.add(k)
 for d in claims[k]['dependencies']:visit(d)
 visiting.remove(k);done.add(k)
for k in claims:visit(k)
for e in model['evidence']:
 p=R/e['path'];assert p.is_file();e['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'data/cmcc.sqlite';con=sqlite3.connect(p)
con.executescript('''
DROP VIEW IF EXISTS OpenObligations;
DROP TABLE IF EXISTS Claims; DROP TABLE IF EXISTS Dependencies;
DROP TABLE IF EXISTS Evidence; DROP TABLE IF EXISTS Revisions;
CREATE TABLE Claims(id TEXT PRIMARY KEY,status TEXT,statement TEXT,proof_section TEXT);
CREATE TABLE Dependencies(parent TEXT,child TEXT,PRIMARY KEY(parent,child));
CREATE TABLE Evidence(id TEXT PRIMARY KEY,path TEXT,sha256 TEXT);
CREATE TABLE Revisions(id TEXT PRIMARY KEY,claim_id TEXT,prior_status TEXT,new_status TEXT,reason TEXT,replacement_id TEXT);
CREATE VIEW OpenObligations AS SELECT id,statement FROM Claims WHERE status='OPEN';
''')
con.executemany('INSERT INTO Claims VALUES (?,?,?,?)',[(c['id'],c['status'],c['statement'],c['proof_section']) for c in claims.values()])
con.executemany('INSERT INTO Dependencies VALUES (?,?)',[(c['id'],d) for c in claims.values() for d in c['dependencies']])
con.executemany('INSERT INTO Evidence VALUES (?,?,?)',[(e['id'],e['path'],e['sha256']) for e in model['evidence']])
con.executemany('INSERT INTO Revisions VALUES (?,?,?,?,?,?)',[(v['id'],v['claim_id'],v['prior_status'],v['new_status'],v['reason'],v['replacement_id']) for v in model['revisions']])
con.commit();assert con.execute("SELECT count(*) FROM Claims WHERE id IN ('P1','P2','P3') AND status='OPEN'").fetchone()[0]==3
out={'claims':len(claims),'revisions':len(model['revisions']),'open_obligations':con.execute('SELECT id,statement FROM OpenObligations').fetchall(),'warning':'Consistency checks do not verify arbitrary proof text.'};con.close()
(R/'data/ledger_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
