"""Account for the complete authored floor and inclined basin walls, without edits."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sham-shui-po-pool-basin-source-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-sham-shui-po-pool-original-terrain-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 context=read(PRIOR/'buried-source-context.json.gz');geom=HERE/'local/government-xl-sham-shui-po-pool-current-ground-v1-20261016/runtime-geometry.json.gz';g=read(geom)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];floor=set(context['faceIndices']);y0=float(t[list(floor),:,1].min());cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);norm=np.linalg.norm(cross,axis=1);ny=np.divide(cross[:,1],norm,out=np.zeros(len(t)),where=norm>1e-12)
 vertices=defaultdict(set);keys=[]
 for i,tri in enumerate(t):
  vs=[tuple(np.round(v,5)) for v in tri];keys.append(vs)
  for v in vs:vertices[v].add(i)
 # Nominate original inclined walls only. The eventual complete boundary proof
 # must establish the perimeter, not this connectivity selector alone.
 eligible=(ny>0)&(ny<.1)&(t[:,:,1].min(axis=1)>=y0-1e-7)
 found=set(floor);queue=deque(floor)
 while queue:
  i=queue.popleft()
  for v in keys[i]:
   for j in vertices[v]:
    if j not in found and eligible[j]:found.add(j);queue.append(j)
 ids=sorted(found);basin=t[ids];polys=shapely.polygons(basin[:,:,[0,2]]);mask=shapely.union_all(polys);assert mask.geom_type=='Polygon' and not mask.interiors;area=float(shapely.area(polys).sum());assert abs(area-mask.area)<1e-6
 # Every exterior point is obtained from original source vertices. Record its
 # complete incident source heights to prove an authored continuous top rim.
 boundary=[]
 for x,z in mask.exterior.coords[:-1]:
  matches=np.where((np.abs(basin[:,:,0]-x)<1e-8)&(np.abs(basin[:,:,2]-z)<1e-8));ys=basin[matches[0],matches[1],1];assert len(ys);boundary.append(dict(x=float(x),z=float(z),minY=float(ys.min()),maxY=float(ys.max())))
 rim=[v['minY'] for v in boundary]+[v['maxY'] for v in boundary];rimRange=[min(rim),max(rim)]
 DOC.mkdir();save(DOC/'basin-source.json.gz',dict(uid=context['uid'],sourceSHA256=context['sourceSHA256'],sourceFaceIndices=ids,floorFaceIndices=sorted(floor),triangles=basin.tolist(),footprintWKT=mask.wkt,outerBoundary=boundary))
 summary=dict(uid=context['uid'],floorFaces=len(floor),inclinedWallFaces=len(found-floor),sourceFaces=len(ids),projectedAreaM2=float(mask.area),projectedOverlapM2=area-mask.area,completeOuterRimHeightRangeM=rimRange,flatOuterRim=max(rim)-min(rim)<1e-7,minimumHeightM=y0,allFaceCoordinatesUnchanged=True,fullAcceptance=False,publication=False)
 save(DOC/'summary.json',summary);refs +=[geom,ROOT/'3d-viewer/city/world.js']
 out=module('pool_basin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-authored-pool-floor-inclined-walls-v1',list(dict.fromkeys(refs)),dict(uids=[context['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
