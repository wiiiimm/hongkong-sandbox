"""Check whether unchanged authored walls cover a source-floor terrain opening."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sham-shui-po-pool-opening-feasibility-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-sham-shui-po-pool-original-terrain-v1-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 context=read(PRIOR/'buried-source-context.json.gz');g=read(HERE/'local/government-xl-sham-shui-po-pool-current-ground-v1-20261016/runtime-geometry.json.gz')['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];floor=t[context['faceIndices']];assert np.max(np.abs(floor[:,:,1]-floor[0,0,1]))<1e-9
 region=shapely.union_all(shapely.polygons(floor[:,:,[0,2]]));assert region.geom_type=='Polygon' and not region.interiors
 helper=module('pool_opening_terrain',HERE/'xl-final-script-pass.py');terrain=np.concatenate([helper.s.terrain_triangles(ROOT/p) for p in read(PRIOR/'summary.json')['terrainPaths']]);polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain,polys=terrain[valid],polys[valid];near=shapely.intersects(polys,region);groundMax=float(terrain[near,:,1].max());floorY=float(floor[0,0,1]);assert groundMax>floorY
 coords=np.asarray(region.exterior.coords);rows=[]
 for edge,(a,b) in enumerate(zip(coords[:-1],coords[1:])):
  delta=b-a;length=float(np.linalg.norm(delta));assert length>1e-8;direction=delta/length
  offset=t[:,:,[0,2]]-a;distance=offset[:,:,0]*direction[1]-offset[:,:,1]*direction[0];collinear=np.max(np.abs(distance),axis=1)<1e-5
  projected=offset@direction;candidate=collinear&(projected.max(axis=1)>=-1e-6)&(projected.min(axis=1)<=length+1e-6)
  faceIds=np.flatnonzero(candidate);wallPolys=[];wallIds=[]
  for i in faceIds:
   p=Polygon(np.column_stack([projected[i],t[i,:,1]]))
   if p.area>1e-10:wallPolys.append(p);wallIds.append(int(i))
  band=box(0,floorY,length,groundMax);union=shapely.union_all(wallPolys);missing=band.difference(union);rows.append(dict(edge=edge,sourceBoundary=[a.tolist(),b.tolist()],lengthM=length,sourceWallFaces=wallIds,bandHeight=[floorY,groundMax],uncoveredAreaM2=float(missing.area),uncoveredWKT=missing.wkt,passed=missing.area<1e-6))
 DOC.mkdir();summary=dict(uid=context['uid'],sourceSHA256=context['sourceSHA256'],sourceFloorFaceIndices=context['faceIndices'],floorY=floorY,sourceFloorAreaM2=float(region.area),sourceFloorWKT=region.wkt,conservativeOriginalTerrainMax=groundMax,edges=len(rows),passedEdges=sum(r['passed'] for r in rows),allSourceWallsCoverOpening=all(r['passed'] for r in rows),missingWallAreaM2=sum(r['uncoveredAreaM2'] for r in rows),qualification='Conservative entire wall band up to the maximum original terrain vertex of every touching terrain face. Passing proves source walls cover a possible opening; failure is not an impossibility proof. No terrain or model geometry generated, modified or accepted.',publication=False)
 save(DOC/'boundary-walls.json.gz',dict(rows=rows));save(DOC/'summary.json',summary)
 out=module('pool_opening_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-floor-opening-wall-feasibility-v1',list(dict.fromkeys(refs)),dict(uids=[context['uid']],fullAcceptance=False,newlyInstalled=0,summary=summary));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
