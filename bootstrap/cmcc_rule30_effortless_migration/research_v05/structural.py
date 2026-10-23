"""Second research cycle: exact structural tests, CMCC cross-representation."""
from pathlib import Path
import json, sqlite3
R=Path(__file__).parent;O=R/'data'
T=2048;a=1;rows=[]
for t in range(T+1):rows.append(a);a=(a<<2)^((a<<1)|a)
def x(i,t): return ((rows[t]>>(i+t))&1) if i+t>=0 else 0
# Finite-window adjacent-period mismatch theorem for j=0,1.
w=[]
for onset in range(101):
 for p in range(1,65):
  candidates=[(t,i) for t in range(onset,2*onset+p+1) for i in (0,1) if x(i,t)!=x(i,t+p)]
  assert candidates
  t,i=candidates[0];w.append([onset,p,t,i])
(O/'adjacent_window_witnesses.json').write_text(json.dumps(w)+'\n')
# Run-length bounds derived in report, tested on every completed run.
bits=[x(0,t) for t in range(T+1)];runs=[];start=0
for end in range(1,T+1):
 if bits[end]!=bits[start]:
  last=end-1;b=bits[start];bound=2*start+1 if b else 4*start+5
  assert last<=bound
  runs.append({'start':start,'end':last,'bit':b,'proved_endpoint_bound':bound});start=end
(O/'constant_runs.json').write_text(json.dumps(runs,indent=2)+'\n')
# CMCC schema with data, predecessor lookups and calculated fields executed by SQLite.
# Values outside the cone are explicitly zero; transactions are snapshot-consistent.
db=O/'cmcc.sqlite';db.unlink(missing_ok=True);con=sqlite3.connect(db)
con.executescript('''
CREATE TABLE Cells(t INTEGER, i INTEGER, bit INTEGER CHECK(bit IN (0,1)), PRIMARY KEY(t,i));
CREATE TABLE Transition(l INTEGER,c INTEGER,r INTEGER,bit INTEGER,PRIMARY KEY(l,c,r));
CREATE VIEW DerivedNext AS
 SELECT a.t+1 AS t,a.i AS i,f.bit AS bit FROM Cells a
 LEFT JOIN Cells l ON l.t=a.t AND l.i=a.i-1
 LEFT JOIN Cells r ON r.t=a.t AND r.i=a.i+1
 JOIN Transition f ON f.l=coalesce(l.bit,0) AND f.c=a.bit AND f.r=coalesce(r.bit,0);
CREATE VIEW Counts AS SELECT t,sum(bit) AS ones,count(*) AS cells FROM Cells GROUP BY t;
''')
table=[0,1,1,1,1,0,0,0]
rulebook=json.loads((R/'rulebook.json').read_text())
con.executemany('INSERT INTO Transition VALUES (?,?,?,?)',[(v['l'],v['c'],v['r'],v['bit']) for v in rulebook['transition_table']])
H=128;W=H+1
con.executemany('INSERT INTO Cells VALUES (0,?,?)',[(i,int(i==0)) for i in range(-W,W+1)])
for t in range(H):con.execute('INSERT INTO Cells SELECT t,i,bit FROM DerivedNext WHERE t=?',(t+1,))
allrows=con.execute('SELECT t,i,bit FROM Cells ORDER BY t,i').fetchall()
assert all(b==x(i,t) for t,i,b in allrows)
con.commit();con.close()
(O/'structural_results.json').write_text(json.dumps({'adjacent_windows_checked':len(w),'constant_completed_runs':len(runs),'cmcc_cells_independently_checked':len(allrows),'cmcc_horizon':H,'proofs':'REPORT.md; tests are finite validation, not proofs'},indent=2)+'\n')
print('PASS',len(w),'adjacent windows;',len(allrows),'CMCC cells')
