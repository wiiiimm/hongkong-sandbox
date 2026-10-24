"""Complete thirteen-original assembly foundations across four coordinate modes."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-six-foundations-contacts-v1-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-park-avenue239350-six-four-world-v1-20261018';GROUND=BASE/'government-xl-park-avenue239350-joint-validation-v1-20261018'
SUPPORTS=['landsd/239350:0','landsd/240161:0','landsd/227455:0']
TARGETS=['landsd/80093:0','landsd/81847:0','landsd/82015:0']
def check(args):
 worker=module('all_thirteen_foundation',HERE/'olympian_two_four_world_foundations_v1_20261018.py');worker.DOC=DOC;return worker.check(args)
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,GROUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'world-triangles.json.gz');sources={r['uid']:r for folder in [GROUND,BASE/'government-xl-park-avenue239350-base-neighbour-identity-runtime-v1-20261018'] for r in read(folder/'selection.json.gz')['rows']};forms={u:r['source']['building'] for u,r in sources.items()};assert len(forms)==6 and set(worlds)=={'original','literal','left','balanced'}
 groundpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';assert str(groundpath.relative_to(ROOT))in pins;capture=read(groundpath)
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 ground=np.unique(np.concatenate([np.asarray(x['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for x in capture['rows']]),axis=0);jobs=[];DOC.mkdir()
 for mode,w in worlds.items():
  combined=np.concatenate([ground,*[np.asarray(w[u],dtype='<f8') for u in SUPPORTS]])
  for uid in forms:jobs.append((uid,mode,np.asarray(w[uid],dtype='<f8'),ground if uid in SUPPORTS else combined,forms[uid]))
 with ProcessPoolExecutor(max_workers=4)as pool:results=list(pool.map(check,jobs))
 contacts=[]
 tool=HERE/'olympian-two-canonical-contacts-v1-20261018.mjs'
 for mode,w in worlds.items():
  rows=[]
  for uid in TARGETS+SUPPORTS:
   t=np.asarray(w[uid],dtype='<f8');rows.append(dict(uid=uid,sourceSHA256=sources[uid]['sourceSHA256'],bottom=float(t[:,:,1].min()),position=t.reshape(-1).tolist(),index=list(range(t.size//3))))
  directory=DOC/mode;save(directory/'geometry-inputs.json.gz',dict(rows=rows,towerUIDs=TARGETS,modelGeometryChanges=0))
  subprocess.run(['node',str(tool),str(directory)],cwd=ROOT,check=True)
  for row in read(directory/'support-checks.json.gz')['rows']:contacts.append(dict(uid=row['uid'],mode=mode,passed=row['interface']['passed'],reasons=row['reasons']))
 refs.extend(HERE/n for n in ['olympian-two-canonical-contacts-v1-20261018.mjs','support-interface.mjs','source-face-query.mjs','support-contact.mjs','triangle-point-index.mjs'])
 assert len(results)==24 and len(contacts)==12;summary=dict(uids=sorted(forms),rows=results,contacts=contacts,allContactsPassed=all(r['passed'] for r in contacts),allModesPassed=all(x['passed']for x in results),fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([HERE/'olympian_two_four_world_foundations_v1_20261018.py',HERE/'xl-final-script-pass.py']);out=module('all_thirteen_foundations_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-six-original-foundations-contacts-four-worlds-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],checks=len(results),passed=sum(r['passed']for r in results)),flush=True)
if __name__=='__main__':main()
