"""Private source-backed terrain test; preserve all government building geometry."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset_collection_v1_20261019 import inset_faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-lower-surface-inset-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021';GROUND=BASE/'government-xl-grandiose-adjoining-ground-v1-20261021';NOM=BASE/'government-xl-grandiose-lower-surface-nomination-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,GROUND,NOM]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,path):
  assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 row=next(r for r in take(SRC,SRC/'selection.json.gz')['rows']if r['uid']=='landsd/246824:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes())
 nom=take(NOM,NOM/'surface-nomination.json.gz');assert abs(nom['summary']['projectedOverlapM2'])<1e-6
 ground=np.asarray(take(GROUND,HERE/'local'/GROUND.name/'246824:0-ground.json.gz')['completeAdjoiningTerrain']);lo,hi=tri.min((0,1)),tri.max((0,1));keep=(ground[:,:,0].max(1)>=lo[0]-2)&(ground[:,:,0].min(1)<=hi[0]+2)&(ground[:,:,2].max(1)>=lo[2]-2)&(ground[:,:,2].min(1)<=hi[2]+2);ground=ground[keep]
 out,proof=inset_faces(ground,np.asarray(nom['triangles']))
 for i,lineage in enumerate(proof['lineage']):
  if lineage['kind']=='unchanged-terrain':assert np.array_equal(out[i],ground[lineage['face']])
 save(DOC/'inset-proof.json.gz',proof);path=LOCAL/'private-source-terrain.json.gz';save(path,dict(triangles=out.tolist()));refs.append(path)
 helper=module('kowloon_private_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];foundation=helper.foundation_context(tri,out,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation);save(DOC/'residual-faces.json.gz',face_diagnostics(helper,tri,out))
 result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],originalTerrainFaces=len(ground),privateTerrainFaces=len(out),changedTerrainFaces=len(proof['changedTerrainFaceIndices']),insetAreaM2=proof['removedProjectedAreaM2'],foundation={k:v for k,v in foundation.items()if k!='components'},sourceGeometryChanges=0,viewerChanges=0,installationApproved=False,qualification='Private exact source-plane inset only. Current full actor scope, retained terrain, contact, renderer and visual acceptance remain required.')
 save(DOC/'summary.json',result);refs.extend(HERE/n for n in ['source_surface_inset_collection_v1_20261019.py','xl-final-script-pass.py','china_ferry_current_foundations_v1_20261020.py','exact_packed_world_geometry_20261009.py'])
 module('kowloon_inset_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kowloon-park-private-source-plane-inset',refs,result);print(result,flush=True)
if __name__=='__main__':main()
