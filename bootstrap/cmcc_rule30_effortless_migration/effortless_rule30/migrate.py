"""One-time raw-data/schema migration; never evaluates Effortless formulas."""
import json,hashlib
from pathlib import Path
R=Path(__file__).parent
old=json.loads((R.parent/'research_v05/rulebook.json').read_text())
book={'$schema':'https://example.com/cmcc-schema/v1','Name':'Rule30Research','Description':'Research provenance and dependency-aware assessments. Human-readable proofs remain imported assertions, not formal certificates.'}
def f(name,datatype='string',type='raw',formula=None,related=None):
 d=dict(name=name,datatype=datatype,type=type,nullable=False,Description=name)
 if formula:d['formula']=formula
 if related:d['RelatedTo']=related
 return d
def table(name,id,fields,rows):
 book[name]={'Description':name,'schema':[f(id),f('Name',type='calculated',formula='={{'+id+'}}')]+fields,'data':rows}
table('Assertions','AssertionId',[f('Statement'),f('ReportedStatus'),f('ProofSection'),f('IsUsable','integer','calculated','=IF(OR({{ReportedStatus}}="DEFINITION",{{ReportedStatus}}="PROVED_HUMAN_READABLE",{{ReportedStatus}}="REDERIVED_KNOWN",{{ReportedStatus}}="FINITE_VERIFIED"),1,0)'),f('IsProofEligible','integer','calculated','=IF(OR({{ReportedStatus}}="DEFINITION",{{ReportedStatus}}="PROVED_HUMAN_READABLE",{{ReportedStatus}}="REDERIVED_KNOWN"),1,0)')],[{'AssertionId':c['id'],'Statement':c['statement'],'ReportedStatus':c['status'],'ProofSection':c['proof_section'] or ''} for c in old['claims']])
table('Dependencies','DependencyId',[f('Conclusion',related='Assertions'),f('Premise',related='Assertions')],[{'DependencyId':c['id']+'-'+d,'Conclusion':c['id'],'Premise':d} for c in old['claims'] for d in c['dependencies']])
claims={c['id']:c for c in old['claims']}
def ancestors(k,seen=None):
 seen=set() if seen is None else seen
 for d in claims[k]['dependencies']:
  if d not in seen:seen.add(d);ancestors(d,seen)
 return seen
table('Prerequisites','PrerequisiteId',[f('ConclusionKey'),f('Premise',related='Assertions'),f('PremiseUsable','integer','lookup','=INDEX(Assertions!{{IsUsable}},MATCH({{Premise}},Assertions!{{AssertionId}},0))'),f('PremiseProofEligible','integer','lookup','=INDEX(Assertions!{{IsProofEligible}},MATCH({{Premise}},Assertions!{{AssertionId}},0))'),f('Blocked','integer','calculated','=1-{{PremiseUsable}}'),f('ProofBlocked','integer','calculated','=1-{{PremiseProofEligible}}')],[{'PrerequisiteId':k+'-'+p,'ConclusionKey':k,'Premise':p} for k in claims for p in sorted(ancestors(k)|{k})])
table('Assessments','AssessmentId',[f('Assertion',related='Assertions'),f('ReportedStatus',type='lookup',formula='=INDEX(Assertions!{{ReportedStatus}},MATCH({{Assertion}},Assertions!{{AssertionId}},0))'),f('BlockedCount','integer','aggregation','=SUMIFS(Prerequisites!{{Blocked}},Prerequisites!{{ConclusionKey}},{{Assertion}})'),f('ProofBlockedCount','integer','aggregation','=SUMIFS(Prerequisites!{{ProofBlocked}},Prerequisites!{{ConclusionKey}},{{Assertion}})'),f('CurrentStatus',type='calculated',formula='=IF({{BlockedCount}}>0,"BLOCKED",{{ReportedStatus}})'),f('ProofEligible','integer','calculated','=IF({{ProofBlockedCount}}=0,1,0)'),f('ProjectKey')],[{'AssessmentId':k,'Assertion':k,'ProjectKey':'Rule30'} for k in claims])
table('Evidence','EvidenceId',[f('Path'),f('Sha256')],[{'EvidenceId':e['id'],'Path':'../research_v05/'+e['path'],'Sha256':hashlib.sha256((R.parent/'research_v05'/e['path']).read_bytes()).hexdigest()} for e in old['evidence']])
table('Revisions','RevisionId',[f('Assertion',related='Assertions'),f('PriorStatus'),f('NewStatus'),f('Reason'),f('Replacement',related='Assertions')],[{'RevisionId':v['id'],'Assertion':v['claim_id'],'PriorStatus':v['prior_status'],'NewStatus':v['new_status'],'Reason':v['reason'],'Replacement':v['replacement_id']} for v in old['revisions']])
table('Loops','LoopId',[f('Kind'),f('State'),f('BuildReceipt'),f('InputHash'),f('OutputHash'),f('ProjectKey')],[{'LoopId':'legacy-'+str(i),'Kind':'LEGACY_RESEARCH','State':'REPORTED_COMPLETE','BuildReceipt':'','InputHash':'','OutputHash':'','ProjectKey':'Rule30'} for i in range(1,14)])
table('Dashboards','DashboardId',[f('ClaimCount','integer','aggregation','=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}})'),f('BlockedCount','integer','aggregation','=COUNTIFS(Assessments!{{ProjectKey}},{{DashboardId}},Assessments!{{CurrentStatus}},"BLOCKED")'),f('CompletedNativeLoops','integer','aggregation','=COUNTIFS(Loops!{{ProjectKey}},{{DashboardId}},Loops!{{Kind}},"EFFORTLESS",Loops!{{State}},"VERIFIED")')],[{'DashboardId':'Rule30'}])
out=R/'effortless-rulebook/effortless-rulebook.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(book,indent=2)+'\n')
print({t:len(v['data']) for t,v in book.items() if isinstance(v,dict)})
