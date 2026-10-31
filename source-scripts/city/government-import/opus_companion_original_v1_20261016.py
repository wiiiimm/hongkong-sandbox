"""Recover the exact original companion component; no placement or publication credit."""
from pathlib import Path
import zipfile,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-companion-original-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-opus-neighbour-support-v1-20261016'
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 cached=HERE/'local/government-xl-seven-new-original-closures-20261008/sheets/11-SW-14D/directory';directory=read(cached/'result.json');directory['models']=[m for m in directory['models']if m['modelId']=='B359791447501063C0'];assert len(directory['models'])==1
 claim=reservations.claim('opus-companion-original-'+str(uuid.uuid4()),['building:landsd/319559:0'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);f=module('opus_companion_recovery',HERE/'xl-final-script-pass.py');record=f.s.acquire(directory,cached/'zip-directory.bin',LOCAL/'original',include_terrain=False);paths=[]
  with zipfile.ZipFile(LOCAL/'original/11-SW-14D.zip')as z:
   for name in z.namelist():
    p=LOCAL/'decoded'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(p)
    if name.endswith('.gltf'):paths.append(p)
  assert len(paths)==1;tri=f.s.context.triangles(paths[0]);assert np.isfinite(tri).all()
  actors=BASE/'government-xl-opus-basic-ground-capture-v1-20261016/basic-actors.json.gz';actor=next(r for r in read(actors)['rows']if r['uid']=='landsd/319559:0');b=actor['building'];projection=f.s.projection_metrics(tri,Polygon(b['rings'][0],b['rings'][1:]));bounds=[tri.reshape(-1,3).min(axis=0).tolist(),tri.reshape(-1,3).max(axis=0).tolist()]
  save(DOC/'original-geometry.json.gz',dict(uid=b['uid'],position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3))))
  summary=dict(uid=b['uid'],modelId=directory['models'][0]['modelId'],faces=len(tri),bounds=bounds,projection=projection,sourceMembers=record['entries'],downloadedBytes=record['receivedBytes'],sourceGeometryChanges=0,fullAcceptance=False)
  save(DOC/'summary.json',summary);refs += [actors,cached/'result.json',cached/'zip-directory.bin',LOCAL/'original/download.json',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',Path(f.s.context.__file__),Path(f.s.context.shared.__file__),ROOT/'source-scripts/city/citywide-native/download.py']
  result=module('opus_companion_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-exact-original-companion-acquisition-v1',list(dict.fromkeys(refs)),dict(uids=[b['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],faces=len(tri),projection=projection,bounds=bounds),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
