"""UNEXECUTED bounded four-stream owned/retained overlap diagnostic.

Complete 19681 owned and40865 retained facets remain accounted. Closed projected
intersection is exact, including degeneracies; 3D contacts require two nonzero
facets. No ownership, collision exemption, terrain retention or support credit.
Triangle-pair areas are not falsely described as projected union area.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_closed_projection_intersection_20261010 import intersection
from exact_original_projection_coverage_20261009 import signed_area
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-sparkle-retained-market-complete-projection-contact-diagnostic-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OWNED=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
RETAINED=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
PROBE=BASE/'government-xl-terrain-recovery-sparkle-tower-podium-current-probe-v1-20261011'
OWN_UIDS=['landsd/242198:0','landsd/228000:0'];RET_UIDS=['landsd/113733:0','landsd/138091:0'];UIDS=OWN_UIDS+RET_UIDS
COUNTS={'landsd/242198:0':12875,'landsd/228000:0':6806,'landsd/113733:0':15641,'landsd/138091:0':25224}
MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
MODES=['originalSource','actualLiteral','explicitLeftAssociatedFloat32','explicitBalancedFloat32']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(r):
 p=ROOT/r['path'];assert p.is_file()and ref(p)==r;return p
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 refs=[ref(Path(__file__)),start];receipts={}
 for folder in [OWNED,RETAINED]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for pin in receipt['evidenceRefs']:verify(pin)
  receipts[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 own_input=OWNED/'literal-source-inputs.json.gz';own_actual=OWNED/'actual-render-attributes.json.gz';ret_input=RETAINED/'native-render-inputs.json.gz';ret_actual=RETAINED/'native-render-ground.json.gz'
 for folder,paths in [(OWNED,[own_input,own_actual]),(RETAINED,[ret_input,ret_actual])]:
  for path in paths:assert ref(path)in receipts[folder.name]['evidenceRefs'];refs.append(ref(path))
 assert read(own_input)['currentManifest']==read(ret_input)['currentManifest']==start
 oi=read(own_input)['rows'];ri=read(ret_input)['rows'];oa=read(own_actual)['rows'];ra=read(ret_actual)['rows']
 assert[r['uid']for r in oi]==[r['uid']for r in oa]==OWN_UIDS
 assert[r['uid']for r in ri]==[r['uid']for r in ra]==RET_UIDS
 arrays={};bindings=[]
 for inputrow,actual in zip(oi+ri,oa+ra):
  uid=inputrow['uid'];asset=ROOT/inputrow['path']if uid in OWN_UIDS else ROOT/inputrow['sourceAsset']['path']
  assert ref(asset)['sha256']==actual['sourceSHA256'];refs.append(ref(asset));original=decode_original_world_triangles(asset.read_bytes())
  assert original.shape==(COUNTS[uid],3,3)
  ids=np.asarray(actual['completeOriginalIndex'],int);assert len(ids)==3*COUNTS[uid]
  streams=[original]
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   pos=np.asarray(actual[key],float).reshape(-1,3);assert np.isfinite(pos).all()and ids.min()>=0 and ids.max()<len(pos);streams.append(pos[ids].reshape(-1,3,3))
  for mode,tri in zip(MODES,streams):
   assert np.isfinite(tri).all();arrays[(mode,uid)]=tri;bindings.append(dict(mode=mode,uid=uid,sourceSHA256=actual['sourceSHA256'],completeFacets=len(tri),completeIndexedWorldSHA256=digest(tri.tobytes())))
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_closed_projection_intersection_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/p)for p in helpers)
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 cache={};rows=[];DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'))
 for mode in MODES:
  for uid in OWN_UIDS:
   for retained in RET_UIDS:
    a,b=arrays[(mode,uid)],arrays[(mode,retained)];key=(digest(a.tobytes()),digest(b.tobytes()))
    if key in cache:
     rows.append(dict(mode=mode,ownedUID=uid,retainedUID=retained,reusedExactWorldTuple=True,proof=cache[key]));pulse();continue
    al,ah=a.min(axis=1),a.max(axis=1);bl,bh=b.min(axis=1),b.max(axis=1);rational_a={};rational_b={};projected=[];contacts=[];zero_pairs=[];tested=0;strict3d_disjoint=0
    def exact(t,ids,i):
     if i not in ids:ids[i]=rational_face(t[i])
     return ids[i]
    # Full inclusive XZ broadphase. Every omitted face pair is strictly disjoint
    # on an exact binary axis; no epsilon, geometry welding or sampled omission.
    for i in range(len(a)):
     candidates=np.flatnonzero(np.all(bl[:,[0,2]]<=ah[i,[0,2]],axis=1)&np.all(bh[:,[0,2]]>=al[i,[0,2]],axis=1))
     for j0 in candidates:
      j=int(j0);tested+=1;xy=intersection(a[i][:,[0,2]],b[j][:,[0,2]])
      if xy:projected.append(dict(ownedFace=i,retainedFace=j,exactClosedIntersectionXZ=[[str(v)for v in p]for p in xy],exactAreaM2=str(abs(signed_area(xy)))))
      if not(np.all(bl[j]<=ah[i])and np.all(bh[j]>=al[i])):strict3d_disjoint+=1;pulse();continue
      aa,bb=exact(a,rational_a,i),exact(b,rational_b,j)
      if not any(cross(sub(aa[1],aa[0]),sub(aa[2],aa[0])))or not any(cross(sub(bb[1],bb[0]),sub(bb[2],bb[0]))):zero_pairs.append([i,j]);pulse();continue
      points=intersection_points(aa,bb)
      if points:contacts.append(dict(ownedFace=i,retainedFace=j,exactContact=contact_measure(points)))
      pulse()
     pulse()
    proof=dict(ownedFacets=len(a),retainedFacets=len(b),ownedWorldSHA256=key[0],retainedWorldSHA256=key[1],totalTrianglePairs=len(a)*len(b),exactInclusiveXZCandidatePairs=tested,strictlyXZDisjointPairs=len(a)*len(b)-tested,allClosedProjectedIntersections=projected,strictly3DDisjointAmongXZCandidates=strict3d_disjoint,exactZero3DFacetPairsRetainedUncredited=zero_pairs,allActual3DContacts=contacts,completeProjectedAndContactPairCensus=True,projectedTrianglePairAreasAreNotUnionArea=True,noCollisionExemption=True,noSupportOrTerrainRetentionCredit=True)
    cache[key]=proof;rows.append(dict(mode=mode,ownedUID=uid,retainedUID=retained,reusedExactWorldTuple=False,proof=proof));save(DOC/'partial-overlap-diagnostic.json.gz',dict(bindings=bindings,completedRows=rows,complete=False));pulse(True)
 assert len(rows)==16 and ref(manifest)==start
 for receipt in receipts.values():
  for pin in receipt['evidenceRefs']:verify(pin)
 for pin in refs:verify(pin)
 result=dict(currentManifest=start,wholeOriginalFacets=60546,completeFourStreamWorldBindings=bindings,rows=rows,retainedEntrySuppressionSemanticsUnchanged=True,allCandidateSourceFacesAccounted=True,allActualContactsAreDiagnosticOnly=True,terrainChanges=0,sourceGeometryChanges=0,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);pulse(True)
 spec=importlib.util.spec_from_file_location('sparkle_market_overlap_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-sparkle-retained-market-four-world-closed-projection-and-3d-contact-diagnostic-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz',DOC/'partial-overlap-diagnostic.json.gz'],dict(currentManifest=start,completeOriginalFacets=60546,completeLabelledWorldPairs=16,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('sparkle-market-overlap-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=7200);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','7200','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
