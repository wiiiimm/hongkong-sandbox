"""Freeze exact upward source faces with actual continuous terrain conflicts.

Diagnostic only: no asset changes, terrain changes, acceptance or publication.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'

def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--runtime',required=True);p.add_argument('--continuous',required=True);p.add_argument('--uid',required=True);a=p.parse_args()
 assert a.batch.startswith('government-xl-') and '/' not in a.batch
 out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 c=take(a.continuous,BASE/a.continuous/(a.uid.split('/')[-1]+'.json.gz'))
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
 selected=take(a.runtime,BASE/a.runtime/'selection.json.gz');r=next(r for r in selected['rows']if r['uid']==a.uid)
 assert c['sourceSHA256']==g['sourceSHA256']==r['sourceSHA256']
 tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert digest(tri.astype('<f8').tobytes())==c['sourceBinding']['decodedWorldTrianglesSHA256']
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
 original=decode_original_world_triangles(asset.read_bytes());assert original.shape==tri.shape
 delta=float(np.abs(original-tri).max());assert delta<=1e-9,'Literal stream must retain exact original ordering and pose'
 rows=[]
 for i,f in enumerate(c['faces']):
  t=tri[i];n=np.cross(t[1]-t[0],t[2]-t[0]);norm=float(np.linalg.norm(n))
  minimum=f.get('minimum');gap=minimum.get('minimumGapM')if isinstance(minimum,dict)else None
  if norm and n[1]>.35*norm and gap is not None and gap<-.5:
   assert i in c['otherAffectedFaces'];o=original[i]
   rows.append(dict(face=i,vertices=o.tolist(),literalVertices=t.tolist(),normalYRatio=float(n[1]/norm),projectedAreaM2=float(n[1]/2),yRange=[float(o[:,1].min()),float(o[:,1].max())],rawCompleteGroundMinimum=minimum))
 assert rows,'No actual upward terrain conflict to correct'
 result=dict(uids=[a.uid],uid=a.uid,sourceSHA256=r['sourceSHA256'],rows=rows,originalLiteralMaximumDeltaM=delta,literalTriangleSHA256=c['sourceBinding']['decodedWorldTrianglesSHA256'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,physicalAcceptance=False,installationApproved=False,qualification='Exact original upward faces selected by the existing normalY>0.35 and continuous gap<-0.5m criteria. This diagnostic grants no terrain edit, physical or publication approval.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py'])
 module('upward_conflict_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-upward-terrain-conflict-context',refs,result)
 print(dict(faces=len(rows),originalLiteralMaximumDeltaM=delta),flush=True)
if __name__=='__main__':main()
