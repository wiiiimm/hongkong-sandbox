"""Complete canonical Oi Sin foundations in captured source-coordinate modes."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-oi-sin-four-world-capture-v1-20261017';PHYS=BASE/'government-xl-oi-sin-qualified-terrain-pair-v2-20261017';BOUND=BASE/'government-xl-oi-sin-four-world-boundary-v2-20261017';BATCH='government-xl-oi-sin-four-world-foundations-v2-20261017';DOC=BASE/BATCH;T='landsd/256280:0';P='landsd/91128:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,CAP,BOUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 assert read(BOUND/'summary.json')['allModesComplete']
 rtpath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';rt=read(rtpath);grounds={g['uid']:np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)for g in rt['rows']};sources={r['uid']:r for r in read(PHYS/'selection.json.gz')['rows']};worlds=read(CAP/'world-triangles.json.gz');final=module('oi_all_world_foundation',HERE/'xl-final-script-pass.py');rows=[];seen={}
 for mode,world in worlds.items():
  tri={u:np.asarray(t,float)for u,t in world.items()}
  for uid in [T,P]:
   ground=np.concatenate([grounds[uid],tri[P]])if uid==T else grounds[uid];key=(uid,digest(tri[uid].tobytes()),digest(ground.tobytes()))
   if key in seen:rows.append(dict(mode=mode,uid=uid,reusedRow=seen[key],strictFoundationAccepted=rows[seen[key]]['strictFoundationAccepted']));continue
   b=sources[uid]['source']['building'];f=final.foundation_context(tri[uid],ground,Polygon(b['rings'][0],b['rings'][1:]));passed=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0;seen[key]=len(rows);rows.append(dict(mode=mode,uid=uid,sourceWorldSHA256=key[1],groundSHA256=key[2],foundation=f,strictFoundationAccepted=passed));print(dict(mode=mode,uid=uid,passed=passed),flush=True)
 save(DOC/'foundations.json',dict(rows=rows,allModesPassed=all(r['strictFoundationAccepted']for r in rows),groundContract='Exact current captured drawn terrain reused; source and support geometry vary over captured original/literal/left/balanced modes. Not a universal GPU camera guarantee.',fullAcceptance=False))
 refs.extend([rtpath,HERE/'xl-final-script-pass.py']);out=module('oi_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-complete-canonical-foundation-four-source-modes-v2',list(set(refs)),dict(uids=[T,P],allModesPassed=all(r['strictFoundationAccepted']for r in rows),fullAcceptance=False,nextStep='Resolve exact source boundary roles and compound identity; full neighbours/browser/publication remain.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
