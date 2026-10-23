import json, hashlib, csv
from pathlib import Path
ROOT=Path(__file__).parent

def step(row):
    n=len(row)
    return [row[i-1] ^ (row[i] | row[i+1]) for i in range(1,n-1)]

def run(T):
    row=[0]*(2*T+1);row[T]=1
    center=[]; triangle=[]
    for t in range(T+1):
        center.append(row[T-t]) if False else center.append(row[len(row)//2])
        if t<T: row=step(row)
    return center

def periodic_prefix(bits,p):
    return all(bits[i]==bits[i-p] for i in range(p,len(bits)))

def main():
    horizons=[100,1000,10000]
    rows=[]
    for T in horizons:
        bits=run(T)
        assert bits[:4]==[1,1,0,1],bits[:4]
        s=''.join(map(str,bits))
        rows.append(dict(horizon=T,ones=sum(bits),zeros=len(bits)-sum(bits),fraction_ones=sum(bits)/len(bits),sha256=hashlib.sha256(s.encode()).hexdigest(),full_prefix_periods_le_100=[p for p in range(1,101) if periodic_prefix(bits,p)]))
        (ROOT/f'center_{T}.txt').write_text(s+'\n')
    (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
