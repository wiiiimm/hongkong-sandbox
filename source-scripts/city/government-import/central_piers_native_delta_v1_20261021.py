"""Compare complete installed-only native baseline and exact private pier terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-native-delta-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,file):
 folder=BASE/name;_,ps=authenticate(folder);p=folder/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
before=take('government-xl-central-piers-native-baseline-v1-20261021','native-neighbour-checks.json');after=take('government-xl-central-piers-native-regression-v1-20261021','native-neighbour-checks.json')
a={r['uid']:r for r in before['rows']};b={r['uid']:r for r in after['rows']};assert len(a)==len(b)==1207 and set(a)==set(b)
# Both runs must consume the same live original assets, catalogues, source forms and runner.
common=set(before['inputHashes'])&set(after['inputHashes'])
for p in common:assert before['inputHashes'][p]==after['inputHashes'][p],p
for evidence in [before,after]:
 for p,h in evidence['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h;refs.append(ROOT/p)
unchanged_flags=[];introduced=[];changed=[]
for uid,r in b.items():
 old=a[uid];t=r['terrain'];ot=old['terrain']
 assert r['vertices']==old['vertices'] and r['triangles']==old['triangles']
 assert r['support']==old['support'] and r.get('unresolvedSupportDependencies',[])==old.get('unresolvedSupportDependencies',[])
 assert t['minimumGapBefore']==ot['minimumGapBefore']
 if r!=old:changed.append(uid)
 if not r['passed']:
  if r==old:unchanged_flags.append(uid)
  else:introduced.append(dict(uid=uid,before=old,after=r))
 if t['newlyWhollyBuried'] or t['newlyUpwardWhollyBuried']:
  introduced.append(dict(uid=uid,reason='new-burial',terrain=t))
forms=take('government-xl-central-piers-form-regression-v1-20261021','summary.json');assert forms['forms']==5312 and forms['ordinaryFlagged']==0
for r in forms['flagged']:assert r['existingNative'] and b[r['uid']]['passed']
summary=dict(uids=['landsd/213352:0','landsd/285475:0'],checked=1207,unchangedBaselineFlags=unchanged_flags,introducedFailures=introduced,changedRows=changed,ordinaryFormsChecked=5312,ordinaryFailures=0,neighbourRegressionPassed=not introduced,installationApproved=False,qualification='All installed originals checked with identical installed-only support availability. Existing identical baseline flags receive no new approval; no newly buried triangles or introduced failures allowed. Original source acceptance remains separate.')
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
save(DOC/'summary.json',summary);r=module('piers_delta_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-original-neighbour-delta',list(dict.fromkeys(refs)),summary);print(dict(jobId=r['jobId'],**summary),flush=True)
