"""ROOT-only41 actual failures + authenticated unchanged main source contacts.
No737-body replay, role/engineering inference, geometry edits or support waiver.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,subprocess,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_certified6170_two_original_current_physical_v3_20261014 as physical
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-tower41-main-source-contact-attribution-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
ROLE=BASE/'government-xl-upton-746-residual-saved-source-role-reconciliation-v1-20261012';MAIN=BASE/'government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012';RUNTIME=HERE/'upton_tower41_actual_support_layers_v1_20261014.mjs'
PODIUM,TOWER=physical.OWNED
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 v=read(physical.DOC/'ROOT-VERIFIED.json');receipt=read(physical.DOC/'result.json');assert v['jobId']==receipt['jobId']=='0f54a6b738ee33b15ad94ecaa71848dbcf981f2a204e2e86c6a0628e1f6aa572'and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
 finite=read(physical.finite.DOC/'complete-actual-union-finite-delta.json.gz');actors={r['uid']:r for r in finite['actors']};roles=read(ROLE/'diagnostic.json.gz');censuses={r['uid']:r['sourceOriginalBodyCensus']for r in roles['fullSourceBodyCensuses']}
 for uid in [PODIUM,TOWER]:assert censuses[uid]['completeWorldTrianglesSHA256']==next(w['wholeWorldSHA256']for w in actors[uid]['worlds']if w['mode']=='original')
 support=read(physical.DOC/'support-checks.json.gz');assert len(support['rows'])==1;support=support['rows'][0];assert support['uid']==TOWER and support['supportUid']==PODIUM and len(support['unresolved'])==41
 body={face:i for i,ids in enumerate(censuses[TOWER]['sharedEdgeConnectedComponents'])for face in ids};mapped=[]
 for f in support['unresolved']:
  assert f['originalSourceFaces'];ids=[r['faceIndex']for r in f['originalSourceFaces']];bodies=sorted({body[i]for i in ids});assert bodies==[0]
  mapped.append(dict(actualFailureVerbatim=f,incidentOriginalFaceIDs=ids,originalSourceBodies=bodies,mainBodyOnly=True,noDecorativeOrStructuralRoleInference=True))
 main=read(MAIN/'diagnostic.json.gz');reused=[]
 for row in main['rows']:
  mode=row['mode'];d=row['diagnostic'];c=d['completeActualWorldEdgeCensus']
  for uid in [PODIUM,TOWER]:assert c[uid]['completeWorldTrianglesSHA256']==next(w['wholeWorldSHA256']for w in actors[uid]['worlds']if w['mode']==mode)
  pair=next(r for r in d['mainInterfaces']if r['uid']==TOWER);assert pair['completeExactMainBodyContacts']['allPairsExamined']
  assert pair['mainFaceIDs']==censuses[TOWER]['sharedEdgeConnectedComponents'][0]and d['main12728Faces']==censuses[PODIUM]['sharedEdgeConnectedComponents'][0]
  reused.append(dict(mode=mode,actualWholeSourceWorldHashes={uid:c[uid]['completeWorldTrianglesSHA256']for uid in [PODIUM,TOWER]},exactSourceOnlyContactsVerbatim=pair['completeExactMainBodyContacts'],oldPacketGroundHashNotRelabelled=main['actualCandidateGroundSHA256'],noOldGradeOrRootPathTransfer=True))
 assert len(reused)==4 and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
 return pins,support,mapped,reused
def schema_only():
 p,s,m,r=load();return dict(passed=True,caller=ref(Path(__file__)),actualFailures=41,allOnOriginalMainBody0=True,uniqueIncidentFaces=len({i for q in m for i in q['incidentOriginalFaceIDs']}),sourceOnlyMainContactModes=4,noLayerHeightSegmentContactDBLeaseWorker=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,support,mapped,reused=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
 for folder in [physical.DOC,MAIN,ROLE]:
  r=read(folder/'result.json')
  with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 fence();DOC.mkdir(parents=True);save(DOC/'input.json',dict(actualSupportChecks=ref(physical.DOC/'support-checks.json.gz'),actualRuntimeGeometry=ref(physical.LOCAL/'runtime-geometry.json.gz')))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-layer-log.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0;pulse(True)
 layers=read(DOC/'actual41-highest-and-all-source-layers.json.gz');assert len(layers['rows'])==41
 for path,digest in layers['inputHashes'].items():q=dict(path=path,sha256=digest);check(q);refs.append(q)
 # Source-source primitives are unchanged and fully authenticated above. Fresh
 # ground-dependent proofs apply only to those exact saved main contacts.
 replay=read(physical.metadata.capture.DOC/'actual-production-replay.json.gz');ground=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);assert physical.finite.sha(ground)==pins['actualGroundSHA256']
 complete=physical.finite.baseline.CompleteGround(ground);cache={};rows=[]
 for old in reused:
  contacts=[]
  for c in old['exactSourceOnlyContactsVerbatim']['contacts']:
   points=c['exactPoints'];proofs=[]
   if c['dimension']>0:
    # Complete line; area boundaries are diagnostics only, never interior credit.
    pairs=[(points[0],points[-1])]if c['dimension']==1 else[(points[i],points[j])for i in range(len(points))for j in range(i+1,len(points))]
    for a,b in pairs:
     key=json.dumps([a,b],sort_keys=True)
     if key not in cache:cache[key]=complete.segment([a,b])
     proofs.append(dict(exactSegment=[a,b],freshCompleteCurrentGround=cache[key]));pulse()
   contacts.append(dict(originalContactVerbatim=c,freshWholeLineOrAreaChordGroundProofs=proofs,areaInteriorNotQualified=c['dimension']==2,rootRoleOrBridgeAccepted=False))
  rows.append(dict(**old,freshMainContactGroundContext=contacts));save(DOC/('completed-'+old['mode']+'.json.gz'),rows[-1]);pulse(True)
 complete.verify_binding();save(DOC/'main41-source-contact-attribution.json.gz',dict(actual41IncidentMainAttribution=mapped,actual41Layers=ref(DOC/'actual41-highest-and-all-source-layers.json.gz'),fourModeAuthenticatedMainContacts=rows,completeNewGroundSHA256=physical.finite.sha(ground),completeCurrentGroundFaces=len(ground),allOriginal138Samples97Strict41FailuresRetained=True,no737ResidualReplay=True,noOldGroundOrRoleApprovalTransfer=True,noLowerLayerHighestSupportWaiver=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton41_source_freezer').freeze(BATCH,'actual41-main-body-failed-support-all-source-layers-exact-current-main-contacts',[check(q)for q in distinct_refs(refs)],dict(uids=physical.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-actual41-main-source-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 uids=physical.finite.baseline.OWNED+[physical.SECONDARY,physical.RETAINED,physical.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton41-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
