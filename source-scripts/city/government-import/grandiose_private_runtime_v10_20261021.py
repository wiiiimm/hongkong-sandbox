"""Construct and strictly validate a private regional terrain replacement."""
from pathlib import Path
import json,subprocess,sys,uuid,traceback
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import grid_surface_faces
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-private-runtime-v10-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SOURCE=BASE/'government-xl-grandiose-private-terrain-v9-20261021';SCOPE=BASE/'government-xl-grandiose-regional-scope-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();refs=[Path(__file__)];pins={}
 selectionFolder=BASE/'government-xl-grandiose-assembly-capture-v1-20261021'
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [SOURCE,selectionFolder]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 assert take(SOURCE,SOURCE/'summary.json')['terrainValidationPassed']
 row=next(r for r in take(selectionFolder,selectionFolder/'selection.json.gz')['rows']if r['uid']=='landsd/246824:0')
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
 target=LOCAL/row['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);refs.append(target);row['candidate']['path']=str(target.relative_to(ROOT))
 take(selectionFolder,ROOT/'3d-viewer/city/data/manifest.json')
 terrains=take(SOURCE,SOURCE/'terrain-candidates.json')
 for t in terrains:assert digest((ROOT/t['path']).read_bytes())==t['sha256'];refs.append(ROOT/t['path'])
 save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(DOC/'terrain-candidates.json',terrains)
 tool=HERE/'acceptance-metrics-multi-retained.mjs'
 command=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==1
 for path,h in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 assert reservations.owns(lease);refs.extend([tool,LOCAL/'runtime-geometry.json.gz'])
 summary=dict(uids=[row['uid']],rows=metrics['rows'],installationApproved=False,productionChanges=0)
 r=module('yoho_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-regional-terrain-runtime',list(dict.fromkeys(refs)),summary);print(r['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/246824:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
