"""UNEXECUTED: all Yoho source facets and exact edge/interface nominations.

Actual frozen current ground only. Complete bodies, zeros and all raw failures
remain diagnostic; point contacts, visual parts and contacts supply no roots.
"""
from pathlib import Path
import ast, copy, importlib.util, json, subprocess, sys, time, uuid
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-yoho-eight-pair-four-stream-finite-edge-interfaces-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PROBE=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-capture-v1'
ATTRS=BASE/'xl-terrain-recovery-20261012-yoho-eight-original-pair-current-attributes-v1'
PROBE_JOB='6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e'
PROBE_SHA='778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/146396:0','landsd/231756:0'];COUNTS=[14792,7731]
RELATED=['landsd/121143:0','landsd/55568:0','landsd/4757:0']
SOURCES=['fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08','d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167']
MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
METHOD=BASE/'government-xl-yoho-eight-four-stream-finite-edge-method-draft-20261012/METHOD.md'
PREFLIGHT=METHOD.parent/'no-worker-schema-hash-preflight.json'
HELPERS=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']

def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file() and ref(p)==pin,pin
 return p
def python_closure():
 queue=[Path(__file__),FREEZER,*[HERE/n for n in HELPERS]];out={}
 while queue:
  p=queue.pop().resolve()
  if str(p) in out:continue
  out[str(p)]=ref(p)
  for node in ast.walk(ast.parse(p.read_text())):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    for parent in [HERE,HERE.parent/'shared-modelling']:
     q=parent/(name.replace('.','/')+'.py')
     if q.is_file():queue.append(q)
 return sorted(out.values(),key=lambda p:p['path'])

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists()
 pre=read(PREFLIGHT);assert pre['passed'] and pre['noWorkerDatabaseOrLease'] and pre['draftCodePins'][str(Path(__file__).resolve().relative_to(ROOT))]==ref(Path(__file__))['sha256']
 refs=python_closure()+[ref(METHOD),ref(PREFLIGHT)];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 def complete_receipt(folder):
  r=read(folder/'result.json')
  assert r['batch']==folder.name and r['newlyInstalled']==0 and r['currentAcceptance'] is False
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for pin in r['evidenceRefs']:check(pin);pulse()
  refs.extend(r['evidenceRefs']);refs.append(ref(folder/'result.json'));return r
 for pin in pre['sourceAndCurrentInputPins']:check(pin);refs.append(pin);pulse()
 probe=complete_receipt(PROBE);attrs=complete_receipt(ATTRS)
 assert probe['jobId']==PROBE_JOB and ref(PROBE/'result.json')['sha256']==PROBE_SHA
 assert attrs['completeOriginalFaces']==22523 and attrs['uids']==UIDS
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 from exact_original_shared_edge_component_census_v2_20261011 import census
 from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
 from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
 from exact_original_shell_intersections_20261009 import rational_face,intersection_points
 from exact_original_component_contacts_20261009 import contact_measure
 selection=read(PROBE/'selection.json.gz')['rows'];rtpath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(rtpath)['rows'];actual=read(ATTRS/'actual-render-attributes.json.gz')['rows']
 assert ref(rtpath) in probe['evidenceRefs'] and ref(PROBE/'selection.json.gz') in probe['evidenceRefs'] and ref(ATTRS/'actual-render-attributes.json.gz') in attrs['evidenceRefs']
 assert [r['uid'] for r in selection]==[r['uid'] for r in runtime]==[r['uid'] for r in actual]==UIDS
 inputs=[]
 for row,rt,a,count,sha in zip(selection,runtime,actual,COUNTS,SOURCES):
  uid=row['uid'];assert uid==rt['uid']==a['uid']
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==rt['sourceSHA256']==a['sourceSHA256']==sha;refs.append(ref(asset))
  index=np.asarray(rt['index'],np.uint32).reshape(-1,3);assert len(index)==count and rt['index']==a['completeOriginalIndex']
  literal=np.asarray(rt['position'],float).reshape(-1,3);assert np.array_equal(literal,np.asarray(a['completeLiteralWorldPosition'],float).reshape(-1,3))
  positions=[literal,np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3),np.asarray(a['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)]
  lo,hi=np.asarray(row['candidate']['entry']['worldBounds'],float)
  for p in positions:
   assert p.shape==literal.shape and np.isfinite(p).all()
   assert np.all(p[:,[0,2]].min(0)>=lo[[0,2]]-1) and np.all(p[:,[0,2]].max(0)<=hi[[0,2]]+1),'Explicit arithmetic positions exceed frozen ground capture region'
  original=decode_original_world_triangles(asset.read_bytes());worlds=[original,*[p[index] for p in positions]]
  ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
  assert ground.shape[0]>0 and np.isfinite(ground).all() and all(w.shape==(count,3,3) and np.isfinite(w).all() for w in worlds)
  inputs.append((row,worlds,ground));pulse(True)
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'))
 finite_rows=[];cache={}
 for uid,(row,worlds,ground),count in zip(UIDS,inputs,COUNTS):
  gsha=digest(ground.tobytes());gxz=ground[:,:,[0,2]]
  for mode,world in zip(MODES,worlds):
   wsha=digest(world.tobytes());key=(uid,wsha,gsha);previous=cache.get(key)
   if previous is not None:
    finite_rows.append(dict(previous,mode=mode,exactCompleteWorldAndGroundReuseFromMode=previous['mode']));pulse(True);continue
   inv=census(world,list(range(count)));proofrows=[]
   for i,face in enumerate(world):
    lo=face[:,[0,2]].min(0);hi=face[:,[0,2]].max(0)
    ids=np.flatnonzero(np.all(gxz.max(1)>=lo,axis=1)&np.all(gxz.min(1)<=hi,axis=1)).tolist()
    if not ids:
     proof=dict(contract='complete-closed-AABB-no-ground-candidate-diagnostic',sourceFaceSHA256=digest(face.tobytes()),completeCurrentGroundSHA256=gsha,allProjectedBoundingCandidateOriginalGroundFacets=[],groundProjectionCovered=False,existingOrdinaryClearanceBoundProved=False,noActualGroundCoverageCredit=True)
     coarse=None;paired=None
    else:
     coarse=coarse_verify(face,ground);assert coarse['allProjectedBoundingCandidateOriginalGroundFacets']==ids
     paired=None if coarse['existingOrdinaryClearanceBoundProved'] else paired_verify(face,ground)
     proof=coarse if paired is None else paired
    assert proof['sourceFaceSHA256']==digest(face.tobytes()) and proof['completeCurrentGroundSHA256']==gsha
    proofrows.append(dict(sourceFace=i,completeOriginalCoarseProof=coarse,completeExactPairedFallback=paired,finalFiniteProof=proof,ordinaryBoundProved=proof['existingOrdinaryClearanceBoundProved'],groundProjectionCovered=proof['groundProjectionCovered'],exactNonrenderingNoSupportCredit=i in inv['exactNonrenderingOriginalFaces']))
    pulse()
    if i%100==0:
     save(LOCAL/(uid.split('/')[1].split(':')[0]+'-'+mode+'-finite-progress.json.gz'),dict(complete=False,uid=uid,mode=mode,completeWorldSHA256=wsha,completeGroundSHA256=gsha,allFaces=proofrows))
     print(json.dumps(dict(uid=uid,mode=mode,completedFaces=i+1,total=count)),flush=True)
   assert len(proofrows)==count
   output=dict(uid=uid,mode=mode,completeWorldSHA256=wsha,completeActualDrawnGroundSHA256=gsha,completeOriginalFaces=count,completeActualDrawnGroundFaces=len(ground),allFaces=proofrows,completeNonzeroEdgeCensus=inv,uncoveredSourceFaces=[p['sourceFace'] for p in proofrows if not p['groundProjectionCovered']],ordinaryUnprovedSourceFaces=[p['sourceFace'] for p in proofrows if not p['ordinaryBoundProved']],exactCompleteWorldAndGroundReuseFromMode=None)
   finite_rows.append(output);cache[key]=output
   save(DOC/(uid.split('/')[1].split(':')[0]+'-'+mode+'-complete-finite.json.gz'),output);pulse(True)
 # Exact interface existence inventory between every closed-bound-overlapping
 # nonzero body pair. One positive witness per body pair; not all contacts.
 interface_rows=[];interface_cache={}
 for m,mode in enumerate(MODES):
  tri=np.concatenate([inp[1][m] for inp in inputs]);worldsha=digest(tri.tobytes());previous=interface_cache.get(worldsha)
  if previous is not None:interface_rows.append(dict(previous,mode=mode,exactCompleteWorldReuseFromMode=previous['mode']));pulse(True);continue
  bodies=[];zeros=[];offset=0;members={}
  for uid,count in zip(UIDS,COUNTS):
   f=next(r for r in finite_rows if r['uid']==uid and r['mode']==mode);inv=f['completeNonzeroEdgeCensus']
   zeros.extend(offset+i for i in inv['exactNonrenderingOriginalFaces'])
   for ids in inv['sharedEdgeConnectedComponents']:
    globalids=[offset+i for i in ids];bodyid=len(bodies)
    assert not set(globalids)&set(members)
    for i in globalids:members[i]=bodyid
    bodies.append(dict(body=bodyid,uid=uid,globalOriginalFaces=globalids,bounds=[tri[globalids].min((0,1)).tolist(),tri[globalids].max((0,1)).tolist()]))
   offset+=count
  assert offset==22523 and sorted(list(members)+zeros)==list(range(22523)) and set(members).isdisjoint(zeros)
  low=np.asarray([b['bounds'][0] for b in bodies]);high=np.asarray([b['bounds'][1] for b in bodies]);pairs=[]
  for a in range(len(bodies)):
   pairs.extend((a,b) for b in range(a+1,len(bodies)) if np.all(low[a]<=high[b]) and np.all(low[b]<=high[a]))
  face_low=tri.min(1);face_high=tri.max(1);rational={};positive=[];points={};tested=0
  def exact(i):
   if i not in rational:rational[i]=rational_face(tri[i])
   return rational[i]
  for cursor,(a,b) in enumerate(pairs):
   left,right=bodies[a]['globalOriginalFaces'],bodies[b]['globalOriginalFaces']
   if len(left)>len(right):left,right=right,left
   right=np.asarray(right,int);witness=None
   for i in left:
    hits=right[np.all(face_low[right]<=face_high[i],axis=1)&np.all(face_high[right]>=face_low[i],axis=1)]
    for j in hits:
     j=int(j);tested+=1;ps=intersection_points(exact(i),exact(j));ids=[i,j] if members[i]==a else [j,i]
     if ps:
      measured=contact_measure(ps)
      if measured['dimension']>0:witness=dict(bodies=[a,b],globalOriginalFaces=ids,exactContact=measured);break
      if (a,b) not in points:points[a,b]=dict(bodies=[a,b],globalOriginalFaces=ids,exactContact=measured,pointOnlyNoBridgeCredit=True)
     pulse()
    if witness is not None:break
   if witness is not None:positive.append(witness)
   pulse()
   if cursor%10==0:
    save(LOCAL/(mode+'-interface-progress.json.gz'),dict(complete=False,completeWorldSHA256=worldsha,completedBodyPairs=cursor+1,totalNominatedPairs=len(pairs),positiveInterfaceNominations=positive,encounteredPointContacts=list(points.values())))
    print(json.dumps(dict(mode=mode,bodyPairs=cursor+1,total=len(pairs),positivePairs=len(positive))),flush=True)
  for p in positive:
   i,j=p['globalOriginalFaces'];assert [members[i],members[j]]==p['bodies'] and contact_measure(intersection_points(exact(i),exact(j)))==p['exactContact'];pulse()
  out=dict(mode=mode,completeWorldSHA256=worldsha,bodies=bodies,exactNonrenderingGlobalFacesRetainedUncredited=zeros,eligibleAllBodyPairs=len(bodies)*(len(bodies)-1)//2,closedInclusiveBodyBoundsCandidates=pairs,strictlyDisjointBodyPairs=len(bodies)*(len(bodies)-1)//2-len(pairs),exactFacePairsTested=tested,onePositiveDimensionalWitnessPerContactingBodyPair=positive,encounteredPointContactsPreservedUncredited=list(points.values()),pointInventoryIsNotComplete=True,allNominatedBodyPairsExamined=True,allWithinAndCrossActorBodyPairsAccounted=True,positiveContactsAreNotExposureOrRootProof=True,exactCompleteWorldReuseFromMode=None)
  interface_rows.append(out);interface_cache[worldsha]=out;save(DOC/(mode+'-complete-interfaces.json.gz'),out);pulse(True)
 for pin in refs:check(pin);pulse()
 assert ref(manifest)==start;assert reservations.owns(lease)
 output=dict(uids=UIDS,completeOriginalFaces=22523,finiteRows=finite_rows,interfaceRows=interface_rows,freshBaselineManifest=start,rawHistoricalAndFreshNegativesPreserved=ref(PROBE/'result.json'),allOriginalZeroFacetsRetainedUncredited=True,allCurrentForeignActorsRetained=True,fullNativeActorReapproval=False,noTerrainProposal=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,currentAcceptance=False,structuralRootOrBridgeCredit=False,visualRoleAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',output);pulse(True)
 spec=importlib.util.spec_from_file_location('yoho_finite_freezer',FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'yoho-complete22523-four-stream-current-finite-edge-interface-diagnostic-v1',[check(p) for p in {(r['path'],r['sha256']):r for r in refs}.values()]+[DOC/'diagnostic.json.gz']+list(LOCAL.glob('*-progress.json.gz')),dict(uids=UIDS,completeOriginalFaces=22523,allFourWorldsAccounted=True,ordinaryUnprovedSourceFaces={r['uid']+':'+r['mode']:r['ordinaryUnprovedSourceFaces'] for r in finite_rows},uncoveredSourceFaces={r['uid']+':'+r['mode']:r['uncoveredSourceFaces'] for r in finite_rows},currentAcceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 controlled=UIDS+RELATED[:2]
 claim=reservations.claim('yoho-pair-finite-interfaces-'+str(uuid.uuid4()),['building:'+u for u in controlled]+['terrain-patch:'+u for u in controlled]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
