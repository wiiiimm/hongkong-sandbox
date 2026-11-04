"""Private source-bounded terrain continuation for seven remaining station perimeter failures."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-residual-source-floor-v2-20261015';DOC=BASE/BATCH;MODEL='B360171738601063C0'
def main():
 assert not DOC.exists();prior=BASE/'government-xl-unmapped-source-floor-candidate-v1-20261015';receipt=read(prior/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selected=[prior/(MODEL+'-private-terrain.json.gz'),prior/(MODEL+'-whole-source.json.gz')]
 for p in selected:
  q=next(q for q in receipt['evidenceRefs']if q['path']==str(p.relative_to(ROOT)));assert digest(p.read_bytes())==q['sha256']
 source=next(r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if r['modelId']==MODEL);asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==10610
 previous=read(selected[0]);baseline=np.asarray(previous['allCandidateTerrainTriplets']);ground=baseline.copy();failures=read(selected[1])['summary']['afterFailures'];assert failures==[960,961,3174,3180,4682,4686,4805]
 poly=shapely.polygons(baseline[:,:,[0,2]]);tree=shapely.STRtree(poly);caps={};nominations=[]
 for i in failures:
  face=tri[i];hits=tree.query(shapely.Polygon(face[:,[0,2]]),predicate='intersects');cap=float(face[:,1].min());normal=np.cross(face[1]-face[0],face[2]-face[0]);normal/=np.linalg.norm(normal)
  for v in baseline[hits].reshape(-1,3):
   key=tuple(v[[0,2]])
   if v[1]>cap:caps[key]=min(cap,caps.get(key,cap))
  nominations.append({'sourceFace':i,'sourceVertices':face.tolist(),'normal':normal.tolist(),'capHKPD':cap,'nominatedTerrainFaces':hits.tolist()})
 for face in ground:
  for v in face:
   key=tuple(v[[0,2]])
   if key in caps:v[1]=min(v[1],caps[key])
 assert np.array_equal(ground[:,:,[0,2]],baseline[:,:,[0,2]])and np.all(ground[:,:,1]<=baseline[:,:,1]);changed=np.flatnonzero(np.any(ground!=baseline,axis=(1,2)))
 lo,hi=tri.min((0,1)),tri.max((0,1));mask=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);regional=ground[mask];polys=shapely.polygons(regional[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;regional=regional[valid];polys=polys[valid];tree=shapely.STRtree(polys);rows=[]
 for i,face in enumerate(tri):
  area=np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]));c=face_ground_context(face,regional,polys,tree)if area else degenerate_ground_context(face,regional,polys,tree);rows.append(c)
  if i%2000==0:print(i,len(tri),flush=True)
 summary={'modelId':MODEL,'sourceSHA256':source['sourceSHA256'],'completeSourceFaces':len(tri),'beforeFailures':failures,'afterFailures':[i for i,c in enumerate(rows)if c.get('minimum')and c['minimum']['minimumGapM']<-.5],'uncovered':[i for i,c in enumerate(rows)if not c['groundProjectionCovered']],'changedTerrainFaces':len(changed),'maximumAdditionalLoweringM':float((baseline[:,:,1]-ground[:,:,1]).max()),'sourceGeometryChanges':0,'liveTerrainChanged':False,'currentRuntimeAcceptance':False}
 DOC.mkdir();save(DOC/'summary.json',summary);save(DOC/'private-terrain.json.gz',{'allCandidateTerrainTriplets':ground.tolist(),'changedFromPriorFaceIds':changed.tolist(),'sourceNominations':nominations,'originalTerrainPaths':previous['terrainPaths'],'sourceSHA256':source['sourceSHA256']});save(DOC/'whole-source.json.gz',{'faces':rows,'summary':summary})
 module('freeze_ets_floor',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-station-residual-source-floor-v2',[Path(__file__),prior/'result.json',*selected,asset,HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_degenerate_ground_context_20261009.py'],{'uids':['landsd/323703:0'],'summary':summary,'fullAcceptance':False,'historicalMapAcceptanceTransferred':False,'nextAction':'Integrate as coordinated replacement of overlapping Caine Road native terrain; perform fresh current source/whole-parent neighbour scope, support and browser checks. Private raw terrain only.'})
 print(summary,flush=True)
if __name__=='__main__':main()
