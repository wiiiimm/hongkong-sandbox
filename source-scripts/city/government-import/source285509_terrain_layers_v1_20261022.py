"""Locate all original terrain layers at canonical failed vertices/centres; diagnostic only."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source-285509-terrain-layers-v1-20261022';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(batch,p):
  _,pins=authenticate(BASE/batch);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',p]);return read(p)
 name='government-xl-source-285509-adjacent-ground-v1-20261022';terrain=np.asarray(take(name,HERE/'local'/name/'combined-original-terrain.json.gz')['triangles']);loc='government-xl-source-285509-failure-locations-v1-20261022';groups=take(loc,BASE/loc/'failure-locations.json.gz')['groups'];faces=np.asarray([t for g in groups for t in g['triangles']]);ids=[i for g in groups for i in g['canonicalRuntimeFaceIds']];points=np.concatenate([faces,faces.mean(1)[:,None,:]],axis=1).reshape(-1,3)
 polygons=shapely.polygons(terrain[:,:,[0,2]]);valid=np.flatnonzero(shapely.area(polygons)>1e-10);polygons=polygons[valid];tree=shapely.STRtree(polygons);pairs=tree.query(shapely.points(points[:,[0,2]]),predicate='intersects');heights=[[]for p in points]
 for pi,ti in pairs.T:
  faceid=int(valid[ti]);f=terrain[faceid];coeff=np.linalg.solve(np.column_stack([f[:,0],f[:,2],np.ones(3)]),f[:,1]);h=float(coeff@[points[pi,0],points[pi,2],1]);heights[pi].append(dict(terrainFace=faceid,height=h))
 rows=[]
 for i,(point,values)in enumerate(zip(points,heights)):
  distinct=[]
  for h in sorted(v['height']for v in values):
   if not distinct or h-distinct[-1]>1e-5:distinct.append(h)
  rows.append(dict(runtimeFace=ids[i//4],sample=i%4,point=point.tolist(),terrainLayers=values,distinctHeights=distinct))
 summary=dict(uids=['landsd/285509:0'],sampleCount=len(points),missingSamples=sum(not r['terrainLayers']for r in rows),multipleHeightSamples=sum(len(r['distinctHeights'])>1 for r in rows),lowerLayerWithinHalfMetreSamples=sum(any(h<=r['point'][1]+.5 for h in r['distinctHeights'])for r in rows),installationApproved=False,sourceGeometryChanges=0,qualification='Exact projected-intersection samples, no sampling tolerance or acceptance waiver. Multiple heights do not authorise selecting a lower layer.')
 save(DOC/'layers.json.gz',dict(rows=rows,terrainFaceOrder='combined-original-terrain.json.gz exact order'));save(DOC/'summary.json',summary);module('285509_layers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-terrain-height-layer-diagnostic',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
