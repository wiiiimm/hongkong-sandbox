"""Compare unchanged Illumination originals against authenticated original terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-original-ground-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-remaining-forty-assembly-runtime-v1-20261021';OLD=BASE/'government-xl-ronsdale-2-contact-20261005';UIDS=['landsd/255531:0','landsd/258737:0']
def main():
 assert not DOC.exists()
 _,pins=authenticate(CAP);_,oldpins=authenticate(OLD);refs=[Path(__file__),CAP/'result.json',OLD/'result.json']
 def consume(p,pins):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=consume(CAP/'selection.json.gz',pins);rows=[r for r in selection['rows']if r['uid']in UIDS];assert len(rows)==2
 runtime=consume(HERE/'local'/CAP.name/'runtime-geometry.json.gz',pins);geometries={r['uid']:r for r in runtime['rows']if r['uid']in UIDS}
 recovery=consume(OLD/'source-recovery.json',oldpins);directory=HERE/'local'/OLD.name/'sheets/11-SE-11A/directory/result.json';d=read(directory);assert d['directorySHA256']==recovery['sourceDirectorySHA256'];refs.append(directory)
 paths=[]
 for e in recovery['terrainFiles']:
  p=HERE/'local'/OLD.name/'sheets/11-SE-11A/terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
  if p.suffix=='.gltf':paths.append(p)
 decoder=module('illumination_original_terrain',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;terrain=np.concatenate([decoder.terrain_triangles(p)for p in paths]);lo=np.min([r['native']['model']['worldBounds'][0]for r in rows],axis=0);hi=np.max([r['native']['model']['worldBounds'][1]for r in rows],axis=0);terrain=terrain[(terrain[:,:,0].max(1)>=lo[0]-10)&(terrain[:,:,0].min(1)<=hi[0]+10)&(terrain[:,:,2].max(1)>=lo[2]-10)&(terrain[:,:,2].min(1)<=hi[2]+10)]
 assert len(terrain)>0
 final=module('illumination_foundations',HERE/'xl-final-script-pass.py');results=[]
 for row in rows:
  g=geometries[row['uid']];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];b=row['source']['building'];poly=Polygon(b['rings'][0],b['rings'][1:]);results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalTerrainFoundation=final.foundation_context(tri,terrain,poly),currentTerrainFoundation=final.foundation_context(tri,np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3),poly)))
 save(DOC/'selection.json.gz',dict(**{k:v for k,v in selection.items()if k!='rows'},rows=rows));save(LOCAL/'original-terrain.json.gz',dict(triangles=terrain.tolist(),sourceDirectorySHA256=recovery['sourceDirectorySHA256']));refs.extend([LOCAL/'original-terrain.json.gz',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'])
 save(DOC/'summary.json',dict(rows=results,terrainTriangles=len(terrain),installationApproved=False))
 module('illumination_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-versus-current-ground-foundations',refs,dict(uids=UIDS,rows=results,installationApproved=False));print([(r['uid'],r['originalTerrainFoundation']['fullyBuriedTriangles'],r['currentTerrainFoundation']['fullyBuriedTriangles'])for r in results],flush=True)
if __name__=='__main__':main()
