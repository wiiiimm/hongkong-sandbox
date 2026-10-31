"""Strict unchanged government assembly support, diagnostic only."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-original-support-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-plaza-ascot-assembly-original-recovery-v1-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();receipt=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};p=CAP/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=read(p)['rows'];world={}
 for row in rows:
  p=ROOT/row['assetPath'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);world[row['uid']]=decode_original_world_triangles(p.read_bytes())
 summary=[];tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 for parent,children in [('landsd/258411:0',[u for u in world if u not in ['landsd/258411:0','landsd/228446:0','landsd/127447:0']]),('landsd/228446:0',['landsd/127447:0'])]:
  assert reservations.owns(lease);folder=DOC/parent.split('/')[1]
  save(folder/'input.json.gz',dict(podium=world[parent].tolist(),rows=[dict(uid=u,position=world[u].reshape(-1).tolist(),index=list(range(world[u].size//3))) for u in children]))
  subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True);report=read(folder/'support.json.gz')
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  for r in report['rows']:
   proof=r['proof'];summary.append(dict(uid=r['uid'],supportUid=parent,samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']),passed=proof['passed']))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Source-coordinate support only. Does not approve identity, complete foundations, runtime, or publication.'))
 refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('ascot_original_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-assembly-strict-support',list(dict.fromkeys(refs)),dict(uids=list(world),rows=summary,installationApproved=False));print(summary,flush=True)

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
