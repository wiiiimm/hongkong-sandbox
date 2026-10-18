"""Exact Times Square facade applicability; retain every failed numerical measurement."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-functional-applicability-v1-20261019';DOC=BASE/BATCH
POD,T1,T2=['landsd/'+x+':0'for x in ['233901','254824','266146']];UIDS={POD,T1,T2};MODES={'original','literal','explicitLeftF32','explicitBalancedF32'}
def folder(name):return BASE/('government-xl-times-square-'+name+'-20261019')
def inputs():
 return dict(physical=read(folder('physical-reconciliation-v1')/'physical-reconciliation.json'),binding=read(folder('wall-binding-v1')/'exact-source-face-bindings.json.gz'),facade=read(folder('source-interpretation-v1')/'ROOT-SOURCE-INTERPRETATION.json'),overlap=read(folder('overlap-review-v1')/'ROOT-OVERLAP-REVIEW.json'),foundations=[read(folder('four-mode-foundations-v1')/(u.split('/')[1]+'-'+m+'.json'))for u in sorted(UIDS)for m in sorted(MODES)],attributions={m:read(folder('tower254824-burial-attribution-v1')/(m+'.json'))for m in MODES},contexts={u:read(folder(u.split('/')[1].split(':')[0]+'-failed-face-context-v1')/'faces.json')for u in [T1,T2]})
def qualify(physical,binding,facade,overlap,foundations,attributions,contexts):
 assert physical['completeLoaderChecksPassed'] and physical['completeNeighbourChecksPassed']
 assert not any(r['remainingReasons']for r in physical['neighbours'])
 rows={r['uid']:r for r in physical['rows']};assert set(rows)==UIDS and len(physical['rows'])==3
 keys={(u,m)for u in UIDS for m in MODES}
 assert len(binding['bindings'])==len(foundations)==12
 assert {(r['uid'],r['mode'])for r in binding['bindings']}=={(r['uid'],r['mode'])for r in foundations}==keys
 decisions={r['uid']:r for r in facade['rows']};assert set(decisions)=={T1,T2}
 assert len(binding['descriptors'])==8 and {(r['uid'],r['mode'])for r in binding['descriptors']}=={(u,m)for u in [T1,T2]for m in MODES}
 for uid,r in rows.items():
  assert r['identityAccepted']
  assert r['remainingPolicyReasons']==([]if uid==POD else['ground-contact-unresolved'])
  assert r['remainingDiagnosticReasons']==([]if uid==POD else['sampled-ground-gap-below-model-bottom'])
  assert set(r['failedFoundationModes'])==(MODES if uid==T1 else set())
  if uid!=POD:
   d=decisions[uid];c=contexts[uid];s=r['rawStrictSupport']
   assert d['reviewer']=='Codex ROOT'and d['sourceFunctionalInterpretationAccepted']and not d['physicalAccepted']and not d['installationApproved']
   assert d['sourceSHA256']==c['sourceSHA256']==r['sourceSHA256']
   assert d['supportSHA256']==c['supportSHA256']==rows[POD]['sourceSHA256']
   assert d['sourceFaceIds']==[f['faceId']for f in c['incidentFaces']]
   assert len(c['incidentFaces'])==(20 if uid==T1 else 8)and all(abs(f['normal'][1])<.01 for f in c['incidentFaces'])
   assert not s['passed']and s['wallIntersections']==0
   assert (s['samples'],s['strictContacts'],len(s['unresolved']))==((190,96,94)if uid==T1 else(207,133,74))
   assert len(c['failedSamples'])==d['failedSamples']==len(s['unresolved'])
 assert overlap['uid']==T1 and overlap['reviewer']=='Codex ROOT'and overlap['sourceOverlapInterpretationAccepted']and not overlap['installationApproved']and not overlap['aiGeometryModelling']
 assert {r['mode']for r in overlap['checks']}==MODES and len(overlap['checks'])==4
 for b in binding['bindings']:
  uid,mode=b['uid'],b['mode'];f=next(r for r in foundations if(r['uid'],r['mode'])==(uid,mode))
  assert b['sourceSHA256']==f['sourceSHA256']==rows[uid]['sourceSHA256']and b['wholeWorldSHA256']==f['wholeWorldSHA256']
  assert f['foundation']['triangles']==f['foundation']['completeTerrainTriangles']==b['completeFaces']
  if uid==T1:
   a=attributions[mode];o=next(r for r in overlap['checks']if r['mode']==mode)
   assert a['uid']==uid and a['mode']==mode and a['rawCompoundFoundation']==f['foundation']
   assert not f['strictFoundationAccepted']and not a['compoundStrictFoundationPassed']
   assert [r['faceId']for r in f['buriedFaces']]==[r['faceId']for r in a['exactFaces']]==[1092]
   assert a['terrainOnlyFoundation']['fullyBuriedTriangles']==o['terrainOnlyBuried']==0
   assert a['terrainOnlyFoundation']['completeTerrainTriangles']==b['completeFaces']
   assert f['foundation']['fullyBuriedTriangles']==o['rawCompoundBuried']==1 and f['foundation']['fullyBuriedUpwardTriangles']==0
  else:assert f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==0
  if uid!=POD:
   d=next(r for r in binding['descriptors']if(r['uid'],r['mode'])==(uid,mode));assert d['wholeWorldSHA256']==b['wholeWorldSHA256']
   assert [x['originalFaceID']for x in d['faces']]==decisions[uid]['sourceFaceIds']
   assert [x['originalFaceID']for x in d['additionalBuriedFaceDescriptors']]==([1092]if uid==T1 else[])
 return dict(uids=sorted(UIDS),sourceScopedApplicabilityAccepted=True,rawPhysicalReconciliation=physical,sourceBindings=binding['bindings'],remainingPhysicalReasons=[],strictInterfacePassed=False,strictAllFoundationsPassed=False,rawNumericalFailuresRemainFailed=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publicationApproved=False,installationApproved=False,stagedAndLiveBrowserStillRequired=True,qualification='Exact original facade-seam and wall-overlap interpretation only. All 168 failed contact samples and the compound-burial face remain numerically failed. No generic threshold changes or independent support claims. Original podium and both towers must be installed together.')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['physical-reconciliation-v1','wall-binding-v1','source-interpretation-v1','overlap-review-v1','four-mode-foundations-v1','tower254824-burial-attribution-v1']:
   p=folder(name)/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 result=qualify(**inputs());save(DOC/'qualification.json',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('times_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=sorted(UIDS),sourceScopedApplicabilityAccepted=True,strictInterfacePassed=False,strictAllFoundationsPassed=False,installationApproved=False))
if __name__=='__main__':main()
