"""Complete adjoining-source foundations and canonical contacts, no publication."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-park-foundations-contacts-v1-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-olympian-two-park-seven-four-world-v2-20261018';OLD=BASE/'government-xl-olympian-two-six-original-four-world-v1-20261018';GROUND=BASE/'government-xl-olympian-two-pair-foundations-v1-20261018';SEL=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018'
TARGETS=['landsd/82096:0','landsd/79627:0','landsd/83600:0','landsd/79657:0','landsd/80122:0','landsd/83837:0'];SUPPORTS=['landsd/265851:0','landsd/239351:0','landsd/72277:0']
def check(args):
 worker=module('park_foundation',HERE/'olympian_two_four_world_foundations_v1_20261018.py');worker.DOC=DOC;return worker.check(args)
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];sources=[CAP,OLD,GROUND,SEL]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in sources:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'world-triangles.json.gz');old=read(OLD/'world-triangles.json.gz');forms={r['uid']:r['source']['building']for r in read(SEL/'selection.json.gz')['rows']};sources={r['uid']:r for r in read(SEL/'selection.json.gz')['rows']};sources.update({r['uid']:r for r in read(BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018/selection.json.gz')['rows']})
 groundrows=read(GROUND/'runtime-geometry.json.gz')['rows'];ground=np.unique(np.concatenate([np.asarray(x['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for x in groundrows]),axis=0);jobs=[];DOC.mkdir()
 for mode,w in worlds.items():
  allworld={**old[mode],**w};combined=np.concatenate([ground,*[np.asarray(allworld[u],dtype='<f8')for u in SUPPORTS]])
  for uid in TARGETS:jobs.append((uid,mode,np.asarray(w[uid],dtype='<f8'),combined,forms[uid]))
  uid='landsd/72277:0';jobs.append((uid,mode,np.asarray(w[uid],dtype='<f8'),ground,forms[uid]))
 with ProcessPoolExecutor(max_workers=4)as pool:results=list(pool.map(check,jobs))
 combinedworld={**old['original'],**worlds['original']};rows=[]
 for uid in TARGETS+SUPPORTS:
  t=np.asarray(combinedworld[uid],dtype='<f8');rows.append(dict(uid=uid,sourceSHA256=sources[uid]['sourceSHA256'],bottom=float(t[:,:,1].min()),position=t.reshape(-1).tolist(),index=list(range(t.size//3))))
 save(DOC/'geometry-inputs.json.gz',dict(rows=rows,towerUIDs=TARGETS,modelGeometryChanges=0))
 tool=HERE/'olympian-two-canonical-contacts-v1-20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True)
 contacts=read(DOC/'support-checks.json.gz');summary=dict(uids=TARGETS+SUPPORTS,foundationResults=results,foundationsPassed=all(x['passed']for x in results),canonicalContacts=[dict(uid=x['uid'],passed=x['interface']['passed'],reasons=x['reasons'])for x in contacts['rows']],fullAcceptance=False,newlyInstalled=0)
 save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend(HERE/n for n in ['olympian_two_four_world_foundations_v1_20261018.py','xl-final-script-pass.py','olympian-two-canonical-contacts-v1-20261018.mjs','support-interface.mjs','source-face-query.mjs','support-contact.mjs','triangle-point-index.mjs'])
 out=module('park_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-adjoining-original-foundations-contacts-v1',list(set(refs)),summary);print(out['jobId'],flush=True)
if __name__=='__main__':main()
