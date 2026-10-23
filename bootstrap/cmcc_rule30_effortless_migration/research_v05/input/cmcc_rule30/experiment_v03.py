from pathlib import Path
import json, hashlib
ROOT=Path(__file__).parent
s=(ROOT/'center_10000.txt').read_text().strip()
assert len(s)==10001 and set(s)<={'0','1'}
N=len(s); P=1000
cert={}
for p in range(1,P+1):
    mismatches=[t for t in range(N-p) if s[t]!=s[t+p]]
    assert mismatches
    t=mismatches[-1]
    cert[str(p)]={'witness_t':t,'bits':[int(s[t]),int(s[t+p])], 'excluded_onsets_through':t}
    assert all(s[v['witness_t']]!=s[v['witness_t']+int(k)] for k,v in [(str(p),cert[str(p)])])
# strongest uniform onset range that is excluded for every period in [1,P]
uniform=min(v['excluded_onsets_through'] for v in cert.values())
result={'sequence_length':N,'periods_checked':[1,P], 'all_eventual_period_onsets_at_most':uniform,'excluded_for_every_tested_period':True,'min_witness_periods':[int(p) for p,v in cert.items() if v['witness_t']==uniform], 'center_sha256':hashlib.sha256(s.encode()).hexdigest(), 'limitation':'No finite prefix can exclude eventual periodicity with an onset later than the observed prefix. This is not a Rule 30 prize proof.'}
(ROOT/'results_v03.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'period_witnesses_v03.json').write_text(json.dumps(cert,indent=2)+'\n')
print(json.dumps(result,indent=2))
