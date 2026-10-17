"""Independent exact-source contact witness verification and bounded source-specific review."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-remaining-interfaces-v1-20261018';PATHS=BASE/'government-xl-wave-four-world-paths-v1-20261017';ASSEMBLY=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';BATCH='government-xl-wave-towers-interface-review-v1-20261018';DOC=BASE/BATCH
UIDS=['landsd/275510:0','landsd/275511:0']
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(PATHS/'worlds.json.gz');residual={(r['mode'],r['uid']):r for r in read(PRIOR/'interfaces.json.gz')['rows']};foundations={(r['mode'],r['uid']):r for r in read(ASSEMBLY/'summary.json')['rows']};rows=[]
 for r in read(PATHS/'paths.json.gz')['rows']:
  mode,uid=r['mode'],r['uid']
  if uid not in UIDS:continue
  tri=np.asarray(worlds[mode][uid]);podium=np.asarray(worlds[mode]['landsd/301560:0']);new=residual[(mode,uid)];assert {tuple(f['position'])for f in new['unresolved']}=={tuple(p['position'])for p in r['paths']};f=foundations[(mode,uid)];assert f['strictFoundationAccepted']and f['buried']==f['upwardBuried']==0 and new['strictContacts']>0
  checks=[]
  for p in r['paths']:
   w=p['witness'];assert w is not None;point=np.asarray(p['position']);contact=np.asarray(w['contact']);chain=w['sourceFaces'];seg=np.asarray(w['finiteContactSegment']);assert np.linalg.norm(seg[1]-seg[0])>1e-6
   assert len(w['sharedEdges'])==len(chain)-1 and np.linalg.norm(closest(point,tri[chain[0]])-point)<=.001
   assert np.linalg.norm(contact-point)<=.5+1e-9 and abs(np.linalg.norm(contact-point)-w['distanceM'])<=1e-9
   for q in [contact,*seg]:
    assert np.linalg.norm(closest(q,tri[chain[-1]])-q)<=.001
    assert np.linalg.norm(closest(q,podium[w['supportFace']])-q)<=.001
    assert np.linalg.norm(q-point)<=.5+1e-8
   for i,edge in enumerate(w['sharedEdges']):
    edge=np.asarray(edge);assert np.linalg.norm(edge[1]-edge[0])>1e-9
    # The recorded crossing belongs to an actual identical edge of both original faces.
    shared=set(map(tuple,tri[chain[i]]))&set(map(tuple,tri[chain[i+1]]));assert len(shared)>=2
    for q in edge:
     assert np.linalg.norm(closest(q,tri[chain[i]])-q)<=.001 and np.linalg.norm(closest(q,tri[chain[i+1]])-q)<=.001 and np.linalg.norm(q-point)<=.5+1e-8
   checks.append(dict(position=p['position'],verified=True,distanceM=w['distanceM'],sourceFaces=chain,supportFace=w['supportFace']))
  rows.append(dict(mode=mode,uid=uid,strictContacts=new['strictContacts'],verifiedResidualConnections=len(checks),maximumConnectionDistanceM=max(x['distanceM']for x in checks),checks=checks));print({k:v for k,v in rows[-1].items()if k!='checks'},flush=True)
 assert len(rows)==8
 review=dict(uids=UIDS,sourceSpecificInterfaceInterpretationAccepted=True,fullAcceptance=False,installationApproved=False,currentMapAcceptance=False,rawStrictWarningsPreserved=True,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,rows=rows,reason='These two exact originals already contact the original podium extensively. Every remaining vertical-ray failure has a finite local original-surface connection to that same podium, independently checked in all four coordinate modes, while complete source foundations retain zero buried faces. The ray warning is resolved as original interface/edge geometry for these exact source tuples, not a floating whole building or changed coordinate. This is a source-specific interpretation of existing local connection evidence; no generic policy limit changes and no engineering certification.',remaining=['Current complete identity/source binding and affected-neighbour acceptance','Other assembly source interface reviews, including301562 and195000 and retained194544','Current runtime dependency/fallback and complete staged/live browser acceptance','Guarded publication and installed ledger recording'])
 save(DOC/'ROOT-INTERFACE-REVIEW.json',review);refs=[Path(__file__),PRIOR/'result.json',HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/p for p in pins]];out=module('wave_towers_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-wave-original-towers-source-specific-interface-review-v1',refs,dict(uids=UIDS,sourceSpecificInterfaceInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
