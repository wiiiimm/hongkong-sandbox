"""Exact ground crossings and exposed vertices on explicit original wall faces.

Diagnostic only. No roof-path, engineering, physical or publication approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes','ground-context','uid']:p.add_argument('--'+k,required=True)
 p.add_argument('--face',action='append',type=int,required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,BASE/a.runtime/'selection.json.gz');r=next(r for r in selection['rows']if r['uid']==a.uid)
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
 attr=next(r for r in take(a.attributes,BASE/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
 ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[f]).reshape(-1,3)[ix]for m,f in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
 ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes());ids=sorted(set(a.face));assert len(ids)==len(a.face)and ids and all(0<=i<r['triangles']for i in ids);rows=[]
 for mode,tri in worlds.items():
  low=take(a.ground_context,BASE/a.ground_context/(mode+'.json.gz'));assert low['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())and low['groundSHA256']==ground_sha
  records={x['sourceFace']:x for x in low['rows']};assert set(ids)<=set(records)
  for i in ids:
   q=records[i];assert q['absoluteNormalYRatio'] is not None and q['absoluteNormalYRatio']<.25 and q['highestVertexAboveEveryOverlappingGroundFace']
   assert np.array_equal(tri[i],np.asarray(q['vertices']))
  interfaces=exact_upper_ground_interfaces(tri,ids,ground);assert {x['sourceFace']for x in interfaces}==set(ids)
  save(out/(mode+'.json.gz'),dict(sourceWorldSHA256=low['sourceWorldSHA256'],groundSHA256=ground_sha,sourceFaces=[records[i]for i in ids],exactFiniteUpperGradeInterfaces=interfaces))
  rows.append(dict(mode=mode,sourceFaces=ids,allWallLike=True,allHighestVerticesExposed=True,positiveDimensionalGroundInterfaces=len(interfaces),allFacesHaveExactUpperGroundCrossing=True))
 result=dict(uids=[a.uid],sourceSHA256=r['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,rawRoofPathFailuresPreserved=True,qualification='Each explicit unchanged original wall triangle has a positive-dimensional exact finite upper-ground interface and its own highest original vertex is exposed above every overlapping drawn ground facet, in all4streams. A triangle is convex, so the interface-to-vertex span stays on that same original face. This is grade-crossing geometry evidence only, not a claimed clear-roof path, structural root, architectural purpose or publication approval.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py']);module('exposed_face_grade_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-exposed-original-wall-finite-upper-ground-context',refs,result)
if __name__=='__main__':main()
