"""Exact lower-source paths for diagnostic rim failures; no acceptance waiver."""
from pathlib import Path
from fractions import Fraction as F
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-kai-tak-cruise-original-component-checks-v2-20261019';LAY=BASE/'government-xl-kai-tak-cruise-support-layers-v1-20261019';BATCH='government-xl-kai-tak-cruise-lower-paths-v1-20261019';DOC=BASE/BATCH
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,LAY]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 data=read(SRC/'input.json.gz');layers=read(LAY/'layers.json.gz');sources={r['uid']:r for r in read(SRC/'selection.json.gz')['rows']};checks=[];exact=[];rows=[];limit=F(1e-8)**2
 for row in data['rows']:
  uid=row['uid'];layer=next(r for r in layers['rows']if r['uid']==uid)
  if not layer['failures']:continue
  tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];lo=tri.min(1);hi=tri.max(1);details=[];failures=[]
  for fail in layer['failures']:
   p=np.asarray(fail['position']);ids=np.flatnonzero(np.all(lo<=p+1e-8,axis=1)&np.all(hi>=p-1e-8,axis=1));faces=[]
   for i in ids:
    d=squared_distance(fail['position'],tri[i].tolist())
    if d<=limit:faces.append(dict(faceIndex=int(i),vertices=tri[i].tolist(),exactSquaredDistance=str(d)))
   details.append(dict(position=fail['position'],exactStartFaces=[f['faceIndex']for f in faces],faces=faces));failures.append(dict(position=fail['position'],reason=fail['reason'],gap=fail.get('gap'),originalSourceFaces=faces))
  rows.append(dict(row,bottom=layer['bottom'],sourceSHA256=sources[uid]['sourceSHA256']));checks.append(dict(uid=uid,unresolved=failures));exact.append(dict(uid=uid,details=details));print(dict(uid=uid,samples=len(details),withoutExactStart=sum(not d['exactStartFaces']for d in details)),flush=True)
 podium=np.asarray(data['podium']);toweruids=[r['uid']for r in rows];rows.append(dict(uid='landsd/263423:0',position=podium.reshape(-1).tolist(),index=list(range(len(podium)*3))))
 save(DOC/'geometry-inputs.json.gz',dict(rows=rows,towerUIDs=toweruids));save(DOC/'support-checks.json.gz',dict(rows=checks));save(DOC/'exact-start-faces.json.gz',dict(rows=exact,squaredTolerance=str(limit)))
 tool=HERE/'olympian-two-source-face-paths-v4-20261018.mjs';subprocess.run(['node',str(tool),str(DOC),str(DOC/'paths.json.gz'),str(DOC/'exact-start-faces.json.gz')],cwd=ROOT,check=True);out=read(DOC/'paths.json.gz');summary=[{k:v for k,v in r.items()if k!='details'}for r in out['rows']];save(DOC/'summary.json',dict(rows=summary,installationApproved=False));refs.extend([tool,HERE/'support-contact.mjs',HERE/'exact_point_triangle_distance_20261018.py'])
 module('kai_lower_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-exact-lower-source-shared-edge-path-diagnostics',list(dict.fromkeys(refs)),dict(uids=toweruids,rows=summary,installationApproved=False))
if __name__=='__main__':main()
