"""Node private terrain on an exactly Float32-representable XZ lattice."""
from pathlib import Path
import copy,importlib.util
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_private_terrain_join_v1_20261015 import height
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-primrose-private-terrain-join-v1-20261015';BATCH='government-xl-primrose-private-terrain-join-v4-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;GRID=2**-10

def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(PREV/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 candidate=read(PREV/'terrain-candidates.json')[0];patch=copy.deepcopy(read(ROOT/candidate['path']));t=np.asarray(patch['nativeMesh']['position']).reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)];polys=shapely.polygons(t[:,:,[0,2]]);assert np.all(shapely.area(polys)>1e-10)
 snapped=shapely.set_precision(polys,GRID);lines=shapely.union_all(shapely.boundary(snapped),grid_size=GRID);cells=list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(lines)))));tree=shapely.STRtree(polys);points={};output=[];lineage=[];max_delta=0
 for cell in cells:
  if cell.area<=1e-10:continue
  centre=cell.representative_point();hits=tree.query(centre,predicate='dwithin',distance=2*GRID);assert len(hits)
  source=int(min(hits,key=lambda i:polys[i].distance(centre)))
  for part in shapely.get_parts(shapely.constrained_delaunay_triangles(cell)):
   if part.area<=1e-10:continue
   face=[]
   for x,z in list(part.exterior.coords)[:3]:
    key=(x,z)
    if key not in points:
     point=shapely.Point(x,z);hits=tree.query(point,predicate='dwithin',distance=2*GRID);assert len(hits);distance=min(polys[i].distance(point)for i in hits);nearest=[int(i)for i in hits if polys[i].distance(point)<=distance+1e-12];points[key]=max(height(t[i],x,z)for i in nearest)
    y=points[key];max_delta=max(max_delta,abs(y-height(t[source],x,z)));face.append([x,y,z])
   output.append(face);lineage.append(source)
 out=np.asarray(output);patch['nativeMesh']['position']=out.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(out)*3));patch['nativeMesh']['source']['privateScriptedJoin']['sharedEdgeNoding']=dict(projectedGridM=GRID,maximumVertexPlaneDifferenceM=max_delta,originalBuildingsUnchanged=True);patch['id']=BATCH
 DOC.mkdir();LOCAL.mkdir();p=LOCAL/'government-native-primrose-private-join.json';save(p,patch)
 spec=importlib.util.spec_from_file_location('pub',HERE.parent/'island-detail-integration/publish.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
 try:pub.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'));validation=dict(passed=True)
 except Exception as e:validation=dict(passed=False,error=repr(e))
 save(DOC/'validation.json',validation);save(DOC/'construction.json.gz',dict(previousCandidate=candidate,previousFaces=len(t),triangles=len(out),cells=len(cells),vertexCount=len(points),savedFaceLineage=lineage,maximumVertexPlaneDifferenceM=max_delta,projectedGridM=GRID,sourceGeometryChanges=0,publication=False,installationApproved=False));save(DOC/'terrain-candidates.json',[{**candidate,'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes()),'triangles':len(out)}])
 refs=[ROOT/q['path']for q in r['evidenceRefs']]+[PREV/'result.json',Path(__file__),HERE/'primrose_private_terrain_join_v1_20261015.py',p,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']
 spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'private-terrain-float32-representable-edge-noding-v4',refs,dict(uids=['landsd/74569:0','landsd/74570:0','landsd/74573:0'],publisherTerrainValidation=validation,fullAcceptance=False,qualification='Shared edge repair of private computed terrain only; original government building bytes unchanged; runtime and physical review pending.'));print(dict(triangles=len(out),maxDelta=max_delta,validation=validation),flush=True)
if __name__=='__main__':main()
