import json,hashlib,platform
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).parent

def bitset_center(T):
    width=2*T+1; mask=(1<<width)-1; row=1<<T; out=[]
    for t in range(T+1):
        out.append((row>>T)&1)
        if t<T: row=(((row<<1) ^ (row | (row>>1))) & mask)
    return out

def local_center(T):
    row=[0]*(2*T+1);row[T]=1; out=[]
    for t in range(T+1):
        out.append(row[T])
        if t<T: row=[row[i-1]^(row[i]|row[i+1]) if 0<i<2*T else 0 for i in range(2*T+1)]
    return out

def main():
    T=10000; a=bitset_center(T)
    baseline=(ROOT/'center_10000.txt').read_text().strip()
    assert ''.join(map(str,a))==baseline
    assert local_center(256)==a[:257]
    assert [((l^(c|r))) for l,c,r in [(0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),(1,1,0),(1,1,1)]]==[0,1,1,1,1,0,0,0]
    n=len(a); pmax=1000
    last_mismatch={p:max((t for t in range(n-p) if a[t]!=a[t+p]),default=-1) for p in range(1,pmax+1)}
    lower={p:last_mismatch[p]+1 for p in last_mismatch}
    blocks={str(k):{'counts':{' '.join(map(str,key)):val for key,val in sorted(Counter(tuple(a[i:i+k]) for i in range(n-k+1)).items())},'max_abs_deviation_from_uniform':max(abs(v/(n-k+1)-1/2**k) for v in Counter(tuple(a[i:i+k]) for i in range(n-k+1)).values())} for k in (2,3,4)}
    lag={str(p):sum(1 if a[i]==a[i+p] else -1 for i in range(n-p))/(n-p) for p in (1,2,3,4,5,10,20,50,100)}
    res={'T':T,'n':n,'independent_bitset_matches_v01_sha256':hashlib.sha256(baseline.encode()).hexdigest(),'independent_local_matches_bitset_through_t':256,'period_range':[1,pmax],'eventual_period_start_lower_bound_min':min(lower.values()),'eventual_period_start_lower_bound_max':max(lower.values()),'selected_period_start_lower_bounds':{str(p):lower[p] for p in (1,2,3,5,10,30,100,500,1000)},'block_frequencies':blocks,'lag_spin_correlations':lag,'python_version':platform.python_version(),'caveat':'Finite-prefix exclusions only; no asymptotic proof.'}
    (ROOT/'results_v02.json').write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps({k:v for k,v in res.items() if k not in ('block_frequencies','lag_spin_correlations')},indent=2))
if __name__=='__main__':main()
