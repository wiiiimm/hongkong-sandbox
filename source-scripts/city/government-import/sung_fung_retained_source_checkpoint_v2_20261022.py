"""Verify retained-terrain progress and persist the exact remaining original-source hold."""
import subprocess,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sung-fung-retained-source-checkpoint-v2-20261022'
RUNTIME='government-xl-sung-fung-retained-native-runtime-v1-20261022';NEIGH='government-xl-sung-fung-retained-native-neighbours-v3-20261022'
IDENT='government-xl-validated-parent-return-followthrough-v1-20261022-candidates-79098-0-identity';OLD='government-xl-validated-parent-return-followthrough-v1-20261022-candidates-79098-0-runtime'
NAMES=['government-xl-validated-parent-return-followthrough-v1-20261022','government-xl-sung-fung-retained-native-candidate-v1-20261022',RUNTIME,NEIGH,IDENT,OLD]
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)];verified=[];pins={}
 for name in NAMES:
  r,ps=authenticate(BASE/name);refs.append(BASE/name/'result.json');verified.append(dict(batch=name,jobId=r['jobId'],exactNeonReadback=True))
  for p,h in ps.items():
   assert p not in pins or pins[p]==h
   if p not in pins:assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p);pins[p]=h
 current=read(HERE/'local'/RUNTIME/'runtime-geometry.json.gz')['rows'][0];prior=read(HERE/'local'/OLD/'runtime-geometry.json.gz')['rows'][0]
 assert current['uid']==prior['uid']=='landsd/79098:0'
 assert all(current[k]==prior[k]for k in ['sourceSHA256','position','index'])
 identity=read(BASE/IDENT/'79098:0/identity.json');assert identity['passed'] and identity['proof']['identityAccepted']
 metrics=read(BASE/RUNTIME/'metrics.json');m=metrics['rows'][0];policy=module('sung_fung_source_policy',HERE/'acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=m['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile'])
 assert reasons==['ground-contact-unresolved'],reasons
 n=read(BASE/NEIGH/'summary.json');assert n['forms']==26 and not n['basicFlags']and len(n['nativeResolved'])==len(n['requiredNativeUids'])==5
 doc.mkdir()
 tests=['test_retained_terrain_inset_clip_v1.mjs','test_native_dependency_context_v1.mjs','test_surveyed_fallback_support_geometry_v1.mjs']
 with(doc/'tests.log').open('w')as log:subprocess.run(['node','--test',*[str(HERE/p)for p in tests]],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 refs.extend(HERE/p for p in tests);refs.append(HERE/'acceptance-policy.py')
 result=dict(uids=['landsd/79098:0'],sourceSHA256=m['sourceSHA256'],verifiedJobs=verified,distinctCurrentReferenceHashesVerified=len(pins),sourceStreamsUnchanged=True,currentCompleteModelFaces=len(current['index'])//3,baseFormsChecked=26,basicRegressions=0,nativeNeighboursPassed=n['nativeResolved'],remainingPolicyReasons=reasons,lowRimGapRangeM=[m['minLowGap'],m['maxLowGap']],humanStatus='held-unknown',heldReason='original-source-ground-contact-gap',nextStep='Inspect original government source hierarchy, support records and alternative official ground revisions. No source movement, invented footing or threshold waiver.',requiresHumanDecision=False,aiGeometryModellingRequired=False,newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Retained native replacement is private and validated; exact actual source remains 0.199–0.200m above ground, exceeding unchanged 0.1m contact gate. Source acceptance and installation remain incomplete.')
 save(doc/'summary.json',result)
 module('sung_fung_source_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-source-retained-terrain-progress-and-hold',refs,result)
 print(dict(faces=result['currentCompleteModelFaces'],baseForms=26,nativeNeighboursPassed=5,remaining=reasons,lowRimGapRangeM=result['lowRimGapRangeM']),flush=True)
if __name__=='__main__':main()
