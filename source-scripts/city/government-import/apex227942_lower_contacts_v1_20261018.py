"""Whole lower-envelope contact context in four coordinate modes; no acceptance waiver."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-apex227942-four-world-v2-20261018';PHYS=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';BATCH='government-xl-apex227942-lower-contacts-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for folder in [CAP,PHYS]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PHYS/'selection.json.gz')['rows'][0];uid=row['uid'];worlds=read(CAP/'world-triangles.json.gz');p=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';ground=np.asarray(read(p)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);refs.append(p);save(DOC/'ground.json.gz',dict(rows=[dict(uid=uid,terrainTriangles=ground.tolist())]));summary=[]
 for mode,values in worlds.items():
  t=np.asarray(values[uid],dtype='<f8');model=DOC/(mode+'-model.json.gz');output=DOC/(mode+'-contacts.json');save(model,dict(rows=[dict(uid=uid,sourceSHA256=row['sourceSHA256'],triangles=t.tolist(),worldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],worldTrianglesSHA256=digest(t.tobytes()))]))
  with(DOC/(mode+'.log')).open('w')as log:subprocess.run(['node',str(HERE/'original-lower-profile-contact-diagnostic-v3.mjs'),str(model.relative_to(ROOT)),str((DOC/'ground.json.gz').relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  data=read(output)
  for p,h in data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
  result=data['rows'][0];summary.append(dict(mode=mode,**{k:result[k]for k in ['checks','lowerChecks','missingTerrain','missingLowerProfile','minLowerGap','maxLowerGap','lowerWithinStrictContact','lowerBelowPenetrationLimit','contactFaceOrientations']}));print(summary[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));out=module('apex_lower_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-current-four-world-lower-envelope-contact-diagnostic-v1',list(set(refs)),dict(uids=[uid],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
