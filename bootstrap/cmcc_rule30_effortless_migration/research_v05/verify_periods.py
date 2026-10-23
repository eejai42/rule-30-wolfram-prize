"""Independent certificate replay using the whole triangular state as one integer."""
from pathlib import Path
from array import array
import json,time
R=Path(__file__).parent;O=R/'data';records=json.loads((O/'diagonal_periods.json').read_text())
K=len(records)-1;M=max(r['period'] for r in records);mask=(1<<(K+1))-1
states=array('Q');s=1;start=time.perf_counter()
for t in range(2*M):
 states.append(s);s=(s^((s<<1)|(s<<2)))&mask
assert s==1
for rec in records:
 k=rec['k'];P=rec['period'];block=bytearray((states[t]>>k)&1 for t in range(P))
 # Check full period over the entire full-state orbit (enough for all future).
 assert all(((states[t]^states[t+P])>>k)&1==0 for t in range(M))
 assert P==1 or any(((states[t]^states[t+P//2])>>k)&1 for t in range(P))
 assert sum(block)==rec['ones']
result={'PASS':True,'offsets':[0,K],'full_state_period':M,'steps':2*M,'method':'whole-state bit operations, all offsets over one complete joint orbit','elapsed_seconds':time.perf_counter()-start}
(O/'period_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
