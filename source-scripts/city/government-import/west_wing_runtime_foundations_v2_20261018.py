"""Whole original assembly against actual before/after drawn terrain, all modes."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-runtime-foundations-v2-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-west-wing-group-four-world-v1-20261018';GROUND=BASE/'government-xl-west-wing-exterior-capture-v2-20261018'
def check(args):
 stage,uid,mode,tri,ground,form=args
 helper=module('west_runtime_foundation',HERE/'olympian_two_four_world_foundations_v1_20261018.py');helper.DOC=DOC/stage
 result=helper.check((uid,mode,tri,ground,form));return dict(stage=stage,**result)
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,GROUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'worlds.json.gz');rows=read(CAP/'selection.json.gz')['rows'];work=[]
 for stage in ['before','after']:
  g=read(GROUND/(stage+'-ground.json.gz'));assert g['allDrawnFacetsIncludingVerticalAndDegenerateRetained'];ground=np.asarray(g['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3)
  for mode,w in worlds.items():
   for r in rows:work.append((stage,r['uid'],mode,np.asarray(w[r['uid']],dtype='<f8'),ground,r['source']['building']))
 DOC.mkdir()
 with ProcessPoolExecutor(max_workers=2)as pool:results=list(pool.map(check,work))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'summary.json',dict(rows=results,allAfterPassed=all(r['passed']for r in results if r['stage']=='after'),physicalAccepted=False,publication=False))
 refs.extend(ROOT/p for p in pins);refs.extend([HERE/'olympian_two_four_world_foundations_v1_20261018.py',HERE/'xl-final-script-pass.py'])
 out=module('west_runtime_foundations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-complete-before-after-runtime-foundations-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],results=results,physicalAccepted=False,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
