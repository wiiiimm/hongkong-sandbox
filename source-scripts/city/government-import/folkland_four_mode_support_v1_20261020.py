"""Whole original sources against current ground/support in four render representations."""
from pathlib import Path
import numpy as np, subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-four-mode-support-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-coverage-assembly-closure-20261007-264677-0';ATTR=BASE/'government-xl-folkland-pair-runtime-capture-v1-20261020'
PAIRS={'landsd/264677:0':'landsd/225387:0','landsd/225387:0':None}
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];worlds={'original':{}}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [ATTR]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CAP/'selection.json.gz')['rows'];capture=read(ATTR/'attributes.json.gz');assert capture['startEndAllInputsVerified']
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(raw)
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in capture['rows']}
 out=[];tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 for mode,world in worlds.items():
  folder=DOC/mode
  save(folder/'input.json.gz',dict(podium=world['landsd/225387:0'].tolist(),rows=[dict(uid=u,position=t.reshape(-1).tolist(),index=list(range(t.shape[0]*3)))for u,t in world.items()if u!='landsd/225387:0']))
  subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
  result=read(folder/'support.json.gz')
  for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  for r in result['rows']:
   out.append(dict(uid=r['uid'],mode=mode,passed=r['proof']['passed'],samples=r['proof']['samples'],strictContacts=r['proof']['strictContacts'],unresolved=len(r['proof']['unresolved'])))
 save(DOC/'summary.json',dict(rows=out,installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('star_park_four_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-four-world-strict-support',list(dict.fromkeys(refs)),dict(uids=list(PAIRS),rows=out,installationApproved=False,modelGeometryChanges=0))
if __name__=='__main__':main()
