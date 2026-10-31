"""Whole original podium against authenticated government terrain; diagnostic only."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tower6803-original-terrain-foundation-v1-20261020'
DOC=BASE/BATCH
CAP=BASE/'government-xl-tower6803-current-capture-v1-20261020'
FACES=BASE/'government-xl-tower6803-buried-faces-v1-20261020'
def main():
 assert not DOC.exists()
 refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,FACES]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
  refs.append(p);return read(p)
 rt=consume(HERE/'local'/CAP.name/'runtime-geometry.json.gz')
 selection=consume(CAP/'selection.json.gz')
 faces=consume(FACES/'15047:0.json')
 folder=HERE/'local/government-xl-hanford-plaza-terrain-continuation-v5-20261005/sheets/6-SW-11C'
 proof=read(folder/'original/download.json');directory=read(folder/'directory/result.json')
 assert proof['directorySHA256']==directory['directorySHA256']
 assert proof['terrainGeometryIncluded'] and proof['sheet']==directory['sheet']==folder.name
 refs.extend([folder/'original/download.json',folder/'directory/result.json'])
 files=[e for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]
 assert any(e['name'].endswith('.gltf') for e in files)
 for e in files:
  p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 second=module('tower6803_original_tin_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
 terrain=np.concatenate([second.terrain_triangles(folder/'terrain'/e['name']) for e in files if e['name'].endswith('.gltf')])
 final=module('tower6803_original_tin_foundation',HERE/'xl-final-script-pass.py')
 row=next(r for r in selection['rows'] if r['uid']=='landsd/15047:0')
 g=next(r for r in rt['rows'] if r['uid']==row['uid'])
 t=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert len(t)==1924 and digest(t.tobytes())==faces['sourceWorldSHA256']
 b=row['source']['building'];foundation=final.foundation_context(t,terrain,Polygon(b['rings'][0],b['rings'][1:]))
 save(DOC/'foundation.json',foundation)
 vertices=np.asarray([r['vertices'] for r in faces['rows']]);points=np.concatenate([vertices,vertices.mean(1)[:,None,:]],axis=1)
 polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
 h=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain[valid],shapely.STRtree(polys[valid])).reshape(-1,4)
 rows=[dict(faceId=r['faceId'],upward=r['upward'],originalTerrainGapsM=(points[i,:,1]-h[i]).tolist(),currentTerrainGapsM=r['groundOnlyGapsM']) for i,r in enumerate(faces['rows'])]
 save(DOC/'flagged-face-comparison.json',dict(rows=rows,terrainTriangles=len(terrain),sourceFiles=files,installationApproved=False))
 refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);refs.extend(p for p in (HERE/'local'/BATCH).rglob('*') if p.is_file())
 result=module('tower6803_original_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-podium-government-terrain-diagnostic',refs,dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],foundation=foundation,flaggedFaces=rows,originalTerrainOnly=True,fullAcceptance=False))
 print(dict(jobId=result['jobId'],terrainTriangles=len(terrain),foundation=foundation),flush=True)
if __name__=='__main__':main()
