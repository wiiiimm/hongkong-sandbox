"""Exact finite lower-source/current carrier prism intersection inventory only.
Preserves genuine source interior overlap. No collision or support exemptions.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,cross,sub
from exact_closed_two_level_mesh_vertical_ray_20261010 import verify as ray
from exact_original_finite_triangle_contacts_20261010 import dimension
BATCH='government-xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-tower-only-current-complete-inputs-v3-20261011';CONTACT=DOC.parent/'government-xl-lippo-upper-originals-actual-basic-podium-support-diagnostic-v1-20261011'
def clean(points):
 out=[]
 for p in points:
  if not out or p!=out[-1]:out.append(p)
 if len(out)>1 and out[0]==out[-1]:out.pop()
 return out

def clip(poly,function):
 if not poly:return []
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a,b=function(p),function(q);inside=a>=0;other=b>=0
  if inside:out.append(p)
  if inside!=other:
   t=a/(a-b);out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(3)))
 return clean(out)
def polygon_dimension(poly):
 if not poly:return -1
 if len(set(poly))==1:return 0
 for p in poly[1:]:
  for q in poly[1:]:
   if any(cross(sub(p,poly[0]),sub(q,poly[0]))):return 2
 return 1

def main():
 assert not DOC.exists();inp=read(INPUT/'input.json.gz');g=read(INPUT/'complete-current-geometry.json.gz');manifestpath=ROOT/inp['currentManifest']['path'];before=manifestpath.read_bytes();assert digest(before)==inp['currentManifest']['sha256']
 for folder in [INPUT,CONTACT]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for path,sha in g['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 raw=next(r for r in g['completeCurrentBasicGeometry'] if r['uid']=='landsd/231645:0');basic=np.array(raw['position'],dtype='<f8').reshape(-1,3)[np.array(raw['index'],dtype=np.int64).reshape(-1,3)];assert basic.shape==(284,3,3)
 low,top=F(float(basic[:,:,1].min())),F(float(basic[:,:,1].max()));caps=np.flatnonzero(np.all(basic[:,:,1]==float(top),axis=1)).tolist();assert len(caps)==70
 row=inp['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];original=decode_original_world_triangles(asset.read_bytes());render=g['row'];idx=np.array(render['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
 worlds=[('providerOriginal',original),('actualLiteral',np.array(render['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[idx]),('explicitLeftAssociatedF32ModelMatrix',np.array(render['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[idx]),('explicitBalancedF32ModelMatrix',np.array(render['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[idx])]
 nodes=[n for n in read(CONTACT/'diagnostic.json.gz')['nodes'] if n['uid']==row['uid']];component={fi:n['component'] for n in nodes for fi in n['completeOwnedSourceFaceIDs']};nonrender=sorted(set(range(3597))-set(component));assert nonrender==[13,25,2091,2744];assert all(dimension(rational_face(original[fi]))<2 for fi in nonrender)
 records=[];cache={}
 for mode,world in worlds:
  key=digest(world.tobytes());assert world.shape==(3597,3,3)
  if key in cache:records.append(dict(mode=mode,**cache[key]));continue
  candidates=np.flatnonzero(world[:,:,1].min(1)<float(top));pieces=[];strict=[];above=[];below=[];tested=0
  for fi in range(3597):
   if world[fi,:,1].min()>=float(top):above.append(fi);continue
   if world[fi,:,1].max()<=float(low):below.append(fi)
   q=rational_face(world[fi]);ys=clip(clip(q,lambda p:p[1]-low),lambda p:top-p[1]);assert all(low<=p[1]<=top for p in ys)
   for cap in caps:
    if any(world[fi,:,k].max()<basic[cap,:,k].min() or world[fi,:,k].min()>basic[cap,:,k].max() for k in [0,2]):continue
    cq=rational_face(basic[cap]);area=sum(p[0]*r[2]-r[0]*p[2] for p,r in zip(cq,cq[1:]+cq[:1]));assert area!=0;sign=1 if area>0 else -1;poly=ys
    for p,r in zip(cq,cq[1:]+cq[:1]):poly=clip(poly,lambda v,p=p,r=r:sign*((r[0]-p[0])*(v[2]-p[2])-(r[2]-p[2])*(v[0]-p[0])))
    tested+=1;assert tested<=1000000
    if not poly:continue
    d=polygon_dimension(poly);point=tuple(sum(p[k] for p in poly)/len(poly) for k in range(3));record=dict(sourceFace=fi,originalRealComponent=component.get(fi),nonrenderingSourcePrimitiveNoRootCredit=fi in nonrender,currentBasicCapFace=cap,exactSourcePrimitiveDimension=dimension(q),exactClippedPolygonDimension=d,exactFiniteClippedPolygon=[[str(v) for v in p] for p in poly],exactMinimumY=str(min(p[1] for p in poly)),exactMaximumY=str(max(p[1] for p in poly)),exactMaximumDepthBelowCurrentBasicTop=str(top-min(p[1] for p in poly)))
    if d==2 and low<point[1]<top:
     proof=ray(basic,point)
     if proof['strictOddParityInterior']:
      record['strictCurrentClosedBodyInteriorWitness']=proof;record['sourceRelativeInteriorPointBarycentreOfCompleteClippedPolygon']=[str(v) for v in point];strict.append(record)
    pieces.append(record)
  result=dict(completeOwnedFaces=3597,completeCurrentBasicFaces=284,completeNonrenderingOriginalSourceFaceIDs=nonrender,zeroAreaRootOrBridgeCredit=False,wholeWorldSHA256=key,completeSourceFacesBelowCurrentBasicTop=[int(i) for i in candidates],completeSourceFacesAtOrAboveTop=above,completeSourceFacesEntirelyBelowBasicBottom=below,allCandidateSourceFacesExamined=True,completeFiniteClosedPrismIntersections=pieces,strictPositiveSourceFacetInteriorPieces=strict,originalComponentsWithGenuineCurrentBasicInterior=sorted({r['originalRealComponent'] for r in strict if r['originalRealComponent'] is not None}),maximumExactDepthBelowCurrentBasicTop=str(max((F(r['exactMaximumDepthBelowCurrentBasicTop']) for r in pieces),default=F(0))),exactCapPrismCandidatesTested=tested,collisionExemption=False,sourceFacesOmitted=0)
  cache[key]=result;records.append(dict(mode=mode,**result));save(DOC/'progress.json.gz',dict(rows=records));print(json.dumps(dict(mode=mode,completeBelowTopFaces=len(candidates),finitePieces=len(pieces),strictInteriorPieces=len(strict),interiorComponents=result['originalComponentsWithGenuineCurrentBasicInterior'],maxExactDepth=result['maximumExactDepthBelowCurrentBasicTop'])),flush=True)
 result=dict(uid=row['uid'],currentManifest=inp['currentManifest'],rawCurrentTowerBaseHKPD=row['source']['building']['baseHeightHKPD'],rawCurrentPodiumTopHKPD=raw['currentForm']['topHeightHKPD'],currentTowerPodiumEqualRecordedJoinHeight=row['source']['building']['baseHeightHKPD']==raw['currentForm']['topHeightHKPD'],rows=records,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete exact finite source-face/current BASIC two-level-prism intersections and strict source-interior closed-body witnesses. Genuine shallow penetration remains explicit. Recorded primary-current join height is contextual only, not legal ownership, original podium runtime/support credit, source role acceptance, structural claim or any generic collision exemption.')
 save(DOC/'diagnostic.json.gz',result);assert manifestpath.read_bytes()==before
 for path,sha in g['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 refs=[Path(__file__),INPUT/'input.json.gz',INPUT/'complete-current-geometry.json.gz',INPUT/'result.json',CONTACT/'diagnostic.json.gz',CONTACT/'result.json',asset,*[ROOT/path for path in g['inputHashes']]]
 refs += [HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_closed_two_level_mesh_vertical_ray_20261010.py','test_exact_closed_two_level_mesh_vertical_ray_20261010.py']]
 s=importlib.util.spec_from_file_location('lower_source_current_carrier_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-current-basic-carrier-exact-lower-original-interior-partition-diagnostic-v2-complete-zero-area-inventory',refs,dict(uids=[row['uid'],raw['uid']],completeOwnedFaces=3597,completeCurrentBasicFaces=284,currentTowerPodiumEqualRecordedJoinHeight=result['currentTowerPodiumEqualRecordedJoinHeight'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'])),flush=True)
if __name__=='__main__':main()
