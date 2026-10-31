"""Exact current-ground cover of the unchanged pier's complete residual lower facets."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_ground_line_cover_v1_20261030 import prove as line
from exact_ground_polygon_cover_v1_20261030 import prove as area
P='government-xl-disneyland-piers-after-passenger-'
BATCH=P+'75642-fallback-lower-face-cover-v1-20261030'
UID='landsd/75642:0'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'exact_ground_line_cover_v1_20261030.py',HERE/'exact_ground_polygon_cover_v1_20261030.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 def take(suffix,path):
  b=P+suffix
  if b not in pins:pins[b]=authenticate(base/b)[1];refs.append(base/b/'result.json')
  assert digest(path.read_bytes())==pins[b][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 def doc(s,n):return take(s,base/(P+s)/n)
 runtime='all-basic-fallback-patch-runtime-v2-20261030';buried='all-basic-fallback-patch-buried-v2-20261030';attrbatch='joint-attributes-v1-20261030'
 selected=next(r for r in doc(runtime,'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==selected['sourceSHA256']=='49cdebceca290d6ceccf3e1891546efbafa28218ae144da7c389190773c302c0';refs.append(asset)
 attr=next(r for r in doc(attrbatch,'attributes.json.gz')['rows']if r['uid']==UID);index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds={'packed':decode_original_world_triangles(asset.read_bytes())}
 for f in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:worlds[f]=np.asarray(attr[f]).reshape(-1,3)[index]
 ctx=doc(buried,'75642:0.json');ids=[f['faceIndex']for f in ctx['buriedFaces']];assert len(ids)==26 and all(not f['upward']for f in ctx['buriedFaces'])
 g=next(r for r in take(runtime,HERE/'local'/(P+runtime)/'runtime-geometry.json.gz')['rows']if r['uid']==UID);ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 rows=[];failures=[]
 for mode,tri in worlds.items():
  assert len(tri)==18007
  for faceid in ids:
   face=tri[faceid];top=float(face[:,1].max());assert top<2.505
   points=np.unique(face[:,[0,2]],axis=0);lo,hi=points.min(0),points.max(0)
   mask=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[1])&(ground[:,:,2].min(1)<=hi[1]);selected_ground=ground[mask];faceids=np.flatnonzero(mask).tolist()
   try:
    assert len(points)>=2,'Point primitive requires a separate exact point proof'
    rational=[tuple(F(float(x))for x in p)for p in points]
    dim2=len(points)==3 and (rational[1][0]-rational[0][0])*(rational[2][1]-rational[0][1])!=(rational[1][1]-rational[0][1])*(rational[2][0]-rational[0][0])
    if dim2:
     proof=area(face[:,[0,2]],top,selected_ground);proof['completeGroundFaceIndices']=[faceids[i]for i in proof['groundFaces']]
    else:
     proof=line(points[0],points[-1],top,selected_ground)
     for piece in proof['pieces']:piece['completeGroundFaceIndex']=faceids[piece['groundFace']]
    rows.append(dict(mode=mode,sourceFaceId=faceid,sourceVertices=face.tolist(),sourceMaximumHeightM=top,proof=proof))
   except AssertionError as exc:failures.append(dict(mode=mode,sourceFaceId=faceid,reason=str(exc),sourceVertices=face.tolist()))
 result=dict(uids=[UID],sourceSHA256=selected['sourceSHA256'],completeOriginalFaces=18007,residualBuriedFaceIds=ids,rows=rows,failures=failures,allResidualFacetsCovered=not failures,sourceGeometryChanges=0,sourcePoseChanges=0,ordinaryBurialPolicyPassed=False,physicalAcceptance=False,installationApproved=False,qualification='Complete residual lower facets against actual proposed ground in all four source streams. Exact line or area cover of a conservative whole-facet ceiling, no epsilon or sampling. No native-government burial claim or source/physical acceptance. Fallback-ground preservation and source interface interpretation remain separate.')
 save(out/'summary.json',result);module('pier_lower_cover_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-residual-lower-facet-current-ground-cover',refs,result);print(dict(proofs=len(rows),failures=failures))
if __name__=='__main__':main()
