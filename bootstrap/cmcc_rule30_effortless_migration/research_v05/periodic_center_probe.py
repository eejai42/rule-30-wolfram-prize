"""Relaxed right-neighbor dynamics under a periodic center hypothesis.
The second-right neighbor is a free input: this is deliberately an overapproximation.
"""
from pathlib import Path
from itertools import product
import json
O=Path(__file__).parent/'data'
def components(edges):
 # Tiny graphs: mutual reachability is simpler to audit than a Tarjan implementation.
 reach=[]
 for v in range(len(edges)):
  seen={v};todo=[v]
  while todo:
   w=todo.pop()
   for z in edges[w]:
    if z not in seen:seen.add(z);todo.append(z)
  reach.append(seen)
 left=set(range(len(edges)));out=[]
 while left:
  v=min(left);part={w for w in left if w in reach[v] and v in reach[w]};out.append(part);left-=part
 return out
records=[]
for p in range(1,11):
 for word in product((0,1),repeat=p):
  if any(p%d==0 and all(word[t]==word[t%d] for t in range(p)) for d in range(1,p)):continue
  edges=[]
  for phase in range(p):
   for r in (0,1):edges.append({2*((phase+1)%p)+(word[phase]^(r|s)) for s in (0,1)})
  comps=components(edges)
  branching=any(any(len(edges[v]&part)>1 for v in part) for part in comps)
  records.append({'word':''.join(map(str,word)),'p':p,'recurrent_branching_right_trace':branching})
summary={'primitive_words_tested':len(records),'nonbranching_words':[r['word'] for r in records if not r['recurrent_branching_right_trace']],'nonconstant_words_without_branching':[r['word'] for r in records if len(set(r['word']))>1 and not r['recurrent_branching_right_trace']], 'interpretation':'Recurrent branching permits nonperiodic paths in the relaxed right-neighbor system; these paths are NOT certified full Rule 30 histories or compatible with the single seed.'}
(O/'periodic_center_probe.json').write_text(json.dumps({'summary':summary,'records':records},indent=2)+'\n');print(json.dumps(summary,indent=2))
