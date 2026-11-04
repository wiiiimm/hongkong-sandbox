"""Complete four-mode original tower foundations against current captured ground."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-four-world-foundations-v1-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-olympian-two-six-original-four-world-v1-20261018';GROUND=BASE/'government-xl-olympian-two-compound-foundations-v4-20261018'
TOWERS=['landsd/270317:0','landsd/269908:0','landsd/269839:0','landsd/269837:0'];SUPPORTS=['landsd/265851:0','landsd/239351:0']

def check(args):
 uid,mode,tri,ground,form=args;final=module('olympian_four_foundation',HERE/'xl-final-script-pass.py');f=final.foundation_context(tri,ground,Polygon(form['rings'][0],form['rings'][1:]));ok=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0
 result=dict(uid=uid,mode=mode,worldSHA256=digest(tri.tobytes()),surfaceSHA256=digest(ground.tobytes()),foundation=f,passed=ok);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),result);summary=dict(uid=uid,mode=mode,passed=ok,faces=f['triangles'],covered=f['completeTerrainTriangles'],buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles']);print(summary,flush=True);return summary

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'world-triangles.json.gz');assert set(worlds)=={'original','literal','left','balanced'};ground=np.asarray(read(GROUND/'runtime-geometry.json.gz')['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);forms={b['uid']:b for b in read(ROOT/'3d-viewer/city/data/tiles/0_-2.json')['buildings']};jobs=[]
 for mode,w in worlds.items():
  combined=np.concatenate([ground,*[np.asarray(w[u],dtype='<f8')for u in SUPPORTS]])
  for uid in TOWERS:jobs.append((uid,mode,np.asarray(w[uid],dtype='<f8'),combined,forms[uid]))
 DOC.mkdir()
 with ProcessPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,jobs))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 summary=dict(rows=results,allModesPassed=all(x['passed']for x in results),fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary);refs.extend(ROOT/p for p in pins);refs.append(HERE/'xl-final-script-pass.py')
 out=module('olympian_four_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-four-original-tower-foundations-four-worlds-v1',list(set(refs)),dict(uids=TOWERS,**summary));print(out['jobId'],flush=True)
if __name__=='__main__':main()
