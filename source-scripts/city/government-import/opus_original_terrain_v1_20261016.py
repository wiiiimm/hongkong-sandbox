"""Acquire only official Opus terrain and compare the unchanged complete source."""
from pathlib import Path
import zipfile,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-original-terrain-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=BASE/'government-xl-opus-current-ground-v1-20261016'
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 cached=HERE/'local/government-xl-seven-new-original-closures-20261008/sheets/11-SW-14D/directory';directory=read(cached/'result.json');directory['models']=[]
 claim=reservations.claim('opus-original-terrain-'+str(uuid.uuid4()),['original-terrain:11-SW-14D'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);f=module('opus_native_terrain',HERE/'xl-final-script-pass.py');f.s.LOCAL=LOCAL;record=f.s.acquire(directory,cached/'zip-directory.bin',LOCAL/'original',include_terrain=True);paths=[]
  with zipfile.ZipFile(LOCAL/'original/11-SW-14D.zip')as z:
   for name in z.namelist():
    if name.startswith('TERRAIN')and name.endswith(('.gltf','.bin')):
     p=LOCAL/'terrain'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(p)
     if name.endswith('.gltf'):paths.append(p)
  assert paths;ground=np.concatenate([f.s.terrain_triangles(p)for p in paths]);geometry=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=read(geometry)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];b=read(PRIOR/'selection.json.gz')['rows'][0]['source']['building'];assert len(tri)==12382
  foundation=f.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));summary=dict(uid='landsd/322573:0',sourceSHA256=g['sourceSHA256'],terrainPaths=[str(p.relative_to(ROOT))for p in paths],terrainSource=record,terrainFaces=len(ground),foundation=foundation,fullAcceptance=False)
  save(DOC/'summary.json',summary);refs += [geometry,PRIOR/'selection.json.gz',cached/'result.json',cached/'zip-directory.bin',LOCAL/'original/download.json',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',Path(f.s.context.__file__),Path(f.s.context.shared.__file__)]
  refs += [p for p in(LOCAL/'terrain-repairs').rglob('*')if p.is_file()]
  result=module('opus_terrain_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-original-terrain-complete-foundation-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/322573:0'],foundation=foundation,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],foundation=foundation),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
