"""Compare actual unchanged acceptance conditions, retaining baseline support failures."""
from pathlib import Path
import json,subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-native-delta-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,file):
 d=BASE/name;_,ps=authenticate(d);p=d/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([d/'result.json',p]);return read(p)
before=take('government-xl-harbourfront-tower-native-baseline-v1-20261021','native-neighbour-checks.json');after=take('government-xl-harbourfront-tower-native-regression-v2-20261021','native-neighbour-checks.json')
a={r['uid']:r for r in before['rows']};b={r['uid']:r for r in after['rows']};assert len(a)==len(b)==17 and set(a)==set(b)
for p in set(before['inputHashes'])&set(after['inputHashes']):assert before['inputHashes'][p]==after['inputHashes'][p],p
for report in [before,after]:
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h;refs.append(ROOT/p)
def inputs(r):
 return dict(newlyBuried=r['terrain']['newlyWhollyBuried'],newlyUpward=r['terrain']['newlyUpwardWhollyBuried'],terrainRelevant=r['terrain']['minimumGapAfter']<=2,supportFraction=r['support']['supportFraction'])
records=[dict(uid=u,before=inputs(a[u]),after=inputs(b[u]))for u in sorted(a)];save(DOC/'policy-inputs.json',records)
js="import{readFileSync}from'node:fs';import{nativeNeighbourAccepted}from'./source-scripts/city/government-import/native-neighbour-policy.mjs';const rows=JSON.parse(readFileSync(process.argv[1]));console.log(JSON.stringify(rows.map(r=>({uid:r.uid,before:nativeNeighbourAccepted(r.before),after:nativeNeighbourAccepted(r.after)}))));"
outputs=json.loads(subprocess.check_output(['node','--input-type=module','-e',js,str(DOC/'policy-inputs.json')],cwd=ROOT,text=True));save(DOC/'policy-replay.json',outputs)
unchanged=[];introduced=[];changes=[]
for out in outputs:
 uid=out['uid'];old=a[uid];r=b[uid]
 assert old['vertices']==r['vertices']and old['triangles']==r['triangles']
 assert old['support']==r['support']and old.get('unresolvedSupportDependencies',[])==r.get('unresolvedSupportDependencies',[])
 assert old['terrain']['minimumGapBefore']==r['terrain']['minimumGapBefore']
 assert old['passed']==(out['before']and not old.get('unresolvedSupportDependencies'))
 assert r['passed']==(out['after']and not r.get('unresolvedSupportDependencies'))
 if old!=r:changes.append(dict(uid=uid,before=old,after=r))
 if not r['passed']:
  if not old['passed']and inputs(old)==inputs(r):unchanged.append(dict(uid=uid,conditions=inputs(r),support=r['support']))
  else:introduced.append(dict(uid=uid,reason='new-failed-policy-condition'))
 if r['terrain']['newlyWhollyBuried']or r['terrain']['newlyUpwardWhollyBuried']:introduced.append(dict(uid=uid,reason='new-burial'))
forms=take('government-xl-harbourfront-tower-form-regression-v2-20261021','summary.json');assert forms['forms']==127 and not forms['flagged']
summary=dict(uids=['landsd/118230:0'],checked=17,ordinaryFormsChecked=127,ordinaryFailures=0,unchangedBaselineFailureConditions=unchanged,introducedFailures=introduced,neighbourRegressionPassed=not introduced,installationApproved=False,qualification='Canonical nativeNeighbourAccepted replay on exact before/after decision inputs. Existing support failures remain unapproved; raw numerical terrain deltas are retained separately and are not asserted byte-identical. No new failure condition, burial or ordinary-form regression.')
save(DOC/'raw-row-changes.json',changes);save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
refs.append(HERE/'native-neighbour-policy.mjs');r=module('harbourfront_native_delta_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-neighbour-policy-delta',list(dict.fromkeys(refs)),summary);print(dict(jobId=r['jobId'],passed=not introduced,baselineFlags=len(unchanged)),flush=True)
