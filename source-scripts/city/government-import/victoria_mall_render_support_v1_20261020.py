"""Strict support on immutable captured render coordinates; no acceptance waiver."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-victoria-mall-render-support-v1-20261020'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-victoria-mall-actual-render-attributes-v1-20261020'
POD='landsd/227593:0'
UIDS=[POD,'landsd/251609:0','landsd/251614:0','landsd/251615:0']

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 receipt=read(CAP/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 refs=[Path(__file__),CAP/'result.json'];capture_path=CAP/'attributes.json.gz'
 assert digest(capture_path.read_bytes())==pins[str(capture_path.relative_to(ROOT))]
 refs.append(capture_path);capture=read(capture_path)
 assert capture['startEndAllInputsVerified'] and {r['uid'] for r in capture['rows']}==set(UIDS)
 # This phase consumes the archived exact coordinate capture, not its historical
 # mutable manifest. It grants no fresh-current or installation acceptance.
 for row in capture['rows']:assert row['sourceGeometryChanges']==0
 tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 summary=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  assert reservations.owns(lease)
  world={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in capture['rows']}
  folder=DOC/mode
  save(folder/'input.json.gz',dict(podium=world[POD].tolist(),rows=[dict(uid=u,position=t.reshape(-1).tolist(),index=list(range(len(t)*3))) for u,t in world.items() if u!=POD]))
  subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
  result=read(folder/'support.json.gz')
  for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  for row in result['rows']:
   proof=row['proof'];item=dict(uid=row['uid'],mode=mode,samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']),passed=proof['passed'],sourceWorldSHA256=digest(world[row['uid']].tobytes()),supportWorldSHA256=digest(world[POD].tobytes()))
   summary.append(item);print(item,flush=True)
 assert digest(capture_path.read_bytes())==pins[str(capture_path.relative_to(ROOT))] and reservations.owns(lease)
 save(DOC/'summary.json',dict(rows=summary,sourceOnly=True,installationApproved=False,currentMapReacceptance=False,sourceGeometryChanges=0))
 module('victoria_render_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'strict-captured-render-coordinate-original-support',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,sourceGeometryChanges=0))

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
