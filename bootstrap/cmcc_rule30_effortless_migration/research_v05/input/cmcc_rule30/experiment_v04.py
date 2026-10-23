import json
from pathlib import Path
T=4096; K=12
# diagonal recurrence independent of full row simulation
Y=[[0]*(T+1) for _ in range(K+1)]
Y[0]=[1]*(T+1)
for k in range(1,K+1):
    for t in range(T):
        a=Y[k-1][t]
        b=Y[k-2][t] if k>=2 else 0
        Y[k][t+1]=Y[k][t]^(a|b)
# full evolution independently: sparse set
live={0}
for t in range(T+1):
    for k in range(K+1):
        assert Y[k][t]==int(t-k in live),(t,k)
    if t<T:
        cand=set()
        for i in live: cand.update((i-1,i,i+1))
        live={i for i in cand if (int(i-1 in live)^(int(i in live) | int(i+1 in live)))}
# exact minimal periods for each right diagonal over checked horizon
out=[]
for k in range(K+1):
    expected=1 if k==0 else 2**k
    assert all(Y[k][t]==Y[k][t+expected] for t in range(T+1-expected))
    minperiod=next(p for p in range(1,expected+1) if all(Y[k][t]==Y[k][t+p] for t in range(T+1-p)))
    out.append({'offset':k,'guaranteed_period':expected,'observed_minimal_period':minperiod,'first_32_bits':''.join(map(str,Y[k][:32]))})
Path(__file__).with_name('results_v04.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
