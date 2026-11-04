"""ROOT-only missing current BASIC tower before/after proof, exact ground unchanged.
Rest1911/52 BASIC +6650 native +allfour original worlds reuse completed exact refs.
No source geometry/terrain edits, original tower support waiver or publication.
"""
from pathlib import Path
from fractions import Fraction as F
import copy,json,sys,subprocess,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_certified6170_two_original_current_physical_v3_20261014 as physical
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-podium-standalone-tower-fallback-guard-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PODIUM,TOWER=physical.OWNED;RUNTIME=HERE/'upton_podium_standalone_tower_fallback_capture_v1_20261014.mjs'
PHYSICAL_JOB='0f54a6b738ee33b15ad94ecaa71848dbcf981f2a204e2e86c6a0628e1f6aa572'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(physical.DOC/'result.json');v=read(physical.DOC/'ROOT-VERIFIED.json');assert receipt['jobId']==v['jobId']==PHYSICAL_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
 rows=read(physical.DOC/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==physical.OWNED
 decision=read(physical.DOC/'support-ground-resolution.json');podium=next(r for r in decision['rows']if r['uid']==PODIUM);assert not podium['remainingPolicyReasons']and not podium['remainingDiagnosticReasons']
 f=next(r for r in read(physical.DOC/'foundation.json')['rows']if r['uid']==PODIUM);assert f['strictFoundationAccepted']and f['sourceSHA256']==rows[0]['sourceSHA256']
 finite=read(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz');assert finite['completeNativeActorScope']==6650 and len(finite['completeBasicRows'])==1911 and sum('findings'in r for r in finite['completeBasicRows'])==52
 assert not any(r['uid']==TOWER for r in finite['completeBasicRows'])
 for r in finite['completeBasicRows']:
  if 'findings'in r:
   for w in r['findings']['worlds']:assert not w['findings']['currentClearCandidateUnproved']
 for r in finite['actors']:
  for w in r['worlds']:assert not w['findings']['currentClearCandidateUnproved']
 replay=read(physical.metadata.capture.DOC/'actual-production-replay.json.gz')
 before=np.asarray(replay['before']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);after=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3)
 assert len(before)==9214 and len(after)==11645 and physical.finite.sha(after)==finite['newGroundSHA256']==pins['actualAfterGroundSHA256']
 assert physical.finite.sha(before)==pins['actualBeforeGroundSHA256']and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
 neighbours=read(physical.DOC/'neighbour-inputs.json.gz');tower=next(r for r in rows if r['uid']==TOWER)
 assert next(r['building']for r in neighbours['rows']if r['building']['uid']==TOWER)==tower['source']['building']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
 return pins,rows,tower,before,after,neighbours,finite
def schema_only():
 pins,rows,t,b,a,n,f=load();return dict(passed=True,caller=ref(Path(__file__)),standaloneUID=PODIUM,heldTowerUID=TOWER,completeBeforeFaces=len(b),completeAfterFaces=len(a),complete1911ExistingBASIC52AffectedRetained=True,currentNativeScope=6650,noConstructorFiniteSamplerDBLeaseWorker=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,rows,tower,before,after,neighbours,finite=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 receipt=read(physical.DOC/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PHYSICAL_JOB,)).fetchone()==('complete',receipt)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True)
 save(DOC/'fallback-input.json',dict(currentForm=tower['source']['building'],currentTile=dict(path='3d-viewer/'+tower['source']['tile'],sha256=tower['source']['tileSHA256']),currentManifest=dict(path='3d-viewer/city/data/manifest.json',sha256=physical.CURRENT),standaloneOwnedUID=PODIUM))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-constructor-log.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0;pulse(True)
 captured=read(DOC/'current-tower-BASIC-constructor.json.gz');assert captured['startEndAllInputsVerified'];row=captured['row'];assert row['uid']==TOWER and row['currentForm']==tower['source']['building']
 for path,digest in captured['inputHashes'].items():q=dict(path=path,sha256=digest);check(q);refs.append(q)
 position=np.asarray(row['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(row['index'],dtype=np.int64).reshape(-1,3);world=physical.finite.triangles(position[ix]);scope=physical.finite.closed_face_scope(world,physical.finite.baseline.DOMAIN)
 assert len(world)>0 and all(scope['wholeFaceWithinCapturedDomain'])and not scope['strictClosedBoundsDisjointFaceIDs']
 complete_before=physical.finite.baseline.CompleteGround(before);complete_after=physical.finite.baseline.CompleteGround(after);findings=[];regressed=[]
 for face in scope['selectedFaceIDs']:
  exact=[[F(float(v))for v in p]for p in world[face]];oldids,oldbind=complete_before.select(exact);newids,newbind=complete_after.select(exact)
  old=physical.finite.finite_record(world[face],before[oldids]);new=physical.finite.finite_record(world[face],after[newids])
  if old['ordinaryBoundProved']and not new['ordinaryBoundProved']:regressed.append(face)
  findings.append(dict(face=face,sourceFaceSHA256=physical.finite.sha(world[face]),completeCurrentGroundSelection=oldbind,completeCandidateGroundSelection=newbind,currentVerbatim=old,candidateVerbatim=new));pulse()
 complete_before.verify_binding();complete_after.verify_binding()
 save(DOC/'whole-current-tower-BASIC-finite-regression.json.gz',dict(uid=TOWER,completeWorldSHA256=physical.finite.sha(world),completeFaces=len(world),completeUnusedPositionVertices=len(position),completeScope=scope,beforeGroundSHA256=physical.finite.sha(before),afterGroundSHA256=physical.finite.sha(after),rows=findings,currentClearCandidateUnproved=regressed,allOldNegativeRecordsRetained=True,sourceGeometryChanges=0,physicalAccepted=False))
 # Same patch bytes and all neighbour forms, only standalone candidate membership
 # changes. Tower now receives the existing ordinary neighbour regression guard.
 neighbours=copy.deepcopy(neighbours);neighbours['candidateIds']=[PODIUM];save(DOC/'neighbour-inputs.json.gz',neighbours)
 command=['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'];fence();p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-standard-neighbours-log.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0
 report=read(DOC/'neighbour-checks.json');prior=read(physical.DOC/'neighbour-checks.json');priorrows={r['uid']:r for r in prior['rows']};actualrows={r['uid']:r for r in report['rows']};assert set(actualrows)==set(priorrows)
 for uid,r in actualrows.items():
  expected=copy.deepcopy(priorrows[uid])
  if uid==TOWER:expected['candidate']=False;expected['reasons']=r['reasons']
  assert r==expected,('Unexpected unchanged neighbour difference',uid)
 for path,digest in report['inputHashes'].items():q=dict(path=path,sha256=digest);check(q);refs.append(q)
 native=read(physical.DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons=['current-BASIC-tower-finite-regression']if regressed else[]
 reasons+=['neighbour-regression:'+r['uid']for r in report['rows']if r['reasons']and r['uid']not in resolved]
 save(DOC/'standalone-podium-prerequisites.json',dict(standaloneOwnedUID=PODIUM,heldOriginalTowerUID=TOWER,heldOriginalTowerReasonsVerbatim=read(physical.DOC/'current-physical-raw-gates.json'),standaloneCurrentTowerFallbackGuardPassed=not reasons,reasons=sorted(set(reasons)),actualPodiumPhysical=ref(physical.DOC/'result.json'),unchanged1911BASIC52FourModeNativeProof=ref(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz'),unchangedNativeFullMeshProof=ref(physical.DOC/'native-neighbour-checks.json'),qualifiedTerrainUnchanged=read(physical.DOC/'current-physical-raw-gates.json')['metadataOnlyTerrain'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_standalone_fallback_freezer').freeze(BATCH,'standalone-podium-current-uninstalled-tower-BASIC-complete-before-after-regression',[check(q)for q in distinct_refs(refs)],dict(uids=[PODIUM,TOWER,physical.SECONDARY,physical.RETAINED,physical.FOREIGN],currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-standalone-podium-tower-fallback-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 uids=physical.finite.baseline.OWNED+[physical.SECONDARY,physical.RETAINED,physical.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-podium-fallback-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
