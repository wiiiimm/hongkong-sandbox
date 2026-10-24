"""Whole foundation checks for every captured assembly coordinate mode."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex227942-four-foundations-v1-20261018';DOC=BASE/BATCH;CAP=BASE/'government-xl-apex227942-four-world-v2-20261018';PHYS=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for d in [CAP,PHYS]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 worlds=read(CAP/'world-triangles.json.gz');rows={r['uid']:r for r in read(PHYS/'selection.json.gz')['rows']};rt=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';geometry={r['uid']:r for r in read(rt)['rows']};final=module('namcheong244683_four_foundations',HERE/'xl-final-script-pass.py');results=[];cache={}
 for mode,values in worlds.items():
  for uid,r in rows.items():
   tri=np.asarray(values[uid],dtype='<f8');ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);supports=[]
   key=(uid,digest(tri.tobytes()),digest(ground.tobytes()));b=r['source']['building'];f=cache.get(key)
   if f is None:f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));cache[key]=f
   ok=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0;entry=dict(uid=uid,mode=mode,sourceSHA256=r['sourceSHA256'],completeWorldSHA256=key[1],completeSurfaceSHA256=key[2],supportUids=supports,foundation=f,strictFoundationAccepted=ok);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),entry);results.append(dict(uid=uid,mode=mode,passed=ok,buried=f['fullyBuriedTriangles']));print(results[-1],flush=True)
 save(DOC/'summary.json',dict(rows=results,allModesPassed=all(r['passed']for r in results),fullAcceptance=False));refs.extend([rt,HERE/'xl-final-script-pass.py']);out=module('namcheong244683_four_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-assembly-foundations-all-captured-modes-v1',list(set(refs)),dict(uids=sorted(rows),summary=results,allModesPassed=all(r['passed']for r in results),fullAcceptance=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
