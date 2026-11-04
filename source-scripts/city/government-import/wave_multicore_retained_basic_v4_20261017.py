"""Test whether existing non-XL BASIC companions can remain unchanged on the original podium."""
from pathlib import Path
import numpy as np,subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017';WORLD=BASE/'government-xl-wave-four-world-paths-v1-20261017';BATCH='government-xl-wave-multicore-retained-basic-v4-20261017';DOC=BASE/BATCH
UIDS=['landsd/301559:0','landsd/301561:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [CAP,WORLD]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 rows=[r for r in read(CAP/'basic-actors.json.gz')['rows']if r['uid']in UIDS];assert {r['uid']for r in rows}==set(UIDS);worlds=read(WORLD/'worlds.json.gz');podium=np.array(worlds['literal']['landsd/301560:0']);save(DOC/'input.json.gz',dict(rows=rows,podium=podium.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proofs=read(DOC/'support.json.gz');ground=np.array(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);final=module('wave_retained_basic_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  t=np.array(r['position']).reshape(-1,3)[np.array(r['index']).reshape(-1,3)];b=r['building'];f=final.foundation_context(t,np.concatenate([ground,podium]),Polygon(b['rings'][0],b['rings'][1:]));proof=next(x['proof']for x in proofs['rows']if x['uid']==r['uid']);item=dict(uid=r['uid'],actualBasicFaces=len(t),supportPassed=proof['passed'],strictContacts=proof['strictContacts'],samples=proof['samples'],compoundBuried=f['fullyBuriedTriangles'],compoundUpwardBuried=f['fullyBuriedUpwardTriangles'],complete=f['completeTerrainTriangles']==f['triangles']);summary.append(item);save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);print(item,flush=True)
 for p,h in proofs['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([tool,HERE/'xl-final-script-pass.py']);save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='Existing basic forms preserved exactly; source-specific detailed podium support diagnostics only. No source model installed, deleted or deemed corrupt. Rendering dependency and complete neighbour acceptance remain required.'))
 out=module('wave_retained_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-basic-companions-original-podium-contact-v1',list(set(refs)),dict(uids=UIDS,summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
