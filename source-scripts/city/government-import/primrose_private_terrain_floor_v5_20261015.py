"""Private terrain-only cap derived from two unchanged upward podium surfaces."""
from pathlib import Path
import copy,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v1_20261015 import BASE,CAPTURE,PODIUM,module
BATCH='government-xl-primrose-private-terrain-floor-v5-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PREV=BASE/'government-xl-primrose-private-terrain-join-v4-20261015';CONTEXT=BASE/'government-xl-primrose-podium-flagged-context-v1-20261015'
def main():
 assert not DOC.exists()and not LOCAL.exists();refs={}
 for folder in [PREV,CONTEXT,CAPTURE]:
  r=read(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 context=read(CONTEXT/'context.json');faceids=[1845,1846];worldfaces=[np.asarray(r['vertices'])for r in context['rows']if r['sourceFace']in faceids]
 captured=next(r for r in read(CAPTURE/'attributes.json.gz')['rows']if r['uid']==PODIUM);ix=np.asarray(captured['completeOriginalIndex']).reshape(-1,3)
 for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
  worldfaces.extend(np.asarray(captured[key]).reshape(-1,3)[ix[faceids]])
 assert all(np.ptp(t[:,1])==0 for t in worldfaces);cap=min(float(t[:,1].min())for t in worldfaces)
 footprint=shapely.union_all([shapely.Polygon(t[:,[0,2]])for t in worldfaces])
 c=read(PREV/'terrain-candidates.json')[0];patch=copy.deepcopy(read(ROOT/c['path']));m=patch['nativeMesh'];positions=np.asarray(m['position'],float).reshape(-1,3);indices=np.asarray(m['index']).reshape(-1,3);tri=positions[indices]
 hits=shapely.STRtree(shapely.polygons(tri[:,:,[0,2]])).query(footprint,predicate='intersects')
 keys={(float(v[0]),float(v[2]))for v in tri[hits].reshape(-1,3)if v[1]>cap};changed=[];before=positions.copy()
 for i,v in enumerate(positions):
  if (float(v[0]),float(v[2]))in keys and v[1]>cap:positions[i,1]=cap;changed.append(i)
 assert changed;assert np.array_equal(before[:,[0,2]],positions[:,[0,2]])
 assert np.all(positions[:,1]<=before[:,1]);affected=np.flatnonzero(np.any(np.isin(indices,changed),axis=1))
 m['position']=positions.reshape(-1).tolist();patch['id']=BATCH
 m['source']['privateScriptedFloorCap']=dict(sourceUID=PODIUM,sourceSHA256=context['sourceSHA256'],sourceFaces=faceids,capHeightHKPD=cap,originalBuildingsUnchanged=True,reason='Prevent computed terrain covering two original upward podium surfaces; retain source underside geometry.')
 DOC.mkdir();LOCAL.mkdir();path=LOCAL/'government-native-primrose-private-floor.json';save(path,patch)
 pub=module('primrose_floor_pub',HERE.parent/'island-detail-integration/publish.py')
 try:pub.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'));validation=dict(passed=True)
 except Exception as e:validation=dict(passed=False,error=repr(e))
 save(DOC/'validation.json',validation);save(DOC/'construction.json.gz',dict(previousCandidate=c,sourceFaces=faceids,capHeightHKPD=cap,touchingTerrainFaces=hits.tolist(),affectedTerrainFaces=affected.tolist(),changedVertexIndices=changed,changedBefore=before[changed].tolist(),changedAfter=positions[changed].tolist(),maximumLoweringM=float(np.max(before[:,1]-positions[:,1])),sourceGeometryChanges=0,publication=False))
 save(DOC/'terrain-candidates.json',[{**c,'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}])
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 paths=[ROOT/p for p in refs]+[Path(__file__),path,HERE/'primrose_compound_foundation_v1_20261015.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']
 module('floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-source-driven-two-floor-terrain-cap-v1',paths,dict(uids=[PODIUM],publisherTerrainValidation=validation,fullAcceptance=False,qualification='Terrain-only private candidate. Fresh renderer, full source/neighbour/foundation and visual acceptance required; no source edits or publication.'))
 print(dict(affectedFaces=len(affected),changedVertices=len(changed),cap=cap,validation=validation),flush=True)
if __name__=='__main__':main()
