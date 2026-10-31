"""UNEXECUTED: literal retained triangle versus collar, complete owned bodies.

No terrain construction/clipping, source changes, acceptance or publication.
Bind actual v3/v4 failures. Distinguish rectangle-only projection from actual
triangle projection and finite same-XZ height; none is support/role credit.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_closed_projection_intersection_20261010 import intersection
from exact_original_projection_coverage_20261009 import signed_area
from exact_original_triangle_pair_column_gap_20261010 import verify as column_gap
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub
from sparkle_retained_literal_terrain_construction_20261011 import dyadic_facet_boxes

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261012-sparkle-retained-literal-triangle-height-body-diagnostic-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
V3=BASE/'xl-terrain-recovery-20261011-sparkle-authentic-retained-market-terrain-candidate-v3'
V4=BASE/'xl-terrain-recovery-20261012-sparkle-authentic-retained-market-terrain-candidate-v4'
CENSUS=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-original-contact-census-v2'
ATTR=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
OWN_UIDS=['landsd/242198:0','landsd/228000:0'];UIDS=OWN_UIDS+['landsd/113733:0','landsd/138091:0']
MODES=['originalSource','actualLiteral','explicitLeftAssociatedFloat32','explicitBalancedFloat32']
COUNTS=[12875,6806];CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
REUSE='xl-terrain-recovery-20261012-sparkle-authentic-retained-market-terrain-candidate-v4.py'
HELPERS=['exact_packed_world_geometry_20261009.py','exact_original_closed_projection_intersection_20261010.py',
 'exact_original_projection_coverage_20261009.py','exact_original_triangle_pair_column_gap_20261010.py',
 'exact_original_shell_intersections_20261009.py','sparkle_retained_literal_terrain_construction_20261011.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py']

def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(pin):
 p=ROOT/pin['path'];assert p.is_file()and ref(p)==pin;return p
def load_module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dimension(points):
 if abs(signed_area(points)):return 2
 return 1 if len(set(points))>1 else 0
def nonzero(face):
 a=rational_face(face);return bool(any(cross(sub(a[1],a[0]),sub(a[2],a[0]))))

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 reuse_pin=ref(HERE/REUSE);assert reuse_pin['sha256']=='02182a7a60b21282c0c912587b3c8fd0fa29be7bc974b0c8d1124eb6e04d4b5a'
 reuse=load_module('sparkle_literal_height_current_inputs',REUSE)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs=[ref(Path(__file__)),reuse_pin,*[ref(HERE/n)for n in HELPERS]]
 assert ref(manifest)['sha256']==CURRENT
 # Reuse only the reviewed INPUT/receipt gates, never its constructor.
 start,current,rebind=reuse.current_rebind(manifest,refs);assert start['sha256']==CURRENT
 for folder,job in [(V3,'5af889d91d4c1dd611d5262f4e946b462dcc99035e75785c083be7314ece3544'),
  (V4,'200a782f35de4e5ecda340d0d2b6e6e31efaacbe39664329b13d235fa289927c'),
  (CENSUS,'37bc98c07be9da3f8ea4499d39ec048ee3d24784bc6263f73ec76ff9a31fd49d'),
  (ATTR,'80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c')]:reuse.completed(folder,job,refs)
 pins={'v3Packed':(V3/'packed-protection-inputs.json.gz','f6d81c6f5d625c81d0cea7bd66132d34a03f4b828c9781edd2f4acb108726b78'),
  'v3Finite':(V3/'packed-protection-exact-finite.json.gz','05b29fc9bf719d6af78c8af31e8470caa1e1752f1ad38da8ca515943800a5bca'),
  'v4Collars':(V4/'whole-retained-collar-inputs.json.gz','885958772aebe1f1741e5625dfc8f42dc85b1042cd5be25ec4c71f97d2d6f8a4'),
  'v4Separation':(V4/'whole-retained-collar-exact-owned-separation.json.gz','e22ce8c926545bcbce25d9fff3185fffaa3ebe3753da2324df443e6e8ff1a2ce'),
  'sourceCensus':(CENSUS/'diagnostic.json.gz','4f40dd9cc527ab874e64bc6fca7d0a4573c0e27b44ce79416a8404ee921377de')}
 for path,sha in pins.values():assert ref(path)['sha256']==sha;refs.append(ref(path))
 old=read(pins['v3Packed'][0]);protected=read(pins['v4Collars'][0]);saved=read(pins['v4Separation'][0]);source=read(pins['sourceCensus'][0])
 ground=np.asarray(protected['wholeRetainedLiteralXYZ'],float);collars=np.asarray(protected['completeOutwardDyadicCollars'],float)
 assert ground.shape==(3039,3,3)and np.isfinite(ground).all()and np.array_equal(ground,ground.astype(np.float32).astype(float))
 assert np.asarray(old['wholeRetainedLiteralXYZ'],float).tobytes()==ground.tobytes()
 assert np.array_equal(dyadic_facet_boxes([ground],collar_cells=1),collars)
 assert saved['completeWorldRows']==8 and saved['actualClosedIntersectionPairs']==77672
 inputs=read(ATTR/'literal-source-inputs.json.gz');actual=read(ATTR/'actual-render-attributes.json.gz')
 assert [r['uid']for r in inputs['rows']]==[r['uid']for r in actual['rows']]==OWN_UIDS
 arrays={};bindings=[];source_bytes=[]
 for inp,row,uid,count in zip(inputs['rows'],actual['rows'],OWN_UIDS,COUNTS):
  assert inp['uid']==row['uid']==uid
  asset=ROOT/inp['path'];assert ref(asset)['sha256']==row['sourceSHA256'];refs.append(ref(asset))
  original=decode_original_world_triangles(asset.read_bytes());assert original.shape==(count,3,3)
  source_bytes.append(original);indices=np.asarray(row['completeOriginalIndex'],int);assert len(indices)==3*count
  modes=[original]
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   pos=np.asarray(row[key],float).reshape(-1,3);assert np.isfinite(pos).all()and indices.min()>=0 and indices.max()<len(pos)
   modes.append(pos[indices].reshape(-1,3,3))
  for mode,world in zip(MODES,modes):
   arrays[mode,uid]=world;bindings.append(dict(uid=uid,mode=mode,completeFacets=count,worldSHA256=digest(world.tobytes()),sourceSHA256=row['sourceSHA256']))
 assert digest(np.concatenate(source_bytes).tobytes())==source['completeOriginalWorldSHA256']
 assert source['uids']==OWN_UIDS and source['completeOriginalFaces']==19681 and source['allSourceFacesAccounted']
 bodies=source['bodies'];zeros=source['exactNonrenderingGlobalFacesRetainedUncredited'];assert len(bodies)==25 and len(zeros)==150
 memberships={f:i for i,b in enumerate(bodies)for f in b['globalOriginalFaces']}
 assert sum(len(b['globalOriginalFaces'])for b in bodies)==len(memberships)
 assert set(memberships).isdisjoint(zeros)and set(memberships)|set(zeros)==set(range(19681))
 assert [r['uid']for r in actual['rows']]==OWN_UIDS
 # Map each deduplicated collar to ALL literal facets that produced it.
 collar_lookup={tuple(b):i for i,b in enumerate(collars)};collar_to_ground={i:[]for i in range(len(collars))}
 for j,face in enumerate(ground):
  key=tuple(dyadic_facet_boxes([face.reshape(1,3,3)],collar_cells=1)[0]);assert key in collar_lookup
  collar_to_ground[collar_lookup[key]].append(j)
 assert all(collar_to_ground.values())and sum(map(len,collar_to_ground.values()))==len(ground)
 for pin in refs:verify(pin)
 DOC.mkdir(parents=True);(DOC/'actual-current-manifest.json').write_bytes(manifest.read_bytes())
 refs.append(ref(DOC/'actual-current-manifest.json'));save(DOC/'current-input-rebind.json',rebind)
 last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 cache={};rows=[];ground_lo=ground.min(axis=1);ground_hi=ground.max(axis=1);ground_sha=digest(ground.tobytes())
 for mode in MODES:
  for uid,count,offset in zip(OWN_UIDS,COUNTS,[0,12875]):
   world=arrays[mode,uid];key=(digest(world.tobytes()),ground_sha)
   if key in cache:proof=cache[key];reused=True;pulse(True)
   else:
    records=[];projected={};nominated=0
    for i,face in enumerate(world):
     global_id=i+offset;lower,upper=face.min(axis=0),face.max(axis=0)
     candidates=np.flatnonzero(np.all(ground_lo[:,[0,2]]<=upper[[0,2]],axis=1)&np.all(ground_hi[:,[0,2]]>=lower[[0,2]],axis=1))
     nominated+=len(candidates)
     for j0 in candidates:
      j=int(j0);xz=intersection(face[:,[0,2]],ground[j][:,[0,2]])
      if not xz:pulse();continue
      assert xz;projected[i,j]=True
      low=F(float(lower[1]))-F(float(ground_hi[j,1]));high=F(float(upper[1]))-F(float(ground_lo[j,1]))
      nz_a,nz_b=nonzero(face),nonzero(ground[j]);contact=[]
      if low>0 or high<0:
       height=dict(method='conservative-complete-facet-Y-bounds',lowerGapBoundM=str(low),upperGapBoundM=str(high),exactExtremaNotClaimed=True)
      else:
       height=column_gap(face,ground[j]);assert height['exactClosedHorizontalProjectionsMeet']
       gaps=[F(r['exactGapM'])for r in height['allExactBasicFeasibleColumnVertices']];assert gaps
       low,high=min(gaps),max(gaps);height['exactMaximumFiniteColumnGapM']=str(high)
       if nz_a and nz_b:
        points=intersection_points(rational_face(face),rational_face(ground[j]))
        assert bool(points)==(low<=0<=high),'Exact height/contact predicates disagree'
        contact=[[str(v)for v in p]for p in sorted(points)]
      classification='sourceStrictlyAboveLiteralTerrain'if low>0 else 'sourceStrictlyBelowLiteralTerrain'if high<0 else 'finiteColumnHeightContact'
      records.append(dict(actorLocalFaceID=i,globalOriginalFaceID=global_id,originalBodyID=memberships.get(global_id),
       originalZeroFacet=global_id in zeros,actualNonzeroFacet=nz_a,retainedLiteralFacetID=j,
       exactClosedProjectionDimension=dimension(xz),completeClosedXZ=[[str(v)for v in p]for p in xz],
       height=height,classification=classification,actual3DIntersectionPoints=contact,
       degenerate3DFacetsRetainedUncredited=not(nz_a and nz_b),supportOrCollisionExemption=False));pulse()
     pulse()
    # Different arithmetic modes retain labels; cache ONLY byte-identical worlds.
    proof=dict(worldSHA256=key[0],retainedLiteralXYZSHA256=key[1],completeOwnedFacets=count,
     completeRetainedFacets=len(ground),completePairs=count*len(ground),inclusiveXZCandidates=nominated,
     strictlyXZBoxSeparatedPairs=count*len(ground)-nominated,actualClosedProjectedPairs=len(records),
     records=records,allOwnedFacetsAccounted=True,nonrenderingFacetsReceiveNoCredit=True)
    cache[key]=proof;reused=False
   assert proof['completeOwnedFacets']==count
   # Every saved v4 rectangle nomination is compared with each actual whole
   # retained triangle enclosed by THAT collar, using this complete pair census.
   actual_pairs={(r['actorLocalFaceID'],r['retainedLiteralFacetID'])for r in proof['records']}
   collar_rows=[]
   for prior in saved['nominations']:
    if prior['uid']!=uid or prior['mode']!=mode or prior['strictlySeparated']:continue
    i=prior['completeOriginalFaceID'];targets=collar_to_ground[prior['collarID']]
    matches=[j for j in targets if (i,j)in actual_pairs]
    collar_rows.append(dict(actorLocalFaceID=i,globalOriginalFaceID=i+offset,originalBodyID=memberships.get(i+offset),
     collarID=prior['collarID'],completeEnclosedRetainedFacetIDs=targets,actualTriangleProjectedHits=matches,
     enclosingCollarOnlyOverlap=not matches,rectangleFailureRemainsUnchanged=True))
   body_rows=[]
   for body_id,body in enumerate(bodies):
    if body['actorUID']!=uid:continue
    faces=set(body['globalOriginalFaces']);found=[r for r in proof['records']if r['globalOriginalFaceID']in faces]
    body_rows.append(dict(originalBodyID=body_id,completeOriginalFaces=body['globalOriginalFaces'],
     completeFacets=len(faces),actualProjectedPairs=len(found),heightClassifications=dict(Counter(r['classification']for r in found)),
     actual3DContactPairs=sum(bool(r['actual3DIntersectionPoints'])for r in found),noRoleOrRootCredit=True))
   rows.append(dict(uid=uid,mode=mode,reusedExactWorldTuple=reused,proof=proof,
    completeOwnedBodyRows=body_rows,priorV4CollarComparisons=collar_rows))
   save(DOC/'partial-diagnostic.json.gz',dict(complete=False,completedRows=rows));pulse(True)
 assert len(rows)==8 and sum(len(r['completeOwnedBodyRows'])for r in rows)==100
 assert sum(len(r['priorV4CollarComparisons'])for r in rows)==77672
 for pin in refs:verify(pin)
 assert ref(manifest)==start;pulse(True)
 diagnostic=dict(uids=UIDS,currentManifest=start,completeOwnedOriginalFaces=19681,completeOriginalBodies=25,
  originalZeroGlobalFaceIDsRetainedUncredited=zeros,allFourWorldBindings=bindings,
  wholeRetainedLiteralFacets=3039,collarToWholeLiteralFacetIDs=collar_to_ground,rows=rows,
  terrainConstruction=False,terrainChanges=0,sourceGeometryChanges=0,currentAcceptance=False,
  triangleShapedOutwardProtectionNotConstructed=True,missingGroundCoverageNotCertified=True,
  noSupportOrNativeReapproval=True,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',diagnostic)
 freeze=load_module('sparkle_literal_height_freeze',HELPERS[-1])
 freeze.freeze(BATCH,'sparkle-whole-owned-body-literal-retained-triangle-height-diagnostic-v1',
  [verify(p)for p in {p['path']:p for p in refs}.values()]+[DOC/'diagnostic.json.gz',DOC/'partial-diagnostic.json.gz'],
  dict(uids=UIDS,completeOwnedOriginalFaces=19681,completeBodyWorldRows=100,completeLabelledWorldRows=8,
   diagnosticOnly=True,terrainChanges=0,sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 resources=['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('sparkle-literal-height-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok']
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),
  '--ttl','3600','--',sys.executable,__file__,'--owned','--current-manifest-sha',CURRENT],cwd=ROOT,check=True)
if __name__=='__main__':main()
