"""Complete source 285509 foundation coverage using authenticated cached adjoining TIN."""
from pathlib import Path
import zlib
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source-285509-adjacent-ground-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/285509:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];consumed={}
 def take(batch,path):
  _,pins=authenticate(BASE/batch);key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];consumed[key]=pins[key];refs.extend([BASE/batch/'result.json',path]);return read(path)
 cap='government-xl-next-three-terrain-runtime-v1-20261021';rows=take(cap,BASE/cap/'selection.json.gz')['rows'];row=next(r for r in rows if r['uid']==UID);g=next(r for r in take(cap,HERE/'local'/cap/'runtime-geometry.json.gz')['rows']if r['uid']==UID);assert g['sourceSHA256']==row['sourceSHA256']
 primary='government-xl-third-original-ground-v1-20261021';original=take(primary,HERE/'local'/primary/'original-terrain.json.gz');original_tri=np.asarray(original['triangles'])
 audit='government-xl-adjoining-current-terrain-directory-audit-20261007';d=take(audit,HERE/'local'/audit/'sheets/6-SW-12C/directory/result.json')
 cache=HERE/'local/government-xxl-second-20260911/sheets/6-SW-12C';old=read(cache/'directory/result.json');assert all(old[k]==d[k]for k in ['sourceURL','etag','directorySHA256'])
 rawpath=cache/'directory/zip-directory.bin';raw=rawpath.read_bytes();assert digest(raw)==d['directorySHA256'];refs.extend([cache/'directory/result.json',rawpath]);ac=module('adjacent285509_acquire',HERE.parent/'landmark-acquisition/acquire.py');infos,_=ac.parse_directory(raw);paths=[];members=[]
 for e in infos:
  if not e.filename.startswith('TERRAIN')or not e.filename.endswith(('.gltf','.bin')):continue
  p=cache/'terrain'/e.filename;assert p.resolve().is_relative_to((cache/'terrain').resolve());v=p.read_bytes();assert len(v)==e.file_size and zlib.crc32(v)&0xffffffff==e.CRC;refs.append(p);consumed[str(p.relative_to(ROOT))]=digest(v);members.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(v),sourceCRC32=e.CRC))
  if p.suffix=='.gltf':paths.append(p)
 assert len(paths)==1;decoder=module('adjacent285509_decode',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;adj=decoder.terrain_triangles(paths[0]);low,high=row['native']['model']['worldBounds'];adj=adj[(adj[:,:,0].max(1)>=low[0]-10)&(adj[:,:,0].min(1)<=high[0]+10)&(adj[:,:,2].max(1)>=low[2]-10)&(adj[:,:,2].min(1)<=high[2]+10)];terrain=np.concatenate([original_tri,adj]);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];b=row['source']['building'];f=module('adjacent285509_foundation',HERE/'xl-final-script-pass.py').foundation_context(tri,terrain,Polygon(b['rings'][0],b['rings'][1:]));out=LOCAL/'combined-original-terrain.json.gz';save(out,dict(triangles=terrain.tolist(),sourcePaths=original['sourcePaths']+[str(p.relative_to(ROOT))for p in paths]));refs.append(out)
 save(DOC/'adjacent-provenance.json',dict(sheet='6-SW-12C',directorySHA256=d['directorySHA256'],members=members,cachedRevisionMatchesAuthenticatedAudit=True))
 result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],originalTerrainTriangles=len(original_tri),adjacentTerrainTriangles=len(adj),completeOriginalTriangles=len(tri),combinedOriginalTerrainFoundation=f,sourceGeometryChanges=0,installationApproved=False);save(DOC/'summary.json',result)
 for p,h in consumed.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE.parent/'landmark-acquisition/acquire.py']);module('adjacent285509_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'adjoining-original-terrain-complete-foundation-check',refs,result);print(f,flush=True)
if __name__=='__main__':main()
