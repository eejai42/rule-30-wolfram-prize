"""Deterministic experiments. Python standard library only. No random sampling."""
from pathlib import Path
import json, hashlib, platform, time
from collections import Counter
R=Path(__file__).parent
O=R/'data'; O.mkdir(exist_ok=True)
def dump(name,obj): (O/name).write_text(json.dumps(obj,indent=2)+'\n')
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def center(T):
    # Growing row; bit j represents physical position j-t. Lookup-table
    # truth function is used by independent dictionary implementation below.
    a=1; out=[]
    for t in range(T+1):
        out.append((a>>t)&1)
        a=(a<<2)^((a<<1)|a)
    return out

def audit():
    root=R/'input/cmcc_rule30'; rerun=R/'rerun'; checks={}
    for p in sorted(root.iterdir()):
        checks[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
        if p.suffix=='.json':
            a=json.loads(p.read_text()); b=json.loads((rerun/p.name).read_text())
            if p.name=='results_v02.json': a.pop('python_version');b.pop('python_version')
            checks[p.name]['rerun_equal_ignoring_python_version']=a==b
            assert a==b,p.name
        elif p.name.startswith('center_'):
            T=int(p.stem.split('_')[1]); s=''.join(map(str,center(T)))
            assert s==p.read_text().strip()
            checks[p.name]['independent_growing_row_equal']=True
    dump('audit.json',checks)

def periods(K=80,cap=2**21):
    words=[bytearray([1])]; records=[{'k':0,'period':1,'ones':1}]
    for k in range(1,K+1):
        a=words[-1];b=words[-2] if k>1 else bytearray([0]);P=max(len(a),len(b))
        if 2*P>cap: break
        q=bytearray(a[t%len(a)]|b[t%len(b)] for t in range(P))
        # Reduce the forcing to its true least period, known to be a power of 2.
        while len(q)>1 and q[:len(q)//2]==q[len(q)//2:]: q=q[:len(q)//2]
        Q=len(q); parity=sum(q)%2; M=Q*(1+parity)
        y=bytearray(M);v=0
        for t in range(M): y[t]=v;v^=q[t%Q]
        assert v==0
        while len(y)>1 and y[:len(y)//2]==y[len(y)//2:]: y=y[:len(y)//2]
        assert len(y)==M  # exact-period lemma, including constant forcing
        words.append(y)
        records.append({'k':k,'parent_common_period':P,'forcing_period':Q,'forcing_parity':parity,'period':M,'ones':sum(y),'first_one':y.index(1),'sha256':hashlib.sha256(y).hexdigest()})
        assert y.index(1)==(k+1)//2
        assert M>(k+1)//2
    dump('diagonal_periods.json',records)
    # Compare all retained period words to 1024 full-state rows by table lookup.
    live={0}; table=[0,1,1,1,1,0,0,0]
    for t in range(1025):
        for k,y in enumerate(words): assert y[t%len(y)]==int(t-k in live),(k,t)
        live={i for i in range(-t-1,t+2) if table[4*(i-1 in live)+2*(i in live)+(i+1 in live)]}
    # Test tempting stronger claims; retain first counterexample.
    hypotheses={
      'every_diagonal_k_ge_1_balanced':next((r for r in records[1:] if 2*r['ones']!=r['period']),None),
      'period_doubles_every_k_ge_3':next((records[k] for k in range(3,len(records)) if records[k]['period']!=2*records[k-1]['period']),None),
      'periods_nondecreasing':next((records[k] for k in range(1,len(records)) if records[k]['period']<records[k-1]['period']),None)}
    dump('hypotheses.json',hypotheses)
    return records

def centers(T=100000):
    bits=center(T);s=''.join(map(str,bits)); (O/f'center_{T}.txt').write_text(s+'\n')
    assert s[:10001]==(R/'input/cmcc_rule30/center_10000.txt').read_text().strip()
    # Independent fixed-coordinate implementation through full new horizon.
    a=1<<T;mask=(1<<(2*T+1))-1
    for t in range(T+1):
        assert ((a>>T)&1)==bits[t]
        a=((a<<1)^(a|(a>>1)))&mask
    witnesses={}
    for p in range(1,10001):
        t=T-p
        while t>=0 and bits[t]==bits[t+p]:t-=1
        assert t>=0
        witnesses[p]=[t,bits[t],bits[t+p]]
    dump('period_witnesses.json',witnesses)
    # Residue decomposition: exact discrepancies, not confidence intervals.
    residue=[]
    for p in (2,4,8,16,32,64):
        residue.append({'modulus':p,'classes':[{'r':r,'n':len(bits[r::p]),'ones':sum(bits[r::p])} for r in range(p)]})
    out={'T':T,'n':len(bits),'ones':sum(bits),'zeros':len(bits)-sum(bits),'sha256_no_newline':digest(s),'first_100000_ones':sum(bits[:100000]),'uniform_onsets_excluded_through':min(w[0] for w in witnesses.values()),'periods_tested':[1,10000],'blocks':{k:dict(sorted(Counter(s[i:i+k] for i in range(len(s)-k+1)).items())) for k in (2,3,4)},'residues':residue}
    dump('center_results.json',out)
    return out

def periodic_pairs():
    # Periodic time words: local inverse propagates a pair leftward. Enumeration
    # demonstrates that local consistency alone does not encode the seed.
    counts={}
    for p in range(1,9):
        mask=(1<<p)-1
        def shift(v):return (v>>1)|((v&1)<<(p-1))
        edges={}; cycles=[]
        for a in range(1<<p):
            for b in range(1<<p): edges[(a,b)]=(shift(a)^(a|b),a)
        seen=set()
        for start in edges:
            if start in seen:continue
            path=[];loc={};v=start
            while v not in seen and v not in loc:
                loc[v]=len(path);path.append(v);v=edges[v]
            if v in loc:cycles.append(path[loc[v]:])
            seen.update(path)
        counts[p]={'states':len(edges),'cycles':len(cycles),'cycle_lengths':dict(Counter(map(len,cycles))),'constant_zero_center_right_choices':[b for b in range(1<<p)],'warning':'Periodic local spacetime extensions are not single-seed solutions.'}
    dump('periodic_pair_graphs.json',counts)

if __name__=='__main__':
    start=time.perf_counter();audit();r=periods();c=centers();periodic_pairs()
    dump('environment.json',{'python':platform.python_version(),'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-start,'wolfram_executed':False,'lean_kernel_checked':False})
    print(json.dumps({'max_diagonal':r[-1],'center':{k:v for k,v in c.items() if k not in ('blocks','residues')}},indent=2))
