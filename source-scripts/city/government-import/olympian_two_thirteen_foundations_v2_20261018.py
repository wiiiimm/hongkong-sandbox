"""Complete thirteen-original assembly foundations across four coordinate modes."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-thirteen-foundations-v2-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-olympian-two-park-seven-four-world-v2-20261018';OLD=BASE/'government-xl-olympian-two-six-original-four-world-v1-20261018';GROUND=BASE/'government-xl-olympian-two-three-podium-terrain-v2-20261018';SEL=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018';OLDSEL=BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018'
SUPPORTS=['landsd/265851:0','landsd/239351:0','landsd/72277:0']
def check(args):
 worker=module('all_thirteen_foundation',HERE/'olympian_two_four_world_foundations_v1_20261018.py');worker.DOC=DOC;return worker.check(args)
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,OLD,GROUND,SEL,OLDSEL]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 new=read(CAP/'world-triangles.json.gz');old=read(OLD/'world-triangles.json.gz');worlds={mode:{**old[mode],**w}for mode,w in new.items()};forms={r['uid']:r['source']['building']for folder in [SEL,OLDSEL]for r in read(folder/'selection.json.gz')['rows']};assert len(forms)==13
 groundpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';assert str(groundpath.relative_to(ROOT))in pins;capture=read(groundpath)
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 ground=np.unique(np.concatenate([np.asarray(x['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for x in capture['rows']]),axis=0);jobs=[];DOC.mkdir()
 for mode,w in worlds.items():
  combined=np.concatenate([ground,*[np.asarray(w[u],dtype='<f8')for u in SUPPORTS]])
  for uid in forms:jobs.append((uid,mode,np.asarray(w[uid],dtype='<f8'),ground if uid in SUPPORTS else combined,forms[uid]))
 with ProcessPoolExecutor(max_workers=4)as pool:results=list(pool.map(check,jobs))
 assert len(results)==52;summary=dict(uids=sorted(forms),rows=results,allModesPassed=all(x['passed']for x in results),fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([HERE/'olympian_two_four_world_foundations_v1_20261018.py',HERE/'xl-final-script-pass.py']);out=module('all_thirteen_foundations_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-thirteen-original-foundations-four-worlds-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],checks=len(results),passed=sum(r['passed']for r in results)),flush=True)
if __name__=='__main__':main()
