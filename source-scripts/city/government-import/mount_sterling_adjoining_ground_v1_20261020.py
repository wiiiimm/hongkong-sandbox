"""Acquire complete adjoining government terrain and diagnose immutable XL sources.
Fresh source revisions are recorded independently; this grants no installation approval.
"""
from pathlib import Path
import json,sys,uuid,zipfile,numpy as np
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-mount-sterling-adjoining-ground-v1-20261020';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';INDEX=HERE.parent/'landmark-acquisition/index.json'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 receipt=read(SRC/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[r for r in read(SRC/'selection.json.gz')['rows']if r['uid']in ['landsd/289787:0']];assert len(rows)==1;index=read(INDEX);assert index['completePagination']and index['spatialReference']['wkid']==2326
 sheets={};byuid={}
 for row in rows:
  lo,hi=row['candidate']['entry']['worldBounds'];bounds=box(lo[0]+834500-2,816500-hi[2]-2,hi[0]+834500+2,816500-lo[2]+2)
  selected=[f['attributes']for f in index['features']if Polygon(f['geometry']['rings'][0]).intersects(bounds)]
  assert selected;byuid[row['uid']]=sorted(f['SHEETNO']for f in selected);sheets.update({f['SHEETNO']:f for f in selected})
 save(DOC/'selection.json',dict(sheetsByUid=byuid,indexSHA256=digest(INDEX.read_bytes()),sourceReceipt=receipt['jobId']))
 helper=module('next_adjoining_decode',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;final=module('next_adjoining_foundation',HERE/'xl-final-script-pass.py');ground={};refs=[Path(__file__),INDEX,SRC/'result.json',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'];acquisitions=[]
 for sheet,attrs in sorted(sheets.items()):
  folder=LOCAL/'sheets'/sheet;directory,_=helper.recovery.scan(attrs,folder/'directory');directory['models']=[]
  acquired=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original',include_terrain=True)
  terrainpaths=[]
  with zipfile.ZipFile(folder/'original'/(sheet+'.zip'))as z:
   assert len(z.namelist())==len(set(z.namelist()))
   for name in z.namelist():
    if name.startswith('TERRAIN')and name.endswith(('.gltf','.bin')):
     p=folder/'terrain'/helper.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(p)
     if name.endswith('.gltf'):terrainpaths.append(p)
  assert terrainpaths,sheet
  ground[sheet]=np.concatenate([helper.terrain_triangles(p)for p in terrainpaths])
  rec=dict(sheet=sheet,etag=directory['etag'],directorySHA256=directory['directorySHA256'],terrainPaths=[str(p.relative_to(ROOT))for p in terrainpaths],triangles=len(ground[sheet]))
  acquisitions.append(rec);save(DOC/'acquisitions.json',acquisitions)
  refs.extend(folder/p for p in ['directory/result.json','directory/zip-directory.bin','original/download.json']);assert reservations.owns(lease);print('Acquired',sheet,len(ground[sheet]),flush=True)
 summaries=[]
 for row in rows:
  uid=row['uid'];tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert len(tri)==row['triangles'];terrain=np.concatenate([ground[sheet]for sheet in byuid[uid]]);b=row['source']['building']
  f=final.foundation_context(tri,terrain,Polygon(b['rings'][0],b['rings'][1:]));key=uid.split('/')[1];save(DOC/(key+'.json'),dict(uid=uid,sheets=byuid[uid],sourceSHA256=row['sourceSHA256'],foundation=f,freshTerrainRevision=True,installationApproved=False));save(LOCAL/(key+'-ground.json.gz'),dict(completeAdjoiningTerrain=terrain.tolist(),sheets=byuid[uid]))
  item=dict(uid=uid,**{k:v for k,v in f.items()if k!='components'});summaries.append(item);print(item,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins);refs.extend(p for p in (LOCAL/'terrain-repairs').rglob('*')if p.is_file());refs.extend(LOCAL.glob('*-ground.json.gz'))
 save(DOC/'summary.json',dict(rows=summaries,freshTerrainRevision=True,installationApproved=False))
 module('next_adjoining_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'mount-sterling-complete-adjoining-government-ground-diagnostics',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=summaries,freshTerrainRevision=True,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 import subprocess
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
