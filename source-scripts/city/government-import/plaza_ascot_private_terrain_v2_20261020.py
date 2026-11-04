"""Stage original government terrain under Plaza Ascot; no production writes."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-private-terrain-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SCOPE=BASE/'government-xl-plaza-ascot-current-scope-v1-20261020';GROUND=BASE/'government-xl-plaza-ascot-domain-ground-v1-20261020';UID='landsd/258411:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [SCOPE,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE,SCOPE/'scope.json');assert not scope['overlappingInstalledTerrain']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';take(SCOPE,manifest)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(SCOPE,parentpath)
 path=HERE/'local'/GROUND.name/'258411:0-ground.json.gz';data=take(GROUND,path);ground=np.asarray(data['completeAdjoiningTerrain'])
 bounds=scope['baseReplacementExtent'];keep=(ground[:,:,0].max(1)>=bounds[0])&(ground[:,:,0].min(1)<=bounds[2])&(ground[:,:,2].max(1)>=bounds[1])&(ground[:,:,2].min(1)<=bounds[3]);native=ground[keep]
 source=dict(provider='Lands Department / HKSAR',crs='EPSG:2326',verticalDatum='HKPD',sourceFiles=[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))],sheets=data['sheets'])
 builder=module('ascot_private_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 patch=builder.make_patch(dict(uids=[UID],cells=scope['baseReplacementCells']),parent,native,[source]);out=LOCAL/'candidate-terrain.json';save(out,patch);refs.append(out)
 save(DOC/'terrain-candidates.json',[dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=[UID],bounds=bounds,triangles=len(patch['nativeMesh']['index'])//3)])
 summary=dict(uids=[UID],sourceTerrainFaces=len(ground),intersectingSourceTerrainFaces=len(native),candidateFaces=len(patch['nativeMesh']['index'])//3,retainedNativeUids=scope['touchingBaseDomainNativeUids'],terrainValidationPassed=True,installationApproved=False,productionTerrainChanges=0,sourceGeometryChanges=0)
 save(DOC/'summary.json',summary);module('ascot_private_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-with-parent-edge-transition',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
