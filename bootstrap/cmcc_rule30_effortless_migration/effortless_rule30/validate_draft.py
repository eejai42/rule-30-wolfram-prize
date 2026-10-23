"""Structural checks only; NOT Effortless transpilation or formula execution."""
from pathlib import Path
import json
R=Path(__file__).parent
b=json.loads((R/'effortless-rulebook/effortless-rulebook.json').read_text())
tables={k:v for k,v in b.items() if isinstance(v,dict) and 'schema' in v}
graph={k:set() for k in tables}
for k,t in tables.items():
 names=[f['name'] for f in t['schema']]
 assert len(names)==len(set(names)) and 'Name' in names
 pk=names[0];ids=[r[pk] for r in t['data']];assert len(ids)==len(set(ids))
 for f in t['schema']:
  if 'RelatedTo' in f:
   target=f['RelatedTo'];assert target in tables;graph[k].add(target)
   tf=tables[target];tp=tf['schema'][0]['name'];valid={r[tp] for r in tf['data']}
   assert all(r[f['name']] in valid for r in t['data'])
seen=set()
def visit(k,active):
 assert k not in active,'table relationship cycle'
 if k in seen:return
 for p in graph[k]:visit(p,active|{k})
 seen.add(k)
for k in tables:visit(k,set())
parents={r['AssertionId']:set() for r in tables['Assertions']['data']}
for r in tables['Dependencies']['data']:parents[r['Conclusion']].add(r['Premise'])
def closure(k,active):
 assert k not in active,'claim cycle'
 return {k}|set().union(*(closure(p,active|{k}) for p in parents[k]))
for k in parents:
 actual={r['Premise'] for r in tables['Prerequisites']['data'] if r['ConclusionKey']==k}
 assert actual==closure(k,set())
counts={k:len(t['data']) for k,t in tables.items()}
out={'structural_checks':'PASS','native_build':'NOT_EXECUTED','formula_evaluation':'NOT_EXECUTED','database_execution':'NOT_EXECUTED','verified_native_loops':0,'draft_rows':counts}
(R/'receipts/structural-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
